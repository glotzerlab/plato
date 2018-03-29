import numpy as np
import json
from collections import defaultdict
from ... import draw

class Scene(draw.Scene):
    __doc__ = draw.Scene.__doc__

    def render(self):
        json_scene = defaultdict(dict)
        #json_scene['features'] = self.features
        json_scene['size'] = self.size.tolist()
        json_scene['translation'] = self.translation.tolist()
        json_scene['rotation'] = self.rotation.tolist()
        json_scene['zoom'] = self.zoom
        json_scene['pixel_scale'] = self.pixel_scale

        json_prims = []
        for i, prim in enumerate(self._primitives):
            json_prims.append(prim.render())

        json_scene['primitives'] = json_prims

        return json.dumps(json_scene)
