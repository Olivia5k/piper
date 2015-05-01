import mock
import yaml


# Actually use the current project piper.yml for tests. Dogfood that shit, yo!
with open('piper.yml') as f:
    BASE_CONFIG = yaml.safe_load(f.read())

with open('piperd.yml') as f:
    AGENT_CONFIG = yaml.safe_load(f.read())


class SQLATest(object):
    """
    Test base for tests that want a database setup

    """

    def setup_method(self, method):
        # Just to avoid any future kind of circular dependencies
        from piper.db.db_sqlalchemy import SQLAlchemyDB

        self.db = SQLAlchemyDB()
        self.config = mock.Mock()
        self.config.raw = {
            'db': {
                'host': 'localhost',
            }
        }
        self.build = mock.Mock()


def builtin(target):
    """
    Return the correct string to mock.patch depending on Py3k or not.

    """

    return '{0}.{1}'.format(
        'builtins' if mock.inPy3k else '__builtin__',
        target,
    )
