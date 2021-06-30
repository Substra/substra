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
    "key": "7b75b728-9b9b-45fe-a867-4bb1525b7b5d",
    "name": "6da6c34034a94899ae58e364d88acec9_global - Objective 0",
    "owner": "MyOrg1MSP",
    "data_manager_key": "b41c0678-e1c0-42bc-b57f-c5def23fbdab",
    "data_sample_keys": [
        "3ab0067d-33c9-426b-b9c7-50190ba047c7"
    ],
    "metadata": {},
    "permissions": {
        "process": {
            "public": True,
            "authorized_ids": [
                "MyOrg1MSP"
            ]
        },
        "download": {
            "public": True,
            "authorized_ids": [
                "MyOrg1MSP"
            ]
        }
    },
    "description": {
        "checksum": "77c7a32520f7564b03f4abac4271307cc639cd9fb78b90435328278f3f24d796",
        "storage_address": "http://testserver/objective/7b75b728-9b9b-45fe-a867-4bb1525b7b5d/description/"
    },
    "metrics_name": "test metrics",
    "metrics": {
        "checksum": "52eea19fccfde2b12e30f4d16fd7d48f035e03210ad5804616f71799c4bdc0de",
        "storage_address": "http://testserver/objective/7b75b728-9b9b-45fe-a867-4bb1525b7b5d/metrics/"
    }
}

DATASET = {
    "key": "d7dc4a5b-e81f-4f3f-b94c-5e2bbaca15cd",
    "name": "c5e21113fcc64160b4dfac17892db879_test_composite_traintuple_data_samples_relative_order - Dataset 0",
    "owner": "MyOrg1MSP",
    "objective_key": "68cb00d8-7165-4b70-a40b-a844da02e916",
    "permissions": {
        "process": {
            "public": True,
            "authorized_ids": [
                "MyOrg1MSP"
            ]
        },
        "download": {
            "public": True,
            "authorized_ids": [
                "MyOrg1MSP"
            ]
        }
    },
    "type": "Test",
    "train_data_sample_keys": [],
    "test_data_sample_keys": [],
    "opener": {
        "checksum": "9d6cdc6cc5963476f371acc3d2a6e5a68727c2cc0d8f3af6262f2bad70421887",
        "storage_address": "http://testserver/data_manager/d7dc4a5b-e81f-4f3f-b94c-5e2bbaca15cd/opener/"
    },
    "description": {
        "checksum": "0cfe73931279111b113b3c084ee3c7d4a2c84960b4bd9862ce67039fc118684e",
        "storage_address": "http://testserver/data_manager/d7dc4a5b-e81f-4f3f-b94c-5e2bbaca15cd/description/"
    },
    "metadata": {}
}

