import os
from unittest import TestCase

from substra_sdk_py import get, list, add

dir_path = os.path.dirname(os.path.realpath(__file__))


class TestE2E(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_list_asset(self):
        res = list('dataset')
        self.assertTrue(len(res))

    def test_get_asset(self):
        datasets = list('dataset')
        res = get('dataset', datasets[0]['key'])
        self.assertEqual(res['name'], datasets[0]['name'])

    def test_add_asset(self):
        data = {
            'name': 'ISIC 2018',
            'data_opener': os.path.join(dir_path, './fixtures/dataset/opener.py'),
            'type': 'Images',
            'description': os.path.join(dir_path,  './fixtures/dataset/description.md'),
            'permissions': 'all',
        }
        res = add('dataset', data)
        self.assertEqual(res['message'], 'Error: endorsement failure during invoke. chaincode result: status:500 message:"dataset with this opener already exists" \n')
