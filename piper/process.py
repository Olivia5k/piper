import subprocess as sub

import logbook


class Process(object):
    """
    Helper class for running processes

    """

    def __init__(self, cmd):
        self.cmd = cmd

        self.popen = None
        self.success = None
        self.log = logbook.Logger(self.cmd)

    def setup(self):
        """
        Setup the Popen object used in execution

        """

        self.log.debug('Spawning process handler')

        self.popen = sub.Popen(
            self.cmd.split(),
            stdout=sub.PIPE,
            stderr=sub.PIPE,
        )

    def run(self):
        self.log.debug('Executing')

        while not self.popen.poll():
            # TODO: Gracefully handle stderr as well
            line = self.popen.stdout.readline()

            if not line:
                break

            self.log.info(line.decode('utf-8').rstrip())

        exit = self.popen.wait()
        self.log.debug('Exitcode {0}'.format(exit))

        self.success = exit == 0
        if not self.success:
            self.log.error(self.popen.stderr.read())
