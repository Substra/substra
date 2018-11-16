import json
import os
from subprocess import PIPE, Popen as popen
from unittest import TestCase

from substra.commands import Config

challenge = [[{
    "descriptionStorageAddress": "http://127.0.0.1:8001/challenge/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/description/",
    "key": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
    "metrics": {"hash": "750f622262854341bd44f55c1018949e9c119606ef5068bd7d137040a482a756",
                "name": "macro-average recall",
                "storageAddress": "http://127.0.0.1:8001/challenge/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/metrics/"},
    "name": "Skin Lesion Classification Challenge",
    "owner": "67c8a4121569cbc56031fb3fccce68a50a3f8b12d7386397db623ced654ac86e", "permissions": "all",
    "testDataKeys": ["e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1"]}, {
    "descriptionStorageAddress": "http://127.0.0.1:8000/challenge/6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c/description/",
    "key": "6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c",
    "metrics": {"hash": "0bc732c26bafdc41321c2bffd35b6835aa35f7371a4eb02994642c2c3a688f60",
                "name": "macro-average recall",
                "storageAddress": "http://127.0.0.1:8000/challenge/6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c/metrics/"},
    "name": "Simplified skin lesion classification",
    "owner": "b6f337e92750d3878666fc458e203051eb38b8baa91786daa596ff8879ae2d95", "permissions": "all",
    "testDataKeys": ["2d0f943aa81a9cb3fe84b162559ce6aff068ccb04e0cb284733b8f9d7e06517e",
                     "533ee6e7b9d8b247e7e853b24547f57e6ef351852bac0418f13a0666173448f1"]}]]

dataset = [[{"challengeKeys": [],
             "description": {"hash": "7a90514f88c70002608a9868681dd1589ea598e78d00a8cd7783c3ea0f9ceb09",
                             "storageAddress": "http://127.0.0.1:8001/dataset/ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994/description/"},
             "key": "ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994", "name": "ISIC 2018",
             "nbData": 2,
             "openerStorageAddress": "http://127.0.0.1:8001/dataset/ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994/opener/",
             "owner": "67c8a4121569cbc56031fb3fccce68a50a3f8b12d7386397db623ced654ac86e", "permissions": "all",
             "size": 553113, "type": "Images"}, {
                "challengeKeys": ["6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c",
                                  "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f"],
                "description": {"hash": "258bef187a166b3fef5cb86e68c8f7e154c283a148cd5bc344fec7e698821ad3",
                                "storageAddress": "http://127.0.0.1:8000/dataset/b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0/description/"},
                "key": "b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0",
                "name": "Simplified ISIC 2018", "nbData": 6,
                "openerStorageAddress": "http://127.0.0.1:8000/dataset/b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0/opener/",
                "owner": "b6f337e92750d3878666fc458e203051eb38b8baa91786daa596ff8879ae2d95", "permissions": "all",
                "size": 1415097, "type": "Images"}]]

data = [{"pkhash": "e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1", "validated": True,
         "file": "http://127.0.0.1:8000/media/data/e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1/0024900.zip"},
        {"pkhash": "4b5152871b181d10ee774c10458c064c70710f4ba35938f10c0b7aa51f7dc010", "validated": True,
         "file": "http://127.0.0.1:8000/media/data/4b5152871b181d10ee774c10458c064c70710f4ba35938f10c0b7aa51f7dc010/0024701.zip"},
        {"pkhash": "93e4b1e040b08cfa8a68b13f9dddb95a6672e8a377378545b2b1254691cfc060", "validated": True,
         "file": "http://127.0.0.1:8000/media/data/93e4b1e040b08cfa8a68b13f9dddb95a6672e8a377378545b2b1254691cfc060/0024317.zip"},
        {"pkhash": "eed4c6ea09babe7ca6428377fff6e54102ef5cdb0cae593732ddbe3f224217cb", "validated": True,
         "file": "http://127.0.0.1:8000/media/data/eed4c6ea09babe7ca6428377fff6e54102ef5cdb0cae593732ddbe3f224217cb/0024316.zip"},
        {"pkhash": "2d0f943aa81a9cb3fe84b162559ce6aff068ccb04e0cb284733b8f9d7e06517e", "validated": True,
         "file": "http://127.0.0.1:8000/media/data/2d0f943aa81a9cb3fe84b162559ce6aff068ccb04e0cb284733b8f9d7e06517e/0024315.zip"},
        {"pkhash": "533ee6e7b9d8b247e7e853b24547f57e6ef351852bac0418f13a0666173448f1", "validated": True,
         "file": "http://127.0.0.1:8000/media/data/533ee6e7b9d8b247e7e853b24547f57e6ef351852bac0418f13a0666173448f1/0024318.zip"}]

