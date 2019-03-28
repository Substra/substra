import json
from unittest import TestCase, mock

from substra_sdk_py.bulk_update import bulkUpdate as bulkUpdateFunction

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

    def raise_for_status(self):
        if self.status_code > 400:
            raise requests.exceptions.HTTPError(self.status_code)


def mocked_requests_post_data(*args, **kwargs):
    return MockResponse(data, 201)


class TestBulkUpdate(TestCase):
    def setUp(self):
        self.data_samples_file_path = './tests/assets/data_sample/bulk_update_data_samples.json'

        self.config = {
            'url': 'http://toto.com',
            'version': '1.0',
            'auth': False,
            'insecure': False,
        }

    def tearDown(self):
        pass

    @mock.patch('substra_sdk_py.bulk_update.requests.post', side_effect=mocked_requests_post_data)
    def test_bulk_update_data(self, mock_get):
        with open(self.data_samples_file_path, 'r') as f:
            content = json.loads(f.read())

            res = bulkUpdateFunction('data_sample', content, config=self.config)

            self.assertTrue(res, data)
            self.assertEqual(len(mock_get.call_args_list), 1)
