import os
import tempfile
import shutil

import logbook
import jsonschema

from piper.utils import DotDict


class Env(object):
    def __init__(self, conf):
        self.conf = DotDict(conf)

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
                'type': {
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

    def validate(self, config):
        jsonschema.validate(config, self.schema)


class TempDirEnv(Env):
    """
    Example implementation of an env, probably useful as well

    Does the build in a temporary directory as done by the tempfile module.
    Once build is done, the temporary directory is removed unless specified
    to be kept.

    """

    def setup(self):
        self.dir = tempfile.mkdtemp()

        os.chdir(self.dir)
        self.log.info("Working directory set to '{0}'".format(self.dir))

    def teardown(self):
        if self.conf.delete_when_done:
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

        step.execute()
