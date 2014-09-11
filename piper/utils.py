import subprocess as sub


class DotDict(object):
    """
    Immutable dict-like objects accessible by dot notation

    Used because the amount of configuration access is very high and just using
    dots instead of the dict notation feels good.

    It should be noted that this class could definitely have a more elegant
    writing, possibly inheriting from dict(). However, this is probably good
    enough and will probably not cause any trouble.

    """

    def __init__(self, data):
        # TODO: Make this more elegant
        if isinstance(data, DotDict):
            self.data = data.data
        else:
            self.data = data

    def __repr__(self):  # pragma: nocover
        return '<DotDict {}>'.format(self.data)

    def __getattr__(self, key):
        if key in ('values', 'keys', 'items'):
            # Dict methods, just return and run them.
            return getattr(self.data, key)

        # Default to None
        val = self.data.get(key, None)

        if isinstance(val, dict):
            val = DotDict(val)

        return val

    def __eq__(self, other):
        if isinstance(other, dict):
            return self.data == other
        elif isinstance(other, DotDict):
            return self.data == other.data
        else:
            return False

    def __iter__(self):
        for x in self.data:
            yield x

    # So that we can still access as dicts
    __getitem__ = __getattr__


def dynamic_load(target):
    """
    Dynamically import a class and return it

    This is used by the core parts of the main configuration file since
    one of the main features is to let the user specify which class to use.

    """

    split = target.split('.')
    module_name = '.'.join(split[:-1])
    class_name = split[-1]

    mod = __import__(module_name, fromlist=[class_name])
    return getattr(mod, class_name)


def oneshot(cmd):
    """
    Oneshot execution of a subprocess. Returns output as a single string.

    This is only to cut down on boiler.

    """

    popen = sub.Popen(cmd.split(), stdout=sub.PIPE, stderr=sub.PIPE)
    exit = popen.wait()

    if exit != 0:
        raise Exception(
            "Execution of '{0}' failed with exitcode {1}\n\n{2}".format(
                cmd, exit, popen.stderr.read().decode().strip()
            )
        )

    return str(popen.stdout.read().decode().strip())
