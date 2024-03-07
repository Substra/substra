"""Packaging settings."""

import os
from codecs import open

from setuptools import find_packages
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))


with open(os.path.join(here, "README.md"), "r", "utf-8") as fp:
    readme = fp.read()


about = {}
with open(os.path.join(here, "substra", "__version__.py"), "r", "utf-8") as fp:
    exec(fp.read(), about)


setup(
    name="substra",
    version=about["__version__"],
    description="Low-level Python library for interacting with a Substra network",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://docs.substra.org",
    author="Owkin, Inc.",
    license="Apache 2.0",
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Utilities",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords=["cli", "substra"],
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    install_requires=[
        "requests",
        "urllib3<2",
        "docker",
        "pyyaml",
        "pydantic>=2.3.0,<3.0.0",
        "tqdm",
        "python-slugify",
    ],
    python_requires=">=3.9",
    extras_require={
        "dev": [
            "pandas",
            "pytest",
            "pytest-cov",
            "pytest-mock",
            "substratools>=0.21.2",
            "black",
            "flake8",
            "isort",
            "docstring_parser",
        ],
    },
    zip_safe=False,
)
