import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand

install_requires = (
    'Logbook==0.6.0',
    'PyYAML==3.11',
    'jsonschema==2.3.0',
    'blessings==1.5.1',
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
        self.test_args = ['test', '--cov=piper']
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


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
            'piper = piper:main',
        ],
    },
    cmdclass={'test': PyTest},
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2.6',
        'Topic :: Software Development :: Build Tools',
    ],
)
