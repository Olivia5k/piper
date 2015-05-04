import mock
import yaml


# Actually use the current project piper.yml for tests. Dogfood that shit, yo!
with open('piper.yml') as f:
    BASE_CONFIG = yaml.safe_load(f.read())

with open('piperd.yml') as f:
    AGENT_CONFIG = yaml.safe_load(f.read())


def builtin(target):
    """
    Return the correct string to mock.patch depending on Py3k or not.

    """

    return '{0}.{1}'.format(
        'builtins' if mock.inPy3k else '__builtin__',
        target,
    )
