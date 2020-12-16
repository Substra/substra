from pathlib import Path

import substra


def test_client_tmp_dir():
    """Test the creation of a temp directory for the debug client"""
    client = substra.Client(debug=True)
    assert client.temp_directory


def test_client_multi_nodes_dataset(dataset_query):
    """Assert that the owner is gotten from the metadata in debug mode"""
    client = substra.Client(debug=True)
    dataset_query['metadata'] = {substra.DEBUG_OWNER: 'owner_1'}

    key = client.add_dataset(dataset_query)
    asset = client.get_dataset(key)
    assert asset.owner == 'owner_1'


def test_client_multi_nodes_cp(asset_factory):
    """Assert that there is one CP local folder per node"""
    client = substra.Client(debug=True)

    dataset_query = asset_factory.create_dataset(metadata={substra.DEBUG_OWNER: 'owner_1'})
    dataset_1_key = client.add_dataset(dataset_query)

    dataset_2_query = asset_factory.create_dataset(metadata={substra.DEBUG_OWNER: 'owner_2'})
    dataset_2_key = client.add_dataset(dataset_2_query)

    data_sample = asset_factory.create_data_sample(datasets=[dataset_1_key], test_only=False)
    sample_1_key = client.add_data_sample(data_sample)

    data_sample = asset_factory.create_data_sample(datasets=[dataset_2_key], test_only=False)
    sample_2_key = client.add_data_sample(data_sample)

    algo_query = asset_factory.create_algo()
    algo_key = client.add_algo(algo_query)

    cp = asset_factory.create_compute_plan()
    cp.traintuples = [
        substra.sdk.schemas.ComputePlanTraintupleSpec(
            algo_key=algo_key,
            data_manager_key=dataset_1_key,
            traintuple_id=1,
            train_data_sample_keys=[sample_1_key],
        ),
        substra.sdk.schemas.ComputePlanTraintupleSpec(
            algo_key=algo_key,
            data_manager_key=dataset_2_key,
            traintuple_id=2,
            train_data_sample_keys=[sample_2_key],
        )
    ]

    client.add_compute_plan(cp)

    path_cp_1 = Path.cwd() / "local-worker" / "compute_plans" / "owner_1"
    path_cp_2 = Path.cwd() / "local-worker" / "compute_plans" / "owner_2"

    assert path_cp_1.is_dir()
    assert path_cp_2.is_dir()
