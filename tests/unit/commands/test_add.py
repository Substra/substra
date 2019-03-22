import json
import os
from io import StringIO
import sys

from unittest import TestCase, mock

from substra.commands import Add, Config

data_manager = {
    "challengeKey": "",
    "description": {"hash": "7a90514f88c70002608a9868681dd1589ea598e78d00a8cd7783c3ea0f9ceb09",
                    "storageAddress": "http://127.0.0.1:8001/data_manager/ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994/description/"},
    "key": "ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994", "name": "ISIC 2018", "nbData": 2,
    "openerStorageAddress": "http://127.0.0.1:8001/data_manager/ccbaa3372bc74bce39ce3b138f558b3a7558958ef2f244576e18ed75b0cea994/opener/",
    "owner": "c657699f8b03c19e6eadc7b474c23f26dd83454395266a673406f2cf44de2ca2", "permissions": "all",
    "size": 100, "type": "Images"}

challenge = {
    "descriptionStorageAddress": "http://127.0.0.1:8001/challenge/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/description/",
    "key": "d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f",
    "metrics": {"hash": "750f622262854341bd44f55c1018949e9c119606ef5068bd7d137040a482a756",
                "name": "macro-average recall",
                "storageAddress": "http://127.0.0.1:8001/challenge/d5002e1cd50bd5de5341df8a7b7d11b6437154b3b08f531c9b8f93889855c66f/metrics/"},
    "name": "Skin Lesion Classification Challenge",
    "owner": "c657699f8b03c19e6eadc7b474c23f26dd83454395266a673406f2cf44de2ca2", "permissions": "all",
    "testDataKeys": ["e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1"]}

algo = {"challengeKey": "6b8d16ac3eae240743428591943fa8e66b34d4a7e0f4eb8e560485c7617c222c",
        "description": {"hash": "3b1281cbdd6ebfec650d0a9f932a64e45a27262848065d7cecf11fd7191b4b1f",
                        "storageAddress": "http://127.0.0.1:8001/algo/7742aea2001ceb40e9ce8a37fa27237d5b2d1f574e06d48677af945cfdf42ec0/description/"},
        "key": "7742aea2001ceb40e9ce8a37fa27237d5b2d1f574e06d48677af945cfdf42ec0",
        "name": "Logistic regression for balanced problem",
        "owner": "c657699f8b03c19e6eadc7b474c23f26dd83454395266a673406f2cf44de2ca2", "permissions": "all",
        "storageAddress": "http://127.0.0.1:8001/algo/7742aea2001ceb40e9ce8a37fa27237d5b2d1f574e06d48677af945cfdf42ec0/file/"}

data = {"pkhash": "e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1", "validated": True,
        "file": "http://127.0.0.1:8000/media/data/e11aeec290749e4c50c91305e10463eced8dbf3808971ec0c6ea0e36cb7ab3e1/0024700.zip"}


def mocked_client_add(asset, st):
    return {'result': asset,
            'status_code': st}

@mock.patch('substra.commands.api.config_path', '/tmp/.substra', create=True)
class TestAdd(TestCase):
    def setUp(self):
        self.data_manager_file_path = './tests/assets/data_manager/data_manager.json'
        self.challenge_file_path = './tests/assets/challenge/challenge.json'
        self.algo_file_path = './tests/assets/algo/algo.json'
        self.data_file_path = './tests/assets/data/data.json'

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

    @mock.patch('substra.commands.api.Client.add', return_value=mocked_client_add(data_manager, 201))
    def test_add_data_manager(self, mock_add):
        # open data_manager file
        with open(self.data_manager_file_path, 'r') as f:
            data = f.read()

            res = Add({
                '<asset>': 'data-manager',
                '<args>': data,
            }).run()

            self.assertEqual(json.loads(res)['status_code'], 201)
            self.assertEqual(json.loads(res)['result'], data_manager)
            self.assertEqual(len(mock_add.call_args_list), 1)

    @mock.patch('substra.commands.api.Client.add', return_value=mocked_client_add(data_manager, 201))
    def test_add_data_manager_from_file(self, mock_add):

        res = Add({
            '<asset>': 'data-manager',
            '<args>': self.data_manager_file_path,
        }).run()

        self.assertEqual(json.loads(res)['status_code'], 201)
        self.assertEqual(json.loads(res)['result'], data_manager)
        self.assertEqual(len(mock_add.call_args_list), 1)

    @mock.patch('substra.commands.api.Client.add', return_value=mocked_client_add(data_manager, 201))
    def test_add_data_manager_invalid_args(self, mock_add):
        with self.assertRaises(Exception) as e:
            Add({
                '<asset>': 'data-manager',
                '<args>': 'test',
            }).run()
            self.assertEqual(str(e), 'Invalid args. Please review help')

        self.assertEqual(len(mock_add.call_args_list), 0)

    @mock.patch('substra.commands.api.Client.add', return_value=mocked_client_add(challenge, 201))
    def test_add_challenge(self, mock_add):
        # open challenge file
        with open(self.challenge_file_path, 'r') as f:
            data = f.read()

            res = Add({
                '<asset>': 'challenge',
                '<args>': data,
            }).run()

            self.assertEqual(json.loads(res)['status_code'], 201)
            self.assertEqual(json.loads(res)['result'], challenge)
            self.assertEqual(len(mock_add.call_args_list), 1)

    @mock.patch('substra.commands.api.Client.add', return_value=mocked_client_add(algo, 201))
    def test_add_algo(self, mock_add):
        # open algo file
        with open(self.algo_file_path, 'r') as f:
            data = f.read()

            res = Add({
                '<asset>': 'algo',
                '<args>': data,
            }).run()

            self.assertEqual(json.loads(res)['status_code'], 201)
            self.assertEqual(json.loads(res)['result'], algo)
            self.assertEqual(len(mock_add.call_args_list), 1)

    @mock.patch('substra.commands.api.Client.add', return_value=mocked_client_add(data, 201))
    def test_add_data(self, mock_add):
        # open algo file
        with open(self.data_file_path, 'r') as f:
            content = f.read()

            res = Add({
                '<asset>': 'data',
                '<args>': content,
            }).run()

            print(res)

            self.assertEqual(json.loads(res)['status_code'], 201)
            self.assertEqual(json.loads(res)['result'], data)
            self.assertEqual(len(mock_add.call_args_list), 1)

    @mock.patch('substra.commands.api.Client.add', side_effect=Exception('fail'))
    def test_returns_challenge_list_fail(self, mock_add):
        with open(self.challenge_file_path, 'r') as f:
            data = f.read()
            with self.assertRaises(Exception) as e:
                Add({
                    '<asset>': 'challenge',
                    '<args>': data,
                }).run()
                self.assertTrue(str(e) == 'Failed to create challenge')

            self.assertEqual(len(mock_add.call_args_list), 1)


