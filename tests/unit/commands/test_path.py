import json
import os
from unittest import TestCase, mock

from substra.commands import Get, Config

model = {
    "testtuple": {
        "algo": {
            "hash": "6dcbfcf29146acd19c6a2997b2e81d0cd4e88072eea9c90bbac33f0e8573993f",
            "name": "Logistic regression",
            "storageAddress": "http://chunantes.substrabac:8001/algo/6dcbfcf29146acd19c6a2997b2e81d0cd4e88072eea9c90bbac33f0e8573993f/file/"
        },
        "challenge": {
            "hash": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
            "metrics": {
                "hash": "750f622262854341bd44f55c1018949e9c119606ef5068bd7d137040a482a756",
                "storageAddress": "http://owkin.substrabac:8000/challenge/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/metrics/"
            }
        },
        "creator": "02599f2b053b4a43f5f5cc8dad4fb7683c132b6ea9bbdaefb8290df92ec28a2a",
        "data": {
            "keys": [
                "e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1"
            ],
            "openerHash": "b4d2deeb9a59944d608e612abc8595c49186fa24075c4eb6f5e6050e4f9affa0",
            "perf": 1,
            "worker": "ad3fc6d0f1a368981afb57c45c2f0137852a65d8b7745981834cc27516470fa0"
        },
        "key": "caff5a26adc6c8d75b8990ccba8481a9c1fb9ec05e7b40670cd8e4dd804b3727",
        "log": "Test - CPU:0.00 % - Mem:0.00 GB - GPU:0.00 % - GPU Mem:0.00 GB; ",
        "model": {
            "hash": "fe900588d43263c0ce1709116fe07c68d299acbbb6cfb241b0e8795bc8a1fbcb",
            "storageAddress": "http://chunantes.substrabac:8001/model/fe900588d43263c0ce1709116fe07c68d299acbbb6cfb241b0e8795bc8a1fbcb/file/",
            "traintupleKey": "640496cd77521be69122092213c0ab4fb3385250656aed7cd71c42e324f67356"
        },
        "permissions": "all",
        "status": "done"
    },
    "traintuple": {
        "algo": {
            "hash": "6dcbfcf29146acd19c6a2997b2e81d0cd4e88072eea9c90bbac33f0e8573993f",
            "name": "Logistic regression",
            "storageAddress": "http://chunantes.substrabac:8001/algo/6dcbfcf29146acd19c6a2997b2e81d0cd4e88072eea9c90bbac33f0e8573993f/file/"
        },
        "challenge": {
            "hash": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
            "metrics": {
                "hash": "750f622262854341bd44f55c1018949e9c119606ef5068bd7d137040a482a756",
                "storageAddress": "http://owkin.substrabac:8000/challenge/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/metrics/"
            }
        },
        "creator": "02599f2b053b4a43f5f5cc8dad4fb7683c132b6ea9bbdaefb8290df92ec28a2a",
        "data": {
            "keys": [
                "62fb3263208d62c7235a046ee1d80e25512fe782254b730a9e566276b8c0ef3a",
                "42303efa663015e729159833a12ffb510ff92a6e386b8152f90f6fb14ddc94c9"
            ],
            "openerHash": "ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994",
            "perf": 1,
            "worker": "02599f2b053b4a43f5f5cc8dad4fb7683c132b6ea9bbdaefb8290df92ec28a2a"
        },
        "fltask": "",
        "inModel": None,
        "key": "640496cd77521be69122092213c0ab4fb3385250656aed7cd71c42e324f67356",
        "log": "Train - CPU:153.45 % - Mem:0.14 GB - GPU:0.00 % - GPU Mem:0.00 GB; ",
        "outModel": {
            "hash": "fe900588d43263c0ce1709116fe07c68d299acbbb6cfb241b0e8795bc8a1fbcb",
            "storageAddress": "http://chunantes.substrabac:8001/model/fe900588d43263c0ce1709116fe07c68d299acbbb6cfb241b0e8795bc8a1fbcb/file/"
        },
        "permissions": "all",
        "rank": 0,
        "status": "done"
    }
}

class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


def mocked_requests_get_model(*args, **kwargs):
    return MockResponse(model, 200)


@mock.patch('substra.commands.api.config_path', '/tmp/.substra', create=True)
class TestPath(TestCase):
    def setUp(self):
        with mock.patch('substra.commands.config.config_path', '/tmp/.substra', create=True):
            Config({
                '<url>': 'http://toto.com',
                '<version>': '1.0',
            }).run()

    def tearDown(self):
        try:
            os.remove('/tmp/.substra')
        except:
            pass

    @mock.patch('substra.commands.path.requests.get', side_effect=mocked_requests_get_model)
    def test_returns_challenge_list(self, mock_get):
        res = Get({
            '<entity>': 'model',
            '<pkhash>': '640496cd77521be69122092213c0ab4fb3385250656aed7cd71c42e324f67356',
            '<path>': 'details',
        }).run()

        self.assertTrue(json.loads(res) == model)
        self.assertEqual(len(mock_get.call_args_list), 1)
