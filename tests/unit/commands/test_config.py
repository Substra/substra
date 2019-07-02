import json
import os
from unittest import TestCase, mock

from mock import mock_open

from substra.commands.config import Config, default_config, ConfigException

empty_file = mock_open(
    read_data=json.dumps({}))

loaded_file = mock_open(
    read_data=json.dumps({
        "default": {"url": "http://127.0.0.1:8000", "version": "0.0"}}))

custom_loaded_file = mock_open(
    read_data=json.dumps({
        "default": {"url": "http://tutu:8000", "version": "1.0"}}))

corrupt_file = mock_open(read_data='tutu')


class TestConfig(TestCase):

    def test_init_config_empty(self):
        with mock.patch('substra.commands.config.open', empty_file, create=True):
            res = Config({
                '<url>': 'http://127.0.0.1:8000',
                '<version>': '0.0',
            }).run()

            self.assertEqual(res, default_config)

    def test_init_config(self):
        with mock.patch('substra.commands.config.open', loaded_file, create=True):
            res = Config({
                '<url>': 'http://foo.com',
                '<version>': '1.0',
            }).run()

            self.assertEqual(res, {
                'default': {
                    'url': 'http://foo.com',
                    'version': '1.0',
                    'insecure': False,
                    'auth': False
                }
            })

    def test_init_config_override(self):
        with mock.patch('substra.commands.config.open', custom_loaded_file, create=True):
            res = Config({
                '<url>': 'http://override.com',
                '<version>': '9.9',
            }).run()

            self.assertEqual(res, {
                'default': {
                    'url': 'http://override.com',
                    'version': '9.9',
                    'insecure': False,
                    'auth': False
                }
            })

    def test_init_config_corrupt(self):
        with mock.patch('substra.commands.config.open', corrupt_file, create=True):
            with self.assertRaises(ConfigException):
                Config({
                    '<url>': 'http://foo.com',
                    '<version>': '1.0',
                }).run()

    def test_init_config_basic_auth(self):
        with mock.patch('substra.commands.config.open', empty_file, create=True):
            res = Config({
                '<url>': 'http://foo.com',
                '<version>': '0.1',
                '<user>': 'foo',
                '<password>': 'bar'
            }).run()

            self.assertEqual(res, {
                'default': {
                    'url': 'http://foo.com',
                    'version': '0.1',
                    'insecure': False,
                    'auth': {
                        'user': 'foo',
                        'password': 'bar'
                    },
                }
            })


class TestConfigOverride(TestCase):
    def setUp(self):
        json.dump({
            'default': {
                'url': 'http://localhost',
                'version': '0.0'
            }
        }, open('/tmp/.substra_config', 'w+'))

    def tearDown(self):
        try:
            os.remove('/tmp/.substra_config')
        except Exception:
            pass

    def test_add_profile(self):
        res = Config({
            '<url>': 'http://foo.com',
            '<version>': '1.0',
            '--profile': 'test',
            '--config': '/tmp/.substra_config'
        }).run()

        self.assertEqual(res, {
            'default': {
                'url': 'http://localhost',
                'version': '0.0',
            },
            'test': {
                'url': 'http://foo.com',
                'version': '1.0',
                'insecure': False,
                'auth': False,
            }
        })
