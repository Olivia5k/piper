import os
import tempfile
import shutil

import logbook
import jsonschema

from piper.utils import DotDict
from piper.process import Process


class EnvBase(object):
    def __init__(self, ns, config):
        self.ns = ns
        self.config = DotDict(config)
        self.log = logbook.Logger(self.__class__.__name__)

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
                },
            }

        return self._schema

    def setup(self):  # pragma: nocover
        pass

    def teardown(self):  # pragma: nocover
        pass

    def execute(self, step):
        cmd = step.get_command()

        proc = Process(self.ns, cmd, step.log_key)
        proc.setup()
        proc.run()

        return proc

    def validate(self):
        jsonschema.validate(self.config.data, self.schema)


class TempDirEnv(EnvBase):
    """
    Example implementation of an env, probably useful as well

    Does the build in a temporary directory as done by the tempfile module.
    Once build is done, the temporary directory is removed unless specified
    to be kept.

    """

    @property
    def schema(self):
        if not hasattr(self, '_schema'):
            self._schema = super(TempDirEnv, self).schema
            self._schema['properties']['delete_when_done'] = {
                'description':
                    'If true, temporary directory will be deleted when build '
                    'has finished. Default is true.',
                'type': 'boolean',
            }

        return self._schema

    def setup(self):
        self.dir = tempfile.mkdtemp(prefix='piper-')
        self.log.info("Created temporary dir '{0}'".format(self.dir))

        self.cwd = os.path.join(self.dir, os.getcwd().split('/')[-1])
        self.log.info("Copying repo to '{0}'...".format(self.cwd))

        shutil.copytree(os.getcwd(), self.cwd)
        self.log.info("Copying done.")

        os.chdir(self.dir)
        self.log.info("Working directory set to '{0}'".format(self.cwd))

    def teardown(self):
        verb = 'Keeping'
        if self.config.delete_when_done:
            verb = 'Removing'
            shutil.rmtree(self.dir)

        self.log.info("{1} '{0}'".format(self.dir, verb))

    def execute(self, step):
        cwd = os.getcwd()
        if cwd != self.cwd:
            self.log.warning(
                "Directory changed to '{0}'. Resetting to '{1}'.".format(
                    cwd, self.cwd
                )
            )
            os.chdir(self.cwd)

        # Execute the base method
        return super(TempDirEnv, self).execute(step)
