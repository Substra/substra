import json

from unittest import mock

from .test_base import data_manager, objective, algo, data_sample
from .test_base import TestBase, MockResponse


def mocked_requests_post_data_manager(*args, **kwargs):
    return MockResponse(data_manager, 201)


def mocked_requests_post_objective(*args, **kwargs):
    return MockResponse(objective, 201)


def mocked_requests_post_algo(*args, **kwargs):
    return MockResponse(algo, 201)


def mocked_requests_post_data(*args, **kwargs):
    return MockResponse(data_sample, 201)


def mocked_requests_add_objective_fail(*args, **kwargs):
    return MockResponse('fail', 500)


class TestAdd(TestBase):

    @mock.patch('substra_sdk_py.http_cli.requests.post', side_effect=mocked_requests_post_data_manager)
    def test_add_data_manager(self, mock_get):
        # open data_manager file
        with open(self.data_manager_file_path, 'r') as f:
            data = json.loads(f.read())

        res = self.client.add('data_manager', data)

        self.assertEqual(res, data_manager)
        self.assertEqual(len(mock_get.call_args_list), 1)
        self.assertEqual(mock_get.call_args[1].get('data').get('permissions'), 'all')

    @mock.patch('substra_sdk_py.http_cli.requests.post', side_effect=mocked_requests_post_data_manager)
    def test_add_data_manager_invalid_args(self, mock_get):
        try:
            self.client.add('data_manager', {})
        except Exception as e:
            print(e)
            self.assertEqual(str(e), "The 'data_opener' attribute is missing.")
        self.assertEqual(len(mock_get.call_args_list), 0)

    @mock.patch('substra_sdk_py.http_cli.requests.post', side_effect=mocked_requests_post_objective)
    def test_add_objective(self, mock_get):
        # open objective file
        with open(self.objective_file_path, 'r') as f:
            data = json.loads(f.read())

            res = self.client.add('objective', data)

            self.assertEqual(res, objective)
            self.assertEqual(len(mock_get.call_args_list), 1)
            self.assertEqual(mock_get.call_args[1].get('data').get('permissions'), 'all')

    @mock.patch('substra_sdk_py.http_cli.requests.post', side_effect=mocked_requests_post_algo)
    def test_add_algo(self, mock_get):
        # open algo file
        with open(self.algo_file_path, 'r') as f:
            data = json.loads(f.read())

            res = self.client.add('algo', data)

            self.assertEqual(res, algo)
            self.assertEqual(len(mock_get.call_args_list), 1)
            self.assertEqual(mock_get.call_args[1].get('data').get('permissions'), 'all')

    @mock.patch('substra_sdk_py.http_cli.requests.post', side_effect=mocked_requests_post_data)
    def test_add_data(self, mock_get):
        # open algo file
        with open(self.data_sample_file_path, 'r') as f:
            content = json.loads(f.read())

            res = self.client.add('data_sample', content)

            self.assertEqual(res, data_sample)
            self.assertEqual(len(mock_get.call_args_list), 1)

    @mock.patch('substra_sdk_py.http_cli.requests.post', side_effect=mocked_requests_add_objective_fail)
    def test_returns_objective_list_fail(self, mock_get):
        with open(self.objective_file_path, 'r') as f:
            data = json.loads(f.read())
            try:
                self.client.add('objective', data)
            except Exception as e:
                print(str(e))
                self.assertEqual(str(e), '500')

            self.assertEqual(len(mock_get.call_args_list), 1)