@mock.patch('substra.commands.api.config_path', '/tmp/.substra', create=True)
class TestAddNoConfig(TestCase):
    def setUp(self):
        self.data_manager_file_path = './tests/assets/data_manager/data_manager.json'
        try:
            os.remove('/tmp/.substra')
        except:
            pass

    @mock.patch('substra.commands.api.Client.add', return_value=mocked_client_add(data_manager, 201))
    def test_add_data_manager(self, mock_add):
        # open data_manager file
        with open(self.data_manager_file_path, 'r') as f:
            data = f.read()

            saved_stdout = sys.stdout

            out = StringIO()
            sys.stdout = out

            with self.assertRaises(SystemExit) as se:
                Add({
                    '<asset>': 'data-manager',
                    '<args>': data,
                }).run()

                self.assertEqual(se.exception.code, 1)

            e = out.getvalue().strip()
            sys.stdout = saved_stdout
            self.assertEqual(str(e), 'No config file "/tmp/.substra" found, please run "substra config <url> [<version>] [--profile=<profile>] [--config=<configuration_file_path>]"')

            self.assertEqual(len(mock_add.call_args_list), 0)


@mock.patch('substra.commands.api.config_path', '/tmp/.substra', create=True)
class TestAddConfigBasicAuth(TestCase):
    def setUp(self):
        self.data_manager_file_path = './tests/assets/data_manager/data_manager.json'

        with mock.patch('substra.commands.config.config_path', '/tmp/.substra', create=True):
            Config({
                '<url>': 'http://toto.com',
                '<version>': '1.0',
                '<user>': 'foo',
                '<password>': 'bar'
            }).run()

    def tearDown(self):
        try:
            os.remove('/tmp/.substra')
        except:
            pass

    @mock.patch('substra.commands.api.Client.add', return_value=mocked_client_add(data_manager, 201))
    def test_add_data_manager(self, mock_add):
        # open data_manager file
        with open(self.data_manager_file_path, 'r') as f:
            data = f.read()

            res = Add({
                '<asset>': 'data-manager',
                '<args>': data,
            }).run()

            self.assertEqual(json.loads(res)['status_code'], 201)
            self.assertEqual(json.loads(res)['result'], data_manager)
            self.assertEqual(len(mock_add.call_args_list), 1)


@mock.patch('substra.commands.api.config_path', '/tmp/.substra', create=True)
class TestAddConfigInsecure(TestCase):
    def setUp(self):
        self.data_manager_file_path = './tests/assets/data_manager/data_manager.json'

        with mock.patch('substra.commands.config.config_path', '/tmp/.substra', create=True):
            Config({
                '<url>': 'http://toto.com',
                '<version>': '1.0',
                '<user>': 'foo',
                '<password>': 'bar',
                '--insecure': True
            }).run()

    def tearDown(self):
        try:
            os.remove('/tmp/.substra')
        except:
            pass

    @mock.patch('substra.commands.api.Client.add', return_value=mocked_client_add(data_manager, 201))
    def test_add_data_manager(self, mock_add):
        # open data_manager file
        with open(self.data_manager_file_path, 'r') as f:
            data = f.read()

            res = Add({
                '<asset>': 'data-manager',
                '<args>': data,
            }).run()

            self.assertEqual(json.loads(res)['status_code'], 201)
            self.assertEqual(json.loads(res)['result'], data_manager)
            self.assertEqual(len(mock_add.call_args_list), 1)
