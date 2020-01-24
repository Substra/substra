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
import pytest
import substra

from .. import datastore
from .utils import mock_requests


def test_add_dataset(client, dataset_query, mocker):
    m_post = mock_requests(mocker, "post", response=datastore.DATASET)
    m_get = mock_requests(mocker, "get", response=datastore.DATASET)
    response = client.add_dataset(dataset_query)

    assert response == datastore.DATASET
    m_post.assert_called()
    m_get.assert_called()


def test_add_dataset_invalid_args(client, dataset_query, mocker):
    mock_requests(mocker, "post", response=datastore.DATASET)
    del dataset_query['data_opener']

    with pytest.raises(substra.sdk.exceptions.LoadDataException):
        client.add_dataset(dataset_query)


def test_add_dataset_response_failure_500(client, dataset_query, mocker):
    mock_requests(mocker, "post", status=500)

    with pytest.raises(substra.sdk.exceptions.InternalServerError):
        client.add_dataset(dataset_query)


def test_add_dataset_response_failure_409(client, dataset_query, mocker):
    mock_requests(mocker, "post", response={"pkhash": "42"}, status=409)

    with pytest.raises(substra.sdk.exceptions.AlreadyExists) as exc_info:
        client.add_dataset(dataset_query)

    assert exc_info.value.pkhash == "42"


def test_add_objective(client, objective_query, mocker):
    m_post = mock_requests(mocker, "post", response=datastore.OBJECTIVE)
    m_get = mock_requests(mocker, "get", response=datastore.OBJECTIVE)
    response = client.add_objective(objective_query)

    assert response == datastore.OBJECTIVE
    m_post.assert_called()
    m_get.assert_called()


def test_add_algo(client, algo_query, mocker):
    m_post = mock_requests(mocker, "post", response=datastore.ALGO)
    m_get = mock_requests(mocker, "get", response=datastore.ALGO)
    response = client.add_algo(algo_query)

    assert response == datastore.ALGO
    m_post.assert_called()
    m_get.assert_called()


def test_add_aggregate_algo(client, algo_query, mocker):
    m_post = mock_requests(mocker, "post", response=datastore.AGGREGATE_ALGO)
    m_get = mock_requests(mocker, "get", response=datastore.AGGREGATE_ALGO)
    response = client.add_aggregate_algo(algo_query)

    assert response == datastore.AGGREGATE_ALGO
    m_post.assert_called()
    m_get.assert_called()


def test_add_composite_algo(client, algo_query, mocker):
    m_post = mock_requests(mocker, "post", response=datastore.COMPOSITE_ALGO)
    m_get = mock_requests(mocker, "get", response=datastore.COMPOSITE_ALGO)
    response = client.add_composite_algo(algo_query)

    assert response == datastore.COMPOSITE_ALGO
    m_post.assert_called()
    m_get.assert_called()


def test_add_data_sample(client, data_sample_query, mocker):
    server_response = [{"key": "42"}]
    m = mock_requests(mocker, "post", response=server_response)
    response = client.add_data_sample(data_sample_query)

    assert response == server_response[0]
    m.assert_called()


def test_add_data_sample_already_exists(client, data_sample_query, mocker):
    m = mock_requests(mocker, "post", response=[{"pkhash": "42"}], status=409)
    response = client.add_data_sample(data_sample_query, exist_ok=True)

    assert response == {"pkhash": "42"}
    m.assert_called()


# We try to add multiple data samples instead of a single one
def test_add_data_sample_with_paths(client, data_samples_query):
    with pytest.raises(ValueError):
        client.add_data_sample(data_samples_query)


def test_add_data_samples(client, data_samples_query, mocker):
    server_response = [{"key": "42"}]
    m = mock_requests(mocker, "post", response=server_response)
    response = client.add_data_samples(data_samples_query)

    assert response == server_response
    m.assert_called()


# We try to add a single data sample instead of multiple ones
def test_add_data_samples_with_path(client, data_sample_query):
    with pytest.raises(ValueError):
        client.add_data_samples(data_sample_query)
