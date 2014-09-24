import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand

install_requires = (
    'Logbook==0.7.0',
    'PyYAML==3.11',
    'jsonschema==2.3.0',
    'blessings==1.5.1',
    'six==1.7.3',
    'ago==0.0.6',
    'facterpy==0.1',
    'SQLAlchemy==0.9.7',
    'Flask==0.10.1',
    'Flask-RESTful==0.2.12',
)

tests_require = (
    'cov-core==1.7',
    'coverage==3.7.1',
    'mock==1.0.1',
    'py==1.4.20',
    'pytest==2.5.2',
    'pytest-cov==1.6',
    'tox==1.7.1',
    'virtualenv==1.11.4',
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
