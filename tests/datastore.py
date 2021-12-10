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
METRIC = {
    "key": "d5002e1c-d50b-d5de-5341-df8a7b7d11b6",
    "name": "Skin Lesion Classification Challenge",
    "owner": "MyOrg1MSP",
    "creation_date": "2021-08-24T13:36:07.428974249Z",
    "metadata": {},
    "permissions": {
        "process": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
        "download": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
    },
    "description": {
        "checksum": "77c7a32520f7564b03f4abac4271307cc639cd9fb78b90435328278f3f24d796",
        "storage_address": "http://testserver/metric/7b75b728-9b9b-45fe-a867-4bb1525b7b5d/description/",
    },
    "address": {
        "checksum": "52eea19fccfde2b12e30f4d16fd7d48f035e03210ad5804616f71799c4bdc0de",
        "storage_address": "http://testserver/metric/7b75b728-9b9b-45fe-a867-4bb1525b7b5d/metrics/",
    },
}

DATASET = {
    "key": "d7dc4a5b-e81f-4f3f-b94c-5e2bbaca15cd",
    "name": "c5e21113fcc64160b4dfac17892db879_test_composite_traintuple_data_samples_relative_order - Dataset 0",
    "owner": "MyOrg1MSP",
    "creation_date": "2021-08-24T13:36:07.428974249Z",
    "permissions": {
        "process": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
        "download": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
    },
    "type": "Test",
    "train_data_sample_keys": [],
    "test_data_sample_keys": [],
    "metadata": {"foo": "bar"},
    "opener": {
        "checksum": "9d6cdc6cc5963476f371acc3d2a6e5a68727c2cc0d8f3af6262f2bad70421887",
        "storage_address": "http://testserver/data_manager/d7dc4a5b-e81f-4f3f-b94c-5e2bbaca15cd/opener/",
    },
    "description": {
        "checksum": "0cfe73931279111b113b3c084ee3c7d4a2c84960b4bd9862ce67039fc118684e",
        "storage_address": "http://testserver/data_manager/d7dc4a5b-e81f-4f3f-b94c-5e2bbaca15cd/description/",
    },
}

ALGO = {
    "key": "17f98afc-2b82-4ce9-b232-1a471633d020",
    "name": "def637b111f2495bb6b4771644d2409e_test_traintuple_data_samples_relative_order - Algo 0",
    "owner": "MyOrg1MSP",
    "creation_date": "2021-08-24T13:36:07.393646367Z",
    "permissions": {
        "process": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
        "download": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
    },
    "metadata": {},
    "category": "ALGO_SIMPLE",
    "description": {
        "checksum": "756589d5971c421a388a751d533ab8ce09715c93040e9e8fff1365e831545aa2",
        "storage_address": "http://testserver/algo/17f98afc-2b82-4ce9-b232-1a471633d020/description/",
    },
    "algorithm": {
        "checksum": "aa8d43bf6e3341b0034a2e396451ab731ccca95a4c1d4f65a4fcd30f9081ec7d",
        "storage_address": "http://testserver/algo/17f98afc-2b82-4ce9-b232-1a471633d020/file/",
    },
}

