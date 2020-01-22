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

import json

from .. import datastore
from .utils import mock_requests


def test_update_dataset(client, mocker):
    item = datastore.DATASET
    m = mock_requests(mocker, "post", response=item)

    response = client.update_dataset(
        'a key',
        {'objective_key': 'an another key', })

    assert response == item
    assert m.is_called()


def test_update_compute_plan(client, mocker):
    item = {}
    item.update(datastore.COMPUTE_PLAN)
    item.update({'keysToIDsMapping': {'foo': 'bar'}})
    m = mock_requests(mocker, "post", response=item)

    response = client.update_compute_plan('foo', {})

    assert response == item
    assert m.is_called()

    keys_to_ids_mapping_file = response['keys_to_ids_mapping_file']
    with open(keys_to_ids_mapping_file, 'r') as f:
        mapping = json.load(f)

    assert mapping == {'foo': 'bar'}
