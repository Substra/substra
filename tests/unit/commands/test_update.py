import json
import os
from unittest import TestCase, mock

from substra.commands import Config, Update

data_manager = {
    "pkhash": "62fb3263208d62c7235a046ee1d80e25512fe782254b730a9e566276b8c0ef3a",
}


def mocked_update_data_manager(data, st):
    return {'result': data,
            'status_code': st}


@mock.patch('substra.commands.api.config_path', '/tmp/.substra', create=True)
class TestUpdate(TestCase):
    def setUp(self):
        self.data_manager_file_path = './tests/assets/data_manager/update_data_manager.json'

        with mock.patch('substra.commands.config.config_path', '/tmp/.substra',
                        create=True):
            Config({
                '<url>': 'http://toto.com',
                '<version>': '1.0',
            }).run()

    def tearDown(self):
        try:
            os.remove('/tmp/.substra')
        except:
            pass

    @mock.patch('substra.commands.api.Client.update',
                return_value=mocked_update_data_manager(data_manager, 200))
    def test_update_data_manager(self, mock_update):
        with open(self.data_manager_file_path, 'r') as f:
            content = f.read()

            res = Update({
                '<asset>': 'data-manager',
                '<pkhash>': '62fb3263208d62c7235a046ee1d80e25512fe782254b730a9e566276b8c0ef3a',
                '<args>': content,
            }).run()

            self.assertEqual(json.loads(res)['status_code'], 200)
            self.assertEqual(json.loads(res)['result'], data_manager)
            self.assertEqual(len(mock_update.call_args_list), 1)
