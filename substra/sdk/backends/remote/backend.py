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

from copy import deepcopy
import logging
import math
import json

from substra.sdk import exceptions, schemas, utils
from substra.sdk.backends import base
from substra.sdk.backends.remote import rest_client

logger = logging.getLogger(__name__)

DEFAULT_RETRY_TIMEOUT = 5 * 60
COMPUTE_PLAN_BATCH_SIZE = 100


def _get_asset_key(data):
    return data.get('pkhash') or data.get('key') or data.get('computePlanID')


def _find_asset_field(data, field):
    """Find data value where location is defined as `field.subfield...`."""
    for f in field.split('.'):
        data = data[f]
    return data


class Remote(base.BaseBackend):

    def __init__(self, url, insecure, token, retry_timeout):
        self._client = rest_client.Client(url, insecure, token)
        self._retry_timeout = retry_timeout or DEFAULT_RETRY_TIMEOUT

    def login(self, username, password):
        return self._client.login(username, password)

    def get(self, asset_type, key):
        """Get an asset by key."""
        return self._client.get(asset_type.to_server(), key)

    def list(self, asset_type, filters=None):
        """List assets per asset type."""
        return self._client.list(asset_type.to_server(), filters)

    def _add(self, asset, data, files=None, exist_ok=False):
        data = deepcopy(data)  # make a deep copy for avoiding modification by reference
        if files:
            kwargs = {
                'data': {
                    'json': json.dumps(data),
                },
                'files': files,
            }

        else:
            kwargs = {
                'json': data,
            }

        return self._client.add(
            asset.to_server(),
            retry_timeout=self._retry_timeout,
            exist_ok=exist_ok,
            **kwargs,
        )

    def _add_data_samples(self, spec, exist_ok, spec_options):
        """Add data sample(s)."""
        # data sample(s) creation must be handled separately as the get request is not
        # available on this ressource. On top of that the exist ok option is working
        # only when adding a single data sample (and not for bulk upload)
        try:
            with spec.build_request_kwargs(**spec_options) as (data, files):
                data_samples = self._add(
                    schemas.Type.DataSample, data, files, exist_ok=exist_ok)

        except exceptions.AlreadyExists as e:
            if not exist_ok or spec.is_many():
                raise

            key = e.pkhash[0]
            logger.warning(f"data_sample already exists: key='{key}'")
            data_samples = [{'pkhash': key}]

        # there is currently a single route in the backend to add a single or many
        # datasamples, this route always returned a list of created data sample keys
        return data_samples if spec.is_many() else data_samples[0]

    def add(self, spec, exist_ok=False, spec_options=None):
        """Add an asset."""
        spec_options = spec_options or {}
        asset_type = spec.__class__.type_

        if asset_type == schemas.Type.DataSample:
            # data sample corner case
            return self._add_data_samples(
                spec,
                exist_ok=exist_ok,
                spec_options=spec_options,
            )
        elif asset_type == schemas.Type.ComputePlan:
            # Compute plan auto batching feature
            return self.__auto_batching_compute_plan(
                spec=spec,
                exist_ok=exist_ok,
                spec_options=spec_options,
            )

        with spec.build_request_kwargs(**spec_options) as (data, files):
            response = self._add(asset_type, data, files=files, exist_ok=exist_ok)
        # The backend has inconsistent API responses when getting or adding an asset
        # (with much less data when responding to adds).
        # A second GET request hides the discrepancies.
        key = _get_asset_key(response)
        return self.get(asset_type, key)

    def __fill_tuple_lists(
        self,
        spec,
        tuple_graph,
        traintuples,
        aggregatetuples,
        composite_traintuples,
        testtuples_by_train_id,
    ):
        for elem_id in tuple_graph:
            if elem_id in traintuples:
                spec.traintuples.append(traintuples[elem_id])
            elif elem_id in aggregatetuples:
                spec.aggregatetuples.append(aggregatetuples[elem_id])
            elif elem_id in composite_traintuples:
                spec.composite_traintuples.append(composite_traintuples[elem_id])
            if elem_id in testtuples_by_train_id:
                spec.testtuples.append(testtuples_by_train_id[elem_id])

    def __get_testtuples_by_train_id(self, spec):
        testtuples_by_train_id = dict()
        for testtuple in spec.testtuples:
            testtuples_by_train_id[testtuple.traintuple_id] = testtuple
        return testtuples_by_train_id

    def __auto_batching_compute_plan(self,
                                     spec,
                                     compute_plan_id=None,
                                     exist_ok=None,
                                     spec_options=None):
        # Auto batching of the compute plan tuples
        # if compute_plan_id is None, we first create the compute plan
        (
            tuple_graph,
            traintuples,
            aggregatetuples,
            composite_traintuples
        ) = spec.get_dependency_graph()
        visited = utils.compute_ranks(node_graph=tuple_graph)
        sorted_by_rank = sorted(visited.items(), key=lambda item: item[1])
        testtuples_by_train_id = self.__get_testtuples_by_train_id(spec)
        compute_plan_parts = list()
        compute_plan = None
        for i in range(math.ceil(len(sorted_by_rank) / COMPUTE_PLAN_BATCH_SIZE)):
            start = i * COMPUTE_PLAN_BATCH_SIZE
            end = min(len(sorted_by_rank), (i + 1) * COMPUTE_PLAN_BATCH_SIZE)
            if i == 0 and compute_plan_id is None:
                tmp_spec = deepcopy(spec)
                tmp_spec.traintuples = list()
                tmp_spec.composite_traintuples = list()
                tmp_spec.aggregatetuples = list()
                tmp_spec.testtuples = list()
                self.__fill_tuple_lists(
                    tmp_spec,
                    sorted_by_rank[start:end],
                    traintuples,
                    aggregatetuples,
                    composite_traintuples,
                    testtuples_by_train_id
                )
                with tmp_spec.build_request_kwargs(**spec_options) as (data, files):
                    compute_plan = self._add(
                        schemas.Type.ComputePlan,
                        data,
                        files=files,
                        exist_ok=exist_ok
                    )
                compute_plan_id = compute_plan['compute_plan_id']
            else:
                tmp_spec = schemas.UpdateComputePlanSpec(
                    traintuples=list(),
                    composite_traintuples=list(),
                    aggregatetuples=list(),
                    testtuples=list(),
                )
                self.__fill_tuple_lists(
                    tmp_spec,
                    sorted_by_rank[start:end],
                    traintuples,
                    aggregatetuples,
                    composite_traintuples,
                    testtuples_by_train_id
                )
                compute_plan_part = self._client.request(
                    'post',
                    schemas.Type.ComputePlan.to_server(),
                    path=f"{compute_plan_id}/update_ledger/",
                    json=tmp_spec.dict(exclude_none=True),
                )
                compute_plan_parts.append(compute_plan_part)
        # TODO assemble compute_plan and compute_plan_parts to return response
        result = compute_plan
        return result

    def update_compute_plan(self, compute_plan_id, spec):
        return self.__auto_batching_compute_plan(
            spec=spec,
            compute_plan_id=compute_plan_id
        )

    def link_dataset_with_objective(self, dataset_key, objective_key):
        return self._client.request(
            'post',
            schemas.Type.Dataset.to_server(),
            path=f"{dataset_key}/update_ledger/",
            data={'objective_key': objective_key, },
        )

    def link_dataset_with_data_samples(self, dataset_key, data_sample_keys):
        data = {
            'data_manager_keys': [dataset_key],
            'data_sample_keys': data_sample_keys,
        }
        return self._client.request(
            'post',
            schemas.Type.DataSample.to_server(),
            path="bulk_update/",
            data=data,
        )

    def download(self, asset_type, url_field_path, key, destination):
        data = self.get(asset_type, key)
        url = _find_asset_field(data, url_field_path)
        response = self._client.get_data(url, stream=True)
        chunk_size = 1024
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size):
                f.write(chunk)

        return destination

    def describe(self, asset_type, key):
        data = self.get(asset_type, key)
        url = data['description']['storageAddress']
        r = self._client.get_data(url)
        return r.text

    def leaderboard(self, objective_key, sort='desc'):
        return self._client.request(
            'get',
            schemas.Type.Objective.to_server(),
            f'{objective_key}/leaderboard',
            params={'sort': sort},
        )

    def cancel_compute_plan(self, compute_plan_id):
        return self._client.request(
            'post',
            schemas.Type.ComputePlan.to_server(),
            path=f"{compute_plan_id}/cancel",
        )