ALGO = {
    "key": "17f98afc-2b82-4ce9-b232-1a471633d020",
    "name": "def637b111f2495bb6b4771644d2409e_test_traintuple_data_samples_relative_order - Algo 0",
    "owner": "MyOrg1MSP",
    "permissions": {
        "process": {
            "public": True,
            "authorized_ids": [
                "MyOrg1MSP"
            ]
        },
        "download": {
            "public": True,
            "authorized_ids": [
                "MyOrg1MSP"
            ]
        }
    },
    "metadata": {},
    "category": "ALGO_SIMPLE",
    "description": {
        "checksum": "756589d5971c421a388a751d533ab8ce09715c93040e9e8fff1365e831545aa2",
        "storage_address": "http://testserver/algo/17f98afc-2b82-4ce9-b232-1a471633d020/description/"
    },
    "algorithm": {
        "checksum": "aa8d43bf6e3341b0034a2e396451ab731ccca95a4c1d4f65a4fcd30f9081ec7d",
        "storage_address": "http://testserver/algo/17f98afc-2b82-4ce9-b232-1a471633d020/file/"
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
    "key": "30c283be-d385-424e-94a6-4d8538275260",
    "category": "TASK_TRAIN",
    "algo": {
        "key": "17f98afc-2b82-4ce9-b232-1a471633d020",
        "name": "def637b111f2495bb6b4771644d2409e_test_traintuple_data_samples_relative_order - Algo 0",
        "owner": "MyOrg1MSP",
        "permissions": {
            "process": {
                "public": True,
                "authorized_ids": [
                    "MyOrg1MSP"
                ]
            },
            "download": {
                "public": True,
                "authorized_ids": [
                    "MyOrg1MSP"
                ]
            }
        },
        "metadata": {},
        "category": "ALGO_SIMPLE",
        "description": {
            "checksum": "756589d5971c421a388a751d533ab8ce09715c93040e9e8fff1365e831545aa2",
            "storage_address": "http://backend-org-1-substra-backend-server.org-1:8000/algo/17f98afc-2b82-4ce9-b232-1a471633d020/description/"
        },
        "algorithm": {
            "checksum": "aa8d43bf6e3341b0034a2e396451ab731ccca95a4c1d4f65a4fcd30f9081ec7d",
            "storage_address": "http://backend-org-1-substra-backend-server.org-1:8000/algo/17f98afc-2b82-4ce9-b232-1a471633d020/file/"
        }
    },
    "owner": "MyOrg1MSP",
    "compute_plan_key": "a428d7a3-7458-421d-a818-7a2448225b8d",
    "metadata": {},
    "status": "STATUS_DONE",
    "worker": "MyOrg1MSP",
    "rank": 0,
    "parent_task_keys": [],
    "tag": "",
    "train": {
        "data_manager_key": "a67b9387-fd80-429a-bc2f-034fac430b0f",
        "data_sample_keys": [
            "3180e12c-a821-434a-ad8a-a341076c7f98",
            "21bb59ca-abd4-4154-b04a-44a92556a078",
            "67512646-2464-4521-84de-419b1b307d30",
            "8c5e430b-cb6b-4f4e-95da-499b523d9f5b"
        ],
        "model_permissions": {
            "process": {
                "public": True,
                "authorized_ids": [
                    "MyOrg1MSP"
                ]
            },
            "download": {
                "public": True,
                "authorized_ids": [
                    "MyOrg1MSP"
                ]
            }
        },
        "models": None
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
    "key": "aa09180a-fec6-46a5-a1a7-58c971b39217",
    "category": "TASK_COMPOSITE",
    "algo": {
        "key": "c663b6e6-dd62-49fb-afe8-191fa7627a64",
        "name": "c5e21113fcc64160b4dfac17892db879_test_aggregate_composite_traintuples - Algo 0",
        "owner": "MyOrg1MSP",
        "permissions": {
            "process": {
                "public": True,
                "authorized_ids": [
                    "MyOrg1MSP"
                ]
            },
            "download": {
                "public": True,
                "authorized_ids": [
                    "MyOrg1MSP"
                ]
            }
        },
        "metadata": {},
        "category": "ALGO_COMPOSITE",
        "description": {
            "checksum": "40483cd8b99ea7fbd3b73020997ea07547771993a6a3fa56fa2a8e9d7860529e",
            "storage_address": "http://backend-org-1-substra-backend-server.org-1:8000/algo/c663b6e6-dd62-49fb-afe8-191fa7627a64/description/"
        },
        "algorithm": {
            "checksum": "51bd5fe2e7f087b203d1b4a73f3b3276b9fde96a0fff9c1f5984de96e4675d59",
            "storage_address": "http://backend-org-1-substra-backend-server.org-1:8000/algo/c663b6e6-dd62-49fb-afe8-191fa7627a64/file/"
        }
    },
    "owner": "MyOrg1MSP",
    "compute_plan_key": "ed74db2f-b302-4a9d-b3d3-336eb8dcc3ff",
    "metadata": {},
    "status": "STATUS_DONE",
    "worker": "MyOrg2MSP",
    "rank": 0,
    "parent_task_keys": [],
    "tag": "",
    "composite": {
        "data_manager_key": "1ae64423-aa99-4b8a-8660-61a56e4ca42d",
        "data_sample_keys": [
            "1288d38c-dec2-4433-bc40-ec17f99f522a"
        ],
        "head_permissions": {
            "process": {
                "public": False,
                "authorized_ids": [
                    "MyOrg2MSP"
                ]
            },
            "download": {
                "public": False,
                "authorized_ids": [
                    "MyOrg2MSP"
                ]
            }
        },
        "trunk_permissions": {
            "process": {
                "public": False,
                "authorized_ids": [
                    "MyOrg1MSP",
                    "MyOrg2MSP"
                ]
            },
            "download": {
                "public": False,
                "authorized_ids": [
                    "MyOrg1MSP",
                    "MyOrg2MSP"
                ]
            }
        },
        "models": None
    }
}

TESTTUPLE = {
    "key": "afa9c7b1-21b5-4e58-a098-79de4ecede35",
    "category": "TASK_TEST",
    "algo": {
        "key": "17f98afc-2b82-4ce9-b232-1a471633d020",
        "name": "def637b111f2495bb6b4771644d2409e_test_traintuple_data_samples_relative_order - Algo 0",
        "owner": "MyOrg1MSP",
        "permissions": {
            "process": {
                "public": True,
                "authorized_ids": [
                    "MyOrg1MSP"
                ]
            },
            "download": {
                "public": True,
                "authorized_ids": [
                    "MyOrg1MSP"
                ]
            }
        },
        "metadata": {},
        "category": "ALGO_SIMPLE",
        "description": {
            "checksum": "756589d5971c421a388a751d533ab8ce09715c93040e9e8fff1365e831545aa2",
            "storage_address": "http://backend-org-1-substra-backend-server.org-1:8000/algo/17f98afc-2b82-4ce9-b232-1a471633d020/description/"
        },
        "algorithm": {
            "checksum": "aa8d43bf6e3341b0034a2e396451ab731ccca95a4c1d4f65a4fcd30f9081ec7d",
            "storage_address": "http://backend-org-1-substra-backend-server.org-1:8000/algo/17f98afc-2b82-4ce9-b232-1a471633d020/file/"
        }
    },
    "owner": "MyOrg1MSP",
    "compute_plan_key": "a428d7a3-7458-421d-a818-7a2448225b8d",
    "metadata": {},
    "status": "STATUS_DONE",
    "worker": "MyOrg1MSP",
    "rank": 0,
    "parent_task_keys": [
        "30c283be-d385-424e-94a6-4d8538275260"
    ],
    "tag": "",
    "test": {
        "data_manager_key": "a67b9387-fd80-429a-bc2f-034fac430b0f",
        "data_sample_keys": [
            "3180e12c-a821-434a-ad8a-a341076c7f98",
            "21bb59ca-abd4-4154-b04a-44a92556a078"
        ],
        "objective_key": "e526243f-f51a-4737-9fea-a5d55f4205fe",
        "certified": False,
        "perf": None
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
    "failed_tuple": {
        "key": "",
        "type": "",
    },
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
