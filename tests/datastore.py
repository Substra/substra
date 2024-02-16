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
    "archive": {
        "checksum": "52eea19fccfde2b12e30f4d16fd7d48f035e03210ad5804616f71799c4bdc0de",
        "storage_address": "http://testserver/metric/7b75b728-9b9b-45fe-a867-4bb1525b7b5d/file/",
    },
    "inputs": {
        "datasamples": {"kind": "ASSET_DATA_SAMPLE", "optional": False, "multiple": True},
        "opener": {"kind": "ASSET_DATA_MANAGER", "optional": False, "multiple": False},
        "predictions": {"kind": "ASSET_MODEL", "optional": False, "multiple": False},
    },
    "outputs": {"performance": {"kind": "ASSET_PERFORMANCE", "multiple": False}},
}

DATASET = {
    "key": "d7dc4a5b-e81f-4f3f-b94c-5e2bbaca15cd",
    "name": "c5e21113fcc64160b4dfac17892db879_test_composite_traintask_data_samples_relative_order - Dataset 0",
    "owner": "MyOrg1MSP",
    "creation_date": "2021-08-24T13:36:07.428974249Z",
    "permissions": {
        "process": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
        "download": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
    },
    "type": "Test",
    "data_sample_keys": [],
    "metadata": {"foo": "bar"},
    "opener": {
        "checksum": "9d6cdc6cc5963476f371acc3d2a6e5a68727c2cc0d8f3af6262f2bad70421887",
        "storage_address": "http://testserver/data_manager/d7dc4a5b-e81f-4f3f-b94c-5e2bbaca15cd/opener/",
    },
    "description": {
        "checksum": "0cfe73931279111b113b3c084ee3c7d4a2c84960b4bd9862ce67039fc118684e",
        "storage_address": "http://testserver/data_manager/d7dc4a5b-e81f-4f3f-b94c-5e2bbaca15cd/description/",
    },
    "logs_permission": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
}

DATA_SAMPLE = {
    "key": "7096db67-c175-4b45-9fb3-ad785eebb347",
    "owner": "MyOrg1MSP",
    "data_manager_keys": ["d7dc4a5b-e81f-4f3f-b94c-5e2bbaca15cd"],
    "creation_date": "2021-08-24T13:36:07.428974249Z",
}

FUNCTION = {
    "key": "17f98afc-2b82-4ce9-b232-1a471633d020",
    "name": "def637b111f2495bb6b4771644d2409e_test_traintask_data_samples_relative_order - Function 0",
    "owner": "MyOrg1MSP",
    "creation_date": "2021-08-24T13:36:07.393646367Z",
    "permissions": {
        "process": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
        "download": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
    },
    "metadata": {},
    "description": {
        "checksum": "756589d5971c421a388a751d533ab8ce09715c93040e9e8fff1365e831545aa2",
        "storage_address": "http://testserver/function/17f98afc-2b82-4ce9-b232-1a471633d020/description/",
    },
    "archive": {
        "checksum": "aa8d43bf6e3341b0034a2e396451ab731ccca95a4c1d4f65a4fcd30f9081ec7d",
        "storage_address": "http://testserver/function/17f98afc-2b82-4ce9-b232-1a471633d020/file/",
    },
    "inputs": {
        "datasamples": {"kind": "ASSET_DATA_SAMPLE", "optional": False, "multiple": True},
        "model": {"kind": "ASSET_MODEL", "optional": True, "multiple": True},
        "opener": {"kind": "ASSET_DATA_MANAGER", "optional": False, "multiple": False},
    },
    "outputs": {"model": {"kind": "ASSET_MODEL", "multiple": False}},
    "status": "FUNCTION_STATUS_READY",
}