algo = [[{"challengeKey": "6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c",
          "description": {"hash": "3b1281cbdd6ebfec650d0a9f932a64e45a27262848065d7cecf11fd7191b4b1f",
                          "storageAddress": "http://127.0.0.1:8001/algo/7742aea2001ceb40e9ce8a37fa27237d5b2d1f574e06d48677af945cfdf42ec0/description/"},
          "key": "7742aea2001ceb40e9ce8a37fa27237d5b2d1f574e06d48677af945cfdf42ec0",
          "name": "Logistic regression for balanced problem",
          "owner": "67c8a4121569cbc56031fb3fccce68a50a3f8b12d7386397db623ced654ac86e", "permissions": "all",
          "storageAddress": "http://127.0.0.1:8001/algo/7742aea2001ceb40e9ce8a37fa27237d5b2d1f574e06d48677af945cfdf42ec0/file/"},
         {"challengeKey": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
          "description": {"hash": "b9463411a01ea00869bdffce6e59a5c100a4e635c0a9386266cad3c77eb28e9e",
                          "storageAddress": "http://127.0.0.1:8001/algo/0acc5180e09b6a6ac250f4e3c172e2893f617aa1c22ef1f379019d20fe44142f/description/"},
          "key": "0acc5180e09b6a6ac250f4e3c172e2893f617aa1c22ef1f379019d20fe44142f", "name": "Neural Network",
          "owner": "67c8a4121569cbc56031fb3fccce68a50a3f8b12d7386397db623ced654ac86e", "permissions": "all",
          "storageAddress": "http://127.0.0.1:8001/algo/0acc5180e09b6a6ac250f4e3c172e2893f617aa1c22ef1f379019d20fe44142f/file/"},
         {"challengeKey": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
          "description": {"hash": "124a0425b746d7072282d167b53cb6aab3a31bf1946dae89135c15b0126ebec3",
                          "storageAddress": "http://127.0.0.1:8001/algo/6dcbfcf29146acd19c6a2997b2e81d0cd4e88072eea9c90bbac33f0e8573993f/description/"},
          "key": "6dcbfcf29146acd19c6a2997b2e81d0cd4e88072eea9c90bbac33f0e8573993f", "name": "Logistic regression",
          "owner": "67c8a4121569cbc56031fb3fccce68a50a3f8b12d7386397db623ced654ac86e", "permissions": "all",
          "storageAddress": "http://127.0.0.1:8001/algo/6dcbfcf29146acd19c6a2997b2e81d0cd4e88072eea9c90bbac33f0e8573993f/file/"},
         {"challengeKey": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
          "description": {"hash": "4acea40c4b51996c88ef279c5c9aa41ab77b97d38c5ca167e978a98b2e402675",
                          "storageAddress": "http://127.0.0.1:8001/algo/f2d9fd38e25cd975c49f3ce7e6739846585e89635a86689b5db42ab2c0c57284/description/"},
          "key": "f2d9fd38e25cd975c49f3ce7e6739846585e89635a86689b5db42ab2c0c57284", "name": "Random Forest",
          "owner": "67c8a4121569cbc56031fb3fccce68a50a3f8b12d7386397db623ced654ac86e", "permissions": "all",
          "storageAddress": "http://127.0.0.1:8001/algo/f2d9fd38e25cd975c49f3ce7e6739846585e89635a86689b5db42ab2c0c57284/file/"}]]

model = [[{"algo": {"hash": "6dcbfcf29146acd19c6a2997b2e81d0cd4e88072eea9c90bbac33f0e8573993f",
                    "name": "Logistic regression",
                    "storageAddress": "http://127.0.0.1:8001/algo/6dcbfcf29146acd19c6a2997b2e81d0cd4e88072eea9c90bbac33f0e8573993f/file/"},
           "challenge": {"hash": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
                         "metrics": {"hash": "750f622262854341bd44f55c1018949e9c119606ef5068bd7d137040a482a756",
                                     "storageAddress": "http://127.0.0.1:8001/challenge/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/metrics/"}},
           "creator": "67c8a4121569cbc56031fb3fccce68a50a3f8b12d7386397db623ced654ac86e",
           "endModel": {"hash": "fe900588d43263c0ce1709116fe07c68d299acbbb6cfb241b0e8795bc8a1fbcb",
                        "storageAddress": "http://127.0.0.1:8001/model/fe900588d43263c0ce1709116fe07c68d299acbbb6cfb241b0e8795bc8a1fbcb/file/"},
           "key": "72ffa024fb7858497338937d2aa302947ee00ec8bd47511959f0062e24e75fb6",
           "log": "Train - CPU:164.58 % - Mem:0.12 GB - GPU:0.00 % - GPU Mem:0.00 GB; Test - CPU:0.00 % - Mem:0.00 GB - GPU:0.00 % - GPU Mem:0.00 GB; ",
           "permissions": "all", "startModel": None, "status": "done",
           "testData": {"keys": ["e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1"],
                        "openerHash": "b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0", "perf": 1,
                        "worker": "b6f337e92750d3878666fc458e203051eb38b8baa91786daa596ff8879ae2d95"}, "trainData": {
        "keys": ["62fb3263208d62c7235a046ee1d80e25512fe782254b730a9e566276b8c0ef3a",
                 "42303efa663015e729159833a12ffb510ff92a6e386b8152f90f6fb14ddc94c9"],
        "openerHash": "ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994", "perf": 1,
        "worker": "67c8a4121569cbc56031fb3fccce68a50a3f8b12d7386397db623ced654ac86e"}}]]

