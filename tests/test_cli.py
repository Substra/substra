"""Tests for our main substra CLI module."""
import json
import os
from subprocess import PIPE, Popen as popen
from unittest import TestCase


from substra import __version__ as VERSION


class TestHelp(TestCase):
    def test_returns_usage_information(self):
        output = popen(['substra', '-h'], stdout=PIPE).communicate()[0]
        print(output.decode('utf-8'))
        self.assertTrue('Usage:' in output.decode('utf-8'))

        output = popen(['substra', '--help'], stdout=PIPE).communicate()[0]
        self.assertTrue('Usage:' in output.decode('utf-8'))


class TestVersion(TestCase):
    def test_returns_version_information(self):
        output = popen(['substra', '--version'], stdout=PIPE).communicate()[0]
        self.assertEqual(output.decode('utf-8').strip(), VERSION)


class TestCommand(TestCase):
    def setUp(self):
        json.dump({
            'default': {
                'url': 'http://localhost',
                'version': '0.0',
                'insecure': False,
            }
        }, open('/tmp/.substra2', 'w+'))

    def tearDown(self):
        try:
            os.remove('/tmp/.substra2')
        except:
            pass

    def test_returns_command(self):
            output = popen(['substra', 'list', 'objective', '--config=/tmp/.substra2'], stdout=PIPE).communicate()[0]

            print(output.decode('utf-8').strip())

            self.assertTrue('Failed to list objective' in output.decode('utf-8').strip())
