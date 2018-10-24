import json
from subprocess import PIPE, Popen as popen
from unittest import TestCase

challenge = [[{
    "descriptionStorageAddress": "http://127.0.0.1:8000/challenge/6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c/description/",
    "key": "6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c",
    "metrics": {"hash": "0bc732c26bafdc41321c2bffd35b6835aa35f7371a4eb02994642c2c3a688f60",
                "name": "macro-average recall",
                "storageAddress": "http://127.0.0.1:8000/challenge/6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c/metrics/"},
    "name": "Simplified skin lesion classification",
    "owner": "40781e92bb83417d306905dccb5b2d8b03293e319e39c8ff9cc787f75aa7d35b", "permissions": "all",
    "testDataKeys": ["2d0f943aa81a9cb3fe84b162559ce6aff068ccb04e0cb284733b8f9d7e06517e",
                     "533ee6e7b9d8b247e7e853b24547f57e6ef351852bac0418f13a0666173448f1"]}, {
    "descriptionStorageAddress": "http://127.0.0.1:8001/challenge/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/description/",
    "key": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
    "metrics": {"hash": "750f622262854341bd44f55c1018949e9c119606ef5068bd7d137040a482a756",
                "name": "macro-average recall",
                "storageAddress": "http://127.0.0.1:8001/challenge/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/metrics/"},
    "name": "Skin Lesion Classification Challenge",
    "owner": "79d985e411f93533a0b6d86fceaab45feba1d80b81271012313173a947b3b274", "permissions": "all",
    "testDataKeys": ["e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1"]}]]

dataset = [[{"challengeKeys": ["6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c",
                               "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f"],
             "description": {"hash": "258bef187a166b3fef5cb86e68c8f7e154c283a148cd5bc344fec7e698821ad3",
                             "storageAddress": "http://127.0.0.1:8000/dataset/b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0/description/"},
             "key": "b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0", "name": "Simplified ISIC 2018",
             "nbData": 6,
             "openerStorageAddress": "http://127.0.0.1:8000/dataset/b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0/opener/",
             "owner": "40781e92bb83417d306905dccb5b2d8b03293e319e39c8ff9cc787f75aa7d35b", "permissions": "all",
             "size": 300, "type": "Images"}, {"challengeKeys": [], "description": {
    "hash": "7a90514f88c70002608a9868681dd1589ea598e78d00a8cd7783c3ea0f9ceb09",
    "storageAddress": "http://127.0.0.1:8001/dataset/ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994/description/"},
                                              "key": "ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994",
                                              "name": "ISIC 2018", "nbData": 2,
                                              "openerStorageAddress": "http://127.0.0.1:8001/dataset/ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994/opener/",
                                              "owner": "79d985e411f93533a0b6d86fceaab45feba1d80b81271012313173a947b3b274",
                                              "permissions": "all", "size": 100, "type": "Images"}]]

data = [{"pkhash": "4b5152871b181d10ee774c10458c064c70710f4ba35938f10c0b7aa51f7dc010", "validated": True,
         "file": "http://127.0.0.1:8000/media/data/4b5152871b181d10ee774c10458c064c70710f4ba35938f10c0b7aa51f7dc010/0024701.zip"},
        {"pkhash": "e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1", "validated": True,
         "file": "http://127.0.0.1:8000/media/data/e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1/0024900.zip"},
        {"pkhash": "eed4c6ea09babe7ca6428377fff6e54102ef5cdb0cae593732ddbe3f224217cb", "validated": True,
         "file": "http://127.0.0.1:8000/media/data/eed4c6ea09babe7ca6428377fff6e54102ef5cdb0cae593732ddbe3f224217cb/0024316.zip"},
        {"pkhash": "2d0f943aa81a9cb3fe84b162559ce6aff068ccb04e0cb284733b8f9d7e06517e", "validated": True,
         "file": "http://127.0.0.1:8000/media/data/2d0f943aa81a9cb3fe84b162559ce6aff068ccb04e0cb284733b8f9d7e06517e/0024315.zip"},
        {"pkhash": "93e4b1e040b08cfa8a68b13f9dddb95a6672e8a377378545b2b1254691cfc060", "validated": True,
         "file": "http://127.0.0.1:8000/media/data/93e4b1e040b08cfa8a68b13f9dddb95a6672e8a377378545b2b1254691cfc060/0024317.zip"},
        {"pkhash": "533ee6e7b9d8b247e7e853b24547f57e6ef351852bac0418f13a0666173448f1", "validated": True,
         "file": "http://127.0.0.1:8000/media/data/533ee6e7b9d8b247e7e853b24547f57e6ef351852bac0418f13a0666173448f1/0024318.zip"}]