FUNCTION_PREDICT = {
    "key": "681eedb9-db00-4480-a66f-63c86cc20280",
    "name": "def637b111f2495bb6b4771644d2409e_test_traintask_data_samples_relative_order - Function Predict",
    "owner": "MyOrg1MSP",
    "creation_date": "2021-08-24T13:36:07.393646367Z",
    "permissions": {
        "process": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
        "download": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
    },
    "metadata": {},
    "description": {
        "checksum": "756589d5971c421a388a751d533ab8ce09715c93040e9e8fff1365e831545aa2",
        "storage_address": "http://testserver/function/681eedb9-db00-4480-a66f-63c86cc20280/description/",
    },
    "archive": {
        "checksum": "aa8d43bf6e3341b0034a2e396451ab731ccca95a4c1d4f65a4fcd30f9081ec7d",
        "storage_address": "http://testserver/function/681eedb9-db00-4480-a66f-63c86cc20280/file/",
    },
    "inputs": {
        "datasamples": {"kind": "ASSET_DATA_SAMPLE", "optional": False, "multiple": True},
        "model": {"kind": "ASSET_MODEL", "optional": False, "multiple": False},
        "opener": {"kind": "ASSET_DATA_MANAGER", "optional": False, "multiple": False},
        "shared": {"kind": "ASSET_MODEL", "optional": True, "multiple": False},
    },
    "outputs": {"predictions": {"kind": "ASSET_MODEL", "multiple": False}},
    "status": "FUNCTION_STATUS_READY",
}


FUNCTION_METRIC = {
    "key": "6a8ada2e-740f-46f4-af0f-11376763ed72",
    "name": "def637b111f2495bb6b4771644d2409e_test_traintask_data_samples_relative_order - Function Metric",
    "owner": "MyOrg1MSP",
    "creation_date": "2021-08-24T13:36:07.393646367Z",
    "permissions": {
        "process": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
        "download": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
    },
    "metadata": {},
    "description": {
        "checksum": "756589d5971c421a388a751d533ab8ce09715c93040e9e8fff1365e831545aa2",
        "storage_address": "http://testserver/function/6a8ada2e-740f-46f4-af0f-11376763ed72/description/",
    },
    "archive": {
        "checksum": "aa8d43bf6e3341b0034a2e396451ab731ccca95a4c1d4f65a4fcd30f9081ec7d",
        "storage_address": "http://testserver/function/6a8ada2e-740f-46f4-af0f-11376763ed72/file/",
    },
    "inputs": {
        "datasamples": {"kind": "ASSET_DATA_SAMPLE", "optional": False, "multiple": True},
        "opener": {"kind": "ASSET_DATA_MANAGER", "optional": False, "multiple": False},
        "predictions": {"kind": "ASSET_MODEL", "optional": False, "multiple": False},
    },
    "outputs": {"performance": {"kind": "ASSET_PERFORMANCE", "multiple": False}},
    "status": "FUNCTION_STATUS_READY",
}


TRAINTASK = {
    "key": "30c283be-d385-424e-94a6-4d8538275260",
    "function": {
        "key": "17f98afc-2b82-4ce9-b232-1a471633d020",
        "name": "def637b111f2495bb6b4771644d2409e_test_traintask_data_samples_relative_order - Function 0",
        "owner": "MyOrg1MSP",
        "creation_date": "2021-08-24T13:36:07.428974249Z",
        "permissions": {
            "process": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
            "download": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
        },
        "metadata": {},
        "description": {
            "checksum": "756589d5971c421a388a751d533ab8ce09715c93040e9e8fff1365e831545aa2",
            "storage_address": "http://backend-org-1-substra-backend-server.org-1:8000/function/17f98afc-2b82-4ce9-b232-1a471633d020/description/",  # noqa: E501
        },
        "archive": {
            "checksum": "aa8d43bf6e3341b0034a2e396451ab731ccca95a4c1d4f65a4fcd30f9081ec7d",
            "storage_address": "http://backend-org-1-substra-backend-server.org-1:8000/function/17f98afc-2b82-4ce9-b232-1a471633d020/file/",  # noqa: E501
        },
        "inputs": {
            "datasamples": {"kind": "ASSET_DATA_SAMPLE", "optional": False, "multiple": True},
            "model": {"kind": "ASSET_MODEL", "optional": True, "multiple": True},
            "opener": {"kind": "ASSET_DATA_MANAGER", "optional": False, "multiple": False},
        },
        "outputs": {"model": {"kind": "ASSET_MODEL", "multiple": False}},
        "status": "FUNCTION_STATUS_READY",
    },
    "owner": "MyOrg1MSP",
    "creation_date": "2021-08-24T13:36:07.393646367Z",
    "compute_plan_key": "a428d7a3-7458-421d-a818-7a2448225b8d",
    "metadata": {},
    "status": "STATUS_DONE",
    "worker": "MyOrg1MSP",
    "rank": 0,
    "tag": "",
    "start_date": "2021-10-12T09:28:06.947765800Z",
    "end_date": "2021-10-12T09:30:04.705947400Z",
    "inputs": [
        {"identifier": "opener", "asset_key": "d7dc4a5b-e81f-4f3f-b94c-5e2bbaca15cd"},
        {"identifier": "datasamples", "asset_key": "3180e12c-a821-434a-ad8a-a341076c7f98"},
        {"identifier": "datasamples", "asset_key": "21bb59ca-abd4-4154-b04a-44a92556a078"},
        {"identifier": "datasamples", "asset_key": "67512646-2464-4521-84de-419b1b307d30"},
        {"identifier": "datasamples", "asset_key": "8c5e430b-cb6b-4f4e-95da-499b523d9f5b"},
    ],
    "outputs": {
        "model": {
            "permissions": {
                "process": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
                "download": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
            },
            "transient": False,
        },
    },
}

