class JSONShape():

    def render(self):
        prim_json = {
            'class': self.__class__.__name__,
            'attributes': {
                k: v.tolist() for k, v in self._attributes.items()},
            'translation': self.translation.tolist(),
            'rotation': self.rotation.tolist()
        }
        return prim_json
