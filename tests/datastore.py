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
        "storage_address": "",
    },
    "key": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
    "metrics": {
        "hash": "750f622262854341bd44f55c1018949e9c119606ef5068bd7d137040a482a756",
        "name": "macro-average recall",
        "storage_address": "",
    },
    "name": "Skin Lesion Classification Challenge",
    "owner": "c657699f8b03c19e6eadc7b474c23f26dd83454395266a673406f2cf44de2ca2",
    "permissions": {
        "process": {
            "public": False,
            "authorized_ids": []
        }
    },
    "test_dataset": {
        "data_manager_key": "ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994",
        "data_sample_keys": [
            "e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1",
        ],
        "metadata": {},
    },
    "metadata": {
        "foo": "bar"
    }
}

DATASET = {
    "objective_key": "7a90514f88c70002608a9868681dd1589ea598e78d00a8cd7783c3ea0f9ceb09",
    "description": {
        "hash": "7a90514f88c70002608a9868681dd1589ea598e78d00a8cd7783c3ea0f9ceb09",
        "storage_address": "",
    },
    "key": "ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994",
    "name": "ISIC 2018",
    "opener": {
        "hash": "7a90514f88c70002608a9868681dd1589ea598e78d00a8cd7783c3ea0f9ceb09",
        "storage_address": "",
    },
    "owner": "c657699f8b03c19e6eadc7b474c23f26dd83454395266a673406f2cf44de2ca2",
    "permissions": {
        "process": {
            "public": False,
            "authorized_ids": []
        }
    },
    # "size": 100,
    "type": "Images",
    "train_data_sample_keys": [],
    "test_data_sample_keys": [],
    "metadata": {
        "foo": "bar"
    }
}

ALGO = {
    "key": "7c9f9799bf64c10002381583a9ffc535bc3f4bf14d6f0c614d3f6f868f72a9d5",
    "name": "Logistic regression",
    "content": {
        "hash": "7c9f9799bf64c10002381583a9ffc535bc3f4bf14d6f0c614d3f6f868f72a9d5",
        "storage_address": ""
    },
    "description": {
        "hash": "124a0425b746d7072282d167b53cb6aab3a31bf1946dae89135c15b0126ebec3",
        "storage_address": ""
    },
    "owner": "ab75010bacbd1a4b826dc2e9ead6f1e4e1c4feade2d62a8b708fdde48fb0edea",
    "permissions": {
        "process": {
            "public": False,
            "authorized_ids": []
        }
    },
    "key": "7c9f9799bf64c10002381583a9ffc535bc3f4bf14d6f0c614d3f6f868f72a9d5",
    "metadata": {
        "foo": "bar"
    }
}

AGGREGATE_ALGO = {
    "key": "7c9f9799bf64c10062381583a9ffc535bc3f4bf14d6f0c614d3f6f868f72a9d5",
    "name": "Logistic regression",
    "content": {
        "hash": "7c9f9799bf64c10002381583a9ffc535bc3f4bf14d6g0c614d3f6f868f72a9d5",
        "storage_address": ""
    },
    "description": {
        "hash": "124a0725b746d7072282d167b53cb6aab3a31bf1946dae89135c15b0126ebec3",
        "storage_address": ""
    },
    "owner": "ab75010bacbd1a4b826dc2e9ead6f1e4e1c4feade2d62a8b708fdde48fb0edeb",
    "permissions": {
        "process": {
            "public": False,
            "authorized_ids": []
        }
    },
    "metadata": {
        "foo": "bar"
    }
}

COMPOSITE_ALGO = {
    "key": "7c9f9799bf64c1000238b583a9ffc535bc3f4bf14d6f0c614d3f6f868f72a9d5",
    "name": "Logistic regression",
    "content": {
        "hash": "7c9f9799bf64c10002381b83a9ffc535bc3f4bf14d6f0c614d3f6f868f72a9d5",
        "storage_address": ""
    },
    "description": {
        "hash": "124a0425b746d7b72282d167b53cb6aab3a31bf1946dae89135c15b0126ebec3",
        "storage_address": ""
    },
    "owner": "ab75010bacbd1a4b826dc2e9ead6f1e4e1c4beade2d62a8b708fdde48fb0edea",
    "permissions": {
        "process": {
            "public": False,
            "authorized_ids": [],
        },
    },
    "metadata": {
        "foo": "bar"
    }
}