TRAINTASK_MODEL = {
    "asset": {
        "key": "6f0ee20a328044fb89e70ee5d219fa0c",
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
    },
    "identifier": "model",
    "kind": "ASSET_MODEL",
}

TRAINTASK_MODEL_RESPONSE = {"count": 1, "previous": None, "next": None, "results": [TRAINTASK_MODEL]}

AGGREGATETASK = {
    "key": "06207faf-1785-4fa9-4220-99a50dcfe064",
    "function": {
        "key": "7c9f9799-bf64-c100-6238-1583a9ffc535",
        "name": "Logistic regression",
        "archive": {
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
        "inputs": {"model": {"kind": "ASSET_MODEL", "optional": False, "multiple": True}},
        "outputs": {"model": {"kind": "ASSET_MODEL", "multiple": False}},
        "status": "FUNCTION_STATUS_READY",
    },
    "owner": "MyOrg1MSP",
    "creation_date": "2021-08-24T13:36:07.393646367Z",
    "compute_plan_key": "",
    "metadata": {"foo": "bar"},
    "status": "STATUS_DONE",
    "worker": "MyOrg1MSP",
    "rank": None,
    "tag": "My super tag",
    "start_date": "2021-10-12T09:28:06.947765800Z",
    "end_date": "2021-10-12T09:30:04.705947400Z",
    "inputs": [],
    "outputs": {
        "model": {
            "permissions": {
                "process": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
                "download": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
            },
            "transient": False,
        },
    },
}

AGGREGATETASK_MODEL = {
    "asset": {
        "key": "5f0ee20a328044fb89e70ee5d219fa0b",
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
    },
    "identifier": "model",
    "kind": "ASSET_MODEL",
}

AGGREGATETASK_MODEL_RESPONSE = {"count": 1, "previous": None, "next": None, "results": [AGGREGATETASK_MODEL]}

COMPOSITE_TRAINTASK = {
    "key": "aa09180a-fec6-46a5-a1a7-58c971b39217",
    "function": {
        "key": "c663b6e6-dd62-49fb-afe8-191fa7627a64",
        "name": "c5e21113fcc64160b4dfac17892db879_test_aggregate_composite_traintasks - Function 0",
        "owner": "MyOrg1MSP",
        "creation_date": "2021-08-24T13:36:07.428974249Z",
        "permissions": {
            "process": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
            "download": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
        },
        "metadata": {},
        "description": {
            "checksum": "40483cd8b99ea7fbd3b73020997ea07547771993a6a3fa56fa2a8e9d7860529e",
            "storage_address": "http://backend-org-1-substra-backend-server.org-1:8000/function/c663b6e6-dd62-49fb-afe8-191fa7627a64/description/",  # noqa: E501
        },
        "archive": {
            "checksum": "51bd5fe2e7f087b203d1b4a73f3b3276b9fde96a0fff9c1f5984de96e4675d59",
            "storage_address": "http://backend-org-1-substra-backend-server.org-1:8000/function/c663b6e6-dd62-49fb-afe8-191fa7627a64/file/",  # noqa: E501
        },
        "inputs": {
            "datasamples": {"kind": "ASSET_DATA_SAMPLE", "optional": False, "multiple": True},
            "local": {"kind": "ASSET_MODEL", "optional": True, "multiple": False},
            "opener": {"kind": "ASSET_DATA_MANAGER", "optional": False, "multiple": False},
            "shared": {"kind": "ASSET_MODEL", "optional": True, "multiple": False},
        },
        "outputs": {
            "local": {"kind": "ASSET_MODEL", "multiple": False},
            "shared": {"kind": "ASSET_MODEL", "multiple": False},
        },
        "status": "FUNCTION_STATUS_READY",
    },
    "owner": "MyOrg1MSP",
    "creation_date": "2021-08-24T13:36:07.393646367Z",
    "compute_plan_key": "ed74db2f-b302-4a9d-b3d3-336eb8dcc3ff",
    "metadata": {},
    "status": "STATUS_DONE",
    "worker": "MyOrg2MSP",
    "rank": 0,
    "tag": "",
    "start_date": "2021-10-12T09:28:06.947765800Z",
    "end_date": "2021-10-12T09:30:04.705947400Z",
    "inputs": [
        {"identifier": "opener", "asset_key": "1ae64423-aa99-4b8a-8660-61a56e4ca42d"},
        {"identifier": "datasamples", "asset_key": "1288d38c-dec2-4433-bc40-ec17f99f522a"},
    ],
    "outputs": {
        "shared": {
            "permissions": {
                "process": {"public": False, "authorized_ids": ["MyOrg1MSP", "MyOrg2MSP"]},
                "download": {"public": False, "authorized_ids": ["MyOrg1MSP", "MyOrg2MSP"]},
            },
            "transient": False,
        },
        "local": {
            "permissions": {
                "process": {"public": False, "authorized_ids": ["MyOrg2MSP"]},
                "download": {"public": False, "authorized_ids": ["MyOrg2MSP"]},
            },
            "transient": False,
        },
    },
}

COMPOSITE_TRAINTASK_SHARED = {
    "asset": {
        "key": "dc9d114d1ed54936b57dd7fef1c0cbf4",
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
    "identifier": "shared",
    "kind": "ASSET_MODEL",
}


COMPOSITE_TRAINTASK_SHARED_RESPONSE = {"count": 1, "previous": None, "next": None, "results": [AGGREGATETASK_MODEL]}

COMPOSITE_TRAINTASK_LOCAL = {
    "asset": {
        "key": "dc9d114d1ed54936b57dd7fef1c0cbf4",
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
    "identifier": "local",
    "kind": "ASSET_MODEL",
}


COMPOSITE_TRAINTASK_LOCAL_RESPONSE = {
    "count": 1,
    "previous": None,
    "next": None,
    "results": [COMPOSITE_TRAINTASK_LOCAL],
}

COMPOSITE_TRAINTASK_DOING = {
    "key": "aa09180a-fec6-46a5-a1a7-58c971b39217",
    "function": {
        "key": "c663b6e6-dd62-49fb-afe8-191fa7627a64",
        "name": "c5e21113fcc64160b4dfac17892db879_test_aggregate_composite_traintasks - Function 0",
        "owner": "MyOrg1MSP",
        "creation_date": "2021-08-24T13:36:07.428974249Z",
        "permissions": {
            "process": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
            "download": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
        },
        "metadata": {},
        "description": {
            "checksum": "40483cd8b99ea7fbd3b73020997ea07547771993a6a3fa56fa2a8e9d7860529e",
            "storage_address": "http://backend-org-1-substra-backend-server.org-1:8000/function/c663b6e6-dd62-49fb-afe8-191fa7627a64/description/",  # noqa: E501
        },
        "archive": {
            "checksum": "51bd5fe2e7f087b203d1b4a73f3b3276b9fde96a0fff9c1f5984de96e4675d59",
            "storage_address": "http://backend-org-1-substra-backend-server.org-1:8000/function/c663b6e6-dd62-49fb-afe8-191fa7627a64/file/",  # noqa: E501
        },
        "inputs": {
            "datasamples": {"kind": "ASSET_DATA_SAMPLE", "optional": False, "multiple": True},
            "local": {"kind": "ASSET_MODEL", "optional": True, "multiple": False},
            "opener": {"kind": "ASSET_DATA_MANAGER", "optional": False, "multiple": False},
            "shared": {"kind": "ASSET_MODEL", "optional": True, "multiple": False},
        },
        "outputs": {
            "local": {"kind": "ASSET_MODEL", "multiple": False},
            "shared": {"kind": "ASSET_MODEL", "multiple": False},
        },
        "status": "FUNCTION_STATUS_READY",
    },
    "owner": "MyOrg1MSP",
    "creation_date": "2021-08-24T13:36:07.393646367Z",
    "compute_plan_key": "ed74db2f-b302-4a9d-b3d3-336eb8dcc3ff",
    "metadata": {},
    "status": "STATUS_EXECUTING",
    "worker": "MyOrg2MSP",
    "rank": 0,
    "tag": "",
    "inputs": [
        {"identifier": "opener", "asset_key": "1ae64423-aa99-4b8a-8660-61a56e4ca42d"},
        {"identifier": "datasamples", "asset_key": "1288d38c-dec2-4433-bc40-ec17f99f522a"},
    ],
    "outputs": {
        "shared": {
            "permissions": {
                "process": {"public": False, "authorized_ids": ["MyOrg1MSP", "MyOrg2MSP"]},
                "download": {"public": False, "authorized_ids": ["MyOrg1MSP", "MyOrg2MSP"]},
            },
            "transient": True,
        },
        "local": {
            "permissions": {
                "process": {"public": False, "authorized_ids": ["MyOrg2MSP"]},
                "download": {"public": False, "authorized_ids": ["MyOrg2MSP"]},
            },
            "transient": False,
        },
    },
}

PREDICTTASK = {
    "key": "afa9c7b1-21b5-4e58-a098-79de4ecede35",
    "function": {
        "key": "681eedb9-db00-4480-a66f-63c86cc20280",
        "name": "def637b111f2495bb6b4771644d2409e_test_traintask_data_samples_relative_order - Function Predict681eedb9-db00-4480-a66f-63c86cc20280",  # noqa: E501
        "owner": "MyOrg1MSP",
        "creation_date": "2021-08-24T13:36:07.428974249Z",
        "permissions": {
            "process": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
            "download": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
        },
        "metadata": {},
        "description": {
            "checksum": "756589d5971c421a388a751d533ab8ce09715c93040e9e8fff1365e831545aa2",
            "storage_address": "http://backend-org-1-substra-backend-server.org-1:8000/function/681eedb9-db00-4480-a66f-63c86cc20280/description/",  # noqa: E501
        },
        "archive": {
            "checksum": "aa8d43bf6e3341b0034a2e396451ab731ccca95a4c1d4f65a4fcd30f9081ec7d",
            "storage_address": "http://backend-org-1-substra-backend-server.org-1:8000/function/681eedb9-db00-4480-a66f-63c86cc20280/file/",  # noqa: E501
        },
        "inputs": {
            "datasamples": {"kind": "ASSET_DATA_SAMPLE", "optional": False, "multiple": True},
            "model": {"kind": "ASSET_MODEL", "optional": False, "multiple": False},
            "opener": {"kind": "ASSET_DATA_MANAGER", "optional": False, "multiple": False},
            "shared": {"kind": "ASSET_MODEL", "optional": True, "multiple": False},
        },
        "outputs": {"predictions": {"kind": "ASSET_MODEL", "multiple": False}},
        "status": "FUNCTION_STATUS_READY",
    },
    "owner": "MyOrg1MSP",
    "creation_date": "2021-08-24T13:36:07.393646367Z",
    "compute_plan_key": "a428d7a3-7458-421d-a818-7a2448225b8d",
    "metadata": {},
    "status": "STATUS_DONE",
    "worker": "MyOrg1MSP",
    "rank": 0,
    "tag": "",
    "start_date": "2021-10-12T09:28:06.947765800Z",
    "end_date": "2021-10-12T09:30:04.705947400Z",
    "inputs": [
        {"identifier": "opener", "asset_key": "d7dc4a5b-e81f-4f3f-b94c-5e2bbaca15cd"},
        {"identifier": "datasamples", "asset_key": "3180e12c-a821-434a-ad8a-a341076c7f98"},
        {"identifier": "datasamples", "asset_key": "21bb59ca-abd4-4154-b04a-44a92556a078"},
        {
            "identifier": "model",
            "parent_task_key": "30c283be-d385-424e-94a6-4d8538275260",
            "parent_task_output_identifier": "model",
        },
    ],
    "outputs": {
        "predictions": {
            "permissions": {
                "process": {"public": True, "authorized_ids": []},
                "download": {"public": True, "authorized_ids": []},
            },
            "transient": False,
        },
    },
}

TESTTASK = {
    "key": "afa9c7b1-21b5-4e58-a098-79de4ecede35",
    "function": {
        "key": "6a8ada2e-740f-46f4-af0f-11376763ed72",
        "name": "def637b111f2495bb6b4771644d2409e_test_traintask_data_samples_relative_order - Function Metric",
        "owner": "MyOrg1MSP",
        "creation_date": "2021-08-24T13:36:07.428974249Z",
        "permissions": {
            "process": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
            "download": {"public": True, "authorized_ids": ["MyOrg1MSP"]},
        },
        "metadata": {},
        "description": {
            "checksum": "756589d5971c421a388a751d533ab8ce09715c93040e9e8fff1365e831545aa2",
            "storage_address": "http://backend-org-1-substra-backend-server.org-1:8000/function/6a8ada2e-740f-46f4-af0f-11376763ed72/description/",  # noqa: E501
        },
        "archive": {
            "checksum": "aa8d43bf6e3341b0034a2e396451ab731ccca95a4c1d4f65a4fcd30f9081ec7d",
            "storage_address": "http://backend-org-1-substra-backend-server.org-1:8000/function/6a8ada2e-740f-46f4-af0f-11376763ed72/file/",  # noqa: E501
        },
        "inputs": {
            "datasamples": {"kind": "ASSET_DATA_SAMPLE", "optional": False, "multiple": True},
            "opener": {"kind": "ASSET_DATA_MANAGER", "optional": False, "multiple": False},
            "predictions": {"kind": "ASSET_MODEL", "optional": False, "multiple": False},
        },
        "outputs": {"performance": {"kind": "ASSET_PERFORMANCE", "multiple": False}},
        "status": "FUNCTION_STATUS_READY",
    },
    "owner": "MyOrg1MSP",
    "creation_date": "2021-08-24T13:36:07.393646367Z",
    "compute_plan_key": "a428d7a3-7458-421d-a818-7a2448225b8d",
    "metadata": {},
    "status": "STATUS_DONE",
    "worker": "MyOrg1MSP",
    "rank": 0,
    "tag": "",
    "start_date": "2021-10-12T09:28:06.947765800Z",
    "end_date": "2021-10-12T09:30:04.705947400Z",
    "inputs": [
        {"identifier": "opener", "asset_key": "d7dc4a5b-e81f-4f3f-b94c-5e2bbaca15cd"},
        {"identifier": "datasamples", "asset_key": "3180e12c-a821-434a-ad8a-a341076c7f98"},
        {"identifier": "datasamples", "asset_key": "21bb59ca-abd4-4154-b04a-44a92556a078"},
        {
            "identifier": "predictions",
            "parent_task_key": "05cf2e58-5862-444b-82de-cdaaead97c53",
            "parent_task_output_identifier": "predictions",
        },
    ],
    "outputs": {
        "performance": {
            "permissions": {
                "process": {"public": True, "authorized_ids": []},
                "download": {"public": True, "authorized_ids": []},
            },
            "transient": False,
        },
    },
}

TASK_LIST = [PREDICTTASK, AGGREGATETASK, COMPOSITE_TRAINTASK, TRAINTASK, TESTTASK]


COMPUTE_PLAN = {
    "key": "e983a185-5368-bd0a-0190-183af9a8e560",
    "tag": "",
    "name": "My test compute plan",
    "owner": "MyOrg1MSP",
    "creation_date": "2021-08-24T13:36:07.393646367Z",
    "start_date": "2021-08-24T13:36:37.947765800Z",
    "end_date": "2021-08-24T13:38:07.705947400Z",
    "estimated_end_date": "2021-08-24T13:38:07.705947400Z",
    "duration": "90",
    "status": "PLAN_STATUS_DONE",
    "task_count": 21,
    "waiting_builder_slot_count": 0,
    "building_count": 0,
    "waiting_parent_tasks_count": 1,
    "waiting_executor_slot_count": 2,
    "executing_count": 3,
    "canceled_count": 4,
    "failed_count": 5,
    "done_count": 6,
    "metadata": {"foo": "bar"},
}

COMPUTE_PLAN_PERF = {
    "results": [
        {
            "compute_task": {
                "key": "afa9c7b1-21b5-4e58-a098-79de4ecede35",
                "data_manager_key": "d7dc4a5b-e81f-4f3f-b94c-5e2bbaca15cd",
                "function_key": "17f98afc-2b82-4ce9-b232-1a471633d020",
                "rank": 1,
                "epoch": None,
                "round_idx": None,
                "data_samples": [
                    "3180e12c-a821-434a-ad8a-a341076c7f98",
                    "21bb59ca-abd4-4154-b04a-44a92556a078",
                ],
                "worker": "MyOrg1MSP",
            },
            "identifier": "performance",
            "perf": 0.673,
        },
        {
            "compute_task": {
                "key": "afa9c7b1-21b5-4e58-a098-79de4ecede35",
                "data_manager_key": "d7dc4a5b-e81f-4f3f-b94c-5e2bbaca15cd",
                "function_key": "17f98afc-2b82-4ce9-b232-1a471633d020",
                "rank": 2,
                "epoch": None,
                "round_idx": None,
                "data_samples": [
                    "3180e12c-a821-434a-ad8a-a341076c7f98",
                    "21bb59ca-abd4-4154-b04a-44a92556a078",
                ],
                "worker": "MyOrg1MSP",
            },
            "identifier": "performance",
            "perf": 0.834,
        },
        {
            "compute_task": {
                "key": "afa9c7b1-21b5-4e58-a098-79de4ecede35",
                "data_manager_key": "d7dc4a5b-e81f-4f3f-b94c-5e2bbaca15cd",
                "function_key": "17f98afc-2b82-4ce9-b232-1a471633d020",
                "rank": 3,
                "epoch": None,
                "round_idx": None,
                "data_samples": [
                    "3180e12c-a821-434a-ad8a-a341076c7f98",
                    "21bb59ca-abd4-4154-b04a-44a92556a078",
                ],
                "worker": "MyOrg1MSP",
            },
            "identifier": "performance",
            "perf": 0.956,
        },
    ],
}

MODEL = {
    "address": {
        "storage_address": "http://substra-backend.org-1.com/model/d7d88d74-d42f-43f4-affa-d0cdb99873fc/file/",
        "checksum": "b7881c547f7b80f01200fd2c41546010a15c66e2db46722dbbffa428a0bd0a26",
    },
    "compute_task_key": "b2b37c0f-de0a-4a61-9d00-58079efa9b33",
    "creation_date": "2022-03-01T11:22:35.791650Z",
    "key": "d7d88d74-d42f-43f4-affa-d0cdb99873fc",
    "owner": "MyOrg1MSP",
    "permissions": {
        "download": {"authorized_ids": ["MyOrg1MSP"], "public": True},
        "process": {"authorized_ids": ["MyOrg1MSP"], "public": True},
    },
}
