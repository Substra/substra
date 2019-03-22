from unittest import TestCase

from substra.commands import Api, DATA_SAMPLE_ASSET, ALGO_ASSET, InvalidAssetException


class TestAPI(TestCase):
    def test_get_asset_option(self):
        class DummyApi(Api):
            ACCEPTED_ASSETS = [DATA_SAMPLE_ASSET]

        valid_api = DummyApi({'<asset>': DATA_SAMPLE_ASSET})
        invalid_api = DummyApi({'<asset>': ALGO_ASSET})

        self.assertEqual(DATA_SAMPLE_ASSET,
                         valid_api.get_asset_option().replace('_', '-'))
        with self.assertRaises(InvalidAssetException):
            invalid_api.get_asset_option()
