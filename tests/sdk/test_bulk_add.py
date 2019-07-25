import json
from unittest import mock

from .test_base import bulk_data_samples
from .test_base import TestBase, mock_success_response


def mocked_requests_post_data_sample(*args, **kwargs):
    return mock_success_response(data=bulk_data_samples)


class TestBulkAdd(TestBase):

    @mock.patch('substra.sdk.rest_client.requests.post', side_effect=mocked_requests_post_data_sample)
    def test_bulk_add_data(self, mock_get):
        # open data file
        with open(self.bulk_data_samples_file_path, 'r') as f:
            data = json.loads(f.read())

        res = self.client.add_data_sample(data)
        self.assertEqual(res, bulk_data_samples)
        self.assertEqual(len(mock_get.call_args_list), 1)
