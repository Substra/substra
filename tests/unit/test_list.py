import json
import os
from unittest import TestCase, mock

from substra_sdk_py.list import list as listFunction
from substra_sdk_py.list import flatten

dataset = [
    [
        {
            "challengeKeys": [],
            "description": {"hash": "7a90514f88c70002608a9868681dd1589ea598e78d00a8cd7783c3ea0f9ceb09",
                            "storageAddress": "http://127.0.0.1:8001/dataset/ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994/description/"},
            "key": "ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994", "name": "ISIC 2018",
            "nbData": 2,
            "openerStorageAddress": "http://127.0.0.1:8001/dataset/ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994/opener/",
            "owner": "c657699f8b03c19e6eadc7b474c23f26dd83454395266a673406f2cf44de2ca2", "permissions": "all",
            "size": 100, "type": "Images"
        },
        {
            "challengeKeys": [],
            "description": {
                "hash": "040dce77ccd8c7781e65438c1a2fec97f83ce8b43f0c5f8b95d34c11157aa926",
                "storageAddress": "http://127.0.0.1:8000/media/datasets/ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994/description_LDUuwzv.md"
            },
            "key": "82315f7c4a3fbd77edf4c22d3cbad474f833220baf94b424d16ae67dd65fd9b6",
            "name": "liver slide", "nbData": 0,
            "openerStorageAddress": "http://127.0.0.1:8000/media/datasets/ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994/opener_KobP3t5.py",
            "owner": "e450e7bf3f3a159ff9772f335612b256eb1e1a138ba8ec88c8ae65c55c2f221d",
            "permissions": "all", "size": 0, "type": "images"
        },
        {
            "challengeKeys": ["6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c",
                              "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f"],
            "description": {"hash": "258bef187a166b3fef5cb86e68c8f7e154c283a148cd5bc344fec7e698821ad3",
                            "storageAddress": "http://127.0.0.1:8000/dataset/b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0/description/"},
            "key": "b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0",
            "name": "Simplified ISIC 2018", "nbData": 6,
            "openerStorageAddress": "http://127.0.0.1:8000/dataset/b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0/opener/",
            "owner": "e450e7bf3f3a159ff9772f335612b256eb1e1a138ba8ec88c8ae65c55c2f221d", "permissions": "all",
            "size": 300, "type": "Images"
        }
    ]
]

challenge = [[{
                   "descriptionStorageAddress": "http://127.0.0.1:8001/challenge/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/description/",
                   "key": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
                   "metrics": {"hash": "750f622262854341bd44f55c1018949e9c119606ef5068bd7d137040a482a756",
                               "name": "macro-average recall",
                               "storageAddress": "http://127.0.0.1:8001/challenge/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/metrics/"},
                   "name": "Skin Lesion Classification Challenge",
                   "owner": "c657699f8b03c19e6eadc7b474c23f26dd83454395266a673406f2cf44de2ca2", "permissions": "all",
                   "testDataKeys": ["e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1"]}, {
                   "descriptionStorageAddress": "http://127.0.0.1:8000/challenge/6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c/description/",
                   "key": "6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c",
                   "metrics": {"hash": "0bc732c26bafdc41321c2bffd35b6835aa35f7371a4eb02994642c2c3a688f60",
                               "name": "macro-average recall",
                               "storageAddress": "http://127.0.0.1:8000/challenge/6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c/metrics/"},
                   "name": "Simplified skin lesion classification",
                   "owner": "e450e7bf3f3a159ff9772f335612b256eb1e1a138ba8ec88c8ae65c55c2f221d", "permissions": "all",
                   "testDataKeys": ["2d0f943aa81a9cb3fe84b162559ce6aff068ccb04e0cb284733b8f9d7e06517e",
                                    "533ee6e7b9d8b247e7e853b24547f57e6ef351852bac0418f13a0666173448f1"]}]]


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


def mocked_requests_get_challenge(*args, **kwargs):
    return MockResponse(challenge, 200)


def mocked_requests_get_dataset(*args, **kwargs):
    return MockResponse(dataset, 200)


def mocked_requests_get_dataset_no_json(*args, **kwargs):
    return MockResponse(open, 200)


def mocked_requests_list_challenge_fail(*args, **kwargs):
    raise Exception('fail')


