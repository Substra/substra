import json
import os
from unittest import TestCase, mock

from substra.commands import Get, Config

data_manager = {
    "objectiveKeys": [],
    "description": {
        "hash": "7a90514f88c70002608a9868681dd1589ea598e78d00a8cd7783c3ea0f9ceb09",
        "storageAddress": "http://127.0.0.1:8001/data_manager/ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994/description/"},
    "key": "ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994",
    "name": "ISIC 2018",
    "nbData": 2,
    "openerStorageAddress": "http://127.0.0.1:8001/data_manager/ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994/opener/",
    "owner": "c657699f8b03c19e6eadc7b474c23f26dd83454395266a673406f2cf44de2ca2",
    "permissions": "all",
    "size": 100,
    "type": "Images"
}

objective = {
    "descriptionStorageAddress": "http://127.0.0.1:8001/objective/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/description/",
    "key": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
    "metrics": {
        "hash": "750f622262854341bd44f55c1018949e9c119606ef5068bd7d137040a482a756",
        "name": "macro-average recall",
        "storageAddress": "http://127.0.0.1:8001/objective/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/metrics/"},
    "name": "Skin Lesion Classification Challenge",
    "owner": "c657699f8b03c19e6eadc7b474c23f26dd83454395266a673406f2cf44de2ca2",
    "permissions": "all",
    "testDataKeys": [
        "e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1"]
}


def mocked_client_get_asset(data, st):
    return {'result': data,
            'status_code': st}


@mock.patch('substra.commands.api.config_path', '/tmp/.substra', create=True)
class TestGet(TestCase):
    def setUp(self):
        with mock.patch('substra.commands.config.config_path', '/tmp/.substra',
                        create=True):
            Config({
                '<url>': 'http://toto.com',
                '<version>': '1.0',
            }).run()

    def tearDown(self):
        try:
            os.remove('/tmp/.substra')
        except:
            pass

    @mock.patch('substra.commands.api.Client.get',
                return_value=mocked_client_get_asset(objective, 200))
    def test_returns_objective_get(self, mock_get):
        res = Get({
            '<asset>': 'objective',
            '<pkhash>': 'd5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f',
        }).run()

        self.assertEqual(json.loads(res)['status_code'], 200)
        self.assertEqual(json.loads(res)['result'], objective)
        self.assertEqual(len(mock_get.call_args_list), 1)

    @mock.patch('substra.commands.api.Client.get',
                side_effect=Exception('fail'))
    def test_returns_objective_get_fail(self, mock_get):
        with self.assertRaises(Exception) as e:
            Get({
                '<asset>': 'objective',
                '<pkhash>': 'd5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f',
            }).run()
            self.assertTrue(str(e) == 'Failed to get objective')

        self.assertEqual(len(mock_get.call_args_list), 1)

    @mock.patch('substra.commands.api.Client.get',
                return_value=mocked_client_get_asset(data_manager, 200))
    def test_returns_data_manager_get(self, mock_get):
        res = Get({
            '<asset>': 'data-manager',
            '<pkhash>': 'ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994',
        }).run()

        self.assertEqual(json.loads(res)['status_code'], 200)
        self.assertEqual(json.loads(res)['result'], data_manager)
        self.assertEqual(len(mock_get.call_args_list), 1)


@mock.patch('substra.commands.api.config_path', '/tmp/.substra', create=True)
class TestGetConfigBasicAuth(TestCase):
    def setUp(self):
        self.data_manager_file_path = './tests/assets/data_manager/data_manager.json'

        with mock.patch('substra.commands.config.config_path', '/tmp/.substra',
                        create=True):
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

    @mock.patch('substra.commands.api.Client.get',
                return_value=mocked_client_get_asset(objective, 200))
    def test_returns_objective_get(self, mock_get):
        res = Get({
            '<asset>': 'objective',
            '<pkhash>': 'd5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f',
        }).run()

        self.assertEqual(json.loads(res)['status_code'], 200)
        self.assertEqual(json.loads(res)['result'], objective)
        self.assertEqual(len(mock_get.call_args_list), 1)


@mock.patch('substra.commands.api.config_path', '/tmp/.substra', create=True)
class TestGetConfigInsecure(TestCase):
    def setUp(self):
        self.data_manager_file_path = './tests/assets/data_manager/data_manager.json'

        with mock.patch('substra.commands.config.config_path', '/tmp/.substra',
                        create=True):
            Config({
                '<url>': 'http://toto.com',
                '<version>': '1.0',
                '<user>': 'foo',
                '<password>': 'bar',
                '-k': True
            }).run()

    def tearDown(self):
        try:
            os.remove('/tmp/.substra')
        except:
            pass

    @mock.patch('substra.commands.api.Client.get',
                return_value=mocked_client_get_asset(objective, 200))
    def test_returns_objective_get(self, mock_get):
        res = Get({
            '<asset>': 'objective',
            '<pkhash>': 'd5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f',
        }).run()

        self.assertEqual(json.loads(res)['status_code'], 200)
        self.assertEqual(json.loads(res)['result'], objective)
        self.assertEqual(len(mock_get.call_args_list), 1)
