import json

from unittest import mock

from .test_base import data_manager, objective, algo, data_sample
from .test_base import TestBase, mock_success_response, mock_fail_response


def mocked_requests_post_data_manager(*args, **kwargs):
    return mock_success_response(data=data_manager)


def mocked_requests_post_objective(*args, **kwargs):
    return mock_success_response(data=objective)


def mocked_requests_post_algo(*args, **kwargs):
    return mock_success_response(data=algo)


def mocked_requests_post_data_sample(*args, **kwargs):
    return mock_success_response(data=data_sample)


def mocked_requests_add_objective_fail(*args, **kwargs):
    return mock_fail_response()


class TestAdd(TestBase):

    @mock.patch('substra.sdk.requests_wrapper.requests.post', side_effect=mocked_requests_post_data_manager)
    def test_add_data_manager(self, mock_get):
        # open data_manager file
        with open(self.data_manager_file_path, 'r') as f:
            data = json.loads(f.read())

        res = self.client.add_dataset(data)

        self.assertEqual(res, data_manager)
        self.assertEqual(len(mock_get.call_args_list), 1)
        self.assertEqual(mock_get.call_args[1].get('data').get('permissions'), 'all')

    @mock.patch('substra.sdk.requests_wrapper.requests.post', side_effect=mocked_requests_post_data_manager)
    def test_add_data_manager_invalid_args(self, mock_get):
        try:
            self.client.add_dataset({})
        except Exception as e:
            print(e)
            self.assertEqual(str(e), "The 'data_opener' attribute is missing.")
        self.assertEqual(len(mock_get.call_args_list), 0)

    @mock.patch('substra.sdk.requests_wrapper.requests.post', side_effect=mocked_requests_post_objective)
    def test_add_objective(self, mock_get):
        # open objective file
        with open(self.objective_file_path, 'r') as f:
            data = json.loads(f.read())

            res = self.client.add_objective(data)

            self.assertEqual(res, objective)
            self.assertEqual(len(mock_get.call_args_list), 1)
            self.assertEqual(mock_get.call_args[1].get('data').get('permissions'), 'all')

    @mock.patch('substra.sdk.requests_wrapper.requests.post', side_effect=mocked_requests_post_algo)
    def test_add_algo(self, mock_get):
        # open algo file
        with open(self.algo_file_path, 'r') as f:
            data = json.loads(f.read())

            res = self.client.add_algo(data)

            self.assertEqual(res, algo)
            self.assertEqual(len(mock_get.call_args_list), 1)
            self.assertEqual(mock_get.call_args[1].get('data').get('permissions'), 'all')

    @mock.patch('substra.sdk.requests_wrapper.requests.post', side_effect=mocked_requests_post_data_sample)
    def test_add_data(self, mock_get):
        # open algo file
        with open(self.data_sample_file_path, 'r') as f:
            content = json.loads(f.read())

            res = self.client.add_data_sample(content)

            self.assertEqual(res, data_sample)
            self.assertEqual(len(mock_get.call_args_list), 1)

    @mock.patch('substra.sdk.requests_wrapper.requests.post', side_effect=mocked_requests_add_objective_fail)
    def test_returns_objective_list_fail(self, mock_get):
        with open(self.objective_file_path, 'r') as f:
            data = json.loads(f.read())
            try:
                self.client.add_objective(data)
            except Exception as e:
                print(str(e))
                self.assertEqual(str(e), '500')

            self.assertEqual(len(mock_get.call_args_list), 1)
