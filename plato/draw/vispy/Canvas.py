import bisect
import logging

import numpy as np
import vispy, vispy.app
import vispy.gloo as gloo

logger = logging.getLogger(__name__)

class NoopContextManager:
    def __enter__(self, *args, **kwargs):
        pass

    def __exit__(self, *args, **kwargs):
        pass

_VERTEX_SHADERS = {}
_FRAGMENT_SHADERS = {}

_VERTEX_SHADERS['post_translucency'] = """
   attribute vec2 a_position;
   varying vec2 v_texcoord;
   void main(void)
   {
       gl_Position = vec4(a_position, 0.0, 1.0);
       v_texcoord = (a_position + 1.0)/2.0;
   }
   """

_VERTEX_SHADERS['post_outlines'] = _VERTEX_SHADERS['post_translucency']

_VERTEX_SHADERS['post_fxaa'] = """
uniform vec2 resolution;

attribute vec2 a_position;

varying vec2 v_texcoord;
varying vec2 v_rgbNW;
varying vec2 v_rgbNE;
varying vec2 v_rgbSW;
varying vec2 v_rgbSE;
varying vec2 v_rgbM;

//This is best suited for mobile devices, like iOS.

void texcoords(vec2 fragCoord, vec2 resolution,
               out vec2 v_rgbNW, out vec2 v_rgbNE,
               out vec2 v_rgbSW, out vec2 v_rgbSE,
               out vec2 v_rgbM)
{
    vec2 inverseVP = 1.0 / resolution.xy;
    v_rgbNW = (fragCoord + vec2(-1.0, -1.0)) * inverseVP;
    v_rgbNE = (fragCoord + vec2(1.0, -1.0)) * inverseVP;
    v_rgbSW = (fragCoord + vec2(-1.0, 1.0)) * inverseVP;
    v_rgbSE = (fragCoord + vec2(1.0, 1.0)) * inverseVP;
    v_rgbM = vec2(fragCoord * inverseVP);
}

void main(void)
{
   gl_Position = vec4(a_position, 0.0, 1.0);
   vec2 texcoord = (a_position + 1.0)/2.0;
   v_texcoord = texcoord;

   //compute the texture coords and store them in varyings
   vec2 fragCoord = texcoord * resolution;
   texcoords(fragCoord, resolution, v_rgbNW, v_rgbNE, v_rgbSW, v_rgbSE, v_rgbM);
}
"""

_VERTEX_SHADERS['post_ssao'] = """
attribute vec2 a_position;

varying vec2 v_texcoord;

void main(void)
{
    gl_Position = vec4(a_position, 0.0, 1.0);
    v_texcoord = (a_position + 1.0)/2.0;
}
"""

_FRAGMENT_SHADERS['post_translucency'] = """
   uniform sampler2D tex_opaque;
   uniform sampler2D tex_accumulation;
   uniform sampler2D tex_revealage;
   varying vec2 v_texcoord;
   void main(void)
   {
       vec4 opaque = texture2D(tex_opaque, v_texcoord);
       vec4 accum = texture2D(tex_accumulation, v_texcoord);
       float r = texture2D(tex_revealage, v_texcoord).r;
       vec4 translucent = vec4(accum.rgb / clamp(accum.a, 1e-5, 5e4), r);
       gl_FragColor = mix(opaque, translucent, 1.0 - translucent.a);
   }
   """

_FRAGMENT_SHADERS['post_outlines'] = """
   uniform mat4 camera;
   uniform float outline;
   uniform sampler2D planeTex;
   uniform sampler2D colorTex;

   varying vec2 v_texcoord;

   // pseudo random number from -1 to 1, with NSA-endorsed constants
   float rand(vec2 co, float delt){
       return 2*(fract(sin(delt*1.0e3 + dot(co.xy, vec2(12.9898, 78.233))) * 43758.5453) - 0.5);
   }

#define PI 3.14159

   void main()
   {
       vec2 deltaTex = (camera*vec4(outline, outline, 0.0, 1.0)).xy;

       float gamma = 0.0;
       vec4 planesHere = texture2D(planeTex, v_texcoord);
       vec4 delta = planesHere;
       vec2 texcoord_scale = vec2(outline)*vec2(camera[0][0], camera[1][1]);
       int samples = 8;
       float dl = PI*(3.0-sqrt(5.0));
       float dz = 1.0/float(samples);
       float l = 0.0;
       float z = 1.0 - dz/2.0;
       float pw;
       float ph;

       for (int i = 0; i <= samples; i ++)
       {
           float r = sqrt(1.0-z);

           pw = cos(l)*r;
           ph = sin(l)*r;
           delta = texture2D(planeTex, v_texcoord + vec2(pw, ph)*texcoord_scale) - planesHere;
           gamma += dot(delta, delta);
           z = z - dz;
           l = l + dl;
       }

       gamma /= samples;
       gamma *= gamma;

       float light = 1.0/max(1.0, gamma);

       vec4 color = texture2D(colorTex, v_texcoord);
       gl_FragColor = vec4(color.xyz*light, color.w);
   }

"""

