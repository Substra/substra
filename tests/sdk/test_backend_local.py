import pytest

import substra
from substra.sdk.backends.local import models

from . import factory


@pytest.mark.slow
def test_tuples_execution_on_same_node():
    """Execution of a traintuple, a following testtuple and a following traintuple."""
    asset_factory = factory.AssetsFactory("test_local")
    client = substra.Client(backend="local",)

    default_dataset_dict = asset_factory.create_dataset()
    default_dataset = client.add_dataset(default_dataset_dict)

    # create train data samples
    for i in range(4):
        spec = asset_factory.create_data_sample(
            datasets=[default_dataset], test_only=False
        )
        client.add_data_sample(spec)

    # create test data sample
    spec = asset_factory.create_data_sample(datasets=[default_dataset], test_only=True)
    test_data_sample = client.add_data_sample(spec)

    default_objective_dict = asset_factory.create_objective(
        dataset=default_dataset, data_samples=[test_data_sample]
    )
    default_objective = client.add_objective(default_objective_dict)

    spec = asset_factory.create_algo()
    algo = client.add_algo(spec)

    # create traintuple
    spec = asset_factory.create_traintuple(
        algo=algo,
        dataset=default_dataset,
        data_samples=default_dataset["trainDataSampleKeys"],
    )
    traintuple = client.add_traintuple(spec)
    assert traintuple.get("status") == models.Status.done.value
    assert traintuple.get("outModel") is not None

    # check we cannot add twice the same traintuple
    with pytest.raises(substra.exceptions.AlreadyExists):
        client.add_traintuple(spec)

    # create testtuple
    # don't create it before to avoid MVCC errors
    spec = asset_factory.create_testtuple(
        objective=default_objective, traintuple=traintuple
    ).dict()
    testtuple = client.add_testtuple(spec)
    assert testtuple.get("status") == models.Status.done.value

    # add a traintuple depending on first traintuple
    spec = asset_factory.create_traintuple(
        algo=algo,
        dataset=default_dataset,
        data_samples=default_dataset["trainDataSampleKeys"],
        traintuples=[traintuple],
    ).dict()
    traintuple = client.add_traintuple(spec)
    assert traintuple.get("status") == models.Status.done.value
    assert len(traintuple.get("inModels")) == 1