TRAINTUPLE = {
    "key": "30c283be-d385-424e-94a6-4d8538275260",
    "category": "TASK_TRAIN",
    "algo": {
        "key": "17f98afc-2b82-4ce9-b232-1a471633d020",
        "name": "def637b111f2495bb6b4771644d2409e_test_traintuple_data_samples_relative_order - Algo 0",
        "owner": "MyOrg1MSP",
        "creation_date": "2021-08-24T13:36:07.428974249Z",
        "permissions": {
            "process": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
            "download": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
        },
        "metadata": {},
        "category": "ALGO_SIMPLE",
        "description": {
            "checksum": "756589d5971c421a388a751d533ab8ce09715c93040e9e8fff1365e831545aa2",
            "storage_address": "http://backend-org-1-substra-backend-server.org-1:8000/algo/17f98afc-2b82-4ce9-b232-1a471633d020/description/",  # noqa: E501
        },
        "algorithm": {
            "checksum": "aa8d43bf6e3341b0034a2e396451ab731ccca95a4c1d4f65a4fcd30f9081ec7d",
            "storage_address": "http://backend-org-1-substra-backend-server.org-1:8000/algo/17f98afc-2b82-4ce9-b232-1a471633d020/file/",  # noqa: E501
        },
    },
    "owner": "MyOrg1MSP",
    "creation_date": "2021-08-24T13:36:07.393646367Z",
    "compute_plan_key": "a428d7a3-7458-421d-a818-7a2448225b8d",
    "metadata": {},
    "status": "STATUS_DONE",
    "worker": "MyOrg1MSP",
    "rank": 0,
    "parent_task_keys": [],
    "tag": "",
    "start_date": "2021-10-12T09:28:06.947765800Z",
    "end_date": "2021-10-12T09:30:04.705947400Z",
    "train": {
        "data_manager_key": "a67b9387-fd80-429a-bc2f-034fac430b0f",
        "data_sample_keys": [
            "3180e12c-a821-434a-ad8a-a341076c7f98",
            "21bb59ca-abd4-4154-b04a-44a92556a078",
            "67512646-2464-4521-84de-419b1b307d30",
            "8c5e430b-cb6b-4f4e-95da-499b523d9f5b",
        ],
        "model_permissions": {
            "process": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
            "download": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
        },
        "models": [
            {
                "key": "6f0ee20a328044fb89e70ee5d219fa0c",
                "category": "MODEL_SIMPLE",
                "compute_task_key": "30c283be-d385-424e-94a6-4d8538275260",
                "address": {
                    "checksum": "40483cd8b99ea7fbd3b73020997ea07547771993a6a3fa56fa2a8e9d7860529e",
                    "storage_address": "http://backend-org-1-substra-backend-server.org-1:8000/model/5f0ee20a328044fb89e70ee5d219fa0b/address/",  # noqa: E501
                },
                "permissions": {
                    "process": {"public": False, "authorized_ids": ["MyOrg1MSP", "MyOrg2MSP"]},
                    "download": {"public": False, "authorized_ids": ["MyOrg1MSP", "MyOrg2MSP"]},
                },
                "owner": "MyOrg1MSP",
                "creation_date": "2021-08-24T13:36:07.393646367Z",
            }
        ],
    },
}

AGGREGATETUPLE = {
    "key": "06207faf-1785-4fa9-4220-99a50dcfe064",
    "category": "TASK_AGGREGATE",
    "algo": {
        "key": "7c9f9799-bf64-c100-6238-1583a9ffc535",
        "name": "Logistic regression",
        "category": "ALGO_AGGREGATE",
        "algorithm": {
            "checksum": "7c9f9799bf64c10002381583a9ffc535bc3f4bf14d6g0c614d3f6f868f72a9d5",
            "storage_address": "",
        },
        "description": {
            "checksum": "124a0725b746d7072282d167b53cb6aab3a31bf1946dae89135c15b0126ebec3",
            "storage_address": "",
        },
        "owner": "ab75010bacbd1a4b826dc2e9ead6f1e4e1c4feade2d62a8b708fdde48fb0edeb",
        "creation_date": "2021-08-24T13:36:07.428974249Z",
        "permissions": {
            "process": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
            "download": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
        },
        "metadata": {"foo": "bar"},
    },
    "owner": "MyOrg1MSP",
    "creation_date": "2021-08-24T13:36:07.393646367Z",
    "compute_plan_key": "",
    "metadata": {"foo": "bar"},
    "status": "STATUS_DONE",
    "worker": "MyOrg1MSP",
    "rank": None,
    "parent_task_keys": [],
    "tag": "My super tag",
    "start_date": "2021-10-12T09:28:06.947765800Z",
    "end_date": "2021-10-12T09:30:04.705947400Z",
    "aggregate": {
        "model_permissions": {
            "process": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
            "download": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
        },
        "models": [
            {
                "key": "5f0ee20a328044fb89e70ee5d219fa0b",
                "category": "MODEL_SIMPLE",
                "compute_task_key": "06207faf-1785-4fa9-4220-99a50dcfe064",
                "address": {
                    "checksum": "40483cd8b99ea7fbd3b73020997ea07547771993a6a3fa56fa2a8e9d7860529e",
                    "storage_address": "http://backend-org-1-substra-backend-server.org-1:8000/model/5f0ee20a328044fb89e70ee5d219fa0b/address/",  # noqa: E501
                },
                "permissions": {
                    "process": {"public": False, "authorized_ids": ["MyOrg1MSP", "MyOrg2MSP"]},
                    "download": {"public": False, "authorized_ids": ["MyOrg1MSP", "MyOrg2MSP"]},
                },
                "owner": "MyOrg1MSP",
                "creation_date": "2021-08-24T13:36:07.393646367Z",
            }
        ],
    },
}