_FRAGMENT_SHADERS['post_fxaa'] = """
/**
Plato implementation of the shader found in the glsl-fxaa project at:

    https://github.com/mattdesl/glsl-fxaa

`glsl-fxaa` license and comments are below.

Basic FXAA implementation based on the code on geeks3d.com with the
modification that the texture2DLod stuff was removed since it's
unsupported by WebGL.

--

From:
https://github.com/mitsuhiko/webgl-meincraft

Copyright (c) 2011 by Armin Ronacher.

Some rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.

    * Redistributions in binary form must reproduce the above
      copyright notice, this list of conditions and the following
      disclaimer in the documentation and/or other materials provided
      with the distribution.

    * The names of the contributors may not be used to endorse or
      promote products derived from this software without specific
      prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

#ifndef FXAA_REDUCE_MIN
    #define FXAA_REDUCE_MIN   (1.0/ 128.0)
#endif
#ifndef FXAA_REDUCE_MUL
    #define FXAA_REDUCE_MUL   (1.0 / 8.0)
#endif
#ifndef FXAA_SPAN_MAX
    #define FXAA_SPAN_MAX     8.0
#endif

//optimized version for mobile, where dependent
//texture reads can be a bottleneck
vec4 fxaa(sampler2D tex, vec2 fragCoord, vec2 resolution,
            vec2 v_rgbNW, vec2 v_rgbNE,
            vec2 v_rgbSW, vec2 v_rgbSE,
            vec2 v_rgbM) {
    vec4 color;
    mediump vec2 inverseVP = vec2(1.0 / resolution.x, 1.0 / resolution.y);
    vec3 rgbNW = texture2D(tex, v_rgbNW).xyz;
    vec3 rgbNE = texture2D(tex, v_rgbNE).xyz;
    vec3 rgbSW = texture2D(tex, v_rgbSW).xyz;
    vec3 rgbSE = texture2D(tex, v_rgbSE).xyz;
    vec4 texColor = texture2D(tex, v_rgbM);
    vec3 rgbM  = texColor.xyz;
    vec3 luma = vec3(0.299, 0.587, 0.114);
    float lumaNW = dot(rgbNW, luma);
    float lumaNE = dot(rgbNE, luma);
    float lumaSW = dot(rgbSW, luma);
    float lumaSE = dot(rgbSE, luma);
    float lumaM  = dot(rgbM,  luma);
    float lumaMin = min(lumaM, min(min(lumaNW, lumaNE), min(lumaSW, lumaSE)));
    float lumaMax = max(lumaM, max(max(lumaNW, lumaNE), max(lumaSW, lumaSE)));

    mediump vec2 dir;
    dir.x = -((lumaNW + lumaNE) - (lumaSW + lumaSE));
    dir.y =  ((lumaNW + lumaSW) - (lumaNE + lumaSE));

    float dirReduce = max((lumaNW + lumaNE + lumaSW + lumaSE) *
                          (0.25 * FXAA_REDUCE_MUL), FXAA_REDUCE_MIN);

    float rcpDirMin = 1.0 / (min(abs(dir.x), abs(dir.y)) + dirReduce);
    dir = min(vec2(FXAA_SPAN_MAX, FXAA_SPAN_MAX),
              max(vec2(-FXAA_SPAN_MAX, -FXAA_SPAN_MAX),
              dir * rcpDirMin)) * inverseVP;

    vec3 rgbA = 0.5 * (
        texture2D(tex, fragCoord * inverseVP + dir * (1.0 / 3.0 - 0.5)).xyz +
        texture2D(tex, fragCoord * inverseVP + dir * (2.0 / 3.0 - 0.5)).xyz);
    vec3 rgbB = rgbA * 0.5 + 0.25 * (
        texture2D(tex, fragCoord * inverseVP + dir * -0.5).xyz +
        texture2D(tex, fragCoord * inverseVP + dir * 0.5).xyz);

    float lumaB = dot(rgbB, luma);
    if ((lumaB < lumaMin) || (lumaB > lumaMax))
        color = vec4(rgbA, texColor.a);
    else
        color = vec4(rgbB, texColor.a);
    return color;
}

uniform vec2 resolution;
uniform sampler2D sceneTex;

varying vec2 v_texcoord;
varying vec2 v_rgbNW;
varying vec2 v_rgbNE;
varying vec2 v_rgbSW;
varying vec2 v_rgbSE;
varying vec2 v_rgbM;

void main()
{
    //can also use gl_FragCoord.xy
    vec2 fragCoord = v_texcoord*resolution;

    gl_FragColor = fxaa(sceneTex, fragCoord, resolution, v_rgbNW, v_rgbNE, v_rgbSW, v_rgbSE, v_rgbM);
}
"""

