import json
import os
from unittest import TestCase, mock

from substra.commands import Config, BulkUpdate, Update

dataset = {
    "pkhash": "62fb3263208d62c7235a046ee1d80e25512fe782254b730a9e566276b8c0ef3a",
}


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


def mocked_requests_post_dataset(*args, **kwargs):
    return MockResponse(dataset, 200)


@mock.patch('substra.commands.api.config_path', '/tmp/.substra', create=True)
class TestUpdate(TestCase):
    def setUp(self):
        self.dataset_file_path = './tests/assets/dataset/update_dataset.json'

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

    @mock.patch('substra.commands.update.requests.post',
                side_effect=mocked_requests_post_dataset)
    def test_update_dataset(self, mock_get):
        with open(self.dataset_file_path, 'r') as f:
            content = f.read()

            res = Update({
                '<asset>': 'dataset',
                '<pkhash>': '62fb3263208d62c7235a046ee1d80e25512fe782254b730a9e566276b8c0ef3a',
                '<args>': content,
            }).run()

            print(res)

            self.assertEqual(json.loads(res)['status_code'], 200)
            self.assertEqual(json.loads(res)['result'], dataset)
            self.assertEqual(len(mock_get.call_args_list), 1)
