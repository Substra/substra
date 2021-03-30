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
        "checksum": "7a90514f88c70002608a9868681dd1589ea598e78d00a8cd7783c3ea0f9ceb09",
        "storage_address": "",
    },
    "key": "d5002e1c-d50b-d5de-5341-df8a7b7d11b6",
    "metrics": {
        "checksum": "750f622262854341bd44f55c1018949e9c119606ef5068bd7d137040a482a756",
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
        "data_manager_key": "ccbaa337-2bc7-4bce-39ce-3b138f558b3a",
        "data_sample_keys": [
            "e11aeec2-9074-9e4c-50c9-1305e10463ec",
        ],
        "metadata": {},
        "worker": "TEST_WORKER",
    },
    "metadata": {
        "foo": "bar"
    }
}

DATASET = {
    "objective_key": "7a90514f-88c7-0002-608a-9868681dd158",
    "description": {
        "checksum": "7a90514f88c70002608a9868681dd1589ea598e78d00a8cd7783c3ea0f9ceb09",
        "storage_address": "",
    },
    "key": "ccbaa337-2bc7-4bce-39ce-3b138f558b3a",
    "name": "ISIC 2018",
    "opener": {
        "checksum": "7a90514f88c70002608a9868681dd1589ea598e78d00a8cd7783c3ea0f9ceb09",
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
    "key": "7c9f9799-bf64-c100-0238-1583a9ffc535",
    "name": "Logistic regression",
    "content": {
        "checksum": "7c9f9799bf64c10002381583a9ffc535bc3f4bf14d6f0c614d3f6f868f72a9d5",
        "storage_address": ""
    },
    "description": {
        "checksum": "124a0425b746d7072282d167b53cb6aab3a31bf1946dae89135c15b0126ebec3",
        "storage_address": ""
    },
    "owner": "ab75010bacbd1a4b826dc2e9ead6f1e4e1c4feade2d62a8b708fdde48fb0edea",
    "permissions": {
        "process": {
            "public": False,
            "authorized_ids": []
        }
    },
    "key": "7c9f9799-bf64-c100-0238-1583a9ffc535",
    "metadata": {
        "foo": "bar"
    }
}

AGGREGATE_ALGO = {
    "key": "7c9f9799-bf64-c100-6238-1583a9ffc535",
    "name": "Logistic regression",
    "content": {
        "checksum": "7c9f9799bf64c10002381583a9ffc535bc3f4bf14d6g0c614d3f6f868f72a9d5",
        "storage_address": ""
    },
    "description": {
        "checksum": "124a0725b746d7072282d167b53cb6aab3a31bf1946dae89135c15b0126ebec3",
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
    "key": "7c9f9799-bf64-c100-0238-b583a9ffc535",
    "name": "Logistic regression",
    "content": {
        "checksum": "7c9f9799bf64c10002381b83a9ffc535bc3f4bf14d6f0c614d3f6f868f72a9d5",
        "storage_address": ""
    },
    "description": {
        "checksum": "124a0425b746d7b72282d167b53cb6aab3a31bf1946dae89135c15b0126ebec3",
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
    "key": "06207faf-1785-4fa9-4220-99a50dcee064",
    "algo": {
        "key": "7c9f9799-bf64-c100-0238-1583a9ffc535",
        "name": "Neural Network",
        "checksum": "0acc5180e09b6a6ac250f4e3c172e2893f617aa1c22ef1f379019d20fe44142f",
        "storage_address": ""
    },
    "creator": "e75db4df2532dc1313ebb5c2462e1eb813b94c3e67de29f6e4b2272ae60385f5",
    "dataset": {
        "key": "8dd01465-003a-9b1e-01c9-9c904d86aa51",
        "worker": "e75db4df2532dc1313ebb5c2462e1eb813b94c3e67de29f6e4b2272ae60385f5",
        "data_sample_keys": [
            "31510dc1-d8be-788f-7c5d-28d05714f7ef",
            "03a1f878-768e-a862-4942-d46a3b438c37"
        ],
        "opener_checksum": "8dd01465003a9b1e01c99c904d86aa518b3a5dd9dc8d40fe7d075c726ac073ca",
    },
    "compute_plan_key": "",
    "in_models": None,
    "log": "[00-01-0032-d415995]",
    "out_model": {
        "key": "11a1f878-768e-a862-4942-d46a3b438c37",
        "checksum": "8dd01465003a9b1e01c99c904d86aa518b3a5dd9dc8d40fe7d075c726ac073ca",
        "storage_address": ""
    },
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
    "key": "06207faf-1785-4fa9-4220-99a50dcfe064",
    "algo": {
        "key": "7c9f9799-bf64-c100-0238-1583a9ffc535",
        "name": "Neural Network",
        "checksum": "0acc5180e09b6a6ac250f4f3c172e2893f617aa1c22ef1f379019d20fe44142f",
        "storage_address": ""
    },
    "creator": "e75db4df2532dc1313ebb5c2462f1eb813b94c3e67de29f6e4b2272ae60385f5",
    "compute_plan_key": "",
    "in_models": [],
    "log": "[00-01-0032-d415995]",
    "out_model": {
        "key": "11a1f878-768e-a862-4942-d46a3b438c37",
        "checksum": "8dd01465003a9b1e01c99c904d86aa518b3a5dd9dc8d40fe7d075c726ac073ca",
        "storage_address": ""
    },
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
    "key": "06207faf-1785-4fa9-4220-99a50dcee064",
    "algo": {
        "key": "7c9f9799-bf64-c100-0238-1583a9ffc535",
        "name": "Neural Network",
        "checksum": "0acc5180e09b6a6ac250f4e3c172e2893f617aa1c22ef1f379019d20fe44142f",
        "storage_address": ""
    },
    "in_head_model": {
        "key": "0acc5180-e09b-6a6a-c250-f4e3d972e289",
        "checksum": "0acc5180e09b6a6ac250f4e3d972e2893f617aa1c22ef1f379019d20fe44142e",
    },
    "in_trunk_model": {
        "key": "0acc5180-e09b-6a6a-c250-f4e3d972e289",
        "checksum": "0acc5180e09b6a6ac250f4e3d972e2893f617aa1c22ef1f379019d20fe44142f",
        "storage_address": ""
    },
    "creator": "e75db4df2532dc1313ebb5c2462e1eb813b94c3e67de29f6e4b2272ae60385f5",
    "dataset": {
        "key": "8dd01465-003a-9b1e-01c9-9c904d86aa51",
        "worker": "e75db4df2532dc1313ebb5c2462e1eb813b94c3e67de29f6e4b2272ae60385f5",
        "data_sample_keys": [
            "31510dc1-d8be-788f-7c5d-28d05714f7ef",
            "03a1f878-768e-a862-4942-d46a3b438c37"
        ],
        "opener_checksum": "8dd01465003a9b1e01c99c904d86aa518b3a5dd9dc8d40fe7d075c726ac073ca",
    },
    "compute_plan_key": "",
    "log": "[00-01-0032-d415995]",
    "out_head_model": {
        "permissions": {
            "process": {
                "public": False,
                "authorized_ids": []
            }
        },
        "out_model": {
            "key": "8a90514f-88c7-0002-608a-9868681dd158",
            "checksum": "8a90514f88c70002608a9868681dd1589ea598e78d00a8cd7783c3ea0f9ceb09",
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
            "key": "9a90514f-88c7-0002-608a-9868681dd158",
            "checksum": "9a90514f88c70002608a9868681dd1589ea598e78d00a8cd7783c3ea0f9ceb09",
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
    "key": "97b53511-e94c-ab17-ea8b-1c31982e0b0d",
    "traintuple_key": "1197bbfc-4a18-9ea0-37a6-835895a81bb8",
    "traintuple_type": "traintuple",
    "compute_plan_key": "",
    "rank": 0,
    "algo": {
        "key": "7c9f9799-bf64-c100-0238-1583a9ffc535",
        "name": "Logistic regression",
        "checksum": "7c9f9799bf64c10002381583a9ffc535bc3f4bf14d6f0c614d3f6f868f72a9d5",
        "storage_address": "",
    },
    "certified": True,
    "creator": "e75db4df2532dc1313ebb5c2462e1eb813b94c3e67de29f6e4b2272ae60385f5",
    "dataset": {
        "key": "ce9f292c-72e9-b826-9744-5117f9c2d1d1",
        "worker": "ab75010bacbd1a4b826dc2e9ead6f1e4e1c4feade2d62a8b708fdde48fb0edea",
        "data_sample_keys": [
            "17d58b67-ae20-2801-8108-c9bf555fa58b",
            "8bf3bf4f-753a-32f2-7d18-c86405e7a406"
        ],
        "opener_checksum": "ce9f292c72e9b82697445117f9c2d1d18ce0f8ed07ff91dadb17d668bddf8932",
        "perf": 0
    },
    "log": "Test - CPU:90.07 % - Mem:0.13 GB - GPU:0.00 % - GPU Mem:0.00 GB;",
    "objective": {
        "key": "3d70ab46-d710-dacb-0f48-cb42db4874fa",
        "metrics": {
            "checksum": "c42dca31fbc2ebb5705643e3bb6ee666bbfd956de13dd03727f825ad8445b4d7",
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
        "key": "c6a6139a-28b5-936c-1086-a49d7c772734",
        "name": "data-network - Objective 1",
        "description": {
            "checksum": "c6a6139a28b5936c1086a49d7c772734f4ad65f4580ca4ab14029a925847faf3",
            "storage_address": ""
        },
        "metrics": {
            "name": "test metrics",
            "checksum": "48e748a15552ea2a8a258f6e8e75b1d67da5d6ca7471f80f9b69dae3cb950335",
            "storage_address": ""
        },
        "owner": "MyOrg2MSP",
        "test_dataset": {
            "data_manager_key": "c0230e3a-b5b9-2e50-fe3c-166471e754e3",
            "data_sample_keys": [
                "d2e599ef-e128-8a86-46b9-9330eb50f385"
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
    "key": "e983a185-5368-bd0a-0190-183af9a8e560",
    "traintuple_keys": [
        "1197bbfc-4a18-9ea0-37a6-835895a81bb8"
    ],
    "aggregatetuple_keys": None,
    "composite_traintuple_keys": None,
    "testtuple_keys": [
        "6c94a1df-7af1-3ebd-176b-05ae9686489f"
    ],
    "tag": "",
    "status": "done",
    "tuple_count": 2,
    "done_count": 2,
    "id_to_key": {
        "62378ca1b5c84e73a3d588adab7e20b2":
        "1197bbfc-4a18-9ea0-37a6-835895a81bb8",
    },
    "metadata": {
        "foo": "bar"
    }
}

MODEL = {
    "key": "8a90514f-88c7-0002-608a-9868681dd158",
    "checksum": "8a90514f88c70002608a9868681dd1589ea598e78d00a8cd7783c3ea0f9ceb09",
    "storage_address": "/some/path/model",
}
