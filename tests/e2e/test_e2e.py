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
        res = self.client.list('data_manager')
        self.assertTrue(len(res))

    def test_get_asset(self):
        res_l = self.client.list('data_manager')
        res = self.client.get('data_manager', res_l['result'][0]['key'])

        self.assertEqual(res['result']['name'], res_l['result'][0]['name'])

    def test_add_asset(self):
        data = {
            'name': 'ISIC 2018',
            'data_opener': os.path.join(dir_path, './fixtures/data_manager/opener.py'),
            'type': 'Images',
            'description': os.path.join(dir_path, './fixtures/data_manager/description.md'),
            'permissions': 'all',
        }
        res = self.client.add('data_manager', data)

        # will fail first time if no precedent populate
        self.assertEqual(res['result']['message'], [{'pkhash': ['data_manager with this pkhash already exists.']}])
