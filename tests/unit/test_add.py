import json

from unittest import TestCase, mock

from substra_sdk_py.add import add as addFunction

dataset = {"challengeKey": "",
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


class TestAdd(TestCase):
    def setUp(self):
        self.dataset_file_path = './tests/assets/dataset/dataset.json'
        self.challenge_file_path = './tests/assets/challenge/challenge.json'
        self.algo_file_path = './tests/assets/algo/algo.json'
        self.data_file_path = './tests/assets/data/data.json'

        self.config = {
            'url': 'http://toto.com',
            'version': '1.0',
            'auth': False,
            'insecure': False,
        }

    def tearDown(self):
        pass

    @mock.patch('substra_sdk_py.add.requests.post', side_effect=mocked_requests_post_dataset)
    def test_add_dataset(self, mock_get):
        # open dataset file
        with open(self.dataset_file_path, 'r') as f:
            data = json.loads(f.read())

            res = addFunction('dataset', data, config=self.config)

            self.assertEqual(res['status_code'], 201)
            self.assertEqual(res['result'], dataset)
            self.assertEqual(len(mock_get.call_args_list), 1)
            self.assertEqual(mock_get.call_args[1].get('data').get('permissions'), 'all')

    @mock.patch('substra_sdk_py.add.requests.post', side_effect=mocked_requests_post_dataset)
    def test_add_dataset_invalid_args(self, mock_get):
        try:
            addFunction('dataset', 'test', config=self.config)
        except Exception as e:
            print(e)
            self.assertEqual(str(e), "The 'data_opener' attribute is missing.")
        self.assertEqual(len(mock_get.call_args_list), 0)

    @mock.patch('substra_sdk_py.add.requests.post', side_effect=mocked_requests_post_challenge)
    def test_add_challenge(self, mock_get):
        # open challenge file
        with open(self.challenge_file_path, 'r') as f:
            data = json.loads(f.read())

            res = addFunction('challenge', data, config=self.config)

            self.assertEqual(res['status_code'], 201)
            self.assertEqual(res['result'], challenge)
            self.assertEqual(len(mock_get.call_args_list), 1)
            self.assertEqual(mock_get.call_args[1].get('data').get('permissions'), 'all')

    @mock.patch('substra_sdk_py.add.requests.post', side_effect=mocked_requests_post_algo)
    def test_add_algo(self, mock_get):
        # open algo file
        with open(self.algo_file_path, 'r') as f:
            data = json.loads(f.read())

            res = addFunction('algo', data, config=self.config)

            print(res)
            self.assertEqual(res['status_code'], 201)
            self.assertEqual(res['result'], algo)
            self.assertEqual(len(mock_get.call_args_list), 1)
            self.assertEqual(mock_get.call_args[1].get('data').get('permissions'), 'all')

    @mock.patch('substra_sdk_py.add.requests.post', side_effect=mocked_requests_post_data)
    def test_add_data(self, mock_get):
        # open algo file
        with open(self.data_file_path, 'r') as f:
            content = json.loads(f.read())

            res = addFunction('data', content, config=self.config)

            print(res)

            self.assertEqual(res['status_code'], 201)
            self.assertEqual(res['result'], data)
            self.assertEqual(len(mock_get.call_args_list), 1)

    @mock.patch('substra_sdk_py.add.requests.post', side_effect=mocked_requests_add_challenge_fail)
    def test_returns_challenge_list_fail(self, mock_get):
        with open(self.challenge_file_path, 'r') as f:
            data = json.loads(f.read())
            try:
                addFunction('challenge', data, config=self.config)
            except Exception as e:
                print(str(e))
                self.assertTrue(str(e) == 'Failed to create challenge')

            self.assertEqual(len(mock_get.call_args_list), 1)


class TestAddConfigBasicAuth(TestCase):
    def setUp(self):
        self.dataset_file_path = './tests/assets/dataset/dataset.json'

        self.config = {
            'url': 'http://toto.com',
            'version': '1.0',
            'auth': True,
            'user': 'foo',
            'password': 'bar',
            'insecure': False
        }

    def tearDown(self):
        pass

    @mock.patch('substra_sdk_py.add.requests.post', side_effect=mocked_requests_post_dataset)
    def test_add_dataset(self, mock_get):
        # open dataset file
        with open(self.dataset_file_path, 'r') as f:
            data = json.loads(f.read())

            res = addFunction('dataset', data, config=self.config)

            self.assertEqual(res['status_code'], 201)
            self.assertEqual(res['result'], dataset)
            self.assertEqual(len(mock_get.call_args_list), 1)


class TestAddConfigInsecure(TestCase):
    def setUp(self):
        self.dataset_file_path = './tests/assets/dataset/dataset.json'

        self.config = {
            'url': 'http://toto.com',
            'version': '1.0',
            'auth': True,
            'user': 'foo',
            'password': 'bar',
            'insecure': True
        }

    def tearDown(self):
        pass

    @mock.patch('substra_sdk_py.add.requests.post', side_effect=mocked_requests_post_dataset)
    def test_add_dataset(self, mock_get):
        # open dataset file
        with open(self.dataset_file_path, 'r') as f:
            data = json.loads(f.read())

            res = addFunction('dataset', data, config=self.config)

            self.assertEqual(res['status_code'], 201)
            self.assertEqual(res['result'], dataset)
            self.assertEqual(len(mock_get.call_args_list), 1)
