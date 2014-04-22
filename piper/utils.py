class DotDict(object):
    """
    Immutable dict-like objects accessible by dot notation

    Used because the amount of configuration access is very high and just using
    dots instead of the dict notation feels good.

    """

    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return '<DotDict {}>'.format(self.data)

    def __getattr__(self, key):
        val = self.data[key]

        if isinstance(val, dict):
            val = DotDict(val)

        return val