traintuple = [{"algo": {"hash": "6dcbfcf29146acd19c6a2997b2e81d0cd4e88072eea9c90bbac33f0e8573993f",
                        "name": "Logistic regression",
                        "storageAddress": "http://127.0.0.1:8001/algo/6dcbfcf29146acd19c6a2997b2e81d0cd4e88072eea9c90bbac33f0e8573993f/file/"},
               "challenge": {"hash": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
                             "metrics": {"hash": "750f622262854341bd44f55c1018949e9c119606ef5068bd7d137040a482a756",
                                         "storageAddress": "http://127.0.0.1:8001/challenge/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/metrics/"}},
               "creator": "67c8a4121569cbc56031fb3fccce68a50a3f8b12d7386397db623ced654ac86e",
               "endModel": {"hash": "fe900588d43263c0ce1709116fe07c68d299acbbb6cfb241b0e8795bc8a1fbcb",
                            "storageAddress": "http://127.0.0.1:8001/model/fe900588d43263c0ce1709116fe07c68d299acbbb6cfb241b0e8795bc8a1fbcb/file/"},
               "key": "72ffa024fb7858497338937d2aa302947ee00ec8bd47511959f0062e24e75fb6",
               "log": "Train - CPU:164.58 % - Mem:0.12 GB - GPU:0.00 % - GPU Mem:0.00 GB; Test - CPU:0.00 % - Mem:0.00 GB - GPU:0.00 % - GPU Mem:0.00 GB; ",
               "permissions": "all", "startModel": None, "status": "done",
               "testData": {"keys": ["e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1"],
                            "openerHash": "b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0", "perf": 1,
                            "worker": "b6f337e92750d3878666fc458e203051eb38b8baa91786daa596ff8879ae2d95"},
               "trainData": {"keys": ["62fb3263208d62c7235a046ee1d80e25512fe782254b730a9e566276b8c0ef3a",
                                      "42303efa663015e729159833a12ffb510ff92a6e386b8152f90f6fb14ddc94c9"],
                             "openerHash": "ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994",
                             "perf": 1, "worker": "67c8a4121569cbc56031fb3fccce68a50a3f8b12d7386397db623ced654ac86e"}}]


# Run this test only after an e2e multi orgs
class TestList(TestCase):

    def setUp(self):
        Config({
            '<url>': 'http://owkin.substrabac:8000',
            '<version>': '0.0',
            '<user>': os.environ.get('BACK_AUTH_USER', ''),
            '<password>': os.environ.get('BACK_AUTH_PASSWORD', ''),
            '--config': '/tmp/.substra_e2e'
        }).run()

    def tearDown(self):
        try:
            os.remove('/tmp/.substra_e2e')
        except:
            pass

    def test_list_challenge(self):
        output = popen(['substra', 'list', 'challenge', '--config=/tmp/.substra_e2e'], stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')

        self.assertTrue(json.loads(res) == challenge)

    def test_list_dataset(self):
        output = popen(['substra', 'list', 'dataset', '--config=/tmp/.substra_e2e'], stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')

        self.assertTrue(json.loads(res) == dataset)

    def test_list_data(self):
        output = popen(['substra', 'list', 'data', '--config=/tmp/.substra_e2e'], stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')

        self.assertTrue(json.loads(res) == data)

    def test_list_algo(self):
        output = popen(['substra', 'list', 'algo', '--config=/tmp/.substra_e2e'], stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')

        self.assertTrue(json.loads(res) == algo)

    def test_list_model(self):
        output = popen(['substra', 'list', 'model', '--config=/tmp/.substra_e2e'], stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')

        self.assertTrue(json.loads(res) == model)

    def test_list_traintuple(self):
        output = popen(['substra', 'list', 'traintuple', '--config=/tmp/.substra_e2e'], stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')

        self.assertTrue(json.loads(res) == traintuple)
