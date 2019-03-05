import os
from unittest import TestCase

from substra_sdk_py import Client

dir_path = os.path.dirname(os.path.realpath(__file__))


class TestE2E(TestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_list_asset(self):
        res = self.client.list('dataset')
        self.assertTrue(len(res))

    def test_get_asset(self):
        datasets = self.client.list('dataset')
        res = self.client.get('dataset', datasets[0]['key'])
        self.assertEqual(res['name'], datasets[0]['name'])

    def test_add_asset(self):
        data = {
            'name': 'ISIC 2018',
            'data_opener': os.path.join(dir_path, './fixtures/dataset/opener.py'),
            'type': 'Images',
            'description': os.path.join(dir_path, './fixtures/dataset/description.md'),
            'permissions': 'all',
        }
        res = self.client.add('dataset', data)

        print(res)
        self.assertEqual(res['message'], [{'pkhash': ['dataset with this pkhash already exists.']}])