COMPOSITE_TRAINTUPLE = {
    "key": "aa09180a-fec6-46a5-a1a7-58c971b39217",
    "category": "TASK_COMPOSITE",
    "algo": {
        "key": "c663b6e6-dd62-49fb-afe8-191fa7627a64",
        "name": "c5e21113fcc64160b4dfac17892db879_test_aggregate_composite_traintuples - Algo 0",
        "owner": "MyOrg1MSP",
        "creation_date": "2021-08-24T13:36:07.428974249Z",
        "permissions": {
            "process": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
            "download": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
        },
        "metadata": {},
        "category": "ALGO_COMPOSITE",
        "description": {
            "checksum": "40483cd8b99ea7fbd3b73020997ea07547771993a6a3fa56fa2a8e9d7860529e",
            "storage_address": "http://backend-org-1-substra-backend-server.org-1:8000/algo/c663b6e6-dd62-49fb-afe8-191fa7627a64/description/",  # noqa: E501
        },
        "algorithm": {
            "checksum": "51bd5fe2e7f087b203d1b4a73f3b3276b9fde96a0fff9c1f5984de96e4675d59",
            "storage_address": "http://backend-org-1-substra-backend-server.org-1:8000/algo/c663b6e6-dd62-49fb-afe8-191fa7627a64/file/",  # noqa: E501
        },
    },
    "owner": "MyOrg1MSP",
    "creation_date": "2021-08-24T13:36:07.393646367Z",
    "compute_plan_key": "ed74db2f-b302-4a9d-b3d3-336eb8dcc3ff",
    "metadata": {},
    "status": "STATUS_DONE",
    "worker": "MyOrg2MSP",
    "rank": 0,
    "parent_task_keys": [],
    "tag": "",
    "start_date": "2021-10-12T09:28:06.947765800Z",
    "end_date": "2021-10-12T09:30:04.705947400Z",
    "composite": {
        "data_manager_key": "1ae64423-aa99-4b8a-8660-61a56e4ca42d",
        "data_sample_keys": ["1288d38c-dec2-4433-bc40-ec17f99f522a"],
        "head_permissions": {
            "process": {"public": False, "authorized_ids": ["MyOrg2MSP"]},
            "download": {"public": False, "authorized_ids": ["MyOrg2MSP"]},
        },
        "trunk_permissions": {
            "process": {"public": False, "authorized_ids": ["MyOrg1MSP", "MyOrg2MSP"]},
            "download": {"public": False, "authorized_ids": ["MyOrg1MSP", "MyOrg2MSP"]},
        },
        "models": [
            {
                "key": "ac4a1a82ced4419b83f4bba78c024b94",
                "category": "MODEL_HEAD",
                "compute_task_key": "aa09180a-fec6-46a5-a1a7-58c971b39217",
                "address": {
                    "checksum": "40483cd8b99ea7fbd3b73020997ea07547771993a6a3fa56fa2a8e9d7860529e",
                    "storage_address": "http://backend-org-1-substra-backend-server.org-1:8000/model/ac4a1a82ced4419b83f4bba78c024b94/address/",  # noqa: E501
                },
                "permissions": {
                    "process": {"public": False, "authorized_ids": ["MyOrg1MSP", "MyOrg2MSP"]},
                    "download": {"public": False, "authorized_ids": ["MyOrg1MSP", "MyOrg2MSP"]},
                },
                "owner": "MyOrg1MSP",
                "creation_date": "2021-08-24T13:36:07.393646367Z",
            },
            {
                "key": "dc9d114d1ed54936b57dd7fef1c0cbf4",
                "category": "MODEL_SIMPLE",
                "compute_task_key": "aa09180a-fec6-46a5-a1a7-58c971b39217",
                "address": {
                    "checksum": "40483cd8b99ea7fbd3b73020997ea07547771993a6a3fa56fa2a8e9d7860529e",
                    "storage_address": "http://backend-org-1-substra-backend-server.org-1:8000/model/ac4a1a82ced4419b83f4bba78c024b94/address/",  # noqa: E501
                },
                "permissions": {
                    "process": {"public": False, "authorized_ids": ["MyOrg1MSP", "MyOrg2MSP"]},
                    "download": {"public": False, "authorized_ids": ["MyOrg1MSP", "MyOrg2MSP"]},
                },
                "owner": "MyOrg1MSP",
                "creation_date": "2021-08-24T13:36:07.393646367Z",
            },
        ],
    },
}

