import json
from unittest import mock

from .test_base import TestBase, mock_success_response

data_sample_keys = [
    {
        "pkhash": "62fb3263208d62c7235a046ee1d80e25512fe782254b730a9e566276b8c0ef3a",
    },
    {
        "pkhash": "42303efa663015e729159833a12ffb510ff92a6e386b8152f90f6fb14ddc94c9",
    }
]


def mocked_requests_post_data_sample(*args, **kwargs):
    return mock_success_response(data=data_sample_keys)


class TestBulkUpdate(TestBase):

    @mock.patch('substra_sdk_py.requests_wrapper.requests.post', side_effect=mocked_requests_post_data_sample)
    def test_bulk_update_data(self, mock_get):
        with open(self.data_samples_file_path, 'r') as f:
            content = json.loads(f.read())

        res = self.client.bulk_update('data_sample', content)

        self.assertTrue(res, data_sample_keys)
        self.assertEqual(len(mock_get.call_args_list), 1)