TRAINTUPLE = {
    "key": "06207faf17854fa9422099a50dcee064753d6c3425a077f097e91622f3199be5",
    "algo": {
        "name": "Neural Network",
        "hash": "0acc5180e09b6a6ac250f4e3c172e2893f617aa1c22ef1f379019d20fe44142f",
        "storage_address": ""
    },
    "creator": "e75db4df2532dc1313ebb5c2462e1eb813b94c3e67de29f6e4b2272ae60385f5",
    "dataset": {
        "key": "8dd01465-003a-9b1e-01c9-9c904d86aa51",
        "worker": "e75db4df2532dc1313ebb5c2462e1eb813b94c3e67de29f6e4b2272ae60385f5",
        "keys": [
            "31510dc1d8be788f7c5d28d05714f7efb9edb667762966b9adc02eadeaacebe9",
            "03a1f878768ea8624942d46a3b438c37992e626c2cf655023bcc3bed69d485d1"
        ],
        "opener_hash": "8dd01465003a9b1e01c99c904d86aa518b3a5dd9dc8d40fe7d075c726ac073ca",
    },
    "compute_plan_id": "",
    "in_models": None,
    "log": "[00-01-0032-d415995]",
    "out_model": None,
    "permissions": {
        "process": {
            "public": False,
            "authorized_ids": []
        }
    },
    "rank": 0,
    "status": "failed",
    "tag": "My super tag",
    "metadata": {
        "foo": "bar"
    }
}

AGGREGATETUPLE = {
    "key": "06207faf17854fa9422099a50dcfe064753d6c3425a077f097e91622f3199be5",
    "algo": {
        "name": "Neural Network",
        "hash": "0acc5180e09b6a6ac250f4f3c172e2893f617aa1c22ef1f379019d20fe44142f",
        "storage_address": ""
    },
    "creator": "e75db4df2532dc1313ebb5c2462f1eb813b94c3e67de29f6e4b2272ae60385f5",
    "compute_plan_id": "",
    "in_models": [],
    "log": "[00-01-0032-d415995]",
    "out_model": None,
    "permissions": {
        "process": {
            "public": False,
            "authorized_ids": []
        }
    },
    "rank": 0,
    "status": "failed",
    "tag": "My super tag",
    "metadata": {
        "foo": "bar"
    },
    "worker": ""
}

COMPOSITE_TRAINTUPLE = {
    "key": "06207faf17854fa9422099a50dcee064753d6c3425a077f097e91622f3199be5",
    "algo": {
        "name": "Neural Network",
        "hash": "0acc5180e09b6a6ac250f4e3c172e2893f617aa1c22ef1f379019d20fe44142f",
        "storage_address": ""
    },
    "in_head_model": {
        "hash": "0acc5180e09b6a6ac250f4e3d972e2893f617aa1c22ef1f379019d20fe44142e",
    },
    "in_trunk_model": {
        "hash": "0acc5180e09b6a6ac250f4e3d972e2893f617aa1c22ef1f379019d20fe44142f",
        "storage_address": ""
    },
    "creator": "e75db4df2532dc1313ebb5c2462e1eb813b94c3e67de29f6e4b2272ae60385f5",
    "dataset": {
        "key": "8dd01465-003a-9b1e-01c9-9c904d86aa51",
        "worker": "e75db4df2532dc1313ebb5c2462e1eb813b94c3e67de29f6e4b2272ae60385f5",
        "keys": [
            "31510dc1d8be788f7c5d28d05714f7efb9edb667762966b9adc02eadeaacebe9",
            "03a1f878768ea8624942d46a3b438c37992e626c2cf655023bcc3bed69d485d1"
        ],
        "opener_hash": "8dd01465003a9b1e01c99c904d86aa518b3a5dd9dc8d40fe7d075c726ac073ca",
    },
    "compute_plan_id": "",
    "log": "[00-01-0032-d415995]",
    "out_head_model": {
        "permissions": {
            "process": {
                "public": False,
                "authorized_ids": []
            }
        },
        "out_model": {
            "hash": "8a90514f88c70002608a9868681dd1589ea598e78d00a8cd7783c3ea0f9ceb09",
        }
    },
    "out_trunk_model": {
        "permissions": {
            "process": {
                "public": False,
                "authorized_ids": []
            }
        },
        "out_model": {
            "hash": "9a90514f88c70002608a9868681dd1589ea598e78d00a8cd7783c3ea0f9ceb09",
            "storage_address": ""
        }
    },
    "rank": 0,
    "status": "failed",
    "tag": "My super tag",
    "metadata": {
        "foo": "bar"
    }
}

