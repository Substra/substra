import json
import os
from subprocess import PIPE, Popen as popen
from unittest import TestCase

from substra.commands import Config


class TestGet(TestCase):

    def setUp(self):
        Config({
            '<url>': 'http://owkin.substrabac:8000',
            '<version>': '0.0',
            '<user>': os.environ.get('BACK_AUTH_USER', ''),
            '<password>': os.environ.get('BACK_AUTH_PASSWORD', ''),
            '--config': '/tmp/.substra_e2e',
        }).run()

    def tearDown(self):
        try:
            os.remove('/tmp/.substra_e2e')
        except:
            pass

    def test_get_objective(self):
        output = \
        popen(['substra', 'get', 'objective', '6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c', '--config=/tmp/.substra_e2e'],
              stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')
        res = json.loads(res)

        self.assertTrue(res['name'] == 'Simplified skin lesion classification')
        self.assertTrue(res[
                            'descriptionStorageAddress'] == 'http://owkin.substrabac:8000/objective/6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c/description/')
        self.assertTrue(res['metrics'] == {"name": "macro-average recall",
                                           "hash": "0bc732c26bafdc41321c2bffd35b6835aa35f7371a4eb02994642c2c3a688f60",
                                           "storageAddress": "http://owkin.substrabac:8000/objective/6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c/metrics/"})
        self.assertTrue(res['owner'] == 'ca77d9070da2732f3dc1fcdb9397cfcf2fad2dcdde4e355dfe34658ad8b9ce55')
        self.assertTrue(res['testDataKeys'] == ["2d0f943aa81a9cb3fe84b162559ce6aff068ccb04e0cb284733b8f9d7e06517e",
                              "533ee6e7b9d8b247e7e853b24547f57e6ef351852bac0418f13a0666173448f1"])
        self.assertTrue(res['permissions'] == 'all')
        self.assertTrue(res['pkhash'] == '6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c')