def mocked_requests_get_challenge_filtered(*args, **kwargs):
    return MockResponse(challenge, 200)


class TestList(TestCase):
    def setUp(self):
        self.config = {
            'url': 'http://toto.com',
            'version': '1.0',
            'auth': False,
            'insecure': False,
        }

    def tearDown(self):
        pass

    @mock.patch('substra_sdk_py.list.requests.get', side_effect=mocked_requests_get_challenge)
    def test_returns_challenge_list(self, mock_get):

        res = listFunction('challenge', self.config)

        self.assertEqual(res['status_code'], 200)
        self.assertEqual(res['result'], flatten(challenge))
        self.assertEqual(len(mock_get.call_args_list), 1)

    @mock.patch('substra_sdk_py.list.requests.get', side_effect=mocked_requests_list_challenge_fail)
    def test_returns_challenge_list_fail(self, mock_get):
        try:
            listFunction('challenge', self.config)
        except Exception as e:
            print(str(e))
            self.assertTrue(str(e) == 'Failed to list challenge')

        self.assertEqual(len(mock_get.call_args_list), 1)

    @mock.patch('substra_sdk_py.list.requests.get', side_effect=mocked_requests_get_dataset)
    def test_returns_dataset_list(self, mock_get):

        res = listFunction('dataset', self.config)

        self.assertEqual(res['status_code'], 200)
        self.assertEqual(res['result'], flatten(dataset))
        self.assertEqual(len(mock_get.call_args_list), 1)

    @mock.patch('substra_sdk_py.list.requests.get', side_effect=mocked_requests_get_dataset_no_json)
    def test_returns_dataset_list_no_json(self, mock_get):
        try:
            listFunction('dataset', self.config)
        except Exception as e:
            print(str(e))
            self.assertTrue(str(e) == 'Can\'t decode response value from server to json.')
        self.assertEqual(len(mock_get.call_args_list), 1)

    @mock.patch('substra_sdk_py.list.requests.get', side_effect=mocked_requests_get_challenge_filtered)
    def test_returns_challenge_list_filters(self, mock_get):

        res = listFunction('challenge', self.config,
                           '["challenge:name:Skin Lesion Classification Challenge", "OR", "dataset:name:Simplified ISIC 2018"]')

        self.assertEqual(res['status_code'], 200)
        self.assertEqual(res['result'], flatten(challenge))
        self.assertEqual(len(mock_get.call_args_list), 1)

    @mock.patch('substra_sdk_py.list.requests.get', side_effect=mocked_requests_get_challenge_filtered)
    def test_returns_challenge_list_bad_filters(self, mock_get):

        res = listFunction('challenge', self.config, 'toto')
        self.assertTrue(res == 'Cannot load filters. Please review the documentation.')

        self.assertEqual(len(mock_get.call_args_list), 0)


class TestListConfigBasicAuth(TestCase):
    def setUp(self):
        self.dataset_file_path = './tests/assets/dataset/dataset.json'
        self.config = {
            'url': 'http://toto.com',
            'version': '1.0',
            'auth': True,
            'password': 'bar',
            'user': 'foo',
            'insecure': False,
        }

    def tearDown(self):
        pass

    @mock.patch('substra_sdk_py.list.requests.get', side_effect=mocked_requests_get_challenge)
    def test_returns_challenge_list(self, mock_get):

        res = listFunction('challenge', self.config)

        self.assertEqual(res['status_code'], 200)
        self.assertEqual(res['result'], flatten(challenge))
        self.assertEqual(len(mock_get.call_args_list), 1)


class TestListConfigInsecure(TestCase):
    def setUp(self):
        self.dataset_file_path = './tests/assets/dataset/dataset.json'

        self.config = {
            'url': 'http://toto.com',
            'version': '1.0',
            'auth': True,
            'password': 'bar',
            'user': 'foo',
            'insecure': True,
        }

    def tearDown(self):
        pass

    @mock.patch('substra_sdk_py.list.requests.get', side_effect=mocked_requests_get_challenge)
    def test_returns_challenge_list(self, mock_get):

        res = listFunction('challenge', self.config)

        self.assertEqual(res['status_code'], 200)
        self.assertEqual(res['result'], flatten(challenge))
        self.assertEqual(len(mock_get.call_args_list), 1)
