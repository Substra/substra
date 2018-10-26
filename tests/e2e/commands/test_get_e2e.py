import json
import os
from subprocess import PIPE, Popen as popen
from unittest import TestCase

from substra.commands import Config


class TestGet(TestCase):

    def setUp(self):
        Config({
            '<url>': 'http://127.0.0.1:8000',
            '<version>': '0.0',
            '--config': '/tmp/.substra_e2e'
        }).run()

    def tearDown(self):
        try:
            os.remove('/tmp/.substra_e2e')
        except:
            pass

    def test_get_challenge(self):
        output = \
        popen(['substra', 'get', 'challenge', '6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c', '--config=/tmp/.substra_e2e'],
              stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')
        res = json.loads(res)

        self.assertTrue(res['name'] == 'Simplified skin lesion classification')
        self.assertTrue(res[
                            'descriptionStorageAddress'] == 'http://127.0.0.1:8000/challenge/6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c/description/')
        self.assertTrue(res['metrics'] == {"name": "macro-average recall",
                                           "hash": "0bc732c26bafdc41321c2bffd35b6835aa35f7371a4eb02994642c2c3a688f60",
                                           "storageAddress": "http://127.0.0.1:8000/challenge/6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c/metrics/"})
        self.assertTrue(res['owner'] == 'b6f337e92750d3878666fc458e203051eb38b8baa91786daa596ff8879ae2d95')
        self.assertTrue(res['testDataKeys'] == ["2d0f943aa81a9cb3fe84b162559ce6aff068ccb04e0cb284733b8f9d7e06517e",
                              "533ee6e7b9d8b247e7e853b24547f57e6ef351852bac0418f13a0666173448f1"])
        self.assertTrue(res['permissions'] == 'all')
        self.assertTrue(res['pkhash'] == '6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c')
