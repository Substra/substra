import json
from unittest import mock

from .test_base import bulk_data_samples
from .test_base import TestBase, MockResponse


def mocked_requests_post_data(*args, **kwargs):
    return MockResponse(bulk_data_samples, 201)


class TestBulkAdd(TestBase):

    @mock.patch('substra_sdk_py.http_cli.requests.post', side_effect=mocked_requests_post_data)
    def test_bulk_add_data(self, mock_get):
        # open data file
        with open(self.bulk_data_samples_file_path, 'r') as f:
            content = json.loads(f.read())

        res = self.client.add('data_sample', content)
        self.assertEqual(res, bulk_data_samples)
        self.assertEqual(len(mock_get.call_args_list), 1)
