import os
from unittest import TestCase

from substra_sdk_py.config import ConfigManager

dir_path = os.path.dirname(os.path.realpath(__file__))


class TestConfig(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_config(self):
        configManager = ConfigManager()
        conf = configManager.create('owkin', url='http://owkin.substrabac:8000', version='0.0')
        self.assertTrue(len(configManager.config) >= 2)
        self.assertEqual(configManager.get('owkin'), conf)

    def test_get_config(self):
        configManager = ConfigManager()
        conf = configManager.get('owkin')
        self.assertEqual(configManager.get('owkin'), conf)
