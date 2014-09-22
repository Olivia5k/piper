import ago
import logbook
import mock

from piper.db.core import LazyDatabaseMixin
from piper.vcs import GitVCS
from piper import utils


class Build(LazyDatabaseMixin):
    """
    The main pipeline runner.

    This class loads the configurations, jobs up all other components,
    executes them in whatever order they are supposed to happen in, collects
    data about the state of the pipeline and persists it, and finally tears
    down the components that needs tearing down.

    """

    def __init__(self, config):
        self.config = config

        self.vcs = GitVCS('github', 'git@github.com')

        self.start = utils.now()

        self.id = None
        self.version = None
        self.steps = {}
        self.order = []
        self.success = None
        self.crashed = False
        self.status = None

        self.log = logbook.Logger(self.__class__.__name__)

        if self.config.dry_run is True:  # pragma: nocover
            self.log.warn('Switching to mock database for dry run')
            self.db = mock.Mock()

    def run(self):
        """
        Main entry point

        This is run when starting the script from the command line.
        Returns boolean success.

        """

        self.log.info('Setting up {0}...'.format(self.config.job))

        self.setup()
        self.execute()
        self.teardown()
        self.finish()

        return self.success

    def finish(self):
        self.end = utils.now()
        self.db.update_build(self, ended=self.end)

        verb = 'finished successfully in'
        if not self.success:
            verb = 'failed after'

        ts = ago.human(
            self.end - self.start,
            precision=5,
            past_tense='%s {0}' % verb  # hee hee
        )
        self.log.info('{0} {1}'.format(self.version, ts))

    def setup(self):
        """
        Performs all setup steps

        This is basically an umbrella function that runs setup for all the
        things that the class needs to run a fully configured execute().

        """

        self.add_build()
        self.lock_agent()
        self.set_version()

        self.configure_env()
        self.configure_steps()
        self.configure_job()

        self.setup_env()

    def add_build(self):
        """
        Add a build object to the database

        Also store the reference to the build

        """

        self.ref = self.db.add_build(self)

    def set_version(self):
        """
        Set the version for this job

        """

        self.log.debug('Determining version...')
        ver_config = self.config.raw['version']
        cls = self.config.classes[ver_config['class']]

        self.version = cls(ver_config)
        self.version.validate()
        self.log.info(str(self.version))

    def configure_env(self):
        """
        Configures the environment according to its config file.

        """

        self.log.debug('Loading environment...')
        env_config = self.config.raw['envs'][self.config.env]
        cls = self.config.classes[env_config['class']]

        self.env = cls(env_config)
        self.log.debug('Validating env config...')
        self.env.validate()
        self.env.log.debug('Environment configured.')

    def configure_steps(self):
        """
        Configures the steps according to their config sections.

        """

        for step_key, step_config in self.config.raw['steps'].items():
            cls = self.config.classes[step_config['class']]

            step = cls(step_config, step_key)
            step.log.debug('Validating config...')
            step.validate()
            step.log.debug('Step configured.')
            self.steps[step_key] = step

    def configure_job(self):
        """
        Places steps in proper order according to the chosen set.

        """

        for step_key in self.config.raw['jobs'][self.config.job]:
            step = self.steps[step_key]
            self.order.append(step)

        self.log.debug('Step order configured.')
        self.log.info('Steps: ' + ', '.join(map(repr, self.order)))

    def setup_env(self):
        """
        Execute setup steps of the env

        """

        self.env.log.debug('Setting up env...')
        self.env.setup()

    def execute(self):
        """
        Runs the steps and determines whether to continue or not.

        Of all the things to happen in this application, this is probably
        the most important part!

        """

        total = len(self.order)
        self.log.info('Running {0}...'.format(self.config.job))

        for x, step in enumerate(self.order, start=1):
            step.set_index(x, total)

            # Update db status to show that we are running this build
            self.status = '{0}/{1}: {2}'.format(x, total, step.key)
            self.db.update_build(self)

            step.log.info('Running...')
            proc = self.env.execute(step)

            if proc.success:
                step.log.info('Step complete.')
            else:
                # If the success is not positive, bail and stop running.
                step.log.error('Step "{0}" failed.'.format(self.config.job))
                self.success = False
                break

        self.status = ''
        # As long as we did not break out of the loop above, the build is
        # to be deemed succesful.
        if self.success is not False:
            self.success = True

    def save_state(self):
        """
        Collects all data about the pipeline being built and persists it.

        """

    def teardown(self):
        self.teardown_env()
        self.unlock_agent()

    def teardown_env(self):
        """
        Execute teardown step of the env

        """

        self.env.log.debug('Tearing down env...')
        self.env.teardown()

    def default_db_kwargs(self):  # pragma: nocover
        """
        Generate a dict with keys to update in the database

        """

        return {
            'success': self.success,
            'crashed': self.crashed,
            'status': self.status,
            'updated': utils.now()
        }

    def lock_agent(self):
        self.log.info('Locking agent')
        self.db.lock_agent(self)

    def unlock_agent(self):
        self.log.info('Unlocking agent')
        self.db.unlock_agent(self)


class ExecCLI(object):
    def __init__(self, config):
        self.config = config

    def compose(self, parser):  # pragma: nocover
        cli = parser.add_parser('exec', help='Execute a job')

        cli.add_argument(
            'job',
            nargs='?',
            default='build',
            help='The job to execute',
        )

        cli.add_argument(
            'env',
            nargs='?',
            default='local',
            help='The environment to execute in',
        )

        cli.add_argument(
            '--dry-run',
            '-n',
            action='store_true',
            help="Only print execution commands, don't actually do anything",
        )

        return 'exec', self.run

    def run(self):
        success = Build(self.config).run()

        return 0 if success else 1
