import json
import os
from unittest import TestCase, mock

from substra.commands import Add, Config

dataset = {"challengeKeys": [],
           "description": {"hash": "7a90514f88c70002608a9868681dd1589ea598e78d00a8cd7783c3ea0f9ceb09",
                           "storageAddress": "http://127.0.0.1:8001/dataset/ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994/description/"},
           "key": "ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994", "name": "ISIC 2018", "nbData": 2,
           "openerStorageAddress": "http://127.0.0.1:8001/dataset/ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994/opener/",
           "owner": "c657699f8b03c19e6eadc7b474c23f26dd83454395266a673406f2cf44de2ca2", "permissions": "all",
           "size": 100, "type": "Images"}

challenge = {
    "descriptionStorageAddress": "http://127.0.0.1:8001/challenge/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/description/",
    "key": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
    "metrics": {"hash": "750f622262854341bd44f55c1018949e9c119606ef5068bd7d137040a482a756",
                "name": "macro-average recall",
                "storageAddress": "http://127.0.0.1:8001/challenge/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/metrics/"},
    "name": "Skin Lesion Classification Challenge",
    "owner": "c657699f8b03c19e6eadc7b474c23f26dd83454395266a673406f2cf44de2ca2", "permissions": "all",
    "testDataKeys": ["e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1"]}

algo = {"challengeKey": "6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c",
        "description": {"hash": "3b1281cbdd6ebfec650d0a9f932a64e45a27262848065d7cecf11fd7191b4b1f",
                        "storageAddress": "http://127.0.0.1:8001/algo/7742aea2001ceb40e9ce8a37fa27237d5b2d1f574e06d48677af945cfdf42ec0/description/"},
        "key": "7742aea2001ceb40e9ce8a37fa27237d5b2d1f574e06d48677af945cfdf42ec0",
        "name": "Logistic regression for balanced problem",
        "owner": "c657699f8b03c19e6eadc7b474c23f26dd83454395266a673406f2cf44de2ca2", "permissions": "all",
        "storageAddress": "http://127.0.0.1:8001/algo/7742aea2001ceb40e9ce8a37fa27237d5b2d1f574e06d48677af945cfdf42ec0/file/"}

data = {"pkhash": "e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1", "validated": True,
        "file": "http://127.0.0.1:8000/media/data/e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1/0024700.zip"}


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


def mocked_requests_post_dataset(*args, **kwargs):
    return MockResponse(dataset, 201)


def mocked_requests_post_challenge(*args, **kwargs):
    return MockResponse(challenge, 201)


def mocked_requests_post_algo(*args, **kwargs):
    return MockResponse(algo, 201)


def mocked_requests_post_data(*args, **kwargs):
    return MockResponse(data, 201)


def mocked_requests_add_challenge_fail(*args, **kwargs):
    raise Exception('fail')


@mock.patch('substra.commands.api.config_path', '/tmp/.substra', create=True)
class TestAdd(TestCase):
    def setUp(self):
        self.dataset_file_path = './tests/assets/dataset/dataset.json'
        self.challenge_file_path = './tests/assets/challenge/challenge.json'
        self.algo_file_path = './tests/assets/algo/algo.json'
        self.data_file_path = './tests/assets/data/data.json'

        with mock.patch('substra.commands.config.config_path', '/tmp/.substra', create=True):
            Config({
                '<url>': 'http://toto.com',
                '<version>': '1.0',
            }).run()

    def tearDown(self):
        try:
            os.remove('/tmp/.substra')
        except:
            pass

    @mock.patch('substra.commands.list.requests.post', side_effect=mocked_requests_post_dataset)
    def test_add_dataset(self, mock_get):
        # open dataset file
        with open(self.dataset_file_path, 'r') as f:
            data = f.read()

            res = Add({
                '<entity>': 'dataset',
                '<args>': data,
            }).run()

            self.assertEqual(json.loads(res), dataset)
            self.assertEqual(len(mock_get.call_args_list), 1)
            self.assertEqual(mock_get.call_args[1].get('data').get('permissions'), 'all')

    @mock.patch('substra.commands.list.requests.post', side_effect=mocked_requests_post_dataset)
    def test_add_dataset_from_file(self, mock_get):

        res = Add({
            '<entity>': 'dataset',
            '<args>': self.dataset_file_path,
        }).run()

        self.assertEqual(json.loads(res), dataset)
        self.assertEqual(len(mock_get.call_args_list), 1)

    @mock.patch('substra.commands.list.requests.post', side_effect=mocked_requests_post_dataset)
    def test_add_dataset_invalid_args(self, mock_get):
        try:
            Add({
                '<entity>': 'dataset',
                '<args>': 'test',
            }).run()
        except Exception as e:
            self.assertTrue(str(e) == 'Invalid args. Please review help')
        self.assertEqual(len(mock_get.call_args_list), 0)

    @mock.patch('substra.commands.list.requests.post', side_effect=mocked_requests_post_challenge)
    def test_add_challenge(self, mock_get):
        # open challenge file
        with open(self.challenge_file_path, 'r') as f:
            data = f.read()

            res = Add({
                '<entity>': 'challenge',
                '<args>': data,
            }).run()

            self.assertEqual(json.loads(res), challenge)
            self.assertEqual(len(mock_get.call_args_list), 1)
            self.assertEqual(mock_get.call_args[1].get('data').get('permissions'), 'all')

    @mock.patch('substra.commands.list.requests.post', side_effect=mocked_requests_post_algo)
    def test_add_algo(self, mock_get):
        # open algo file
        with open(self.algo_file_path, 'r') as f:
            data = f.read()

            res = Add({
                '<entity>': 'algo',
                '<args>': data,
            }).run()

            self.assertEqual(json.loads(res), algo)
            self.assertEqual(len(mock_get.call_args_list), 1)
            self.assertEqual(mock_get.call_args[1].get('data').get('permissions'), 'all')

    @mock.patch('substra.commands.list.requests.post', side_effect=mocked_requests_post_data)
    def test_add_data(self, mock_get):
        # open algo file
        with open(self.data_file_path, 'r') as f:
            content = f.read()

            res = Add({
                '<entity>': 'data',
                '<args>': content,
            }).run()

            print(res)

            self.assertEqual(json.loads(res), data)
            self.assertEqual(len(mock_get.call_args_list), 1)

    @mock.patch('substra.commands.list.requests.post', side_effect=mocked_requests_add_challenge_fail)
    def test_returns_challenge_list_fail(self, mock_get):
        with open(self.challenge_file_path, 'r') as f:
            data = f.read()
            try:
                Add({
                    '<entity>': 'challenge',
                    '<args>': data,
                }).run()
            except Exception as e:
                print(str(e))
                self.assertTrue(str(e) == 'Failed to create challenge')

            self.assertEqual(len(mock_get.call_args_list), 1)


