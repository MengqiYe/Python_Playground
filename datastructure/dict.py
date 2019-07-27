class TwoWayDict(dict):
    def __delitem__(self, key):
        value = super().pop(key)
        super().pop(value, None)
    def __setitem__(self, key, value):
        if key in self:
            del self[self[key]]
        if value in self:
            del self[value]
        super().__setitem__(key, value)
        super().__setitem__(value, key)
    def __repr__(self):
        return f"{type(self).__name__}({super().__repr__()})"
