import logbook
import jsonschema

from piper.utils import DotDict


class StepBase(object):
    """
    Abstract base class of an execution step.

    """

    def __init__(self, key, config):
        # Schema is defined here so that subclasses can change the base schema
        # without it affecting all other classes.
        # Set missing optional keys to None in the config
        opt = set(self.schema['properties']) - set(self.schema['required'])
        for k in opt:
            if k not in config:
                config[k] = None

        self.index = ('x', 'y')
        self.key = key
        self.config = DotDict(config)
        self.success = None
        self.log = logbook.Logger(key)

    def __repr__(self):  # pragma: nocover
        return "<{0} {1}>".format(self.__class__.__name__, self.key)

    @property
    def schema(self):
        if not hasattr(self, '_schema'):
            self._schema = {
                '$schema': 'http://json-schema.org/draft-04/schema',
                'type': 'object',
                'additionalProperties': False,
                'required': ['class'],
                'properties': {
                    'class': {
                        'description': 'Python class to load for this env',
                        'type': 'string',
                    },
                    'depends': {
                        'description': 'Step required to run before this one.',
                        'type': ['string', 'null'],
                    },
                },
            }

        return self._schema

    def set_index(self, cur, tot):
        """
        Store the order of the step running and set up the logger accordingly.

        """

        self.index = (cur, tot)
        self.log_key = '{0} ({1}/{2})'.format(
            self.key, self.index[0], self.index[1]
        )
        self.log = logbook.Logger(self.log_key)

    def validate(self):
        jsonschema.validate(self.config.data, self.schema)

    def get_command(self):
        """
        The main entry point.

        This is what Env()s are supposed to run.

        """

        raise NotImplementedError()


class CommandLineStep(StepBase):
    """
    Step that simply runs a command line from the configuration file.

    KISS.

    """

    @property
    def schema(self):
        if not hasattr(self, '_schema'):
            self._schema = super(CommandLineStep, self).schema
            self._schema['required'].append('command')
            self._schema['properties']['command'] = {
                'description': 'Command line to execute.',
                'type': 'string',
            }

        return self._schema

    def get_command(self):
        return self.config.command
