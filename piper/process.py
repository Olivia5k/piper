import subprocess as sub

import logbook


class Process(object):
    """
    Helper class for running processes

    """

    def __init__(self, cmd):
        self.cmd = cmd

        self.proc = None
        self.success = None
        self.log = logbook.Logger(self.__class__.__name__)

    def setup(self):
        """
        Setup the Popen object used in execution

        """

        self.log.info('Spawning handler for {0}...'.format(self.cmd))

        self.popen = sub.Popen(
            self.cmd.split(),
            stdout=sub.PIPE,
            stderr=sub.PIPE,
        )

    def run(self):
        self.log.info('Executing {0}'.format(self.cmd))

        while not self.popen.poll():
            # TODO: Gracefully handle stderr as well
            line = self.popen.stdout.readline()

            if not line:
                break

            self.log.info(line.decode('utf-8').rstrip())

        exit = self.popen.wait()
        self.log.info('Exitcode {0}'.format(exit))

        self.success = exit == 0
        if not self.success:
            self.log.error(self.popen.stderr.read())
