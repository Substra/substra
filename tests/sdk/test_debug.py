from pathlib import Path
from substra.sdk.schemas import AlgoCategory
import docker
import os
import pytest
import substra
import re
import uuid

from substra.sdk.backends.local.compute.spawner.subprocess import PYTHON_SCRIPT_NAME
from substra.sdk import models

def test_wrong_debug_spawner(monkeypatch):
    monkeypatch.setenv('DEBUG_SPAWNER', "test")
    with pytest.raises(ValueError):
        substra.Client(debug=True)


def test_regex_script_name_valid():
    line = 'ENTRYPOINT ["python3", "metrics-_1.py"]'
    result = re.findall(PYTHON_SCRIPT_NAME, line)
    assert len(result) == 1, "Did not find the script name metrics-_1.py"
    assert result[0] == "metrics-_1.py"


def test_regex_script_name_empty():
    line = 'ENTRYPOINT ["python3", ""]'
    result = re.findall(PYTHON_SCRIPT_NAME, line)
    assert len(result) == 0


def test_regex_script_name_invalid():
    line = 'ENTRYPOINT ["echo", "BLA"]'
    result = re.findall(PYTHON_SCRIPT_NAME, line)
    assert len(result) == 0


class TestsDebug:
    # run tests twice with and without docker
    @pytest.fixture(params=["docker", "subprocess"])
    def spawner(self, monkeypatch, request):
        monkeypatch.setenv('DEBUG_SPAWNER', request.param)

    def test_client_tmp_dir(self):
        """Test the creation of a temp directory for the debug client"""
        client = substra.Client(debug=True)
        assert client.temp_directory

    def test_client_multi_nodes_dataset(self, dataset_query):
        """Assert that the owner is gotten from the metadata in debug mode"""
        client = substra.Client(debug=True)
        dataset_query['metadata'] = {substra.DEBUG_OWNER: 'owner_1'}

        key = client.add_dataset(dataset_query)
        asset = client.get_dataset(key)
        assert asset.owner == 'owner_1'

    @pytest.mark.parametrize("dockerfile_type", ("BAD_ENTRYPOINT", "NO_ENTRYPOINT"))
    def test_client_bad_dockerfile(self, asset_factory, dockerfile_type, spawner):
        client = substra.Client(debug=True)

        dataset_query = asset_factory.create_dataset(metadata={substra.DEBUG_OWNER: 'owner_1'})
        dataset_1_key = client.add_dataset(dataset_query)

        data_sample = asset_factory.create_data_sample(datasets=[dataset_1_key], test_only=False)
        sample_1_key = client.add_data_sample(data_sample)

        algo_query = asset_factory.create_algo(AlgoCategory.simple, dockerfile_type=dockerfile_type)
        algo_key = client.add_algo(algo_query)

        cp = asset_factory.create_compute_plan()
        cp.traintuples = [
            substra.sdk.schemas.ComputePlanTraintupleSpec(
                algo_key=algo_key,
                data_manager_key=dataset_1_key,
                traintuple_id=uuid.uuid4().hex,
                train_data_sample_keys=[sample_1_key],
            ),
        ]
        with pytest.raises((substra.sdk.backends.local.compute.spawner.base.ExecutionError,
                            docker.errors.APIError)):
            client.add_compute_plan(cp)

    def test_chainkey_exists(self, asset_factory, spawner, caplog):
        """ Test that if chainkey is supported but it was not generated warning is logged and adding the compute plan
        passes through nevertheless"""
        os.environ["CHAINKEYS_ENABLED"] = "True"
        # setting wrong directory, chainkeys should not be found
        os.environ["CHAINKEYS_DIR"] = str('/')

        client = substra.Client(debug=True)
        assert len(caplog.text) == 0

        dataset_query = asset_factory.create_dataset(metadata={substra.DEBUG_OWNER: 'owner_1'})
        dataset_1_key = client.add_dataset(dataset_query)

        data_sample = asset_factory.create_data_sample(datasets=[dataset_1_key], test_only=False)
        sample_1_key = client.add_data_sample(data_sample)

        algo_query = asset_factory.create_algo(AlgoCategory.simple)
        algo_key = client.add_algo(algo_query)

        cp = asset_factory.create_compute_plan()
        cp.traintuples = [
            substra.sdk.schemas.ComputePlanTraintupleSpec(
                algo_key=algo_key,
                data_manager_key=dataset_1_key,
                traintuple_id=uuid.uuid4().hex,
                train_data_sample_keys=[sample_1_key],
            )
        ]

        client.add_compute_plan(cp)
        assert 'No chainkeys found' in caplog.text

    def test_client_multi_nodes_cp(self, asset_factory, spawner):
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

        algo_query = asset_factory.create_algo(AlgoCategory.simple)
        algo_key = client.add_algo(algo_query)

        cp = asset_factory.create_compute_plan()
        cp.traintuples = [
            substra.sdk.schemas.ComputePlanTraintupleSpec(
                algo_key=algo_key,
                data_manager_key=dataset_1_key,
                traintuple_id=uuid.uuid4().hex,
                train_data_sample_keys=[sample_1_key],
            ),
            substra.sdk.schemas.ComputePlanTraintupleSpec(
                algo_key=algo_key,
                data_manager_key=dataset_2_key,
                traintuple_id=uuid.uuid4().hex,
                train_data_sample_keys=[sample_2_key],
            )
        ]

        client.add_compute_plan(cp)

        path_cp_1 = Path.cwd() / "local-worker" / "compute_plans" / "owner_1"
        path_cp_2 = Path.cwd() / "local-worker" / "compute_plans" / "owner_2"

        assert path_cp_1.is_dir()
        assert path_cp_2.is_dir()

    def test_compute_plan_add_update(self, asset_factory, spawner):
        client = substra.Client(debug=True)
        compute_plan = client.add_compute_plan(
            substra.sdk.schemas.ComputePlanSpec(
                tag=None,
                clean_models=False,
                metadata=dict(),
            ))

        dataset_query = asset_factory.create_dataset()
        dataset_key = client.add_dataset(dataset_query)

        data_sample = asset_factory.create_data_sample(datasets=[dataset_key], test_only=False)
        data_sample_key = client.add_data_sample(data_sample)

        algo_query = asset_factory.create_algo(AlgoCategory.simple)
        algo_key = client.add_algo(algo_query)

        traintuple_key = client.add_traintuple(
            substra.sdk.schemas.TraintupleSpec(
                algo_key=algo_key,
                data_manager_key=dataset_key,
                train_data_sample_keys=[data_sample_key],
                in_models_keys=None,
                compute_plan_key=compute_plan.key,
                rank=None,
                metadata=None,
            )
        )

        traintuple = substra.sdk.schemas.ComputePlanTraintupleSpec(
            algo_key=algo_key,
            data_manager_key=dataset_key,
            train_data_sample_keys=[data_sample_key],
            in_models_ids=[traintuple_key],
            traintuple_id=uuid.uuid4().hex,
        )

        compute_plan = client.update_compute_plan(
            key=compute_plan.key,
            data={
                "traintuples": [traintuple],
            }
        )

    def test_client_multi_nodes_cp_train_test(self, asset_factory, spawner):
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

        data_sample = asset_factory.create_data_sample(datasets=[dataset_1_key], test_only=True)
        sample_1_test_key = client.add_data_sample(data_sample)

        data_sample = asset_factory.create_data_sample(datasets=[dataset_2_key], test_only=True)
        sample_2_test_key = client.add_data_sample(data_sample)

        # client.link_dataset_with_data_samples(dataset_1_key, [sample_1_test_key])
        # client.link_dataset_with_data_samples(dataset_2_key, [sample_2_test_key])

        metric = asset_factory.create_metric()
        metric_1_key = client.add_metric(metric)

        metric = asset_factory.create_metric()
        metric_2_key = client.add_metric(metric)

        algo_query = asset_factory.create_algo(AlgoCategory.simple)
        algo_key = client.add_algo(algo_query)

        traintuple_id_1 = uuid.uuid4().hex
        traintuple_id_2 = uuid.uuid4().hex
        cp = asset_factory.create_compute_plan()
        cp.traintuples = [
            substra.sdk.schemas.ComputePlanTraintupleSpec(
                algo_key=algo_key,
                data_manager_key=dataset_1_key,
                traintuple_id=traintuple_id_1,
                train_data_sample_keys=[sample_1_key],
            ),
            substra.sdk.schemas.ComputePlanTraintupleSpec(
                algo_key=algo_key,
                data_manager_key=dataset_2_key,
                traintuple_id=traintuple_id_2,
                train_data_sample_keys=[sample_2_key],
            )
        ]

        cp.testtuples = [
            substra.sdk.schemas.ComputePlanTesttupleSpec(
                metric_keys=[metric_1_key],
                traintuple_id=traintuple_id_1,
                data_manager_key=dataset_1_key,
                test_data_sample_keys=[sample_1_test_key]
            ),
            substra.sdk.schemas.ComputePlanTesttupleSpec(
                metric_keys=[metric_2_key],
                traintuple_id=traintuple_id_2,
                data_manager_key=dataset_2_key,
                test_data_sample_keys=[sample_2_test_key]
            ),
        ]

        compute_plan = client.add_compute_plan(cp)

        path_cp_1 = Path.cwd() / "local-worker" / "compute_plans" / "owner_1"
        path_cp_2 = Path.cwd() / "local-worker" / "compute_plans" / "owner_2"

        assert path_cp_1.is_dir()
        assert path_cp_2.is_dir()

        testtuples = client.list_testtuple()
        aucs = [
            list(testtuple.test.perfs.values())[0]
            for testtuple in testtuples if testtuple.compute_plan_key == compute_plan.key
        ]
        assert all(auc == 2 for auc in aucs)

    def test_client_multi_nodes_cp_composite_aggregate(self, asset_factory, spawner):
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

        algo_query = asset_factory.create_algo(AlgoCategory.composite)
        algo_key = client.add_algo(algo_query)

        algo_query = asset_factory.create_algo(AlgoCategory.aggregate)
        aggregate_algo_key = client.add_algo(algo_query)

        cp = asset_factory.create_compute_plan()
        composite_1_key = uuid.uuid4().hex
        composite_2_key = uuid.uuid4().hex
        cp.composite_traintuples = [
            substra.sdk.schemas.ComputePlanCompositeTraintupleSpec(
                algo_key=algo_key,
                data_manager_key=dataset_1_key,
                composite_traintuple_id=composite_1_key,
                train_data_sample_keys=[sample_1_key],
                out_trunk_model_permissions={
                    "public": False,
                    "authorized_ids": [dataset_1_key, dataset_2_key]
                },
            ),
            substra.sdk.schemas.ComputePlanCompositeTraintupleSpec(
                algo_key=algo_key,
                data_manager_key=dataset_2_key,
                composite_traintuple_id=composite_2_key,
                train_data_sample_keys=[sample_2_key],
                out_trunk_model_permissions={
                    "public": False,
                    "authorized_ids": [dataset_1_key, dataset_2_key]
                },
            )
        ]

        cp.aggregatetuples = [
            substra.sdk.schemas.ComputePlanAggregatetupleSpec(
                aggregatetuple_id=uuid.uuid4().hex,
                worker=dataset_1_key,
                algo_key=aggregate_algo_key,
                in_models_ids=[composite_1_key, composite_2_key]
            )
        ]

        compute_plan = client.add_compute_plan(cp)

        path_cp_1 = Path.cwd() / "local-worker" / "compute_plans" / "owner_1"
        path_cp_2 = Path.cwd() / "local-worker" / "compute_plans" / "owner_2"

        assert path_cp_1.is_dir()
        assert path_cp_2.is_dir()

        assert compute_plan.status == models.ComputePlanStatus.done

    def test_tasks_extra_fields(self, asset_factory):
        client = substra.Client(debug=True)

        # set dataset, metric and algo
        dataset_query = asset_factory.create_dataset()
        dataset_key = client.add_dataset(dataset_query)

        data_sample = asset_factory.create_data_sample(datasets=[dataset_key], test_only=False)
        data_sample_key = client.add_data_sample(data_sample)

        algo_query = asset_factory.create_algo(AlgoCategory.simple)
        algo_key = client.add_algo(algo_query)

        composite_algo_query = asset_factory.create_algo(AlgoCategory.composite)
        composite_algo_key = client.add_algo(composite_algo_query)

        metric_query = asset_factory.create_metric()
        metric_key = client.add_metric(metric_query)

        # test traintuple extra field

        traintuple_key = client.add_traintuple(
            substra.sdk.schemas.TraintupleSpec(
                algo_key=algo_key,
                data_manager_key=dataset_key,
                train_data_sample_keys=[data_sample_key],
            )
        )

        traintuple = client.get_traintuple(traintuple_key)
        assert traintuple.train.data_manager
        assert traintuple.train.data_manager.key == dataset_key
        assert traintuple.parent_tasks == []

        # test testtuple extra fields

        testtuple_key = client.add_testtuple(
            substra.sdk.schemas.TesttupleSpec(
                traintuple_key=traintuple_key,
                data_manager_key=dataset_key,
                test_data_sample_keys=[data_sample_key],
                metric_keys=[metric_key]
            )
        )
        testtuple = client.get_testtuple(testtuple_key)
        assert testtuple.test.data_manager
        assert testtuple.test.data_manager.key == dataset_key
        assert testtuple.test.metrics
        assert [m.key for m in testtuple.test.metrics] == [metric_key]
        assert [t.key for t in testtuple.parent_tasks] == [traintuple_key]

        # test composite extra field

        composite_traintuple_key = client.add_composite_traintuple(
            substra.sdk.schemas.CompositeTraintupleSpec(
                algo_key=composite_algo_key,
                data_manager_key=dataset_key,
                train_data_sample_keys=[data_sample_key],
                out_trunk_model_permissions={
                    "public": True,
                    "authorized_ids": []
                },
            )
        )

        composite_traintuple = client.get_composite_traintuple(composite_traintuple_key)
        assert composite_traintuple.composite.data_manager
        assert composite_traintuple.composite.data_manager.key == dataset_key
        assert composite_traintuple.parent_tasks == []
