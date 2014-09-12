import datetime

import ago
import logbook
import six

from piper.utils import dynamic_load


class Build(object):
    """
    The main pipeline runner.

    This class loads the configurations, jobs up all other components,
    executes them in whatever order they are supposed to happen in, collects
    data about the state of the pipeline and persists it, and finally tears
    down the components that needs tearing down.

    """

    def __init__(self, ns, config):
        self.ns = ns
        self.config = config

        self.job_key = self.ns.job
        self.env_key = self.ns.env

        self.start = datetime.datetime.now()

        self.classes = {}
        self.steps = {}
        self.order = []
        self.success = None

        self.log = logbook.Logger(self.__class__.__name__)

    def run(self):
        """
        Main entry point

        This is run when starting the script from the command line.
        Returns boolean success.

        """

        self.log.info('Setting up {0}...'.format(self.job_key))

        self.setup()
        self.execute()
        self.teardown()

        self.end = datetime.datetime.now()

        verb = 'finished successfully in'
        if not self.success:
            verb = 'failed after'

        ts = ago.human(
            self.end - self.start,
            precision=5,
            past_tense='%s {0}' % verb  # hee hee
        )
        self.log.info('{0} {1}'.format(self.version, ts))
        return self.success

    def setup(self):
        """
        Performs all setup steps

        This is basically an umbrella function that runs setup for all the
        things that the class needs to run a fully configured execute().

        """

        self.load_classes()
        self.set_version()
        self.configure_env()
        self.configure_steps()
        self.configure_job()

        self.setup_env()

    def load_classes(self):
        self.log.debug("Loading classes for versions, steps and envs...")

        classes = set()

        classes.add(self.config.version['class'])

        for env in self.config.envs.values():
            classes.add(env['class'])

        for step in self.config.steps.values():
            classes.add(step['class'])

        for cls in classes:
            self.log.debug("Loading class '{0}()'".format(cls))
            self.classes[cls] = dynamic_load(cls)

        self.log.debug("Class loading done.")

    def set_version(self):
        """
        Set the version for this job

        """

        self.log.debug('Determining version...')
        ver_config = self.config.version
        cls = self.classes[ver_config['class']]

        self.version = cls(self.ns, ver_config)
        self.version.validate()
        self.log.info(str(self.version))

    def configure_env(self):
        """
        Configures the environment according to its config file.

        """

        self.log.debug('Loading environment...')
        env_config = self.config.envs[self.env_key]
        cls = self.classes[env_config['class']]

        self.env = cls(self.ns, env_config)
        self.log.debug('Validating env config...')
        self.env.validate()
        self.env.log.debug('Environment configured.')

    def configure_steps(self):
        """
        Configures the steps according to their config sections.

        """

        for step_key, step_config in self.config.steps.items():
            cls = self.classes[step_config['class']]

            step = cls(self.ns, step_config, step_key)
            step.log.debug('Validating config...')
            step.validate()
            step.log.debug('Step configured.')
            self.steps[step_key] = step

    def configure_job(self):
        """
        Places steps in proper order according to the chosen set.

        """

        for step_key in self.config.jobs[self.job_key]:
            step = self.steps[step_key]
            self.order.append(step)

            if step.config.depends:
                self.inject_step_dependency(step, step.config.depends)

        self.log.debug('Step order configured.')
        self.log.info('Steps: ' + ', '.join(map(repr, self.order)))

    def inject_step_dependency(self, step, depends):
        # We can pass both lists and strings. Handle accordingly.
        if isinstance(depends, six.string_types):
            targets = (depends,)
        else:
            targets = depends

        index = self.order.index(step)
        for dep_key in targets:
            dep = self.steps[dep_key]

            self.order.insert(index, dep)
            index += 1  # So that the next one gets the right order

            self.log.debug('Adding {0} as {1} dependency...'.format(dep, step))

            # If the injected step has dependencies as well, we need to
            # recursively add those too.
            if dep.config.depends:
                self.inject_step_dependency(dep, dep.config.depends)

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
        self.log.info('Running {0}...'.format(self.job_key))

        for x, step in enumerate(self.order, start=1):
            step.set_index(x, total)
            step.log.info('Running...')
            proc = self.env.execute(step)

            if proc.success:
                step.log.info('Step complete.')
            else:
                # If the success is not positive, bail and stop running.
                step.log.error('Step "{0}" failed.'.format(self.job_key))
                self.success = False
                break

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

    def teardown_env(self):
        """
        Execute teardown step of the env

        """

        self.env.log.debug('Tearing down env...')
        self.env.teardown()