COMPOSITE_TRAINTUPLE_DOING = {
    "key": "aa09180a-fec6-46a5-a1a7-58c971b39217",
    "category": "TASK_COMPOSITE",
    "algo": {
        "key": "c663b6e6-dd62-49fb-afe8-191fa7627a64",
        "name": "c5e21113fcc64160b4dfac17892db879_test_aggregate_composite_traintuples - Algo 0",
        "owner": "MyOrg1MSP",
        "creation_date": "2021-08-24T13:36:07.428974249Z",
        "permissions": {
            "process": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
            "download": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
        },
        "metadata": {},
        "category": "ALGO_COMPOSITE",
        "description": {
            "checksum": "40483cd8b99ea7fbd3b73020997ea07547771993a6a3fa56fa2a8e9d7860529e",
            "storage_address": "http://backend-org-1-substra-backend-server.org-1:8000/algo/c663b6e6-dd62-49fb-afe8-191fa7627a64/description/",  # noqa: E501
        },
        "algorithm": {
            "checksum": "51bd5fe2e7f087b203d1b4a73f3b3276b9fde96a0fff9c1f5984de96e4675d59",
            "storage_address": "http://backend-org-1-substra-backend-server.org-1:8000/algo/c663b6e6-dd62-49fb-afe8-191fa7627a64/file/",  # noqa: E501
        },
    },
    "owner": "MyOrg1MSP",
    "creation_date": "2021-08-24T13:36:07.393646367Z",
    "compute_plan_key": "ed74db2f-b302-4a9d-b3d3-336eb8dcc3ff",
    "metadata": {},
    "status": "STATUS_DOING",
    "worker": "MyOrg2MSP",
    "rank": 0,
    "parent_task_keys": [],
    "tag": "",
    "composite": {
        "data_manager_key": "1ae64423-aa99-4b8a-8660-61a56e4ca42d",
        "data_sample_keys": ["1288d38c-dec2-4433-bc40-ec17f99f522a"],
        "head_permissions": {
            "process": {"public": False, "authorized_ids": ["MyOrg2MSP"]},
            "download": {"public": False, "authorized_ids": ["MyOrg2MSP"]},
        },
        "trunk_permissions": {
            "process": {"public": False, "authorized_ids": ["MyOrg1MSP", "MyOrg2MSP"]},
            "download": {"public": False, "authorized_ids": ["MyOrg1MSP", "MyOrg2MSP"]},
        },
        "models": None,
    },
}

