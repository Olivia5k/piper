import os
import tempfile
import shutil

import logbook
import jsonschema

from piper.utils import DotDict
from piper.process import Process


class Env(object):
    def __init__(self, config):
        self.config = DotDict(config)

        self.log = logbook.Logger(self.__class__.__name__)

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
            },
        }

    def setup(self):  # pragma: nocover
        pass

    def teardown(self):  # pragma: nocover
        pass

    def execute(self, step):
        raise NotImplementedError()

    def validate(self):
        jsonschema.validate(self.config.data, self.schema)


class TempDirEnv(Env):
    """
    Example implementation of an env, probably useful as well

    Does the build in a temporary directory as done by the tempfile module.
    Once build is done, the temporary directory is removed unless specified
    to be kept.

    """

    def __init__(self, config):
        super(TempDirEnv, self).__init__(config)
        self.schema['properties']['delete_when_done'] = {
            'type': 'boolean'
        }

    def setup(self):
        self.dir = tempfile.mkdtemp()

        os.chdir(self.dir)
        self.log.info("Working directory set to '{0}'".format(self.dir))

    def teardown(self):
        if self.config.delete_when_done:
            shutil.rmtree(self.dir)

    def execute(self, step):
        cwd = os.getcwd()
        if cwd != self.dir:
            self.log.warning(
                "Directory changed to '{0}'. Resetting to '{1}'.".format(
                    cwd, self.dir
                )
            )
            os.chdir(self.dir)

        cmd = step.get_command()
        proc = Process(cmd)
        proc.run()

        return proc
