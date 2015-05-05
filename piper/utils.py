import os
import errno
import sh
import datetime


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
    Oneshot execution of a command. Returns output as a single string.

    This is only to cut down on boiler.

    """

    cmd, *args = cmd.split()
    return sh.Command(cmd)(args).strip()


def mkdir(path):  # pragma: nocover
    """
    Safe implementation of 'mkdir -p'

    """

    # Python 3.2 has os.makedirs(exist_ok=True)...
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def now():
    """
    Mockable now() method. datetime.datetime is immutable and cannot be patched
    by mock.

    """

    return datetime.datetime.now(datetime.timezone.utc)
