import pydantic
import pytest

import substra
from substra.sdk import models
from substra.sdk.exceptions import ComputePlanKeyFormatError

from .. import datastore
from ..utils import mock_requests


def test_add_dataset(client, dataset_query, mocker):
    m_post = mock_requests(mocker, "post", response=datastore.DATASET)
    m_get = mock_requests(mocker, "get", response=datastore.DATASET)
    key = client.add_dataset(dataset_query)
    response = client.get_dataset(key)

    assert response == models.Dataset(**datastore.DATASET)
    m_post.assert_called()
    m_get.assert_called()


def test_add_dataset_invalid_args(client, dataset_query, mocker):
    mock_requests(mocker, "post", response=datastore.DATASET)
    del dataset_query["data_opener"]

    with pytest.raises(pydantic.ValidationError):
        client.add_dataset(dataset_query)


def test_add_dataset_response_failure_500(client, dataset_query, mocker):
    mock_requests(mocker, "post", status=500)

    with pytest.raises(substra.sdk.exceptions.InternalServerError):
        client.add_dataset(dataset_query)


def test_add_dataset_409_success(client, dataset_query, mocker):
    mock_requests(mocker, "post", response={"key": datastore.DATASET["key"]}, status=409)
    mock_requests(mocker, "get", response=datastore.DATASET)

    key = client.add_dataset(dataset_query)

    assert key == datastore.DATASET["key"]


def test_add_function(client, function_query, mocker):
    m_post = mock_requests(mocker, "post", response=datastore.FUNCTION)
    m_get = mock_requests(mocker, "get", response=datastore.FUNCTION)
    key = client.add_function(function_query)
    response = client.get_function(key)

    assert response == models.Function(**datastore.FUNCTION)
    m_post.assert_called()
    m_get.assert_called()


def test_add_data_sample(client, data_sample_query, mocker):
    server_response = [{"key": "42"}]
    m = mock_requests(mocker, "post", response=server_response)
    response = client.add_data_sample(data_sample_query)

    assert response == server_response[0]["key"]
    m.assert_called()


def test_add_data_sample_already_exists(client, data_sample_query, mocker):
    m = mock_requests(mocker, "post", response=[{"key": "42"}], status=409)
    response = client.add_data_sample(data_sample_query)

    assert response == "42"
    m.assert_called()


# We try to add multiple data samples instead of a single one
def test_add_data_sample_with_paths(client, data_samples_query):
    with pytest.raises(ValueError):
        client.add_data_sample(data_samples_query)


def test_add_data_samples(client, data_samples_query, mocker):
    server_response = [{"key": "42"}]
    m = mock_requests(mocker, "post", response=server_response)
    response = client.add_data_samples(data_samples_query)

    assert response == ["42"]
    m.assert_called()


# We try to add a single data sample instead of multiple ones
def test_add_data_samples_with_path(client, data_sample_query):
    with pytest.raises(ValueError):
        client.add_data_samples(data_sample_query)


def test_add_compute_plan_wrong_key_format(client):
    with pytest.raises(ComputePlanKeyFormatError):
        data = {"key": "wrong_format", "name": "A perfectly valid name"}
        client.add_compute_plan(data)
