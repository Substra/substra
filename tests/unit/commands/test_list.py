import json
import os
from unittest import TestCase, mock

from substra.commands import List, Config
from substra.commands.list import flatten

dataset = [
    [
        {
            "objectiveKeys": [],
            "description": {"hash": "7a90514f88c70002608a9868681dd1589ea598e78d00a8cd7783c3ea0f9ceb09",
                            "storageAddress": "http://127.0.0.1:8001/data_manager/ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994/description/"},
            "key": "ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994", "name": "ISIC 2018",
            "nbData": 2,
            "openerStorageAddress": "http://127.0.0.1:8001/data_manager/ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994/opener/",
            "owner": "c657699f8b03c19e6eadc7b474c23f26dd83454395266a673406f2cf44de2ca2", "permissions": "all",
            "size": 100, "type": "Images"
        },
        {
            "objectiveKeys": [],
            "description": {
                "hash": "040dce77ccd8c7781e65438c1a2fec97f83ce8b43f0c5f8b95d34c11157aa926",
                "storageAddress": "http://127.0.0.1:8000/media/data_managers/ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994/description_LDUuwzv.md"
            },
            "key": "82315f7c4a3fbd77edf4c22d3cbad474f833220baf94b424d16ae67dd65fd9b6",
            "name": "liver slide", "nbData": 0,
            "openerStorageAddress": "http://127.0.0.1:8000/media/data_managers/ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994/opener_KobP3t5.py",
            "owner": "e450e7bf3f3a159ff9772f335612b256eb1e1a138ba8ec88c8ae65c55c2f221d",
            "permissions": "all", "size": 0, "type": "images"
        },
        {
            "objectiveKeys": ["6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c",
                              "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f"],
            "description": {"hash": "258bef187a166b3fef5cb86e68c8f7e154c283a148cd5bc344fec7e698821ad3",
                            "storageAddress": "http://127.0.0.1:8000/data_manager/b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0/description/"},
            "key": "b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0",
            "name": "Simplified ISIC 2018", "nbData": 6,
            "openerStorageAddress": "http://127.0.0.1:8000/data_manager/b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0/opener/",
            "owner": "e450e7bf3f3a159ff9772f335612b256eb1e1a138ba8ec88c8ae65c55c2f221d", "permissions": "all",
            "size": 300, "type": "Images"
        }
    ]
]

objective = [[{
                   "descriptionStorageAddress": "http://127.0.0.1:8001/objective/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/description/",
                   "key": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
                   "metrics": {"hash": "750f622262854341bd44f55c1018949e9c119606ef5068bd7d137040a482a756",
                               "name": "macro-average recall",
                               "storageAddress": "http://127.0.0.1:8001/objective/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/metrics/"},
                   "name": "Skin Lesion Classification Challenge",
                   "owner": "c657699f8b03c19e6eadc7b474c23f26dd83454395266a673406f2cf44de2ca2", "permissions": "all",
                   "testDataKeys": ["e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1"]}, {
                   "descriptionStorageAddress": "http://127.0.0.1:8000/objective/6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c/description/",
                   "key": "6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c",
                   "metrics": {"hash": "0bc732c26bafdc41321c2bffd35b6835aa35f7371a4eb02994642c2c3a688f60",
                               "name": "macro-average recall",
                               "storageAddress": "http://127.0.0.1:8000/objective/6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c/metrics/"},
                   "name": "Simplified skin lesion classification",
                   "owner": "e450e7bf3f3a159ff9772f335612b256eb1e1a138ba8ec88c8ae65c55c2f221d", "permissions": "all",
                   "testDataKeys": ["2d0f943aa81a9cb3fe84b162559ce6aff068ccb04e0cb284733b8f9d7e06517e",
                                    "533ee6e7b9d8b247e7e853b24547f57e6ef351852bac0418f13a0666173448f1"]}]]


def mocked_client_list_asset(data, st):
    return {'result': flatten(data),
            'status_code': st}


@mock.patch('substra.commands.api.config_path', '/tmp/.substra', create=True)
class TestList(TestCase):
    def setUp(self):
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

    @mock.patch('substra.commands.api.Client.list', return_value=mocked_client_list_asset(objective, 200))
    def test_returns_objective_list(self, mock_list):

        res = List({
            '<asset>': 'objective',
        }).run()

        self.assertEqual(json.loads(res)['status_code'], 200)
        self.assertEqual(json.loads(res)['result'], flatten(objective))
        self.assertEqual(len(mock_list.call_args_list), 1)

    @mock.patch('substra.commands.api.Client.list', side_effect=Exception('fail'))
    def test_returns_objective_list_fail(self, mock_list):
        with self.assertRaises(Exception) as e:
            List({'<asset>': 'objective'}).run()
            self.assertTrue(str(e) == 'Failed to list objective')

        self.assertEqual(len(mock_list.call_args_list), 1)

    @mock.patch('substra.commands.api.Client.list', return_value=mocked_client_list_asset(dataset, 200))
    def test_returns_dataset_list(self, mock_list):

        res = List({
            '<asset>': 'dataset'
        }).run()

        self.assertEqual(json.loads(res)['status_code'], 200)
        self.assertEqual(json.loads(res)['result'], flatten(dataset))
        self.assertEqual(len(mock_list.call_args_list), 1)

    @mock.patch('substra.commands.api.Client.list', side_effect=Exception('fail'))
    def test_returns_dataset_list_no_json(self, mock_list):
        with self.assertRaises(Exception) as e:
            List({'<asset>': 'dataset'}).run()
            self.assertTrue(str(e) == 'Can\'t decode response value from server to json.')
        self.assertEqual(len(mock_list.call_args_list), 1)

    @mock.patch('substra.commands.api.Client.list', return_value=mocked_client_list_asset(objective, 200))
    def test_returns_objective_list_filters(self, mock_list):

        res = List({
            '<asset>': 'objective',
            '<filters>': '["objective:name:Skin Lesion Classification Challenge", "OR", "data_manager:name:Simplified ISIC 2018"]'
        }).run()

        self.assertEqual(json.loads(res)['status_code'], 200)
        self.assertEqual(json.loads(res)['result'], flatten(objective))
        self.assertEqual(len(mock_list.call_args_list), 1)


@mock.patch('substra.commands.api.config_path', '/tmp/.substra', create=True)
class TestListConfigBasicAuth(TestCase):
    def setUp(self):
        self.dataset_file_path = './tests/assets/data_manager/data_manager.json'

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

    @mock.patch('substra.commands.api.Client.list', return_value=mocked_client_list_asset(objective, 200))
    def test_returns_objective_list(self, mock_list):

        res = List({
            '<asset>': 'objective'
        }).run()

        self.assertEqual(json.loads(res)['status_code'], 200)
        self.assertEqual(json.loads(res)['result'], flatten(objective))
        self.assertEqual(len(mock_list.call_args_list), 1)


@mock.patch('substra.commands.api.config_path', '/tmp/.substra', create=True)
class TestListConfigInsecure(TestCase):
    def setUp(self):
        self.dataset_file_path = './tests/assets/data_manager/data_manager.json'

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

    @mock.patch('substra.commands.api.Client.list', return_value=mocked_client_list_asset(objective, 200))
    def test_returns_objective_list(self, mock_list):

        res = List({
            '<asset>': 'objective'
        }).run()

        self.assertEqual(json.loads(res)['status_code'], 200)
        self.assertEqual(json.loads(res)['result'], flatten(objective))
        self.assertEqual(len(mock_list.call_args_list), 1)