algo = [[{"challengeKey": "6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c",
          "description": {"hash": "3b1281cbdd6ebfec650d0a9f932a64e45a27262848065d7cecf11fd7191b4b1f",
                          "storageAddress": "http://127.0.0.1:8001/algo/7742aea2001ceb40e9ce8a37fa27237d5b2d1f574e06d48677af945cfdf42ec0/description/"},
          "key": "7742aea2001ceb40e9ce8a37fa27237d5b2d1f574e06d48677af945cfdf42ec0",
          "name": "Logistic regression for balanced problem",
          "owner": "79d985e411f93533a0b6d86fceaab45feba1d80b81271012313173a947b3b274", "permissions": "all",
          "storageAddress": "http://127.0.0.1:8001/algo/7742aea2001ceb40e9ce8a37fa27237d5b2d1f574e06d48677af945cfdf42ec0/file/"},
         {"challengeKey": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
          "description": {"hash": "b9463411a01ea00869bdffce6e59a5c100a4e635c0a9386266cad3c77eb28e9e",
                          "storageAddress": "http://127.0.0.1:8001/algo/0acc5180e09b6a6ac250f4e3c172e2893f617aa1c22ef1f379019d20fe44142f/description/"},
          "key": "0acc5180e09b6a6ac250f4e3c172e2893f617aa1c22ef1f379019d20fe44142f", "name": "Neural Network",
          "owner": "79d985e411f93533a0b6d86fceaab45feba1d80b81271012313173a947b3b274", "permissions": "all",
          "storageAddress": "http://127.0.0.1:8001/algo/0acc5180e09b6a6ac250f4e3c172e2893f617aa1c22ef1f379019d20fe44142f/file/"},
         {"challengeKey": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
          "description": {"hash": "124a0425b746d7072282d167b53cb6aab3a31bf1946dae89135c15b0126ebec3",
                          "storageAddress": "http://127.0.0.1:8001/algo/6dcbfcf29146acd19c6a2997b2e81d0cd4e88072eea9c90bbac33f0e8573993f/description/"},
          "key": "6dcbfcf29146acd19c6a2997b2e81d0cd4e88072eea9c90bbac33f0e8573993f", "name": "Logistic regression",
          "owner": "79d985e411f93533a0b6d86fceaab45feba1d80b81271012313173a947b3b274", "permissions": "all",
          "storageAddress": "http://127.0.0.1:8001/algo/6dcbfcf29146acd19c6a2997b2e81d0cd4e88072eea9c90bbac33f0e8573993f/file/"},
         {"challengeKey": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
          "description": {"hash": "4acea40c4b51996c88ef279c5c9aa41ab77b97d38c5ca167e978a98b2e402675",
                          "storageAddress": "http://127.0.0.1:8001/algo/f2d9fd38e25cd975c49f3ce7e6739846585e89635a86689b5db42ab2c0c57284/description/"},
          "key": "f2d9fd38e25cd975c49f3ce7e6739846585e89635a86689b5db42ab2c0c57284", "name": "Random Forest",
          "owner": "79d985e411f93533a0b6d86fceaab45feba1d80b81271012313173a947b3b274", "permissions": "all",
          "storageAddress": "http://127.0.0.1:8001/algo/f2d9fd38e25cd975c49f3ce7e6739846585e89635a86689b5db42ab2c0c57284/file/"}]]

