import json
from unittest import TestCase, mock

from substra_sdk_py.update import update as updateFunction

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


class TestUpdate(TestCase):
    def setUp(self):
        self.dataset_file_path = './tests/assets/dataset/update_dataset.json'

        self.config = {
            'url': 'http://toto.com',
            'version': '1.0',
            'auth': False,
            'insecure': False,
        }

    def tearDown(self):
        pass

    @mock.patch('substra_sdk_py.update.requests.post',
                side_effect=mocked_requests_post_dataset)
    def test_update_dataset(self, mock_get):
        with open(self.dataset_file_path, 'r') as f:
            content = json.loads(f.read())

            res = updateFunction('dataset',
                                 '62fb3263208d62c7235a046ee1d80e25512fe782254b730a9e566276b8c0ef3a',
                                 content,
                                 self.config)

            self.assertEqual(res['status_code'], 200)
            self.assertEqual(res['result'], dataset)
            self.assertEqual(len(mock_get.call_args_list), 1)
