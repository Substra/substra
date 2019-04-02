from unittest import mock

from .test_base import TestBase, mock_success_response, mock_fail_response

from substra_sdk_py.utils import flatten

data_manager = [
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
                   "testDataSampleKeys": ["e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1"]}, {
                   "descriptionStorageAddress": "http://127.0.0.1:8000/objective/6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c/description/",
                   "key": "6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c",
                   "metrics": {"hash": "0bc732c26bafdc41321c2bffd35b6835aa35f7371a4eb02994642c2c3a688f60",
                               "name": "macro-average recall",
                               "storageAddress": "http://127.0.0.1:8000/objective/6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c/metrics/"},
                   "name": "Simplified skin lesion classification",
                   "owner": "e450e7bf3f3a159ff9772f335612b256eb1e1a138ba8ec88c8ae65c55c2f221d", "permissions": "all",
                   "testDataSampleKeys": ["2d0f943aa81a9cb3fe84b162559ce6aff068ccb04e0cb284733b8f9d7e06517e",
                                          "533ee6e7b9d8b247e7e853b24547f57e6ef351852bac0418f13a0666173448f1"]}]]


def mocked_requests_get_objective(*args, **kwargs):
    return mock_success_response(data=objective)


def mocked_requests_get_data_manager(*args, **kwargs):
    return mock_success_response(data=data_manager)


def mocked_requests_get_data_manager_no_json(*args, **kwargs):
    return mock_success_response(data='invalidjson')


def mocked_requests_list_objective_fail(*args, **kwargs):
    return mock_fail_response()


def mocked_requests_get_objective_filtered(*args, **kwargs):
    return mock_success_response(data=objective)


class TestList(TestBase):

    @mock.patch('substra_sdk_py.requests_wrapper.requests.get', side_effect=mocked_requests_get_objective)
    def test_returns_objective_list(self, mock_get):

        res = self.client.list('objective')

        self.assertEqual(res, flatten(objective))
        self.assertEqual(len(mock_get.call_args_list), 1)

    @mock.patch('substra_sdk_py.requests_wrapper.requests.get', side_effect=mocked_requests_list_objective_fail)
    def test_returns_objective_list_fail(self, mock_get):
        try:
            self.client.list('objective')
        except Exception as e:
            self.assertEqual(str(e), '500')

        self.assertEqual(len(mock_get.call_args_list), 1)

    @mock.patch('substra_sdk_py.requests_wrapper.requests.get', side_effect=mocked_requests_get_data_manager)
    def test_returns_data_manager_list(self, mock_get):

        res = self.client.list('data_manager')

        self.assertEqual(res, flatten(data_manager))
        self.assertEqual(len(mock_get.call_args_list), 1)

    @mock.patch('substra_sdk_py.requests_wrapper.requests.get', side_effect=mocked_requests_get_data_manager_no_json)
    def test_returns_data_manager_list_no_json(self, mock_get):
        try:
            self.client.list('data_manager')
        except Exception as e:
            self.assertEqual(str(e), 'Can\'t decode response value from server to json.')
        self.assertEqual(len(mock_get.call_args_list), 1)

    @mock.patch('substra_sdk_py.requests_wrapper.requests.get', side_effect=mocked_requests_get_objective_filtered)
    def test_returns_objective_list_filters(self, mock_get):

        res = self.client.list(
            'objective',
            '["objective:name:Skin Lesion Classification Challenge", "OR", "data_manager:name:Simplified ISIC 2018"]')

        self.assertEqual(res, flatten(objective))
        self.assertEqual(len(mock_get.call_args_list), 1)

    @mock.patch('substra_sdk_py.requests_wrapper.requests.get', side_effect=mocked_requests_get_objective_filtered)
    def test_returns_objective_list_bad_filters(self, mock_get):
        try:
            self.client.list('objective', 'toto')
        except Exception as e:
            self.assertEqual(str(e), 'Cannot load filters. Please review the documentation.')
            self.assertEqual(len(mock_get.call_args_list), 0)