model = [[{"algo": {"hash": "6dcbfcf29146acd19c6a2997b2e81d0cd4e88072eea9c90bbac33f0e8573993f",
                    "name": "Logistic regression",
                    "storageAddress": "http://127.0.0.1:8001/algo/6dcbfcf29146acd19c6a2997b2e81d0cd4e88072eea9c90bbac33f0e8573993f/file/"},
           "challenge": {"hash": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
                         "metrics": {"hash": "750f622262854341bd44f55c1018949e9c119606ef5068bd7d137040a482a756",
                                     "storageAddress": "http://127.0.0.1:8001/challenge/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/metrics/"}},
           "creator": "79d985e411f93533a0b6d86fceaab45feba1d80b81271012313173a947b3b274",
           "endModel": {"hash": "10060f1d9e450d98bb5892190860eee8dd48594f00e0e1c9374a27c5acdba568",
                        "storageAddress": "http://127.0.0.1:8001/model/10060f1d9e450d98bb5892190860eee8dd48594f00e0e1c9374a27c5acdba568/file/"},
           "key": "bcfff3c6afcdd154d879a07dbf7c49025c5d32a193e194c42e3157ce5341c5c4",
           "log": "no error, ah ah ahstill no error, suprah ah ah", "permissions": "all", "startModel": None,
           "status": "done", "testData": {"keys": ["e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1"],
                                          "openerHash": "b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0",
                                          "perf": 0.99,
                                          "worker": "40781e92bb83417d306905dccb5b2d8b03293e319e39c8ff9cc787f75aa7d35b"},
           "trainData": {"keys": ["62fb3263208d62c7235a046ee1d80e25512fe782254b730a9e566276b8c0ef3a",
                                  "42303efa663015e729159833a12ffb510ff92a6e386b8152f90f6fb14ddc94c9"],
                         "openerHash": "ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994", "perf": 0.91,
                         "worker": "79d985e411f93533a0b6d86fceaab45feba1d80b81271012313173a947b3b274"}}, {
              "algo": {"hash": "76fe474d441b03e8416ab37b4950286014fb329e9317126e144342dd0e2ec895",
                       "name": "Neural Network",
                       "storageAddress": "http://127.0.0.1:8001/algo/76fe474d441b03e8416ab37b4950286014fb329e9317126e144342dd0e2ec895/file/"},
              "challenge": {"hash": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
                            "metrics": {"hash": "750f622262854341bd44f55c1018949e9c119606ef5068bd7d137040a482a756",
                                        "storageAddress": "http://127.0.0.1:8001/challenge/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/metrics/"}},
              "creator": "a3119c79a173581425cbe6e06c3034ec396ee805b60d9a34feaa3048beb0e4a9",
              "endModel": {"hash": "30060f1d9e450d98bb5892190860eee8dd48594f00e0e1c9374a27c5acdba568",
                           "storageAddress": "http://127.0.0.1:8001/model/30060f1d9e450d98bb5892190860eee8dd48594f00e0e1c9374a27c5acdba568/file/"},
              "key": "1bb5c8f42315914909c764545ea44e32b04c773468c439c9eb506176670ee6b8",
              "log": "no error, ah ah ahstill no error, suprah ah ah", "permissions": "all",
              "startModel": {"hash": "20060f1d9e450d98bb5892190860eee8dd48594f00e0e1c9374a27c5acdba568",
                             "storageAddress": "http://127.0.0.1:8001/model/20060f1d9e450d98bb5892190860eee8dd48594f00e0e1c9374a27c5acdba568/file/"},
              "status": "done",
              "testData": {"keys": ["4b5152871b181d10ee774c10458c064c70710f4ba35938f10c0b7aa51f7dc010"],
                           "openerHash": "a8b7c235abb9a93742e336bd76ff7cd8ecc49f612e5cf6ea506dc10f4fd6b6f0",
                           "perf": 0.2, "worker": "2d76419f4231cf67bdc53f569201322a4822dff152351fb468db013d484fc762"},
              "trainData": {"keys": ["62fb3263208d62c7235a046ee1d80e25512fe782254b730a9e566276b8c0ef3a",
                                     "42303efa663015e729159833a12ffb510ff92a6e386b8152f90f6fb14ddc94c9"],
                            "openerHash": "ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994",
                            "perf": 0.5, "worker": "a3119c79a173581425cbe6e06c3034ec396ee805b60d9a34feaa3048beb0e4a9"}},
          {"algo": {"hash": "76fe474d441b03e8416ab37b4950286014fb329e9317126e144342dd0e2ec895",
                    "name": "Neural Network",
                    "storageAddress": "http://127.0.0.1:8001/algo/76fe474d441b03e8416ab37b4950286014fb329e9317126e144342dd0e2ec895/file/"},
           "challenge": {"hash": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
                         "metrics": {"hash": "750f622262854341bd44f55c1018949e9c119606ef5068bd7d137040a482a756",
                                     "storageAddress": "http://127.0.0.1:8001/challenge/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/metrics/"}},
           "creator": "a3119c79a173581425cbe6e06c3034ec396ee805b60d9a34feaa3048beb0e4a9",
           "endModel": {"hash": "40060f1d9e450d98bb5892190860eee8dd48594f00e0e1c9374a27c5acdba568",
                        "storageAddress": "http://127.0.0.1:8001/model/40060f1d9e450d98bb5892190860eee8dd48594f00e0e1c9374a27c5acdba568/file/"},
           "key": "2bb5c8f42315914909c764545ea44e32b04c773468c439c9eb506176670ee6b8",
           "log": "no error, ah ah ahstill no error, suprah ah ah", "permissions": "all",
           "startModel": {"hash": "30060f1d9e450d98bb5892190860eee8dd48594f00e0e1c9374a27c5acdba568",
                          "storageAddress": "http://127.0.0.1:8001/model/30060f1d9e450d98bb5892190860eee8dd48594f00e0e1c9374a27c5acdba568/file/"},
           "status": "done", "testData": {"keys": ["4b5152871b181d10ee774c10458c064c70710f4ba35938f10c0b7aa51f7dc010"],
                                          "openerHash": "a8b7c235abb9a93742e336bd76ff7cd8ecc49f612e5cf6ea506dc10f4fd6b6f0",
                                          "perf": 0.35,
                                          "worker": "a3119c79a173581425cbe6e06c3034ec396ee805b60d9a34feaa3048beb0e4a9"},
           "trainData": {"keys": ["62fb3263208d62c7235a046ee1d80e25512fe782254b730a9e566276b8c0ef3a",
                                  "42303efa663015e729159833a12ffb510ff92a6e386b8152f90f6fb14ddc94c9"],
                         "openerHash": "ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994", "perf": 0.7,
                         "worker": "a3119c79a173581425cbe6e06c3034ec396ee805b60d9a34feaa3048beb0e4a9"}}, {
              "algo": {"hash": "76fe474d441b03e8416ab37b4950286014fb329e9317126e144342dd0e2ec895",
                       "name": "Neural Network",
                       "storageAddress": "http://127.0.0.1:8001/algo/76fe474d441b03e8416ab37b4950286014fb329e9317126e144342dd0e2ec895/file/"},
              "challenge": {"hash": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
                            "metrics": {"hash": "750f622262854341bd44f55c1018949e9c119606ef5068bd7d137040a482a756",
                                        "storageAddress": "http://127.0.0.1:8001/challenge/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/metrics/"}},
              "creator": "a3119c79a173581425cbe6e06c3034ec396ee805b60d9a34feaa3048beb0e4a9",
              "endModel": {"hash": "50060f1d9e450d98bb5892190860eee8dd48594f00e0e1c9374a27c5acdba568",
                           "storageAddress": "http://127.0.0.1:8001/model/50060f1d9e450d98bb5892190860eee8dd48594f00e0e1c9374a27c5acdba568/file/"},
              "key": "3bb5c8f42315914909c764545ea44e32b04c773468c439c9eb506176670ee6b8",
              "log": "no error, ah ah ahstill no error, suprah ah ah", "permissions": "all",
              "startModel": {"hash": "40060f1d9e450d98bb5892190860eee8dd48594f00e0e1c9374a27c5acdba568",
                             "storageAddress": "http://127.0.0.1:8001/model/40060f1d9e450d98bb5892190860eee8dd48594f00e0e1c9374a27c5acdba568/file/"},
              "status": "done",
              "testData": {"keys": ["4b5152871b181d10ee774c10458c064c70710f4ba35938f10c0b7aa51f7dc010"],
                           "openerHash": "a8b7c235abb9a93742e336bd76ff7cd8ecc49f612e5cf6ea506dc10f4fd6b6f0",
                           "perf": 0.79, "worker": "a3119c79a173581425cbe6e06c3034ec396ee805b60d9a34feaa3048beb0e4a9"},
              "trainData": {"keys": ["62fb3263208d62c7235a046ee1d80e25512fe782254b730a9e566276b8c0ef3a",
                                     "42303efa663015e729159833a12ffb510ff92a6e386b8152f90f6fb14ddc94c9"],
                            "openerHash": "ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994",
                            "perf": 0.79,
                            "worker": "a3119c79a173581425cbe6e06c3034ec396ee805b60d9a34feaa3048beb0e4a9"}}, {
              "algo": {"hash": "56a0e2f7e046ee948cf2ab38136f7b5ff131d0c538f8d75a97850d6fc06131df",
                       "name": "Random Forest",
                       "storageAddress": "http://127.0.0.1:8001/56a0e2f7e046ee948cf2ab38136f7b5ff131d0c538f8d75a97850d6fc06131df/file/"},
              "challenge": {"hash": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
                            "metrics": {"hash": "750f622262854341bd44f55c1018949e9c119606ef5068bd7d137040a482a756",
                                        "storageAddress": "http://127.0.0.1:8001/challenge/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/metrics/"}},
              "creator": "a3119c79a173581425cbe6e06c3034ec396ee805b60d9a34feaa3048beb0e4a9",
              "endModel": {"hash": "70060f1d9e450d98bb5892190860eee8dd48594f00e0e1c9374a27c5acdba568",
                           "storageAddress": "http://127.0.0.1:8001/model/70060f1d9e450d98bb5892190860eee8dd48594f00e0e1c9374a27c5acdba568/file/"},
              "key": "4bb5c8f42315914909c764545ea44e32b04c773468c439c9eb506176670ee6b8",
              "log": "no error, ah ah ahstill no error, suprah ah ah", "permissions": "all",
              "startModel": {"hash": "60060f1d9e450d98bb5892190860eee8dd48594f00e0e1c9374a27c5acdba568",
                             "storageAddress": "http://127.0.0.1:8001/model/60060f1d9e450d98bb5892190860eee8dd48594f00e0e1c9374a27c5acdba568/file/"},
              "status": "done",
              "testData": {"keys": ["4b5152871b181d10ee774c10458c064c70710f4ba35938f10c0b7aa51f7dc010"],
                           "openerHash": "a8b7c235abb9a93742e336bd76ff7cd8ecc49f612e5cf6ea506dc10f4fd6b6f0",
                           "perf": 0.12, "worker": "a3119c79a173581425cbe6e06c3034ec396ee805b60d9a34feaa3048beb0e4a9"},
              "trainData": {"keys": ["62fb3263208d62c7235a046ee1d80e25512fe782254b730a9e566276b8c0ef3a",
                                     "42303efa663015e729159833a12ffb510ff92a6e386b8152f90f6fb14ddc94c9"],
                            "openerHash": "ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994",
                            "perf": 0.79,
                            "worker": "a3119c79a173581425cbe6e06c3034ec396ee805b60d9a34feaa3048beb0e4a9"}}, {
              "algo": {"hash": "56a0e2f7e046ee948cf2ab38136f7b5ff131d0c538f8d75a97850d6fc06131df",
                       "name": "Random Forest",
                       "storageAddress": "http://127.0.0.1:8001/algo/56a0e2f7e046ee948cf2ab38136f7b5ff131d0c538f8d75a97850d6fc06131df/file/"},
              "challenge": {"hash": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
                            "metrics": {"hash": "750f622262854341bd44f55c1018949e9c119606ef5068bd7d137040a482a756",
                                        "storageAddress": "http://127.0.0.1:8001/challenge/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/metrics/"}},
              "creator": "a3119c79a173581425cbe6e06c3034ec396ee805b60d9a34feaa3048beb0e4a9",
              "endModel": {"hash": "80060f1d9e450d98bb5892190860eee8dd48594f00e0e1c9374a27c5acdba568",
                           "storageAddress": "http://127.0.0.1:8001/model/80060f1d9e450d98bb5892190860eee8dd48594f00e0e1c9374a27c5acdba568/file/"},
              "key": "5bb5c8f42315914909c764545ea44e32b04c773468c439c9eb506176670ee6b8",
              "log": "no error, ah ah ahstill no error, suprah ah ah", "permissions": "all",
              "startModel": {"hash": "70060f1d9e450d98bb5892190860eee8dd48594f00e0e1c9374a27c5acdba568",
                             "storageAddress": "http://127.0.0.1:8001/model/70060f1d9e450d98bb5892190860eee8dd48594f00e0e1c9374a27c5acdba568/file/"},
              "status": "done",
              "testData": {"keys": ["4b5152871b181d10ee774c10458c064c70710f4ba35938f10c0b7aa51f7dc010"],
                           "openerHash": "a8b7c235abb9a93742e336bd76ff7cd8ecc49f612e5cf6ea506dc10f4fd6b6f0",
                           "perf": 0.66, "worker": "a3119c79a173581425cbe6e06c3034ec396ee805b60d9a34feaa3048beb0e4a9"},
              "trainData": {"keys": ["62fb3263208d62c7235a046ee1d80e25512fe782254b730a9e566276b8c0ef3a",
                                     "42303efa663015e729159833a12ffb510ff92a6e386b8152f90f6fb14ddc94c9"],
                            "openerHash": "ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994",
                            "perf": 0.79,
                            "worker": "a3119c79a173581425cbe6e06c3034ec396ee805b60d9a34feaa3048beb0e4a9"}}]]

