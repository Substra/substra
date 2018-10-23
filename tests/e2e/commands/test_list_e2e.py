import json
from subprocess import PIPE, Popen as popen
from unittest import TestCase

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


class TestList(TestCase):

    def test_list_challenge(self):
        output = popen(['substra', 'list', 'challenge'], stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')

        self.assertTrue(res == json.dumps(challenge))
