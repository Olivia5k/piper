import os
import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['test', '--cov=piper']
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


def load_requirements():
    filename = os.path.join(os.path.dirname(sys.argv[0]), 'requirements.txt')

    with open(filename) as handle:
        lines = (line.strip() for line in handle)
        return [line for line in lines if line and not line.startswith("#")]


setup(
    name='piper',
    version='0.0.1',
    url='https://github.com/thiderman/piper',
    author='Lowe Thiderman',
    author_email='lowe.thiderman@gmail.com',
    description=('Manifest-based build pipeline system'),
    license='MIT',
    packages=['piper'],
    install_requires=load_requirements(),
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
