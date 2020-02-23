import numpy as np
import rowan

from ... import draw

LOCAL_HELPER_SCRIPT = """
let is_in_view = function(elt) {
    let bounding_rect = elt.getBoundingClientRect();
    return bounding_rect.bottom >= 0 && bounding_rect.top <= window.innerHeight;
}
"""

class Scene(draw.Scene):
    __doc__ = (draw.Scene.__doc__ or '') + """
    This Scene supports the following features:

    * *ambient_light*: Enable trivial ambient lighting. The given value indicates the magnitude of the light (in [0, 1]).
    * *directional_light*: Add directional lights. The given value indicates the magnitude*direction normal vector.
    * *pan*: Translate, rather than rotate, when dragging with the mouse
    """

    CANVAS_INDEX = 0

    def render(self):
        """Render all the shapes in this scene.

        :returns: HTML string contents to be displayed
        """
        canvas_id = 'zdog_{}'.format(self.CANVAS_INDEX)
        illo_id = 'illo_{}'.format(self.CANVAS_INDEX)
        Scene.CANVAS_INDEX += 1

        html_lines = []

        js_lines = []

        euler = -rowan.to_euler(
            self.rotation, convention='xyz', axis_type='intrinsic')
        translation = self.translation*(1, -1, 1)

        pan_cfg = self.get_feature_config('pan')
        pan = pan_cfg.get('value', True) if pan_cfg is not None else False

        js_lines.append("""
        let {illo_id} = new Zdog.Illustration({{
            element: '#{canvas_id}',
            zoom: {zoom},
            dragRotate: {rotation_enabled},
            rotate: {{x: {angle[0]}, y: {angle[1]}, z: {angle[2]}}},
            translate: {{x: {pos[0]}, y: {pos[1]}, z: {pos[2]}}},
        }});
        """.format(
            illo_id=illo_id, canvas_id=canvas_id, zoom=self.zoom*self.pixel_scale,
            angle=euler, pos=translation,
            rotation_enabled=('false' if pan else 'true')))

        config = self.get_feature_config('ambient_light')
        ambient_light = 0 if config is None else config.get('value', .4)

        config = self.get_feature_config('directional_light')
        directional_light = ([(0, 0, 0)] if config is None else
                             config.get('value', [(0, 0, 0)]))
        directional_light = np.atleast_2d(directional_light)

        shapeIndex = 0
        for i, prim in enumerate(self._primitives):
            js_lines.extend(prim.render(
                rotation=self.rotation, illo_id=illo_id,
                name_suffix=i, ambient_light=ambient_light,
                directional_light=directional_light))

        (width, height) = map(int, self.size_pixels)
        html_lines.append("""
        <canvas id="{canvas_id}" width="{width}" height="{height}"></canvas>
        """.format(canvas_id=canvas_id, width=width, height=height))

        html_lines.append("""<script>
            var fill_{canvas_id} = function() {{
            """.format(canvas_id=canvas_id))
        html_lines.append(LOCAL_HELPER_SCRIPT)
        html_lines.extend(js_lines)

        pan_snippet = """
        new Zdog.Dragger({{
            startElement: {illo_id}.element,
            onDragStart: function( pointer, moveX, moveY) {{
                this.lastX = 0;
                this.lastY = 0;
            }},
            onDragMove: function( pointer, moveX, moveY ) {{
                let deltax = moveX - this.lastX;
                let deltay = moveY - this.lastY;
                let scale = 1.0/{illo_id}.zoom;
                {illo_id}.translate.x += deltax*scale;
                {illo_id}.translate.y += deltay*scale;
                this.lastX = moveX;
                this.lastY = moveY;
            }}
        }});""".format(illo_id=illo_id)
        if pan:
            html_lines.append(pan_snippet)

        html_lines.append("""
            let this_canvas = document.querySelector("#{canvas_id}");
            """.format(canvas_id=canvas_id))
        html_lines.append("""
            let animate_{canvas_id} = function() {{
                if(is_in_view(this_canvas))
                {{
                    {illo_id}.updateRenderGraph();
                }}
                if(document.contains(this_canvas))
                {{
                    requestAnimationFrame(animate_{canvas_id});
                }}
            }};
            animate_{canvas_id}();""".format(canvas_id=canvas_id, illo_id=illo_id))
        # remove the global reference to this function after using it
        html_lines.append('fill_{canvas_id} = null;'.format(canvas_id=canvas_id))
        html_lines.append('};') # end of fill_{canvas_id}
        # now call fill_{canvas_id}, possibly after loading zdog
        html_lines.append("""
            if (typeof Zdog == 'undefined')
            {{
                var script = document.createElement('script');
                script.addEventListener('load', fill_{canvas_id}, false);
                script.src = 'https://unpkg.com/zdog@1/dist/zdog.dist.min.js';
                document.getElementsByTagName('head')[0].appendChild(script);
            }}
            else
                fill_{canvas_id}();
            """.format(canvas_id=canvas_id))
        html_lines.append('</script>')

        return '\n'.join(html_lines)

    def show(self):
        """Render the scene to an image and display using ipython."""
        import IPython.display
        disp = IPython.display.HTML(self.render())
        return IPython.display.display(disp, display_id=str(id(self)))

    def save(self, filename):
        """Save the scene as an HTML file.

        :param filename: target filename to save the result into
        """
        result = self.render()

        with open(filename, 'w') as f:
            f.write(result)

    def _repr_html_(self):
        return self.render()