@mock.patch('substra.commands.api.config_path', '/tmp/.substra', create=True)
class TestAddNoConfig(TestCase):
    def setUp(self):
        self.dataset_file_path = './tests/assets/dataset/dataset.json'
        try:
            os.remove('/tmp/.substra')
        except:
            pass

    @mock.patch('substra.commands.list.requests.post', side_effect=mocked_requests_post_dataset)
    def test_add_dataset(self, mock_get):
        # open dataset file
        with open(self.dataset_file_path, 'r') as f:
            data = f.read()

            try:
                Add({
                    '<entity>': 'dataset',
                    '<args>': data,
                }).run()
            except Exception as e:
                print('test: ', str(e))
                self.assertTrue(str(
                    e) == 'No config file or profile found, please run "substra config <url> [<version>] [--profile=<profile>] [--config=<configuration_file_path>]"')

            self.assertEqual(len(mock_get.call_args_list), 0)


@mock.patch('substra.commands.api.config_path', '/tmp/.substra', create=True)
class TestAddConfigBasicAuth(TestCase):
    def setUp(self):
        self.dataset_file_path = './tests/assets/dataset/dataset.json'

        with mock.patch('substra.commands.config.config_path', '/tmp/.substra', create=True):
            Config({
                '<url>': 'http://toto.com',
                '<version>': '1.0',
                '<user>': 'foo',
                '<password>': 'bar'
            }).run()

    def tearDown(self):
        try:
            os.remove('/tmp/.substra')
        except:
            pass

    @mock.patch('substra.commands.list.requests.post', side_effect=mocked_requests_post_dataset)
    def test_add_dataset(self, mock_get):
        # open dataset file
        with open(self.dataset_file_path, 'r') as f:
            data = f.read()

            res = Add({
                '<entity>': 'dataset',
                '<args>': data,
            }).run()

            self.assertEqual(json.loads(res), dataset)
            self.assertEqual(len(mock_get.call_args_list), 1)


@mock.patch('substra.commands.api.config_path', '/tmp/.substra', create=True)
class TestAddConfigInsecure(TestCase):
    def setUp(self):
        self.dataset_file_path = './tests/assets/dataset/dataset.json'

        with mock.patch('substra.commands.config.config_path', '/tmp/.substra', create=True):
            Config({
                '<url>': 'http://toto.com',
                '<version>': '1.0',
                '<user>': 'foo',
                '<password>': 'bar',
                '--insecure': True
            }).run()

    def tearDown(self):
        try:
            os.remove('/tmp/.substra')
        except:
            pass

    @mock.patch('substra.commands.list.requests.post', side_effect=mocked_requests_post_dataset)
    def test_add_dataset(self, mock_get):
        # open dataset file
        with open(self.dataset_file_path, 'r') as f:
            data = f.read()

            res = Add({
                '<entity>': 'dataset',
                '<args>': data,
            }).run()

            self.assertEqual(json.loads(res), dataset)
            self.assertEqual(len(mock_get.call_args_list), 1)