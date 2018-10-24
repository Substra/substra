import json
from subprocess import PIPE, Popen as popen
from unittest import TestCase

challenge = {"name": "Simplified skin lesion classification",
             "descriptionStorageAddress": "http://127.0.0.1:8000/challenge/6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c/description/",
             "metrics": {"name": "macro-average recall",
                         "hash": "0bc732c26bafdc41321c2bffd35b6835aa35f7371a4eb02994642c2c3a688f60",
                         "storageAddress": "http://127.0.0.1:8000/challenge/6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c/metrics/"},
             "owner": "40781e92bb83417d306905dccb5b2d8b03293e319e39c8ff9cc787f75aa7d35b",
             "testDataKeys": ["2d0f943aa81a9cb3fe84b162559ce6aff068ccb04e0cb284733b8f9d7e06517e",
                              "533ee6e7b9d8b247e7e853b24547f57e6ef351852bac0418f13a0666173448f1"], "permissions": "all",
             "pkhash": "6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c",
             "creation_date": "2018-08-31T17:36:58.196000Z", "last_modified": "2018-08-31T17:37:01.256000Z"}


class TestGet(TestCase):

    def test_get_challenge(self):
        output = popen(['substra', 'get', 'challenge', '6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c'],
              stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')

        self.assertTrue(json.loads(res) == challenge)
