class Dict2Object(dict):
    def __getattr__(self, name):
        value = self[name]
        if isinstance(value, dict):
            value = Dict2Object(value)
        return value
