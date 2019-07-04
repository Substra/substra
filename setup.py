"""Packaging settings."""
from codecs import open
import os

from setuptools import setup, find_packages

from substra import __version__

current_dir = os.path.abspath(os.path.dirname(__file__))


def read_readme_file():
    path = os.path.join(current_dir, 'README.md')
    with open(path, encoding='utf-8') as fp:
        return fp.read()


setup(
    name='substra',
    version=__version__,
    description='Substra CLI for interacting with substrabac',
    long_description=read_readme_file(),
    url='https://github.com/SubstraFoundation/substra-cli',
    author='Owkin, Substra team',
    author_email='substra@owkin.com',
    license='Apache 2.0',
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
    install_requires=['click', 'requests', 'docker', 'consolemd'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-cov', 'pytest-mock'],
    entry_points={
        'console_scripts': [
            'substra=substra.cli.interface:cli',
        ],
    },
)
