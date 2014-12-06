import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand

install_requires = (
    'Flask==0.10.1',
    'Flask-RESTful==0.2.12',
    'Jinja2==2.7.3',
    'Logbook==0.7.0',
    'MarkupSafe==0.23',
    'PyYAML==3.11',
    'SQLAlchemy==0.9.7',
    'Werkzeug==0.9.6',
    'ago==0.0.6',
    'aniso8601==0.83',
    'blessings==1.5.1',
    'facterpy==0.1',
    'itsdangerous==0.24',
    'jsonschema==2.3.0',
    'six==1.7.3',
)

tests_require = (
    'cov-core==1.15.0',
    'coverage==3.7.1',
    'mock==1.0.1',
    'py==1.4.26',
    'pytest==2.6.4',
    'pytest-cov==1.8.1',
    'pytz==2014.10',
    'tox==1.8.0',
    'virtualenv==1.11.6',
)


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = [
            'test',
            '-v',
            '--cov=piper',
            '--cov-report=xml',
            '--cov-report=term-missing',
            '--result-log=pytest-results.log'
        ]
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


class PyTestIntegration(PyTest):
    def finalize_options(self):
        super(PyTestIntegration, self).finalize_options()
        # Only run tests from classes that match "Integration"
        self.test_args.append('-k Integration')


class PyTestUnit(PyTest):
    def finalize_options(self):
        super(PyTestUnit, self).finalize_options()
        # Only run tests from classes that do not match "Integration"
        self.test_args.append('-k not Integration')


setup(
    name='piper',
    version='0.0.1',
    url='https://github.com/thiderman/piper',
    author='Lowe Thiderman',
    author_email='lowe.thiderman@gmail.com',
    description=('Manifest-based build pipeline system'),
    license='MIT',
    packages=['piper'],
    install_requires=install_requires,
    tests_require=tests_require,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'piper = piper.cli.cmd_piper:entry',
            'piperd = piper.cli.cmd_piperd:entry',
        ],
    },
    cmdclass={
        'test': PyTest,
        'integration': PyTestIntegration,
        'unit': PyTestUnit,
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Build Tools',
    ],
)
