import json
from unittest import TestCase, mock

from substra_sdk_py.update import update as updateFunction

data_manager = {
    "pkhash": "62fb3263208d62c7235a046ee1d80e25512fe782254b730a9e566276b8c0ef3a",
}


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


def mocked_requests_post_data_manager(*args, **kwargs):
    return MockResponse(data_manager, 200)


class TestUpdate(TestCase):
    def setUp(self):
        self.data_manager_file_path = './tests/assets/data_manager/update_data_manager.json'

        self.config = {
            'url': 'http://toto.com',
            'version': '1.0',
            'auth': False,
            'insecure': False,
        }

    def tearDown(self):
        pass

    @mock.patch('substra_sdk_py.update.requests.post',
                side_effect=mocked_requests_post_data_manager)
    def test_update_data_manager(self, mock_get):
        with open(self.data_manager_file_path, 'r') as f:
            content = json.loads(f.read())

            res = updateFunction('data_manager',
                                 '62fb3263208d62c7235a046ee1d80e25512fe782254b730a9e566276b8c0ef3a',
                                 content,
                                 self.config)

            self.assertEqual(res['status_code'], 200)
            self.assertEqual(res['result'], data_manager)
            self.assertEqual(len(mock_get.call_args_list), 1)
