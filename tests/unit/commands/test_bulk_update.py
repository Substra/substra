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


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


def mocked_requests_post_data(*args, **kwargs):
    return MockResponse(data, 201)


@mock.patch('substra.commands.api.config_path', '/tmp/.substra', create=True)
class TestBulkUpdate(TestCase):
    def setUp(self):
        self.data_file_path = './tests/assets/data/bulk_update_data.json'

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

    @mock.patch('substra.commands.bulk_update.requests.post', side_effect=mocked_requests_post_data)
    def test_bulk_update_data(self, mock_get):
        with open(self.data_file_path, 'r') as f:
            content = f.read()

            res = BulkUpdate({
                '<asset>': 'data',
                '<args>': content,
            }).run()

            print(res)

            self.assertEqual(json.loads(res)['status_code'], 201)
            self.assertTrue(json.loads(res)['result'], data)
            self.assertEqual(len(mock_get.call_args_list), 1)