TESTTUPLE = {
    "key": "97b53511e94cab17ea8b1c31982e0b0d8b9311e10d35f82bdafab4ea429b7414",
    "traintuple_key": "1197bbfc4a189ea037a6835895a81bb80db37f52f82cc40d74e285b7194f4c91",
    "traintuple_type": "traintuple",
    "compute_plan_id": "",
    "rank": 0,
    "algo": {
        "name": "Logistic regression",
        "hash": "7c9f9799bf64c10002381583a9ffc535bc3f4bf14d6f0c614d3f6f868f72a9d5",
        "storage_address": "",
    },
    "certified": True,
    "creator": "e75db4df2532dc1313ebb5c2462e1eb813b94c3e67de29f6e4b2272ae60385f5",
    "dataset": {
        "key": "ce9f292c-72e9-b826-9744-5117f9c2d1d1",
        "worker": "ab75010bacbd1a4b826dc2e9ead6f1e4e1c4feade2d62a8b708fdde48fb0edea",
        "keys": [
            "17d58b67ae2028018108c9bf555fa58b2ddcfe560e0117294196e79d26140b2a",
            "8bf3bf4f753a32f27d18c86405e7a406a83a55610d91abcca9acc525061b8ecf"
        ],
        "opener_hash": "ce9f292c72e9b82697445117f9c2d1d18ce0f8ed07ff91dadb17d668bddf8932",
        "perf": 0
    },
    "log": "Test - CPU:90.07 % - Mem:0.13 GB - GPU:0.00 % - GPU Mem:0.00 GB;",
    "objective": {
        "hash": "3d70ab46d710dacb0f48cb42db4874fac14e048a0d415e266aad38c09591ee71",
        "metrics": {
            "hash": "c42dca31fbc2ebb5705643e3bb6ee666bbfd956de13dd03727f825ad8445b4d7",
            "storage_address": "",
        }
    },
    "status": "done",
    "tag": "",
    "metadata": {
        "foo": "bar"
    }
}

LEADERBOARD = {
    "objective": {
        "key": "c6a6139a28b5936c1086a49d7c772734f4ad65f4580ca4ab14029a925847faf3",
        "name": "data-network - Objective 1",
        "description": {
            "hash": "c6a6139a28b5936c1086a49d7c772734f4ad65f4580ca4ab14029a925847faf3",
            "storage_address": ""
        },
        "metrics": {
            "name": "test metrics",
            "hash": "48e748a15552ea2a8a258f6e8e75b1d67da5d6ca7471f80f9b69dae3cb950335",
            "storage_address": ""
        },
        "owner": "MyOrg2MSP",
        "test_dataset": {
            "data_manager_key": "c0230e3ab5b92e50fe3c166471e754e393d4a802a48086fc93dd6a1ea38a2441",
            "data_sample_keys": [
                "d2e599efe1288a8646b99330eb50f38593be33d3cb144aabb4058272ec263c93"
            ],
            "worker": ""
        },
        "permissions": {
            "process": {
                "public": True,
                "authorized_ids": []
            }
        }
    },
    "testtuples": []
}

NODES = [
    {'id': 'foo', 'is_current': False},
    {'id': 'bar', 'is_current': True},
]

COMPUTE_PLAN = {
    "compute_plan_id": "e983a1855368bd0a0190183af9a8e560580d1fc8d86c84268fd55c1910114ca3",
    "traintuple_keys": [
        "1197bbfc4a189ea037a6835895a81bb80db37f52f82cc40d74e285b7194f4c91"
    ],
    "aggregatetuple_keys": None,
    "composite_traintuple_keys": None,
    "testtuple_keys": [
        "6c94a1df7af13ebd176b05ae9686489fe563122fee7bca4d35ed9b606f96180c"
    ],
    "tag": "",
    "status": "done",
    "tuple_count": 2,
    "done_count": 2,
    "id_to_key": {
        "62378ca1b5c84e73a3d588adab7e20b2":
        "1197bbfc4a189ea037a6835895a81bb80db37f52f82cc40d74e285b7194f4c91",
    },
    "metadata": {
        "foo": "bar"
    }
}
