import json
import os
from unittest import TestCase, mock

from substra_sdk_py.add import add as addFunction

data = [
    {
        "pkhash": "2d0f943aa81a9cb3fe84b162559ce6aff068ccb04e0cb284733b8f9d7e06517e",
        "validated": True,
        "file": "http://127.0.0.1:8000/media/data_sample/2d0f943aa81a9cb3fe84b162559ce6aff068ccb04e0cb284733b8f9d7e06517e/0024315.zip"
    },
    {
        "pkhash": "4b5152871b181d10ee774c10458c064c70710f4ba35938f10c0b7aa51f7dc010",
        "validated": True,
        "file": "http://127.0.0.1:8000/media/data_sample/4b5152871b181d10ee774c10458c064c70710f4ba35938f10c0b7aa51f7dc010/0024701.zip"
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


class TestBulkAdd(TestCase):
    def setUp(self):
        self.data_samples_file_path = './tests/assets/data_sample/bulk_data_samples.json'

        self.config = {
            'url': 'http://toto.com',
            'version': '1.0',
            'auth': False,
            'insecure': False,
        }

    def tearDown(self):
        pass

    @mock.patch('substra_sdk_py.add.requests.post', side_effect=mocked_requests_post_data)
    def test_bulk_add_data(self, mock_get):
        # open data file
        with open(self.data_samples_file_path, 'r') as f:
            content = json.loads(f.read())

            res = addFunction('data_sample', content, config=self.config)

            self.assertEqual(res['status_code'], 201)
            self.assertEqual(res['result'], data)
            self.assertEqual(len(mock_get.call_args_list), 1)