TESTTUPLE = {
    "key": "afa9c7b1-21b5-4e58-a098-79de4ecede35",
    "category": "TASK_TEST",
    "algo": {
        "key": "17f98afc-2b82-4ce9-b232-1a471633d020",
        "name": "def637b111f2495bb6b4771644d2409e_test_traintuple_data_samples_relative_order - Algo 0",
        "owner": "MyOrg1MSP",
        "creation_date": "2021-08-24T13:36:07.428974249Z",
        "permissions": {
            "process": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
            "download": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
        },
        "metadata": {},
        "category": "ALGO_SIMPLE",
        "description": {
            "checksum": "756589d5971c421a388a751d533ab8ce09715c93040e9e8fff1365e831545aa2",
            "storage_address": "http://backend-org-1-substra-backend-server.org-1:8000/algo/17f98afc-2b82-4ce9-b232-1a471633d020/description/",  # noqa: E501
        },
        "algorithm": {
            "checksum": "aa8d43bf6e3341b0034a2e396451ab731ccca95a4c1d4f65a4fcd30f9081ec7d",
            "storage_address": "http://backend-org-1-substra-backend-server.org-1:8000/algo/17f98afc-2b82-4ce9-b232-1a471633d020/file/",  # noqa: E501
        },
    },
    "owner": "MyOrg1MSP",
    "creation_date": "2021-08-24T13:36:07.393646367Z",
    "compute_plan_key": "a428d7a3-7458-421d-a818-7a2448225b8d",
    "metadata": {},
    "status": "STATUS_DONE",
    "worker": "MyOrg1MSP",
    "rank": 0,
    "parent_task_keys": ["30c283be-d385-424e-94a6-4d8538275260"],
    "tag": "",
    "start_date": "2021-10-12T09:28:06.947765800Z",
    "end_date": "2021-10-12T09:30:04.705947400Z",
    "test": {
        "data_manager_key": "a67b9387-fd80-429a-bc2f-034fac430b0f",
        "data_sample_keys": [
            "3180e12c-a821-434a-ad8a-a341076c7f98",
            "21bb59ca-abd4-4154-b04a-44a92556a078",
        ],
        "metric_keys": ["e526243f-f51a-4737-9fea-a5d55f4205fe"],
        "perfs": {},
    },
}

LEADERBOARD = {
    "metric": {
        "key": "c6a6139a-28b5-936c-1086-a49d7c772734",
        "name": "data-network - Metric 1",
        "data_manager_key": "c0230e3a-b5b9-2e50-fe3c-166471e754e3",
        "data_sample_keys": ["d2e599ef-e128-8a86-46b9-9330eb50f385"],
        "permissions": {
            "process": {"public": True, "authorized_ids": []},
            "download": {"public": True, "authorized_ids": []},
        },
        "description": {
            "checksum": "c6a6139a28b5936c1086a49d7c772734f4ad65f4580ca4ab14029a925847faf3",
            "storage_address": "",
        },
        "address": {
            "checksum": "48e748a15552ea2a8a258f6e8e75b1d67da5d6ca7471f80f9b69dae3cb950335",
            "storage_address": "",
        },
        "owner": "MyOrg2MSP",
        "test_dataset": {
            "data_manager_key": "c0230e3a-b5b9-2e50-fe3c-166471e754e3",
            "data_sample_keys": ["d2e599ef-e128-8a86-46b9-9330eb50f385"],
            "worker": "",
        },
    },
    "testtuples": [],
}

NODES = [
    {"id": "foo", "is_current": False, "creation_date": "2021-08-24T13:36:07.393646367Z"},
    {"id": "bar", "is_current": True, "creation_date": "2021-08-24T13:36:07.393646367Z"},
]

COMPUTE_PLAN = {
    "key": "e983a185-5368-bd0a-0190-183af9a8e560",
    "tag": "",
    "owner": "MyOrg1MSP",
    "creation_date": "2021-08-24T13:36:07.393646367Z",
    "start_date": "2021-08-24T13:36:37.947765800Z",
    "end_date": "2021-08-24T13:38:07.705947400Z",
    "estimated_end_date": "2021-08-24T13:38:07.705947400Z",
    "duration": "90",
    "status": "PLAN_STATUS_DONE",
    "task_count": 21,
    "waiting_count": 1,
    "todo_count": 2,
    "doing_count": 3,
    "canceled_count": 4,
    "failed_count": 5,
    "done_count": 6,
    "metadata": {"foo": "bar"},
}

MODEL = {
    "key": "8a90514f-88c7-0002-608a-9868681dd158",
    "checksum": "8a90514f88c70002608a9868681dd1589ea598e78d00a8cd7783c3ea0f9ceb09",
    "storage_address": "/some/path/model",
    "creation_date": "2021-08-24T13:36:07.393646367Z",
}
