import collections
import logging
import typing

from substra.sdk import exceptions
from substra.sdk import models
from substra.sdk import schemas

logger = logging.getLogger(__name__)

task_types = [
    schemas.Type.Aggregatetuple,
    schemas.Type.CompositeTraintuple,
    schemas.Type.Predicttuple,
    schemas.Type.Testtuple,
    schemas.Type.Traintuple,
]


class InMemoryDb:
    """In memory data db."""

    def __init__(self):
        # assets stored per type and per key
        self._data = collections.defaultdict(dict)

    def add(self, asset):
        """Add an asset."""
        type_ = asset.__class__.type_
        key = getattr(asset, "key", None)
        if not key:
            key = asset.id
        if key in self._data[type_]:
            raise exceptions.KeyAlreadyExistsError(f"The asset key {key} of type {type_} has already been used.")
        self._data[type_][key] = asset
        logger.info(f"{type_} with key '{key}' has been created.")

        return asset

    def get(self, type_, key: str):
        """Return asset."""
        try:
            asset = self._data[type_][key]
        except KeyError:
            raise exceptions.NotFound(f"Wrong pk {key}", 404)

        if type_ in task_types:
            self._link_inputs_addressable(asset)
        return asset

    def _match_asset(self, asset: models._Model, attribute: str, values: typing.Union[typing.Dict, typing.List]):
        """Checks if an asset attributes matches the given values.
        For the metadata, it checks that all the given filters returns True (AND condition)"""
        if attribute == "metadata":
            metadata_conditions = []
            for value in values:
                if value["type"] == models.MetadataFilterType.exists:
                    metadata_conditions.append(value["key"] in asset.metadata.keys())

                elif asset.metadata.get(value["key"]) is None:
                    # for is_equal and contains, if the key is not there then return False
                    metadata_conditions.append(False)

                elif value["type"] == models.MetadataFilterType.is_equal:
                    metadata_conditions.append(str(value["value"]) == str(asset.metadata[value["key"]]))

                elif value["type"] == models.MetadataFilterType.contains:
                    metadata_conditions.append(str(value["value"]) in str(asset.metadata.get(value["key"])))
                else:
                    raise NotImplementedError

            return all(metadata_conditions)

        return str(getattr(asset, attribute)) in values

    def _filter_assets(
        self, db_assets: typing.List[models._Model], filters: typing.Dict[str, typing.List[str]]
    ) -> typing.List[models._Model]:
        """Return assets matching al the given filters"""

        matching_assets = [
            asset
            for asset in db_assets
            if all(self._match_asset(asset, attribute, values) for attribute, values in filters.items())
        ]
        return matching_assets

    def list(
        self, type_: str, filters: typing.Dict[str, typing.List[str]], order_by: str = None, ascending: bool = False
    ):
        """List assets by filters.

        Args:
            type_ (str): asset type. e.g. "algo"
            filters (dict, optional): keys = attributes, values = list of values for this attribute.
                e.g. {"name": ["name1", "name2"]}. "," corresponds to an "OR". Defaults to None.
            order_by (str, optional): attribute name to order the results on. Defaults to None.
                e.g. "name" for an ordering on name.
            ascending (bool, optional): to reverse ordering. Defaults to False (descending order).

        Returns:
            List[Dict] : a List of assets (dicts)
        """
        # get all assets of this type
        assets = list(self._data[type_].values())

        if filters:
            assets = self._filter_assets(assets, filters)
        if order_by:
            assets.sort(key=lambda x: getattr(x, order_by), reverse=(not ascending))

        if type_ in task_types:
            for item in assets:
                self._link_inputs_addressable(item)

        return assets

    def _get_input_kind(self, asset, input):
        for algo_input in asset.algo.inputs:
            if algo_input.identifier == input.identifier:
                return algo_input.kind

    def _link_inputs_addressable(self, asset):
        for input in asset.inputs:
            input_kind = self._get_input_kind(asset, input)
            if input_kind == schemas.AssetKind.data_manager:
                if not input.asset_key:
                    return
                input_data_manager = self.get(schemas.Type.Dataset, input.asset_key)
                input.permissions = input_data_manager.permissions
                input.addressable = input_data_manager.opener
            if input_kind == schemas.AssetKind.model:
                if input.parent_task_key and input.parent_task_output_identifier:
                    parent_task = None
                    for type_ in enumerate(task_types):
                        if input.parent_task_key not in self._data[type_]:
                            continue
                        parent_task = self._data[type_][input.parent_task_key]
                if parent_task:
                    input.permissions = parent_task.outputs[input.parent_task_output_identifier].permissions
                    input.addressable = parent_task.outputs[input.parent_task_output_identifier].value.address

    def update(self, asset):
        type_ = asset.__class__.type_
        key = asset.key

        if key not in self._data[type_]:
            raise exceptions.NotFound(f"Wrong pk {key}", 404)

        self._data[type_][key] = asset
        return


db = InMemoryDb()


def get_db():
    return db
