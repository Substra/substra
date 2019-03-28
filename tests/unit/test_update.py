import json
from unittest import mock

from .test_base import TestBase, MockResponse

data_manager = {
    "pkhash": "62fb3263208d62c7235a046ee1d80e25512fe782254b730a9e566276b8c0ef3a",
}


def mocked_requests_post_data_manager(*args, **kwargs):
    return MockResponse(data_manager, 200)


class TestUpdate(TestBase):

    @mock.patch('substra_sdk_py.http_cli.requests.post',
                side_effect=mocked_requests_post_data_manager)
    def test_update_data_manager(self, mock_get):
        with open(self.data_manager_file_path, 'r') as f:
            content = json.loads(f.read())

        res = self.client.update(
            'data_manager',
            '62fb3263208d62c7235a046ee1d80e25512fe782254b730a9e566276b8c0ef3a',
            content)

        self.assertEqual(res, data_manager)
        self.assertEqual(len(mock_get.call_args_list), 1)
