import json
import os
from unittest import TestCase, mock

from substra.commands import Add, Config

data = [
    {
        "pkhash": "2d0f943aa81a9cb3fe84b162559ce6aff068ccb04e0cb284733b8f9d7e06517e",
        "validated": True,
        "file": "http://127.0.0.1:8000/media/data/2d0f943aa81a9cb3fe84b162559ce6aff068ccb04e0cb284733b8f9d7e06517e/0024315.zip"
    },
    {
        "pkhash": "4b5152871b181d10ee774c10458c064c70710f4ba35938f10c0b7aa51f7dc010",
        "validated": True,
        "file": "http://127.0.0.1:8000/media/data/4b5152871b181d10ee774c10458c064c70710f4ba35938f10c0b7aa51f7dc010/0024701.zip"
    }
]


def mocked_client_add(data, st):
    return {'result': data,
            'status_code': st}


@mock.patch('substra.commands.api.config_path', '/tmp/.substra', create=True)
class TestBulkAdd(TestCase):
    def setUp(self):
        self.data_file_path = './tests/assets/data/bulk_data.json'

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

    @mock.patch('substra.commands.api.Client.add',
                return_value=mocked_client_add(data, 201))
    def test_bulk_add_data(self, mock_add):
        # open data file
        with open(self.data_file_path, 'r') as f:
            content = f.read()

            res = Add({
                '<asset>': 'data_sample',
                '<args>': content,
            }).run()

            self.assertEqual(json.loads(res)['status_code'], 201)
            self.assertEqual(json.loads(res)['result'], data)
            self.assertEqual(len(mock_add.call_args_list), 1)
