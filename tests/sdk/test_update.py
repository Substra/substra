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

from substra.sdk import models, schemas

from .. import datastore
from .utils import mock_requests


def test_update_dataset(client, mocker):
    m = mock_requests(mocker, "post", response={"key": "dataset_key"})

    response = client.link_dataset_with_objective(
        'a key',
        'an another key',
    )

    assert response == "dataset_key"
    m.assert_called()


def test_update_compute_plan(client, mocker):
    item = datastore.COMPUTE_PLAN
    m = mock_requests(mocker, "post", response=item)
    m_get = mock_requests(mocker, "get", response=datastore.COMPUTE_PLAN)

    response = client.update_compute_plan('foo', {})

    assert response == models.ComputePlan(**item)
    m.assert_called
    m_get.assert_called


def test_update_compute_plan_with_schema(client, mocker):
    item = datastore.COMPUTE_PLAN
    m = mock_requests(mocker, "post", response=item)
    m_get = mock_requests(mocker, "get", response=datastore.COMPUTE_PLAN)

    response = client.update_compute_plan('foo', schemas.UpdateComputePlanSpec())

    assert response == models.ComputePlan(**item)
    m.assert_called
    m_get.assert_called
