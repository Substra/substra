from unittest import TestCase

from substra import assets
from substra.commands import Api, InvalidAssetException


class TestAPI(TestCase):
    def test_get_asset_option(self):
        class DummyApi(Api):
            ACCEPTED_ASSETS = [assets.DATA_SAMPLE]

        valid_api = DummyApi({'<asset>': assets.DATA_SAMPLE})
        invalid_api = DummyApi({'<asset>': assets.ALGO})

        self.assertEqual(assets.DATA_SAMPLE, valid_api.get_asset_option())
        with self.assertRaises(InvalidAssetException):
            invalid_api.get_asset_option()
