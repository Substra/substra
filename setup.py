from setuptools import setup

setup(name='substra-sdk-py',
      version='0.0.1',
      description='Python SDK for interacting with the substrabac project',
      url='https://github.com/SubstraFoundation/substra-sdk-py',
      author='Guillaume Cisco',
      author_email='guillaumecisco@gmail.com',
      license='MIT',
      packages=['substra_sdk_py'],
      install_requires=[
          'requests',
      ],
      zip_safe=False)
