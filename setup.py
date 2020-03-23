# Copyright 2018 Owkin, inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
    description='Substra CLI for interacting with substra-backend',
    long_description=readme,
    long_description_content_type="text/markdown",
    url='https://github.com/SubstraFoundation/substra',
    author='Owkin',
    author_email='fldev@owkin.com',
    license='Apache 2.0',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
    ],
    keywords=['cli', 'substra'],
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    install_requires=['click', 'requests', 'docker', 'consolemd', 'pyyaml', 'keyring'],
    python_requires='>=3.6',
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-cov', 'pytest-mock', 'keyrings.alt'],
    entry_points={
        'console_scripts': [
            'substra=substra.cli.interface:cli',
        ],
    },
    zip_safe=False,
)
