import logbook
import jsonschema

from piper.utils import DotDict


class Step(object):
    """
    Definition of an execution step.

    This base implementation will return the command line set in the
    configuration.

    """

    def __init__(self, key, config):
        self.key = key
        self.config = DotDict(config)
        self.success = None

        self.log = logbook.Logger(
            '{0}({1})'.format(self.__class__.__name__, self.key)
        )

        # Schema is defined here so that subclasses can change the base schema
        # without it affecting all other classes.
        self.schema = {
            '$schema': 'http://json-schema.org/draft-04/schema',
            'type': 'object',
            'additionalProperties': False,
            'properties': {
                'version': {
                    'description': 'Semantic version string for this config.',
                    'type': 'string',
                },
                'class': {
                    'description': 'Python class to load for this env',
                    'type': 'string',
                },
                'command': {
                    'description': 'Command line to execute.',
                    'type': 'string',
                },
            },
        }

    def validate(self):
        jsonschema.validate(self.config.data, self.schema)

    def get_command(self):
        """
        The main entry point.

        This is what Env()s are supposed to run.

        """

        return self.config.command