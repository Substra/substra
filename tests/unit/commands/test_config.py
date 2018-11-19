import json
import os
from unittest import TestCase, mock

from mock import mock_open

from substra.commands import Config, default_config

empty_file = mock_open(read_data='')
loaded_file = mock_open(read_data='{"default": {"url": "http://127.0.0.1:8000", "version": "0.0"}}')
custom_loaded_file = mock_open(read_data='{"default": {"url": "http://tutu:8000" "version": "1.0"}}')
corrupt_file = mock_open(read_data='tutu')


class TestConfig(TestCase):

    def test_init_config_empty(self):
        with mock.patch('substra.commands.config.open', empty_file, create=True) as mock_object:
            res = Config({
                '<url>': 'http://127.0.0.1:8000',
                '<version>': '0.0',
            }).run()

            self.assertTrue(res == default_config)

            self.assertEqual(len(mock_object.call_args_list), 2)

    def test_init_config(self):
        with mock.patch('substra.commands.config.open', loaded_file, create=True) as mock_object:
            res = Config({
                '<url>': 'http://toto.com',
                '<version>': '1.0',
            }).run()

            self.assertTrue(res == {
                'default': {
                    'url': 'http://toto.com',
                    'version': '1.0',
                    'auth': False,
                    'insecure': False,
                }
            })

            self.assertEqual(len(mock_object.call_args_list), 1)

    def test_init_config_override(self):
        with mock.patch('substra.commands.config.open', custom_loaded_file, create=True) as mock_object:
            res = Config({
                '<url>': 'http://override.com',
                '<version>': '9.9',
            }).run()

            self.assertTrue(res == {
                'default': {
                    'url': 'http://override.com',
                    'version': '9.9',
                    'insecure': False,
                    'auth': False
                }
            })

            self.assertEqual(len(mock_object.call_args_list), 1)

    def test_init_config_corrupt(self):
        with mock.patch('substra.commands.config.open', corrupt_file, create=True) as mock_object:
            res = Config({
                '<url>': 'http://toto.com',
                '<version>': '1.0',
            }).run()

            self.assertTrue(res == {
                'default': {
                    'url': 'http://toto.com',
                    'version': '1.0',
                    'insecure': False,
                    'auth': False
                }
            })

            self.assertEqual(len(mock_object.call_args_list), 1)

    def test_init_config_basic_auth(self):
        with mock.patch('substra.commands.config.open', empty_file, create=True) as mock_object:
            res = Config({
                '<url>': 'http://toto.com',
                '<version>': '0.1',
                '<user>': 'foo',
                '<password>': 'bar'
            }).run()

            self.assertTrue(res == {
                'default': {
                    'url': 'http://toto.com',
                    'version': '0.1',
                    'insecure': False,
                    'auth': True,
                    'user': 'foo',
                    'password': 'bar'
                }
            })

            self.assertEqual(len(mock_object.call_args_list), 1)


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
        except:
            pass

    def test_add_profile(self):
        Config({
            '<url>': 'http://toto.com',
            '<version>': '1.0',
            '--profile': 'test',
            '--config': '/tmp/.substra_config'
        }).run()

        self.assertTrue({
            'default': {
                'url': 'http://localhost',
                'version': '0.0',
            },
            'test': {
                'url': 'http://toto.com',
                'version': '1.0',
            }
        })
