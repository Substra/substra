from unittest import TestCase

from substra.commands import Api, DATA_ASSET, ALGO_ASSET, InvalidAssetException


class TestAPI(TestCase):
    def test_get_asset_option(self):
        class DummyApi(Api):
            ACCEPTED_ASSETS = [DATA_ASSET]

        valid_api = DummyApi({'<asset>': DATA_ASSET})
        invalid_api = DummyApi({'<asset>': ALGO_ASSET})

        self.assertEqual(DATA_ASSET, valid_api.get_asset_option())
        with self.assertRaises(InvalidAssetException):
            invalid_api.get_asset_option()
