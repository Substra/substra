# Copyright 2018 Owkin, inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

OBJECTIVE = {
    "description": {
        "hash": "7a90514f88c70002608a9868681dd1589ea598e78d00a8cd7783c3ea0f9ceb09",
        "storageAddress": "",
    },
    "key": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
    "metrics": {
        "hash": "750f622262854341bd44f55c1018949e9c119606ef5068bd7d137040a482a756",
        "name": "macro-average recall",
        "storageAddress": "",
    },
    "name": "Skin Lesion Classification Challenge",
    "owner": "c657699f8b03c19e6eadc7b474c23f26dd83454395266a673406f2cf44de2ca2",
    "permissions": {
        "process": {
            "public": False,
            "authorizedIDs": []
        }
    },
    "testDataset": {
        "dataManagerKey": "ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994",
        "dataSampleKeys": [
            "e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1",
        ]
    }
}

DATASET = {
    "objectiveKey": "7a90514f88c70002608a9868681dd1589ea598e78d00a8cd7783c3ea0f9ceb09",
    "description": {
        "hash": "7a90514f88c70002608a9868681dd1589ea598e78d00a8cd7783c3ea0f9ceb09",
        "storageAddress": "",
    },
    "key": "ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994",
    "name": "ISIC 2018",
    "opener": {
        "hash": "7a90514f88c70002608a9868681dd1589ea598e78d00a8cd7783c3ea0f9ceb09",
        "storageAddress": "",
    },
    "owner": "c657699f8b03c19e6eadc7b474c23f26dd83454395266a673406f2cf44de2ca2",
    "permissions": {
        "process": {
            "public": False,
            "authorizedIDs": []
        }
    },
    "size": 100,
    "type": "Images",
    "trainDataSampleKeys": [],
    "testDataSampleKeys": [],
}

ALGO = {
    "key": "7c9f9799bf64c10002381583a9ffc535bc3f4bf14d6f0c614d3f6f868f72a9d5",
    "name": "Logistic regression",
    "content": {
      "hash": "7c9f9799bf64c10002381583a9ffc535bc3f4bf14d6f0c614d3f6f868f72a9d5",
      "storageAddress": ""
    },
    "description": {
      "hash": "124a0425b746d7072282d167b53cb6aab3a31bf1946dae89135c15b0126ebec3",
      "storageAddress": ""
    },
    "owner": "ab75010bacbd1a4b826dc2e9ead6f1e4e1c4feade2d62a8b708fdde48fb0edea",
    "permissions": {
        "process": {
            "public": False,
            "authorizedIDs": []
        }
    },
    "pkhash": "7c9f9799bf64c10002381583a9ffc535bc3f4bf14d6f0c614d3f6f868f72a9d5"
}

AGGREGATE_ALGO = {
    "key": "7c9f9799bf64c10062381583a9ffc535bc3f4bf14d6f0c614d3f6f868f72a9d5",
    "name": "Logistic regression",
    "content": {
      "hash": "7c9f9799bf64c10002381583a9ffc535bc3f4bf14d6g0c614d3f6f868f72a9d5",
      "storageAddress": ""
    },
    "description": {
      "hash": "124a0725b746d7072282d167b53cb6aab3a31bf1946dae89135c15b0126ebec3",
      "storageAddress": ""
    },
    "owner": "ab75010bacbd1a4b826dc2e9ead6f1e4e1c4feade2d62a8b708fdde48fb0edeb",
    "permissions": {
        "process": {
            "public": False,
            "authorizedIDs": []
        }
    },
    "pkhash": "7c9t9799bf64c10002381583a9ffc535bc3f4bf14d6f0c614d3f6f868f72a9d5"
}

COMPOSITE_ALGO = {
    "key": "7c9f9799bf64c1000238b583a9ffc535bc3f4bf14d6f0c614d3f6f868f72a9d5",
    "name": "Logistic regression",
    "content": {
      "hash": "7c9f9799bf64c10002381b83a9ffc535bc3f4bf14d6f0c614d3f6f868f72a9d5",
      "storageAddress": ""
    },
    "description": {
      "hash": "124a0425b746d7b72282d167b53cb6aab3a31bf1946dae89135c15b0126ebec3",
      "storageAddress": ""
    },
    "owner": "ab75010bacbd1a4b826dc2e9ead6f1e4e1c4beade2d62a8b708fdde48fb0edea",
    "permissions_public": False,
    "permissions_authorized_ids": [],
    "pkhash": "7c9f9br9bf64c10002381583a9ffc535bc3f4bf14d6f0c614d3f6f868f72a9d5"
}

