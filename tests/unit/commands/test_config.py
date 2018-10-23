from unittest import TestCase, mock

from mock import mock_open

from substra.commands import Config, default_config

empty_file = mock_open(read_data='')
loaded_file = mock_open(read_data='{"url": "http://127.0.0.1:8000", "version": "0.0.0"}')
custom_loaded_file = mock_open(read_data='{"url": "http://tutu:8000" "version": "1.0.0"}}')
corrupt_file = mock_open(read_data='tutu')


class TestConfig(TestCase):

    def test_init_config_empty(self):
        with mock.patch('substra.commands.config.open', empty_file, create=True) as mock_object:
            res = Config({
                '<url>': 'http://127.0.0.1:8000',
                '<version>': '0.0.0',
            }).run()

            self.assertTrue(res == default_config)

            self.assertEqual(len(mock_object.call_args_list), 1)

    def test_init_config(self):
        with mock.patch('substra.commands.config.open', loaded_file, create=True) as mock_object:
            res = Config({
                '<url>': 'http://toto.com',
                '<version>': '1.0.0',
            }).run()

            self.assertTrue(res == {
                'url': 'http://toto.com',
                'version': '1.0.0',
            })

            self.assertEqual(len(mock_object.call_args_list), 1)

    def test_init_config_override(self):
        with mock.patch('substra.commands.config.open', custom_loaded_file, create=True) as mock_object:
            res = Config({
                '<url>': 'http://override.com',
                '<version>': '9.9.9',
            }).run()

            self.assertTrue(res == {
                'url': 'http://override.com',
                'version': '9.9.9',
            })

            self.assertEqual(len(mock_object.call_args_list), 1)

    def test_init_config_corrupt(self):
        with mock.patch('substra.commands.config.open', corrupt_file, create=True) as mock_object:
            res = Config({
                '<url>': 'http://toto.com',
                '<version>': '1.0.0',
            }).run()

            self.assertTrue(res == {
                'url': 'http://toto.com',
                'version': '1.0.0',
            })

            self.assertEqual(len(mock_object.call_args_list), 1)