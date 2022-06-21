# Copyright 2018 Owkin, inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import collections
import logging
import typing

from substra.sdk import exceptions
from substra.sdk import models

logger = logging.getLogger(__name__)


class InMemoryDb:
    """In memory data db."""

    def __init__(self):
        # assets stored per type and per key
        self._data = collections.defaultdict(dict)

    def add(self, asset):
        """Add an asset."""
        type_ = asset.__class__.type_
        key = asset.key
        if key in self._data[type_]:
            raise exceptions.KeyAlreadyExistsError(f"The asset key {key} of type {type_} has already been used.")
        self._data[type_][key] = asset
        logger.info(f"{type_} with key '{key}' has been created.")

        return asset

    def get(self, type_, key: str):
        """Return asset."""
        try:
            return self._data[type_][key]
        except KeyError:
            raise exceptions.NotFound(f"Wrong pk {key}", 404)

    def _filter_assets(
        self, db_assets: typing.List[models._Model], filters: typing.Dict[str, typing.List[str]]
    ) -> typing.List[models._Model]:
        """Return assets matching one of the values for a given attribute (OR group), and the remaining ones"""
        matching_assets = []

        for asset in db_assets:
            if all(str(getattr(asset, attribute)) in values for attribute, values in filters.items()):
                matching_assets.append(asset)

        return matching_assets

    def list(
        self, type_: str, filters: typing.Dict[str, typing.List[str]], order_by: str = None, ascending: bool = False
    ):
        """List assets by filters.

        Args:
            asset_type (str): asset type. e.g. "algo"
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

        return assets

    def update(self, asset):
        type_ = asset.__class__.type_
        key = asset.key

        if key not in self._data[type_]:
            raise exceptions.NotFound(f"Wrong pk {key}", 404)

        self._data[type_][key] = asset
        return asset
