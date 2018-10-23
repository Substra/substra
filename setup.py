"""Packaging settings."""

from codecs import open
from os.path import abspath, dirname, join
from subprocess import call

from setuptools import Command, find_packages, setup

from substra import __version__

this_dir = abspath(dirname(__file__))
with open(join(this_dir, 'README.rst'), encoding='utf-8') as file:
    long_description = file.read()


class RunTests(Command):
    """Run all tests."""
    description = 'run tests'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run all tests!"""
        errno = call(['py.test', '--cov=substra', '--cov-report=term-missing', '--ignore=tests/e2e'])
        raise SystemExit(errno)


setup(
    name='substra',
    version=__version__,
    description='Substra SDK for interacting with substrabac',
    long_description=long_description,
    url='https://github.com/substra/substraSDK',
    author='Guillaume Cisco',
    author_email='guillaumecisco@gmail.com',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: Private',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords=['cli', 'substra'],
    packages=find_packages(exclude=['docs', 'tests*']),
    install_requires=['docopt', 'requests'],
    extras_require={
        'test': ['coverage', 'pytest', 'pytest-cov', 'mock'],
    },
    entry_points={
        'console_scripts': [
            'substra=substra.cli:main',
        ],
    },
    cmdclass={'test': RunTests},
)