TRAINTUPLE = {
    "key": "06207faf17854fa9422099a50dcee064753d6c3425a077f097e91622f3199be5",
    "algo": {
        "name": "Neural Network",
        "hash": "0acc5180e09b6a6ac250f4e3c172e2893f617aa1c22ef1f379019d20fe44142f",
        "storageAddress": ""
    },
    "creator": "e75db4df2532dc1313ebb5c2462e1eb813b94c3e67de29f6e4b2272ae60385f5",
    "dataset": {
        "worker": "e75db4df2532dc1313ebb5c2462e1eb813b94c3e67de29f6e4b2272ae60385f5",
        "keys": [
            "31510dc1d8be788f7c5d28d05714f7efb9edb667762966b9adc02eadeaacebe9",
            "03a1f878768ea8624942d46a3b438c37992e626c2cf655023bcc3bed69d485d1"
        ],
        "openerHash": "8dd01465003a9b1e01c99c904d86aa518b3a5dd9dc8d40fe7d075c726ac073ca",
        "perf": 0
    },
    "computePlanID": "",
    "inModels": None,
    "log": "[00-01-0032-d415995]",
    "objective": {
        "hash": "3d70ab46d710dacb0f48cb42db4874fac14e048a0d415e266aad38c09591ee71",
        "metrics": {
            "hash": "c42dca31fbc2ebb5705643e3bb6ee666bbfd956de13dd03727f825ad8445b4d7",
            "storageAddress": ""
        }
    },
    "outModel": None,
    "permissions": {
        "process": {
            "public": False,
            "authorizedIDs": []
        }
    },
    "rank": 0,
    "status": "failed",
    "tag": "My super tag"
}

AGGREGATETUPLE = {
    "key": "06207faf17854fa9422099a50dcfe064753d6c3425a077f097e91622f3199be5",
    "algo": {
        "name": "Neural Network",
        "hash": "0acc5180e09b6a6ac250f4f3c172e2893f617aa1c22ef1f379019d20fe44142f",
        "storageAddress": ""
    },
    "creator": "e75db4df2532dc1313ebb5c2462f1eb813b94c3e67de29f6e4b2272ae60385f5",
    "dataset": {
        "worker": "e75db4df2532dc1313ebb5c2f62e1eb813b94c3e67de29f6e4b2272ae60385f5",
        "keys": [
            "31510dc1d8be788f7c5d28d05714f7efbfedb667762966b9adc02eadeaacebe9",
            "03a1f878768ea8624942d46a3b438c379f2e626c2cf655023bcc3bed69d485d1"
        ],
        "openerHash": "8dd01465003a9b1e01c99c904d86aa518b3afdd9dc8d40fe7d075c726ac073ca",
        "perf": 0
    },
    "computePlanID": "",
    "inModels": None,
    "log": "[00-01-0032-d415995]",
    "objective": {
        "hash": "3d70ab46d710dacb0f48cb42db4874fac14e048afd415e266aad38c09591ee71",
        "metrics": {
            "hash": "c42dca31fbc2ebb5705643e3bb6ee666bbfdf56de13dd03727f825ad8445b4d7",
            "storageAddress": ""
        }
    },
    "outModel": None,
    "permissions": {
        "process": {
            "public": False,
            "authorizedIDs": []
        }
    },
    "rank": 0,
    "status": "failed",
    "tag": "My super tag"
}

COMPOSITE_TRAINTUPLE = {
    "key": "06207faf17854fa9422099a50dcee064753d6c3425a077f097e91622f3199be5",
    "algo": {
        "name": "Neural Network",
        "hash": "0acc5180e09b6a6ac250f4e3c172e2893f617aa1c22ef1f379019d20fe44142f",
        "storageAddress": ""
    },
    "inHeadModel": {
        "key": "0acc5180e09b6a6ac250f4e3d972e2893f617aa1c22ef1f379019d20fe44142e",
    },
    "inTrunkModel": {
        "key": "0acc5180e09b6a6ac250f4e3d972e2893f617aa1c22ef1f379019d20fe44142f",
    },
    "creator": "e75db4df2532dc1313ebb5c2462e1eb813b94c3e67de29f6e4b2272ae60385f5",
    "dataset": {
        "worker": "e75db4df2532dc1313ebb5c2462e1eb813b94c3e67de29f6e4b2272ae60385f5",
        "keys": [
            "31510dc1d8be788f7c5d28d05714f7efb9edb667762966b9adc02eadeaacebe9",
            "03a1f878768ea8624942d46a3b438c37992e626c2cf655023bcc3bed69d485d1"
        ],
        "openerHash": "8dd01465003a9b1e01c99c904d86aa518b3a5dd9dc8d40fe7d075c726ac073ca",
        "perf": 0
    },
    "computePlanID": "",
    "log": "[00-01-0032-d415995]",
    "objective": {
        "hash": "3d70ab46d710dacb0f48cb42db4874fac14e048a0d415e266aad38c09591ee71",
        "metrics": {
            "hash": "c42dca31fbc2ebb5705643e3bb6ee666bbfd956de13dd03727f825ad8445b4d7",
            "storageAddress": ""
        }
    },
    "outHeadModel": {
        "permissions": {},
        "outModel": {
            "hash": "8a90514f88c70002608a9868681dd1589ea598e78d00a8cd7783c3ea0f9ceb09",
        }
    },
    "outTrunkModel": {
        "permissions": {},
        "outModel": {
            "hash": "9a90514f88c70002608a9868681dd1589ea598e78d00a8cd7783c3ea0f9ceb09",
        }
    },
    "rank": 0,
    "status": "failed",
    "tag": "My super tag"
}