_FRAGMENT_SHADERS['post_ssao'] = """
/*
SSAO fragment shader modified from martinsh's blog, linked below.

SSAO GLSL shader v1.2
assembled by Martins Upitis (martinsh) (devlog-martinsh.blogspot.com)
original technique is made by Arkano22 (www.gamedev.net/topic/550699-ssao-no-halo-artifacts/)

changelog:
1.2 - added fog calculation to mask AO. Minor fixes.
1.1 - added spiral sampling method from here:
(http://www.cgafaq.info/wiki/Evenly_distributed_points_on_sphere)
*/
#define PI    3.14159265

uniform vec2 resolution;
uniform vec2 clip_planes;
varying vec2 v_texcoord;
uniform sampler2D sceneTex;
uniform sampler2D planeTex;

//------------------------------------------
//general stuff

//user variables
int samples = 16; //ao sample count

float radius = 1.5; //ao radius
float aoclamp = 0.25; //depth clamp - reduces haloing at screen edges
bool noise = true; //use noise instead of pattern for sample dithering
float noiseamount = 0.001; //dithering amount

float diffarea = 0.4; //self-shadowing reduction
float gdisplace = 0.4; //gauss bell center

bool mist = false; //use mist?

bool onlyAO = false; //use only ambient occlusion pass?
float lumInfluence = 0.7; //how much luminance affects occlusion

//--------------------------------------------------------

vec2 rand(vec2 coord) //generating noise/pattern texture for dithering
{
    float noiseX = ((fract(1.0-coord.s*(resolution.x/2.0))*0.25)+(fract(coord.t*(resolution.y/2.0))*0.75))*2.0-1.0;
    float noiseY = ((fract(1.0-coord.s*(resolution.x/2.0))*0.75)+(fract(coord.t*(resolution.y/2.0))*0.25))*2.0-1.0;

    if (noise)
    {
        noiseX = clamp(fract(sin(dot(coord ,vec2(12.9898,78.233))) * 43758.5453),0.0,1.0)*2.0-1.0;
        noiseY = clamp(fract(sin(dot(coord ,vec2(12.9898,78.233)*2.0)) * 43758.5453),0.0,1.0)*2.0-1.0;
    }
    return vec2(noiseX,noiseY)*noiseamount;
}

float doMist()
{
    float depth = texture2D(planeTex, v_texcoord.xy).z;
    float miststart = 0.75;
    float mistend = 1.0;
    return clamp((depth-miststart)/mistend,0.0,1.0);
}

float readDepth(in vec2 coord)
{
    if (v_texcoord.x<0.0||v_texcoord.y<0.0) return 1.0;
    vec4 texread = texture2D(planeTex, coord);
    return 2.0*texread.z - 1.0;
}

float compareDepths(in float depth1, in float depth2,inout int far)
{
    float garea = 2.0; //gauss bell width
    float diff = (depth1 - depth2)*100.0; //depth difference (0-100)
    //reduce left bell width to avoid self-shadowing
    if (diff<gdisplace)
    {
    garea = diffarea;
    }else{
    far = 1;
    }

    float gauss = pow(2.7182,-2.0*(diff-gdisplace)*(diff-gdisplace)/(garea*garea));
    return gauss;
}

float calAO(float depth,float dw, float dh)
{
    float dd = (1.0-depth)*radius;

    float temp = 0.0;
    float temp2 = 0.0;
    float coordw = v_texcoord.x + dw*dd;
    float coordh = v_texcoord.y + dh*dd;
    float coordw2 = v_texcoord.x - dw*dd;
    float coordh2 = v_texcoord.y - dh*dd;

    vec2 coord = vec2(coordw , coordh);
    vec2 coord2 = vec2(coordw2, coordh2);

    int far = 0;
    temp = compareDepths(depth, readDepth(coord),far);
    //DEPTH EXTRAPOLATION:
    if (far > 0)
    {
        temp2 = compareDepths(readDepth(coord2),depth,far);
        temp += (1.0-temp)*temp2;
    }

    return temp;
}

void main(void)
{
    vec2 noise = rand(v_texcoord);
    float depth = readDepth(v_texcoord);

    float w = (1.0 / resolution.x)/clamp(depth,aoclamp,1.0)+(noise.x*(1.0-noise.x));
    float h = (1.0 / resolution.y)/clamp(depth,aoclamp,1.0)+(noise.y*(1.0-noise.y));

    float pw;
    float ph;

    float ao = 0.0;

    float dl = PI*(3.0-sqrt(5.0));
    float dz = 1.0/float(samples);
    float l = 0.0;
    float z = 1.0 - dz/2.0;

    for (int i = 0; i <= samples; i ++)
    {
        float r = sqrt(1.0-z);

        pw = cos(l)*r;
        ph = sin(l)*r;
        ao += calAO(depth,pw*w,ph*h);
        z = z - dz;
        l = l + dl;
    }

    ao /= float(samples);
    ao = 1.0-ao;

    if (mist)
    {
    ao = mix(ao, 1.0,doMist());
    }

    vec3 color = texture2D(sceneTex,v_texcoord).rgb;

    vec3 lumcoeff = vec3(0.299,0.587,0.114);
    float lum = dot(color.rgb, lumcoeff);
    vec3 luminance = vec3(lum, lum, lum);

    vec3 final = vec3(color*mix(vec3(ao),vec3(1.0),luminance*lumInfluence));//mix(color*ao, white, luminance)

    if (onlyAO)
    {
    final = vec3(mix(vec3(ao),vec3(1.0),luminance*lumInfluence)); //ambient occlusion only
    }

    gl_FragColor = vec4(final,1.0);
}
"""

