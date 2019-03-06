from unittest import TestCase

from substra.commands import Api, Base
from substra.commands.api import DATA_ASSET, ALGO_ASSET, InvalidAssetException


class UnFinished(Base):
    pass


class TestBase(TestCase):
    def test_create_command(self):
        unfinished = UnFinished({})
        try:
            unfinished.run()
        except Exception as e:
            self.assertTrue(str(e) == 'You must implement the run() method yourself!')


class TestAPI(TestCase):
    def test_get_asset_option(self):
        class DummyApi(Api):
            ACCEPTED_ASSETS = [DATA_ASSET]

        valid_api = DummyApi({'<asset>': DATA_ASSET})
        invalid_api = DummyApi({'<asset>': ALGO_ASSET})

        self.assertEqual(DATA_ASSET, valid_api.get_asset_option())
        with self.assertRaises(InvalidAssetException):
            invalid_api.get_asset_option()
