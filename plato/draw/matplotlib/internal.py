from matplotlib.collections import PatchCollection
import numpy as np

class PatchUser:
    def render(self, axes, **kwargs):
        patches = self._render_patches(axes, **kwargs)

        all_patches = []
        all_colors = []
        for (p, c) in patches:
            all_patches.extend(p)
            all_colors.append(c)

        all_colors = np.concatenate(all_colors, axis=0)

        collection = PatchCollection(all_patches)
        collection.set_facecolor(all_colors)

        axes.add_collection(collection)
