import json
import os
from unittest import TestCase, mock

from mock import mock_open

from substra.commands import Get, Config

dataset = {
    "challengeKeys": [],
    "description": {"hash": "7a90514f88c70002608a9868681dd1589ea598e78d00a8cd7783c3ea0f9ceb09",
                    "storageAddress": "http://127.0.0.1:8001/dataset/ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994/description/"},
    "key": "ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994", "name": "ISIC 2018",
    "nbData": 2,
    "openerStorageAddress": "http://127.0.0.1:8001/dataset/ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994/opener/",
    "owner": "c657699f8b03c19e6eadc7b474c23f26dd83454395266a673406f2cf44de2ca2", "permissions": "all",
    "size": 100, "type": "Images"
}

challenge = {
    "descriptionStorageAddress": "http://127.0.0.1:8001/challenge/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/description/",
    "key": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
    "metrics": {"hash": "750f622262854341bd44f55c1018949e9c119606ef5068bd7d137040a482a756",
                "name": "macro-average recall",
                "storageAddress": "http://127.0.0.1:8001/challenge/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/metrics/"},
    "name": "Skin Lesion Classification Challenge",
    "owner": "c657699f8b03c19e6eadc7b474c23f26dd83454395266a673406f2cf44de2ca2", "permissions": "all",
    "testDataKeys": ["e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1"]
}


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


def mocked_requests_get_challenge_fail(*args, **kwargs):
    raise Exception('fail')


@mock.patch('substra.commands.api.config_path', '/tmp/.substra', create=True)
class TestGet(TestCase):
    def setUp(self):
        with mock.patch('substra.commands.config.config_path', '/tmp/.substra', create=True):
            Config({
                '<url>': 'http://toto.com',
                '<version>': '1.0.0',
            }).run()

    def tearDown(self):
        try:
            os.remove('/tmp/.substra')
        except:
            pass

    @mock.patch('substra.commands.get.requests.get', side_effect=mocked_requests_get_challenge)
    def test_returns_challenge_list(self, mock_get):
        res = Get({
            '<entity>': 'challenge',
            '<pkhash>': 'd5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f',
        }).run()

        self.assertTrue(res == json.dumps(challenge))
        self.assertEqual(len(mock_get.call_args_list), 1)

    @mock.patch('substra.commands.get.requests.get', side_effect=mocked_requests_get_challenge_fail)
    def test_returns_challenge_list_fail(self, mock_get):
        try:
            Get({
                '<entity>': 'challenge',
                '<pkhash>': 'd5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f',
            }).run()
        except Exception as e:
            print(str(e))
            self.assertTrue(str(e) == 'Failed to get challenge')

        self.assertEqual(len(mock_get.call_args_list), 1)

    @mock.patch('substra.commands.get.requests.get', side_effect=mocked_requests_get_dataset)
    def test_returns_dataset_list(self, mock_get):
        res = Get({
            '<entity>': 'dataset',
            '<pkhash>': 'ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994',
        }).run()

        self.assertTrue(res == json.dumps(dataset))
        self.assertEqual(len(mock_get.call_args_list), 1)

