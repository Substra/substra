"""Packaging settings."""
from codecs import open
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))


with open(os.path.join(here, 'README.md'), 'r', 'utf-8') as fp:
    readme = fp.read()


about = {}
with open(os.path.join(here, 'substra', '__version__.py'), 'r', 'utf-8') as fp:
    exec(fp.read(), about)


setup(
    name='substra',
    version=about['__version__'],
    description='Substra CLI for interacting with substra backend',
    long_description=readme,
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
    include_package_data=True,
    install_requires=['click', 'requests', 'docker', 'consolemd', 'pyyaml'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-cov', 'pytest-mock'],
    entry_points={
        'console_scripts': [
            'substra=substra.cli.interface:cli',
        ],
    },
    zip_safe=False,
)