TESTTUPLE = {
    "key": "97b53511e94cab17ea8b1c31982e0b0d8b9311e10d35f82bdafab4ea429b7414",
    "algo": {
        "name": "Logistic regression",
        "hash": "7c9f9799bf64c10002381583a9ffc535bc3f4bf14d6f0c614d3f6f868f72a9d5",
        "storageAddress": "",
    },
    "certified": True,
    "creator": "e75db4df2532dc1313ebb5c2462e1eb813b94c3e67de29f6e4b2272ae60385f5",
    "dataset": {
        "worker": "ab75010bacbd1a4b826dc2e9ead6f1e4e1c4feade2d62a8b708fdde48fb0edea",
        "keys": [
            "17d58b67ae2028018108c9bf555fa58b2ddcfe560e0117294196e79d26140b2a",
            "8bf3bf4f753a32f27d18c86405e7a406a83a55610d91abcca9acc525061b8ecf"
        ],
        "openerHash": "ce9f292c72e9b82697445117f9c2d1d18ce0f8ed07ff91dadb17d668bddf8932",
        "perf": 0
    },
    "log": "Test - CPU:90.07 % - Mem:0.13 GB - GPU:0.00 % - GPU Mem:0.00 GB;",
    "model": {
        "traintupleKey": "593b8c8a94cf5d372f239c79ac2a4089f7ba4717cda8dc4753599a078e86493d",
        "hash": "523882e8aaa3fd65bfd5f4bd0153ad6a21487f55c50b922bbf26015c6e975965",
        "storageAddress": "",
    },
    "objective": {
        "hash": "3d70ab46d710dacb0f48cb42db4874fac14e048a0d415e266aad38c09591ee71",
        "metrics": {
            "hash": "c42dca31fbc2ebb5705643e3bb6ee666bbfd956de13dd03727f825ad8445b4d7",
            "storageAddress": "",
          }
    },
    "permissions": {
        "process": {
            "public": False,
            "authorizedIDs": []
        }
    },
    "status": "done",
    "tag": ""
}

LEADERBOARD = {
    "objective": {
        "key": "c6a6139a28b5936c1086a49d7c772734f4ad65f4580ca4ab14029a925847faf3",
        "name": "data-network - Objective 1",
        "description": {
            "hash": "c6a6139a28b5936c1086a49d7c772734f4ad65f4580ca4ab14029a925847faf3",
            "storageAddress": ""
        },
        "metrics": {
            "name": "test metrics",
            "hash": "48e748a15552ea2a8a258f6e8e75b1d67da5d6ca7471f80f9b69dae3cb950335",
            "storageAddress": ""
        },
        "owner": "MyOrg2MSP",
        "testDataset": {
            "dataManagerKey": "c0230e3ab5b92e50fe3c166471e754e393d4a802a48086fc93dd6a1ea38a2441",
            "dataSampleKeys": [
                "d2e599efe1288a8646b99330eb50f38593be33d3cb144aabb4058272ec263c93"
            ],
            "worker": ""
        },
        "permissions": {
            "process": {
                "public": True,
                "authorizedIDs": []
            }
        }
    },
    "testtuples": []
}

NODES = [
    {'id': 'foo', 'isCurrent': False},
    {'id': 'bar', 'isCurrent': True},
]

COMPUTE_PLAN = {
    "computePlanID": "e983a1855368bd0a0190183af9a8e560580d1fc8d86c84268fd55c1910114ca3",
    "traintupleKeys": [
        "1197bbfc4a189ea037a6835895a81bb80db37f52f82cc40d74e285b7194f4c91"
    ],
    "aggregatetupleKeys": None,
    "compositeTraintupleKeys": None,
    "testtupleKeys": [
        "6c94a1df7af13ebd176b05ae9686489fe563122fee7bca4d35ed9b606f96180c"
    ],
    "tag": "",
    "status": "done",
    "tupleCount": 2,
    "doneCount": 2,
    "IDToKey": {
        "62378ca1b5c84e73a3d588adab7e20b2":
        "1197bbfc4a189ea037a6835895a81bb80db37f52f82cc40d74e285b7194f4c91",
    }
}
