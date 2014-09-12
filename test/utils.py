import mock


BASE_CONFIG = {
    'version': {
        'class': 'piper.version.Version',
        'version': '0.0.1-alpha1',
    },
    'jobs': {'test': ['test'], 'build': ['test', 'build']},
    'envs': {
        'local': {
            'class': 'piper.env.TempDirEnv',
            'delete_when_done': False,
        },
    },
    'steps': {
        'test': {
            'class': 'piper.step.Step',
            'command': 'python setup.py test',
        },
        'build': {
            'class': 'piper.step.Step',
            'command': 'python setup.py sdist',
        },
    },
}


def builtin(target):
    """
    Return the correct string to mock.patch depending on Py3k or not.

    """

    return '{0}.{1}'.format(
        'builtins' if mock.inPy3k else '__builtin__',
        target,
    )
