from unittest import TestCase, mock

from substra_sdk_py.get import get as getFunction

data_manager = {
    "objectiveKeys": [],
    "description": {"hash": "7a90514f88c70002608a9868681dd1589ea598e78d00a8cd7783c3ea0f9ceb09",
                    "storageAddress": "http://127.0.0.1:8001/data_manager/ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994/description/"},
    "key": "ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994", "name": "ISIC 2018",
    "nbData": 2,
    "openerStorageAddress": "http://127.0.0.1:8001/data_manager/ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994/opener/",
    "owner": "c657699f8b03c19e6eadc7b474c23f26dd83454395266a673406f2cf44de2ca2",
    "permissions": "all",
    "size": 100,
    "type": "Images"
}

objective = {
    "descriptionStorageAddress": "http://127.0.0.1:8001/objective/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/description/",
    "key": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
    "metrics": {"hash": "750f622262854341bd44f55c1018949e9c119606ef5068bd7d137040a482a756",
                "name": "macro-average recall",
                "storageAddress": "http://127.0.0.1:8001/objective/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/metrics/"},
    "name": "Skin Lesion Classification Challenge",
    "owner": "c657699f8b03c19e6eadc7b474c23f26dd83454395266a673406f2cf44de2ca2",
    "permissions": "all",
    "testDataKeys": ["e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1"]
}


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


def mocked_requests_get_objective(*args, **kwargs):
    return MockResponse(objective, 200)


def mocked_requests_get_data_manager(*args, **kwargs):
    return MockResponse(data_manager, 200)


def mocked_requests_get_objective_fail(*args, **kwargs):
    raise Exception('fail')


class TestGet(TestCase):
    def setUp(self):
        self.config = {
            'url': 'http://toto.com',
            'version': '1.0',
            'auth': False,
            'insecure': False,
        }

    def tearDown(self):
        pass

    @mock.patch('substra_sdk_py.get.requests.get', side_effect=mocked_requests_get_objective)
    def test_returns_objective_list(self, mock_get):
        res = getFunction('objective',
                          'd5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f',
                          self.config)

        self.assertEqual(res['status_code'], 200)
        self.assertEqual(res['result'], objective)
        self.assertEqual(len(mock_get.call_args_list), 1)

    @mock.patch('substra_sdk_py.get.requests.get', side_effect=mocked_requests_get_objective_fail)
    def test_returns_objective_list_fail(self, mock_get):
        try:
            getFunction('objective',
                        'd5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f',
                        self.config)
        except Exception as e:
            print(str(e))
            self.assertTrue(str(e) == 'Failed to get objective')

        self.assertEqual(len(mock_get.call_args_list), 1)

    @mock.patch('substra_sdk_py.get.requests.get', side_effect=mocked_requests_get_data_manager)
    def test_returns_data_manager_list(self, mock_get):
        res = getFunction('data_manager',
                          'ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994',
                          self.config)

        self.assertEqual(res['status_code'], 200)
        self.assertEqual(res['result'], data_manager)
        self.assertEqual(len(mock_get.call_args_list), 1)


class TestGetConfigBasicAuth(TestCase):
    def setUp(self):
        self.data_manager_file_path = './tests/assets/data_manager/data_manager.json'

        self.config = {
            'url': 'http://toto.com',
            'version': '1.0',
            'auth': True,
            'user': 'foo',
            'password': 'bar',
            'insecure': False,
        }

    def tearDown(self):
        pass

    @mock.patch('substra_sdk_py.get.requests.get', side_effect=mocked_requests_get_objective)
    def test_returns_objective_list(self, mock_get):
        res = getFunction('objective',
                          'd5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f',
                          self.config)

        self.assertEqual(res['status_code'], 200)
        self.assertEqual(res['result'], objective)
        self.assertEqual(len(mock_get.call_args_list), 1)


class TestGetConfigInsecure(TestCase):
    def setUp(self):
        self.data_manager_file_path = './tests/assets/data_manager/data_manager.json'

        self.config = {
            'url': 'http://toto.com',
            'version': '1.0',
            'auth': True,
            'user': 'foo',
            'password': 'bar',
            'insecure': True,
        }

    def tearDown(self):
        pass

    @mock.patch('substra_sdk_py.get.requests.get', side_effect=mocked_requests_get_objective)
    def test_returns_objective_list(self, mock_get):
        res = getFunction('objective',
                          'd5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f',
                          self.config)

        self.assertEqual(res['status_code'], 200)
        self.assertEqual(res['result'], objective)
        self.assertEqual(len(mock_get.call_args_list), 1)
