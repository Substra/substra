import json
import os
from unittest import TestCase, mock

from substra.commands import Config, BulkUpdate

data = [
    {
        "pkhash": "62fb3263208d62c7235a046ee1d80e25512fe782254b730a9e566276b8c0ef3a",
    },
    {
        "pkhash": "42303efa663015e729159833a12ffb510ff92a6e386b8152f90f6fb14ddc94c9",
    }
]


def mocked_client_bulk_update(data, st):
    return {'result': data,
            'status_code': st}


@mock.patch('substra.commands.api.config_path', '/tmp/.substra', create=True)
class TestBulkUpdate(TestCase):
    def setUp(self):
        self.data_file_path = './tests/assets/data/bulk_update_data.json'

        with mock.patch('substra.commands.config.config_path', '/tmp/.substra',
                        create=True):
            Config({
                '<url>': 'http://foo.com',
                '<version>': '1.0',
            }).run()

    def tearDown(self):
        try:
            os.remove('/tmp/.substra')
        except:
            pass

    @mock.patch('substra.commands.api.Client.bulk_update',
                return_value=mocked_client_bulk_update(data, 201))
    def test_bulk_update_data(self, mock_bulk_update):

        with open(self.data_file_path, 'r') as f:
            content = f.read()

            res = BulkUpdate({
                '<asset>': 'data_sample',
                '<args>': content,
            }).run()

            self.assertEqual(json.loads(res)['status_code'], 201)
            self.assertTrue(json.loads(res)['result'], data)
            self.assertEqual(len(mock_bulk_update.call_args_list), 1)
