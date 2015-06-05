import logbook
import sh

from piper.logging import SEPARATOR


class Process:
    """
    Helper class for running processes

    """

    def __init__(self, config, cmd, parent_key):
        self.config = config
        self.cmd = cmd

        self.sh = None
        self.success = None
        self.log = logbook.Logger(parent_key + SEPARATOR + self.cmd)

    def setup(self):
        """
        Setup the Popen object used in execution

        """

        self.log.debug('Spawning process handler')

        cmd, *args = self.cmd.split()
        self.sh = sh.Command(cmd)(args, _iter=True)

    def run(self):
        self.log.debug('Executing')

        try:
            for line in self.sh:
                self.log.info(line.strip())

        except sh.ErrorReturnCode:
            self.log.error(self.sh.stderr)

        finally:
            exit = self.sh.exit_code
            self.success = exit == 0
            self.log.debug('Exitcode {0}'.format(exit))