def pick_callback(point, fbo, callback_scene, shape_callback, persist=True):
    index = point.astype(np.int32)
    callback_scene._canvas.set_current()
    prim_indices = []
    count = 0
    with fbo:
        gloo.clear(color=(1, 1, 1, 1), depth=True)
        gloo.set_state(
            preset='opaque', blend=False, depth_test=True, depth_mask=True)
        for prim in callback_scene._primitives:
            prim_indices.append(count)
            prim.render_pick(count)
            count += len(prim)
        prim_indices.append(count)
        img = fbo.read()

    pixel_value = np.ascontiguousarray(img[index[1], index[0]]).view(np.int32)
    index = pixel_value[0]
    if index != -1:
        prim_index = bisect.bisect_right(prim_indices, index) - 1
        shape_index = index - prim_indices[prim_index]

        callback_scene.disable('pick', strict=False)
        shape_callback(
            scene=callback_scene, primitive_index=prim_index, shape_index=shape_index)
    elif not persist:
        callback_scene.disable('pick', strict=False)

def fallback_default_pick_callback(scene, primitive_index, shape_index):
    print('Default pick callback on scene {}, primitive {}, shape {}'.format(
        scene, primitive_index, shape_index))

class Canvas(vispy.app.Canvas):
    _VALID_FEATURES = ['translucency', 'outlines', 'fxaa', 'ssao',
                       'additive_rendering', 'pick']

    def __init__(self, scene, **kwargs):
        self._fbos = {}
        self._programs = {}
        self._textures = {}
        self._webgl = 'webgl' in vispy.app.use_app().backend_name
        self._final_render_target = NoopContextManager()
        self._scene = scene
        self._mouse_origin = np.array([0, 0], dtype=np.float32)
        self._selection_callbacks = []
        self._clip_planes = np.array([1, 100], dtype=np.float32)

        super(Canvas, self).__init__(size=scene.size_pixels.astype(np.uint32), **kwargs)

        gloo.set_viewport(0, 0, *scene.size_pixels.astype(np.uint32))

        for feature in self._scene.enabled_features:
            if feature in self._VALID_FEATURES and feature not in self._scene._PROTECTED_FEATURES:
                self._enable_feature(**{feature: self._scene.get_feature_config(feature)})

    def on_resize(self, event):
        size = event.size
        reversed_size = tuple(size[::-1])

        self._scene.size_pixels = size
        self.set_current()
        for name in self._fbos:
            self._fbos[name].resize(reversed_size)

        if 'fxaa' in self._scene.enabled_features:
            self._programs['fxaa_post']['resolution'] = size
        if 'ssao' in self._scene.enabled_features:
            self._programs['ssao_post']['resolution'] = size

        vispy.gloo.set_viewport(0, 0, *size)

    def on_draw(self, *args, **kwargs):
        self.set_current()

        clear_color = (1, 1, 1, 1)
        gloo.set_depth_func('lequal')

        if 'additive_rendering' in self._scene.enabled_features:
            config = self._scene.get_feature_config('additive_rendering')

            if config.get('invert', False):
                clear_color = (1, 1, 1, 1)
                gloo.set_state(preset='additive',
                               depth_test=False,
                               blend=True,
                               depth_mask=False)
                gloo.set_blend_func('one', 'one', 'zero', 'one')
                gloo.set_blend_equation('func_reverse_subtract')
            else:
                clear_color = (0, 0, 0, 1)
                gloo.set_state(preset='additive',
                               depth_test=False,
                               blend=True,
                               depth_mask=False)
                gloo.set_blend_func('one', 'one')
                gloo.set_blend_equation('func_add')
        else:
            gloo.set_state(preset='opaque',
                           depth_test=True,
                           blend=True,
                           depth_mask=True)
            gloo.set_blend_func('src_alpha', 'one_minus_src_alpha')
        gloo.clear(color=clear_color, depth=True)

        if 'translucency' in self._scene.enabled_features:
            with self._fbos['translucency_opaque']:
                gloo.clear(color=clear_color)
                for prim in self._scene._primitives:
                    prim.render_translucency(pass_=-1)

            with self._fbos['translucency_accum']:
                gloo.clear(color=(0, 0, 0, 0), depth=False)
                gloo.set_state(preset=None,
                                   depth_test=True,
                                   blend=True,
                                   depth_mask=False)
                gloo.set_blend_func('one', 'one')

                # Pass 1
                for prim in self._scene._primitives:
                    prim.render_translucency(pass_=1)

            with self._fbos['translucency_reveal']:
                gloo.clear(color=(1, 1, 1, 1), depth=False)
                gloo.set_blend_func('zero', 'one_minus_src_alpha')

                # Pass 2
                for prim in self._scene._primitives:
                    prim.render_translucency(pass_=2)

            # Final compositing
            gloo.set_state(preset='opaque',
                               depth_test=False,
                               blend=False,
                               depth_mask=False)
            with self._final_render_target:
                self._programs['translucency_post'].draw('triangle_strip')
        elif 'outlines' in self._scene.enabled_features:
            gloo.set_state(preset='opaque',
                           depth_test=True,
                           blend=False,
                           depth_mask=True)
            with self._fbos['outlines_color']:
                gloo.clear(color=True, depth=True)
                for prim in self._scene._primitives:
                    prim.render_color()

            with self._fbos['outlines_plane']:
                gloo.clear(color=True, depth=True)
                for prim in self._scene._primitives:
                    prim.render_planes()

            with self._final_render_target:
                gloo.clear(color=True, depth=True)
                self._programs['outlines_post']['camera'] = prim.camera
                self._programs['outlines_post'].draw('triangle_strip')
        elif 'render_normals' in self._scene.enabled_features:
            with self._final_render_target:
                gloo.clear(color=True, depth=True)
                for prim in self._scene._primitives:
                    prim.render_normals()
        else:
            with self._final_render_target:
                gloo.clear(color=clear_color, depth=True)
                for prim in self._scene._primitives:
                    prim.render_color()

        if 'ssao' in self._scene.enabled_features:
            with self._fbos['ssao_plane']:
                gloo.set_state(preset='opaque',
                                   depth_test=True,
                                   blend=False,
                                   depth_mask=True)
                gloo.clear(color=True, depth=True)
                for prim in self._scene._primitives:
                    prim.render_positions()

            gloo.set_state(preset='opaque',
                               depth_test=False,
                               blend=False,
                               depth_mask=False)
            if 'fxaa' in self._scene.enabled_features:
                with self._fbos['fxaa_target']:
                    self._programs['ssao_post'].draw('triangle_strip')
            else:
                self._programs['ssao_post'].draw('triangle_strip')

        if 'fxaa' in self._scene.enabled_features:
            gloo.set_state(preset='opaque',
                               depth_test=False,
                               blend=False,
                               depth_mask=False)
            self._programs['fxaa_post'].draw('triangle_strip')

    def _update_linked_rotation_targets(self):
        if 'link_rotation' in self._scene.enabled_features:
            targets = self._scene.get_feature_config('link_rotation')['targets']
            for target in targets:
                try:
                    canvas = target._canvas
                    canvas.update()
                except AttributeError:
                    pass

    def on_mouse_press(self, event):
        self._mouse_origin[:] = event.pos

    def on_mouse_release(self, event):
        if self._selection_callbacks:
            callback = self._selection_callbacks.pop()
            callback(self._mouse_origin, event.pos)

    def _mouse_translate(self, delta):
        scale = 2/np.array(self._scene.size_pixels)/self._scene.camera[[0, 1], [0, 1]]*[1, -1]
        translation = self._scene.translation
        translation[:2] += scale*delta
        self._scene.translation = translation
        self.update()

    def on_mouse_wheel(self, event):
        self._scene.zoom *= 1.1**event.delta[1]
        self.update()

    def on_mouse_move(self, event):
        if event.handled or self._selection_callbacks:
            return

        if 1 in event.buttons or 2 in event.buttons:
            delta = (event.pos - self._mouse_origin)/np.sqrt(np.product(self._scene.size_pixels))
            self._mouse_origin[:] = event.pos
            if 'control' in event.modifiers or 'meta' in event.modifiers:
                self.planeRotation(event, delta)
            elif 'alt' in event.modifiers or 'pan' in self._scene.enabled_features:
                # undo the mean size scaling we applied above
                self._mouse_translate(delta*np.sqrt(np.product(self._scene.size_pixels)))
            else:
                self.updateRotation(event, delta)

    def on_key_press(self, event):
        if event.key == 'Right' and (
                'control' in event.modifiers or 'meta' in event.modifiers):
            self.updateRotation(event, delta=(np.pi/36, 0))
        elif event.key == 'Left' and (
                'control' in event.modifiers or 'meta' in event.modifiers):
            self.updateRotation(event, delta=(-np.pi/36, 0))
        elif event.key == 'Up' and (
                'control' in event.modifiers or 'meta' in event.modifiers):
            self.updateRotation(event, delta=(0, -np.pi/36))
        elif event.key == 'Down' and (
                'control' in event.modifiers or 'meta' in event.modifiers):
            self.updateRotation(event, delta=(0, np.pi/36))
        elif event.key == 'L':
            self.updateRotation(event, delta=(np.pi/36, 0))
        elif event.key == 'J':
            self.updateRotation(event, delta=(-np.pi/36, 0))
        elif event.key == 'I':
            self.updateRotation(event, delta=(0, -np.pi/36))
        elif event.key == 'K':
            self.updateRotation(event, delta=(0, np.pi/36))
        elif event.key == 'X':
            # rotate about y axis by -pi/2
            rot = [np.cos(-np.pi/4), 0, np.sin(-np.pi/4), 0]
            self._scene.rotation = np.asarray(rot, dtype=np.float32)
        elif event.key == 'Y':
            # rotate about x axis by pi/2
            rot = [np.cos(np.pi/4), np.sin(np.pi/4), 0, 0]
            self._scene.rotation = np.asarray(rot, dtype=np.float32)
        elif event.key == 'Z':
            self._scene.rotation = np.asarray([1., 0., 0., 0.], dtype=np.float32)
        self.update()

    def grab_selection_area(self, callback):
        self._selection_callbacks.append(callback)

    def planeRotation(self, event, delta=(0,0)):
        delta = np.asarray(delta, dtype=np.float32)
        theta = -delta[0] * (0.1 if 'shift' in event.modifiers else 1)
        updated = False

        if np.absolute(theta) > 1e-5:
            theta *= (3.0 if 'shift' not in event.modifiers else 1)
            quat = np.array([np.cos(theta/2), 0, 0, np.sin(theta/2)])
            real = (self._scene.rotation[0]*quat[0] - np.dot(self._scene.rotation[1:], quat[1:]))
            imag = (self._scene.rotation[0]*quat[1:] + quat[0]*self._scene.rotation[1:] + np.cross(quat[1:], self._scene.rotation[1:]))
            self._scene.rotation = [real] + imag.tolist()
            updated = True

        if np.absolute(delta[1]) > 1e-5:
            amount = -delta[1]*(1. if 'shift' in event.modifiers else 20.)
            self._scene.zoom *= 1.1**amount
            updated = True

        if updated:
            self._update_linked_rotation_targets()
            self.update()

    def updateRotation(self, event, delta=(0,0), suppress=False):
        delta = np.asarray(delta, dtype=np.float32)[::-1]
        theta = np.sqrt(np.sum(delta**2)) * (0.1 if (not suppress)
                                                  and ('shift' in event.modifiers)
                                                  else 1)

        if np.absolute(theta) > 1e-5:
            norm = delta/(theta * (10 if (not suppress) and ('shift' in event.modifiers) else 1))
            theta *= (3.0 if (suppress) or ('shift' not in event.modifiers) else 1)
            quat = np.array([np.cos(theta/2),
                             np.sin(theta/2)*norm[0],
                             np.sin(theta/2)*norm[1], 0])
            real = (self._scene.rotation[0]*quat[0] - np.dot(self._scene.rotation[1:], quat[1:]))
            imag = (self._scene.rotation[0]*quat[1:] + quat[0]*self._scene.rotation[1:] + np.cross(quat[1:], self._scene.rotation[1:]))
            rotation = np.array([real] + imag.tolist(), dtype=np.float32)
            # normalize to prevent accumulation of FP errors
            rotation /= np.linalg.norm(rotation)
            self._scene.rotation = rotation
            self._update_linked_rotation_targets()
            self.update()

    def _enable_feature(self, *features, **param_features):
        """Enable an optional rendering feature. Takes any number of feature
        arguments as strings. Features that take optional arguments
        can be passed in as keyword arguments, with the value
        corresponding to the argument as the options for the feature.

        Available features:
        - translucency: Performs order independent transparency
        - outlines: Compute two-pass, cartoony-effect outlines based on rendered plane equations of the scene. Not recommended for use. Takes a parameter 'outline' that scales the size of the produced outlines.
        - fxaa: Performs fast approximate antialiasing. Particularly useful when other multipass features are enabled, which causes the default openGL multisampling antialiasing to be unavailable.
        - ssao: Computes simple ambient occlusion effects, which typically improve the sense of depth in scene lighting.

        Example::

          canvas._enable_feature('translucency', 'fxaa')
        """
        features = set(features).union(param_features)
        size = self.size
        for feature in features:
            params = param_features[feature] if feature in param_features else {}
            if feature == 'translucency':
                tex = self._textures['translucency_opaque'] = vispy.gloo.Texture2D(
                    shape=(size[1], size[0], 4) , format='rgba')
                depth = self._textures['translucency_opaque_depth'] = vispy.gloo.RenderBuffer((size[1], size[0]))
                self._fbos['translucency_opaque'] = vispy.gloo.FrameBuffer(color=tex, depth=depth)

                tex = self._textures['translucency_accum'] = vispy.gloo.Texture2D(
                    shape=(size[1], size[0], 4) , format='rgba',
                    internalformat='rgba32f', interpolation='linear')
                self._fbos['translucency_accum'] = vispy.gloo.FrameBuffer(color=tex, depth=depth)

                tex = self._textures['translucency_reveal'] = vispy.gloo.Texture2D(
                    shape=(size[1], size[0], 4) , format='rgba',
                    internalformat='rgba32f', interpolation='linear')
                self._fbos['translucency_reveal'] = vispy.gloo.FrameBuffer(color=tex, depth=depth)

                self._programs['translucency_post'] = vispy.gloo.Program(
                    _VERTEX_SHADERS['post_translucency'],
                    _FRAGMENT_SHADERS['post_translucency'])
                self._programs['translucency_post']['tex_opaque'] = self._textures['translucency_opaque']
                self._programs['translucency_post']['tex_accumulation'] = self._textures['translucency_accum']
                self._programs['translucency_post']['tex_revealage'] = self._textures['translucency_reveal']
                self._programs['translucency_post']['a_position'] = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            elif feature == 'outlines':
                if self._webgl:
                    logger.warning('Can\'t use outlines with webgl')
                    continue

                self._programs['outlines_post'] = vispy.gloo.Program(
                    _VERTEX_SHADERS['post_outlines'],
                    _FRAGMENT_SHADERS['post_outlines'])

                tex = self._textures['outlines_plane'] = vispy.gloo.Texture2D(
                    shape=(size[1], size[0], 4) , format='rgba',
                    internalformat='rgba32f', interpolation='linear')
                depth = self._textures['outlines_plane_depth'] = vispy.gloo.RenderBuffer((size[1], size[0]))
                self._fbos['outlines_plane'] = vispy.gloo.FrameBuffer(color=tex, depth=depth)
                self._programs['outlines_post']['planeTex'] = tex

                tex = self._textures['outlines_color'] = vispy.gloo.Texture2D(
                    shape=(size[1], size[0], 4) , format='rgba', interpolation='linear')
                depth = self._textures['outlines_color_depth'] = vispy.gloo.RenderBuffer((size[1], size[0]))
                self._fbos['outlines_color'] = vispy.gloo.FrameBuffer(color=tex, depth=depth)
                self._programs['outlines_post']['colorTex'] = tex

                self._programs['outlines_post']['outline'] = params.get('value', .1)
                self._programs['outlines_post']['a_position'] = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            elif feature == 'fxaa':
                if self._webgl:
                    logger.warning('Can\'t use FXAA with webgl')
                    continue

                self._programs['fxaa_post'] = vispy.gloo.Program(
                    _VERTEX_SHADERS['post_fxaa'],
                    _FRAGMENT_SHADERS['post_fxaa'])

                tex = self._textures['fxaa_target'] = vispy.gloo.Texture2D(shape=(size[1], size[0], 4))
                depth = self._textures['fxaa_target_depth'] = vispy.gloo.RenderBuffer((size[1], size[0]))
                self._fbos['fxaa_target'] = vispy.gloo.FrameBuffer(color=tex, depth=depth)

                self._programs['fxaa_post']['sceneTex'] = self._textures['fxaa_target']
                self._programs['fxaa_post']['resolution'] = size
                self._programs['fxaa_post']['a_position'] = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

                if 'ssao' in self._scene.enabled_features and 'ssao_target' in self._fbos:
                    self._final_render_target = self._fbos['ssao_target']
                else:
                    self._final_render_target = self._fbos['fxaa_target']
            elif feature == 'ssao':
                if self._webgl:
                    logger.warning('Can\'t use SSAO with webgl')
                    continue

                self._programs['ssao_post'] = vispy.gloo.Program(
                    _VERTEX_SHADERS['post_ssao'],
                    _FRAGMENT_SHADERS['post_ssao'])

                tex = self._textures['ssao_plane'] = vispy.gloo.Texture2D(
                    shape=(size[1], size[0], 4) , format='rgba',
                    internalformat='rgba32f', interpolation='linear')
                depth = self._textures['ssao_plane_depth'] = vispy.gloo.RenderBuffer((size[1], size[0]))
                self._fbos['ssao_plane'] = vispy.gloo.FrameBuffer(color=tex, depth=depth)
                self._programs['ssao_post']['planeTex'] = tex

                tex = self._textures['ssao_target'] = vispy.gloo.Texture2D(shape=(size[1], size[0], 4))
                depth = self._textures['ssao_target_depth'] = vispy.gloo.RenderBuffer((size[1], size[0]))
                self._fbos['ssao_target'] = vispy.gloo.FrameBuffer(color=tex, depth=depth)

                self._programs['ssao_post']['sceneTex'] = self._textures['ssao_target']
                self._programs['ssao_post']['resolution'] = size
                self._programs['ssao_post']['clip_planes'] = self._clip_planes
                self._programs['ssao_post']['a_position'] = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

                self._final_render_target = self._fbos['ssao_target']
            elif feature == 'additive_rendering':
                pass
            elif feature == 'pick':
                if self._webgl:
                    logger.warning('Can\'t use picking rendering with webgl')
                    continue

                params = param_features[feature] if feature in param_features else {}

                tex = self._textures['pick_target'] = vispy.gloo.Texture2D(
                    shape=(size[1], size[0], 4))
                depth = self._textures['pick_target_depth'] = vispy.gloo.RenderBuffer(
                    (size[1], size[0]))
                fbo = self._fbos['pick_target'] = vispy.gloo.FrameBuffer(color=tex, depth=depth)

                callback = params.get('value', None) or fallback_default_pick_callback
                persist = params.get('persist', True)

                self._scene.enable(
                    'select_point', pick_callback, units='pixels_gui', fbo=fbo,
                    callback_scene=self._scene, shape_callback=callback, persist=persist)
            else:
                raise RuntimeError('Unknown rendering feature {}'.format(feature))

    def _disable_feature(self, *features):
        """Removes a feature from the set of used features. Features must be
        passed in by name only."""
        features = set(features)
        for feature in features:
            if feature not in self._VALID_FEATURES:
                raise RuntimeError('Unknown rendering feature {}'.format(feature))
            else:
                for mem in [self._fbos, self._programs, self._textures]:
                    for key in [k for k in mem if k.startswith(feature)]:
                        del mem[key]

                if feature == 'ssao':
                    self._final_render_target = NoopContextManager()
                    if 'fxaa' in self._scene.enabled_features:
                        self._enable_feature('fxaa')

                if feature == 'fxaa':
                    self._final_render_target = NoopContextManager()
                    # redo SSAO setup so it will have the correct buffers
                    if 'ssao' in self._scene.enabled_features:
                        self._enable_feature('ssao')

    @property
    def clip_planes(self):
        return self._clip_planes

    @clip_planes.setter
    def clip_planes(self, clip):
        self._clip_planes[:] = clip
        if 'ssao' in self._scene.enabled_features:
            self._programs['ssao_post']['clip_planes'] = self._clip_planes