traintuple = [{"algo": {"hash": "6dcbfcf29146acd19c6a2997b2e81d0cd4e88072eea9c90bbac33f0e8573993f",
                        "name": "Logistic regression",
                        "storageAddress": "http://127.0.0.1:8001/algo/6dcbfcf29146acd19c6a2997b2e81d0cd4e88072eea9c90bbac33f0e8573993f/file/"},
               "challenge": {"hash": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
                             "metrics": {"hash": "750f622262854341bd44f55c1018949e9c119606ef5068bd7d137040a482a756",
                                         "storageAddress": "http://127.0.0.1:8001/challenge/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/metrics/"}},
               "creator": "79d985e411f93533a0b6d86fceaab45feba1d80b81271012313173a947b3b274",
               "endModel": {"hash": "10060f1d9e450d98bb5892190860eee8dd48594f00e0e1c9374a27c5acdba568",
                            "storageAddress": "http://127.0.0.1:8001/model/10060f1d9e450d98bb5892190860eee8dd48594f00e0e1c9374a27c5acdba568/file/"},
               "key": "bcfff3c6afcdd154d879a07dbf7c49025c5d32a193e194c42e3157ce5341c5c4",
               "log": "no error, ah ah ahstill no error, suprah ah ah", "permissions": "all", "startModel": None,
               "status": "done",
               "testData": {"keys": ["e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1"],
                            "openerHash": "b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0",
                            "perf": 0.99, "worker": "40781e92bb83417d306905dccb5b2d8b03293e319e39c8ff9cc787f75aa7d35b"},
               "trainData": {"keys": ["62fb3263208d62c7235a046ee1d80e25512fe782254b730a9e566276b8c0ef3a",
                                      "42303efa663015e729159833a12ffb510ff92a6e386b8152f90f6fb14ddc94c9"],
                             "openerHash": "ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994",
                             "perf": 0.91,
                             "worker": "79d985e411f93533a0b6d86fceaab45feba1d80b81271012313173a947b3b274"}}]


class TestList(TestCase):

    def test_list_challenge(self):
        output = popen(['substra', 'list', 'challenge'], stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')

        self.assertTrue(res == json.dumps(challenge))

    def test_list_dataset(self):
        output = popen(['substra', 'list', 'dataset'], stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')

        self.assertTrue(res == json.dumps(dataset))

    def test_list_data(self):
        output = popen(['substra', 'list', 'data'], stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')

        self.assertTrue(res == json.dumps(data))

    def test_list_algo(self):
        output = popen(['substra', 'list', 'algo'], stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')

        self.assertTrue(res == json.dumps(algo))

    def test_list_model(self):
        output = popen(['substra', 'list', 'model'], stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')

        self.assertTrue(res == json.dumps(model))

    def test_list_traintuple(self):
        output = popen(['substra', 'list', 'traintuple'], stdout=PIPE).communicate()[0]
        res = output.decode('utf-8')

        self.assertTrue(res == json.dumps(traintuple))
