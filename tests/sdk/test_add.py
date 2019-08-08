import pytest
import substra

from .. import datastore
from .utils import mock_requests


def test_add_dataset(client, dataset_query, mocker):
    m = mock_requests(mocker, "post", response=datastore.DATASET)
    response = client.add_dataset(dataset_query)

    assert response == datastore.DATASET
    assert m.is_called()


def test_add_dataset_invalid_args(client, dataset_query, mocker):
    mock_requests(mocker, "post", response=datastore.DATASET)
    del dataset_query['data_opener']

    with pytest.raises(substra.sdk.utils.LoadDataException):
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
    m = mock_requests(mocker, "post", response=datastore.OBJECTIVE)
    response = client.add_objective(objective_query)

    assert response == datastore.OBJECTIVE
    assert m.is_called()


def test_add_algo(client, algo_query, mocker):
    m = mock_requests(mocker, "post", response=datastore.ALGO)
    response = client.add_algo(algo_query)

    assert response == datastore.ALGO
    assert m.is_called()


def test_add_data_sample(client, data_sample_query, mocker):
    server_response = [{"key": "42"}]
    m = mock_requests(mocker, "post", response=server_response)
    response = client.add_data_sample(data_sample_query)

    assert response == server_response[0]
    assert m.is_called()


def test_add_data_sample_failure_409(client, data_sample_query, mocker):
    m = mock_requests(mocker, "post", response=[{"pkhash": "42"}], status=409)
    response = client.add_data_sample(data_sample_query, exist_ok=True)

    assert response == {"pkhash": "42"}
    assert m.is_called()


def test_add_data_samples(client, data_samples_query, mocker):
    server_response = [{"key": "42"}]
    m = mock_requests(mocker, "post", response=server_response)
    response = client.add_data_samples(data_samples_query)

    assert response == server_response
    assert m.is_called()
