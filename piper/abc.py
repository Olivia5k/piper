import logbook
import jsonschema


class DynamicItem(object):
    """
    Dynamic base class that defines things all Piper classes need.

    Many parts of the piper infrastructure is about being able to dynamically
    choose which classes should execute actions. This class includes the things
    that are identical in all of these, solely to avoid repetition.

    """

    def __init__(self, config):
        self.config = config
        self.log = logbook.Logger(self.__class__.__name__)

        # Set missing optional keys to None or default values
        for k in set(self.schema['properties']) - set(self.schema['required']):
            if k not in config:
                # If there is a default field specified, use that value
                # otherwise None
                config[k] = self.schema['properties'][k].get('default')

    def __repr__(self):  # pragma: nocover
        return self.__str__()

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
                        'description': 'Dynamic class to load.',
                        'type': 'string',
                    },
                },
            }

        return self._schema

    def validate(self):
        jsonschema.validate(self.config, self.schema)
