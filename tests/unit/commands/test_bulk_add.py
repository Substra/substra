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


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


def mocked_requests_post_data(*args, **kwargs):
    return MockResponse(data, 201)


@mock.patch('substra.commands.api.config_path', '/tmp/.substra', create=True)
class TestAdd(TestCase):
    def setUp(self):
        self.data_file_path = './tests/assets/data/bulk_data.json'

        with mock.patch('substra.commands.config.config_path', '/tmp/.substra', create=True):
            Config({
                '<url>': 'http://toto.com',
                '<version>': '1.0',
            }).run()

    def tearDown(self):
        try:
            os.remove('/tmp/.substra')
        except:
            pass

    @mock.patch('substra.commands.list.requests.post', side_effect=mocked_requests_post_data)
    def test_add_data(self, mock_get):
        # open algo file
        with open(self.data_file_path, 'r') as f:
            content = f.read()

            res = Add({
                '<entity>': 'data',
                '<args>': content,
            }).run()

            print(res)

            self.assertTrue(res == json.dumps(data))
            self.assertEqual(len(mock_get.call_args_list), 1)
