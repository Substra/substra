"""Tests for our main substra CLI module."""


from subprocess import PIPE, Popen as popen
from unittest import TestCase

from substra import __version__ as VERSION


class TestHelp(TestCase):
    def test_returns_usage_information(self):
        output = popen(['substra', '-h'], stdout=PIPE).communicate()[0]
        self.assertTrue('Usage:' in output.decode('utf-8'))

        output = popen(['substra', '--help'], stdout=PIPE).communicate()[0]
        self.assertTrue('Usage:' in output.decode('utf-8'))


class TestVersion(TestCase):
    def test_returns_version_information(self):
        output = popen(['substra', '--version'], stdout=PIPE).communicate()[0]
        self.assertEqual(output.decode('utf-8').strip(), VERSION)


class TestCommand(TestCase):
    def test_returns_command(self):
        output = popen(['substra', 'list', 'challenge'], stdout=PIPE).communicate()[0]
        self.assertTrue(output.decode('utf-8') == "Can't decode response value to json. Please make sure the substrabac instance is live.\n")