from unittest import TestCase, mock

import requests

from substra_sdk_py import Client

data_manager = {
    "objectiveKey": "",
    "description": {
        "hash": "7a90514f88c70002608a9868681dd1589ea598e78d00a8cd7783c3ea0f9ceb09",
        "storageAddress": "http://127.0.0.1:8001/data_manager/ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994/description/"},
    "key": "ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994", "name": "ISIC 2018", "nbData": 2,
    "openerStorageAddress": "http://127.0.0.1:8001/data_manager/ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994/opener/",
    "owner": "c657699f8b03c19e6eadc7b474c23f26dd83454395266a673406f2cf44de2ca2", "permissions": "all",
    "size": 100, "type": "Images"}

objective = {
    "descriptionStorageAddress": "http://127.0.0.1:8001/objective/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/description/",
    "key": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
    "metrics": {
        "hash": "750f622262854341bd44f55c1018949e9c119606ef5068bd7d137040a482a756",
        "name": "macro-average recall",
        "storageAddress": "http://127.0.0.1:8001/objective/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/metrics/"},
    "name": "Skin Lesion Classification Challenge",
    "owner": "c657699f8b03c19e6eadc7b474c23f26dd83454395266a673406f2cf44de2ca2", "permissions": "all",
    "testDataKeys": ["e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1"]}

algo = {
    "objectiveKey": "6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c",
    "description": {
        "hash": "3b1281cbdd6ebfec650d0a9f932a64e45a27262848065d7cecf11fd7191b4b1f",
        "storageAddress": "http://127.0.0.1:8001/algo/7742aea2001ceb40e9ce8a37fa27237d5b2d1f574e06d48677af945cfdf42ec0/description/"},
    "key": "7742aea2001ceb40e9ce8a37fa27237d5b2d1f574e06d48677af945cfdf42ec0",
    "name": "Logistic regression for balanced problem",
    "owner": "c657699f8b03c19e6eadc7b474c23f26dd83454395266a673406f2cf44de2ca2", "permissions": "all",
    "storageAddress": "http://127.0.0.1:8001/algo/7742aea2001ceb40e9ce8a37fa27237d5b2d1f574e06d48677af945cfdf42ec0/file/"}

data_sample = {
    "pkhash": "e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1", "validated": True,
    "file": "http://127.0.0.1:8000/media/data_sample/e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1/0024700.zip"}

bulk_data_samples = [
    {
        "pkhash": "2d0f943aa81a9cb3fe84b162559ce6aff068ccb04e0cb284733b8f9d7e06517e",
        "validated": True,
        "file": "http://127.0.0.1:8000/media/data_sample/2d0f943aa81a9cb3fe84b162559ce6aff068ccb04e0cb284733b8f9d7e06517e/0024315.zip"
    },
    {
        "pkhash": "4b5152871b181d10ee774c10458c064c70710f4ba35938f10c0b7aa51f7dc010",
        "validated": True,
        "file": "http://127.0.0.1:8000/media/data_sample/4b5152871b181d10ee774c10458c064c70710f4ba35938f10c0b7aa51f7dc010/0024701.zip"
    }
]


def mock_success_response(data=None, status_code=200):
    m = mock.MagicMock(spec=requests.Response)
    m.status_code = status_code
    m.json = mock.MagicMock(return_value=data)
    return m


def mock_fail_response(data=None, status_code=500, message=None):
    m = mock_success_response(data=data, status_code=status_code)
    message = str(status_code) if message is None else message
    m.raise_for_status = mock.MagicMock(
        side_effect=requests.exceptions.HTTPError(message, response=m))
    return m


class TestBase(TestCase):

    def setUp(self):
        self.client = Client()

        self.data_manager_file_path = './tests/assets/data_manager/data_manager.json'
        self.objective_file_path = './tests/assets/objective/objective.json'
        self.algo_file_path = './tests/assets/algo/algo.json'
        self.data_sample_file_path = './tests/assets/data_sample/data_sample.json'
        self.bulk_data_samples_file_path = './tests/assets/data_sample/bulk_data_samples.json'
        self.data_samples_file_path = self.bulk_data_samples_file_path
