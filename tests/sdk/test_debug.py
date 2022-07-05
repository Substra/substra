import os
import re
import uuid
from pathlib import Path

import docker
import pytest

import substra
from substra.sdk import models
from substra.sdk.backends.local.compute.spawner.subprocess import PYTHON_SCRIPT_NAME
from substra.sdk.exceptions import InvalidRequest
from substra.sdk.exceptions import KeyAlreadyExistsError
from substra.sdk.schemas import AlgoCategory


def test_wrong_debug_spawner(monkeypatch):
    monkeypatch.setenv("DEBUG_SPAWNER", "test")
    with pytest.raises(ValueError) as err:
        substra.Client(debug=True)
    assert str(err.value) == "'test' is not a valid BackendType"


def test_get_backend_type_docker(monkeypatch):
    monkeypatch.setenv("DEBUG_SPAWNER", str(substra.BackendType.LOCAL_DOCKER.value))
    client = substra.Client(debug=True)
    assert client.backend_mode == substra.BackendType.LOCAL_DOCKER


def test_get_backend_type_subprocess(monkeypatch):
    monkeypatch.setenv("DEBUG_SPAWNER", str(substra.BackendType.LOCAL_SUBPROCESS.value))
    client = substra.Client(debug=True)
    assert client.backend_mode == substra.BackendType.LOCAL_SUBPROCESS


def test_get_backend_type_deployed():
    client = substra.Client(url="foo.com")
    assert client.backend_mode == substra.BackendType.DEPLOYED


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
    @pytest.fixture(
        params=[str(substra.BackendType.LOCAL_DOCKER.value), str(substra.BackendType.LOCAL_SUBPROCESS.value)]
    )
    def spawner(self, monkeypatch, request):
        monkeypatch.setenv("DEBUG_SPAWNER", request.param)

    def test_client_tmp_dir(self):
        """Test the creation of a temp directory for the debug client"""
        client = substra.Client(debug=True)
        assert client.temp_directory

    def test_client_multi_organizations_dataset(self, dataset_query):
        """Assert that the owner is gotten from the metadata in debug mode"""
        client = substra.Client(debug=True)
        dataset_query["metadata"] = {substra.DEBUG_OWNER: "owner_1"}

        key = client.add_dataset(dataset_query)
        asset = client.get_dataset(key)
        assert asset.owner == "owner_1"

    @pytest.mark.parametrize("dockerfile_type", ("BAD_ENTRYPOINT", "NO_ENTRYPOINT"))
    def test_client_bad_dockerfile(self, asset_factory, dockerfile_type, spawner):
        client = substra.Client(debug=True)

        dataset_query = asset_factory.create_dataset(metadata={substra.DEBUG_OWNER: "owner_1"})
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
                traintuple_id=str(uuid.uuid4()),
                train_data_sample_keys=[sample_1_key],
            ),
        ]
        with pytest.raises((substra.sdk.backends.local.compute.spawner.base.ExecutionError, docker.errors.APIError)):
            client.add_compute_plan(cp)

    def test_chainkey_exists(self, asset_factory, spawner, caplog):
        """Test that if chainkey is supported but it was not generated warning is
        logged and adding the compute plan passes through nevertheless"""
        os.environ["CHAINKEYS_ENABLED"] = "True"
        # setting wrong directory, chainkeys should not be found
        os.environ["CHAINKEYS_DIR"] = str("/")

        client = substra.Client(debug=True)
        assert len(caplog.text) == 0

        dataset_query = asset_factory.create_dataset(metadata={substra.DEBUG_OWNER: "owner_1"})
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
                traintuple_id=str(uuid.uuid4()),
                train_data_sample_keys=[sample_1_key],
            )
        ]

        client.add_compute_plan(cp)
        assert "No chainkeys found" in caplog.text

    def test_client_multi_organizations_cp(self, asset_factory, spawner):
        """Assert that there is one CP local folder per organization"""
        client = substra.Client(debug=True)

        dataset_query = asset_factory.create_dataset(metadata={substra.DEBUG_OWNER: "owner_1"})
        dataset_1_key = client.add_dataset(dataset_query)

        dataset_2_query = asset_factory.create_dataset(metadata={substra.DEBUG_OWNER: "owner_2"})
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
                traintuple_id=str(uuid.uuid4()),
                train_data_sample_keys=[sample_1_key],
            ),
            substra.sdk.schemas.ComputePlanTraintupleSpec(
                algo_key=algo_key,
                data_manager_key=dataset_2_key,
                traintuple_id=str(uuid.uuid4()),
                train_data_sample_keys=[sample_2_key],
            ),
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
                key=str(uuid.uuid4()),
                tag=None,
                name="My ultra cool compute plan",
                clean_models=False,
                metadata=dict(),
            )
        )

        assert compute_plan.status == models.ComputePlanStatus.empty

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
            traintuple_id=str(uuid.uuid4()),
        )

        compute_plan = client.add_compute_plan_tuples(
            key=compute_plan.key,
            data={
                "traintuples": [traintuple],
            },
        )

    def test_client_multi_organizations_cp_train_test(self, asset_factory, spawner):
        """Assert that there is one CP local folder per organization"""
        client = substra.Client(debug=True)

        dataset_query = asset_factory.create_dataset(metadata={substra.DEBUG_OWNER: "owner_1"})
        dataset_1_key = client.add_dataset(dataset_query)

        dataset_2_query = asset_factory.create_dataset(metadata={substra.DEBUG_OWNER: "owner_2"})
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

        metric = asset_factory.create_algo(category=AlgoCategory.metric)
        metric_1_key = client.add_algo(metric)

        metric = asset_factory.create_algo(category=AlgoCategory.metric)
        metric_2_key = client.add_algo(metric)

        algo_query = asset_factory.create_algo(AlgoCategory.simple)
        algo_key = client.add_algo(algo_query)

        traintuple_id_1 = str(uuid.uuid4())
        traintuple_id_2 = str(uuid.uuid4())
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
            ),
        ]

        predicttuple_id_1 = str(uuid.uuid4())
        predicttuple_id_2 = str(uuid.uuid4())
        cp.predicttuples = [
            substra.sdk.schemas.ComputePlanPredicttupleSpec(
                predicttuple_id=predicttuple_id_1,
                algo_key=algo_key,
                traintuple_id=traintuple_id_1,
                data_manager_key=dataset_1_key,
                test_data_sample_keys=[sample_1_test_key],
            ),
            substra.sdk.schemas.ComputePlanPredicttupleSpec(
                predicttuple_id=predicttuple_id_2,
                algo_key=algo_key,
                traintuple_id=traintuple_id_2,
                data_manager_key=dataset_2_key,
                test_data_sample_keys=[sample_2_test_key],
            ),
        ]

        cp.testtuples = [
            substra.sdk.schemas.ComputePlanTesttupleSpec(
                algo_key=metric_1_key,
                predicttuple_id=predicttuple_id_1,
                data_manager_key=dataset_1_key,
                test_data_sample_keys=[sample_1_test_key],
            ),
            substra.sdk.schemas.ComputePlanTesttupleSpec(
                algo_key=metric_2_key,
                predicttuple_id=predicttuple_id_2,
                data_manager_key=dataset_2_key,
                test_data_sample_keys=[sample_2_test_key],
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
            for testtuple in testtuples
            if testtuple.compute_plan_key == compute_plan.key
        ]
        assert all(auc == 2 for auc in aucs)

    def test_client_multi_organizations_cp_composite_aggregate(self, asset_factory, spawner):
        """Assert that there is one CP local folder per organization"""
        client = substra.Client(debug=True)

        dataset_query = asset_factory.create_dataset(metadata={substra.DEBUG_OWNER: "owner_1"})
        dataset_1_key = client.add_dataset(dataset_query)

        dataset_2_query = asset_factory.create_dataset(metadata={substra.DEBUG_OWNER: "owner_2"})
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
        composite_1_key = str(uuid.uuid4())
        composite_2_key = str(uuid.uuid4())
        cp.composite_traintuples = [
            substra.sdk.schemas.ComputePlanCompositeTraintupleSpec(
                algo_key=algo_key,
                data_manager_key=dataset_1_key,
                composite_traintuple_id=composite_1_key,
                train_data_sample_keys=[sample_1_key],
                out_trunk_model_permissions={"public": False, "authorized_ids": [dataset_1_key, dataset_2_key]},
            ),
            substra.sdk.schemas.ComputePlanCompositeTraintupleSpec(
                algo_key=algo_key,
                data_manager_key=dataset_2_key,
                composite_traintuple_id=composite_2_key,
                train_data_sample_keys=[sample_2_key],
                out_trunk_model_permissions={"public": False, "authorized_ids": [dataset_1_key, dataset_2_key]},
            ),
        ]

        cp.aggregatetuples = [
            substra.sdk.schemas.ComputePlanAggregatetupleSpec(
                aggregatetuple_id=str(uuid.uuid4()),
                worker=dataset_1_key,
                algo_key=aggregate_algo_key,
                in_models_ids=[composite_1_key, composite_2_key],
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

        metric_query = asset_factory.create_algo(category=AlgoCategory.metric)
        metric_key = client.add_algo(metric_query)

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

        # test predicttuple extra fields
        predicttuple_key = client.add_predicttuple(
            substra.sdk.schemas.PredicttupleSpec(
                traintuple_key=traintuple_key,
                algo_key=algo_key,
                data_manager_key=dataset_key,
                test_data_sample_keys=[data_sample_key],
            )
        )

        predicttuple = client.get_predicttuple(predicttuple_key)
        assert predicttuple.predict.data_manager
        assert predicttuple.predict.data_manager.key == dataset_key
        assert [p.key for p in predicttuple.parent_tasks] == [traintuple_key]

        # test testtuple extra fields

        testtuple_key = client.add_testtuple(
            substra.sdk.schemas.TesttupleSpec(
                predicttuple_key=predicttuple_key,
                data_manager_key=dataset_key,
                test_data_sample_keys=[data_sample_key],
                algo_key=metric_key,
            )
        )
        testtuple = client.get_testtuple(testtuple_key)
        assert testtuple.test.data_manager
        assert testtuple.test.data_manager.key == dataset_key
        assert testtuple.algo
        assert testtuple.algo.key == metric_key
        assert [t.key for t in testtuple.parent_tasks] == [predicttuple_key]

        # test composite extra field

        composite_traintuple_key = client.add_composite_traintuple(
            substra.sdk.schemas.CompositeTraintupleSpec(
                algo_key=composite_algo_key,
                data_manager_key=dataset_key,
                train_data_sample_keys=[data_sample_key],
                out_trunk_model_permissions={"public": True, "authorized_ids": []},
            )
        )

        composite_traintuple = client.get_composite_traintuple(composite_traintuple_key)
        assert composite_traintuple.composite.data_manager
        assert composite_traintuple.composite.data_manager.key == dataset_key
        assert composite_traintuple.parent_tasks == []

    def test_traintuple_with_test_data_sample(self, asset_factory, spawner):
        """Check that we can't use test data samples for traintuples"""
        client = substra.Client(debug=True)

        dataset_query = asset_factory.create_dataset(metadata={substra.DEBUG_OWNER: "owner_1"})
        dataset_1_key = client.add_dataset(dataset_query)

        data_sample_1 = asset_factory.create_data_sample(datasets=[dataset_1_key], test_only=False)
        sample_1_key = client.add_data_sample(data_sample_1)

        data_sample_2 = asset_factory.create_data_sample(datasets=[dataset_1_key], test_only=True)
        sample_2_key = client.add_data_sample(data_sample_2)

        algo_query = asset_factory.create_algo(AlgoCategory.simple)
        algo_key = client.add_algo(algo_query)

        with pytest.raises(InvalidRequest) as e:
            client.add_traintuple(
                substra.sdk.schemas.TraintupleSpec(
                    algo_key=algo_key,
                    data_manager_key=dataset_1_key,
                    traintuple_id=str(uuid.uuid4()),
                    train_data_sample_keys=[sample_1_key, sample_2_key],
                )
            )

        assert "Cannot create train task with test data" in str(e.value)

    def test_composite_traintuple_with_test_data_sample(self, asset_factory, spawner):
        """Check that we can't use test data samples for composite_traintuples"""
        client = substra.Client(debug=True)

        dataset_query = asset_factory.create_dataset(metadata={substra.DEBUG_OWNER: "owner_1"})
        dataset_1_key = client.add_dataset(dataset_query)

        data_sample = asset_factory.create_data_sample(datasets=[dataset_1_key], test_only=True)
        sample_1_key = client.add_data_sample(data_sample)

        composite_algo_query = asset_factory.create_algo(AlgoCategory.composite)
        composite_algo_key = client.add_algo(composite_algo_query)

        with pytest.raises(InvalidRequest) as e:
            client.add_composite_traintuple(
                substra.sdk.schemas.CompositeTraintupleSpec(
                    algo_key=composite_algo_key,
                    data_manager_key=dataset_1_key,
                    traintuple_id=str(uuid.uuid4()),
                    train_data_sample_keys=[sample_1_key],
                    out_trunk_model_permissions={"public": True, "authorized_ids": []},
                )
            )

        assert "Cannot create train task with test data" in str(e.value)

    def test_add_two_compute_plan_with_same_cp_key(self, spawner):
        client = substra.Client(debug=True)
        common_cp_key = str(uuid.uuid4())
        client.add_compute_plan(
            substra.sdk.schemas.ComputePlanSpec(
                key=common_cp_key,
                tag=None,
                name="My compute plan",
                clean_models=False,
                metadata=dict(),
            )
        )
        with pytest.raises(KeyAlreadyExistsError):
            client.add_compute_plan(
                substra.sdk.schemas.ComputePlanSpec(
                    key=common_cp_key,
                    tag=None,
                    name="My other compute plan",
                    clean_models=False,
                    metadata=dict(),
                )
            )

    def test_live_performances_json_file_exist(self, asset_factory, spawner):
        """Assert the performances file is well created."""
        client = substra.Client(debug=True)

        dataset_query = asset_factory.create_dataset(metadata={substra.DEBUG_OWNER: "owner"})
        dataset_key = client.add_dataset(dataset_query)

        data_sample = asset_factory.create_data_sample(datasets=[dataset_key], test_only=False)
        sample_key = client.add_data_sample(data_sample)

        algo_query = asset_factory.create_algo(AlgoCategory.simple)
        algo_key = client.add_algo(algo_query)

        metric = asset_factory.create_algo(category=AlgoCategory.metric)
        metric_key = client.add_algo(metric)

        cp = asset_factory.create_compute_plan()

        traintuple = substra.sdk.schemas.ComputePlanTraintupleSpec(
            algo_key=algo_key,
            data_manager_key=dataset_key,
            traintuple_id=str(uuid.uuid4()),
            train_data_sample_keys=[sample_key],
        )

        predicttuple = substra.sdk.schemas.ComputePlanPredicttupleSpec(
            algo_key=algo_key,
            data_manager_key=dataset_key,
            traintuple_id=traintuple.traintuple_id,
            predicttuple_id=str(uuid.uuid4()),
            test_data_sample_keys=[sample_key],
        )

        cp.testtuples = [
            substra.sdk.schemas.ComputePlanTesttupleSpec(
                algo_key=metric_key,
                predicttuple_id=predicttuple.predicttuple_id,
                data_manager_key=dataset_key,
                test_data_sample_keys=[sample_key],
            )
        ]
        cp.traintuples = [traintuple]
        cp.predicttuples = [predicttuple]

        client.add_compute_plan(cp)

        json_perf_path = Path.cwd() / "local-worker" / "live_performances" / cp.key / "performances.json"

        assert json_perf_path.is_file()


class TestsList:
    "Test client.list... functions"

    @pytest.mark.parametrize("asset_name", ["dataset", "algo"])
    def test_list_assets(self, asset_name, asset_factory):
        client = substra.Client(debug=True)
        query = getattr(asset_factory, f"create_{asset_name}")(metadata={substra.DEBUG_OWNER: "owner_1"})
        key = getattr(client, f"add_{asset_name}")(query)

        assets = getattr(client, f"list_{asset_name}")()

        assert assets[0].key == key

    @pytest.fixture
    def _init_data_samples(self, asset_factory):
        client = substra.Client(debug=True)
        data_samples_keys = []
        dataset_query = asset_factory.create_dataset(metadata={substra.DEBUG_OWNER: "owner_1"})
        dataset_key = client.add_dataset(dataset_query)

        data_sample_1 = asset_factory.create_data_sample(datasets=[dataset_key], test_only=False)
        data_samples_keys.append(client.add_data_sample(data_sample_1))

        data_sample_2 = asset_factory.create_data_sample(datasets=[dataset_key], test_only=True)
        data_samples_keys.append(client.add_data_sample(data_sample_2))

        data_sample_3 = asset_factory.create_data_sample(datasets=[dataset_key], test_only=False)
        data_samples_keys.append(client.add_data_sample(data_sample_3))
        return client, data_samples_keys

    def test_list_datasamples_all(self, _init_data_samples):
        # get all datasamples
        client, _ = _init_data_samples
        data_samples = client.list_data_sample(ascending=False)
        assert len(data_samples) == 3
        # assert dates in descending order
        assert all(
            data_samples[i].creation_date >= data_samples[i + 1].creation_date for i in range(len(data_samples) - 1)
        )

    def test_list_datasamples_all_order_ascending(self, _init_data_samples):
        # get all datasamples
        client, _ = _init_data_samples
        data_samples = client.list_data_sample(ascending=True)
        assert len(data_samples) == 3
        # assert dates in ascending order
        assert all(
            data_samples[i].creation_date <= data_samples[i + 1].creation_date for i in range(len(data_samples) - 1)
        )

    def test_list_datasamples_key(self, _init_data_samples):
        # Get sample 1 by key
        client, data_sample_keys = _init_data_samples
        filters = {"key": [data_sample_keys[0]]}
        data_samples = client.list_data_sample(filters=filters)
        assert len(data_samples) == 1
        assert data_samples[0].key == data_sample_keys[0]

    def test_list_datasamples_test_only(self, _init_data_samples):
        # Get all samples with test_only
        client, data_sample_keys = _init_data_samples
        filters = {"test_only": ["False"]}
        data_samples = client.list_data_sample(filters=filters)
        assert len(data_samples) == 2
        assert data_samples[0].key == data_sample_keys[2]
        assert data_samples[1].key == data_sample_keys[0]

    def test_list_datasamples_OR(self, _init_data_samples):
        # Get sample 1 and 2 by key
        client, data_sample_keys = _init_data_samples
        filters = {"key": [data_sample_keys[0], data_sample_keys[1]]}
        data_samples = client.list_data_sample(filters=filters)
        assert len(data_samples) == 2
        assert data_samples[0].key == data_sample_keys[1]
        assert data_samples[1].key == data_sample_keys[0]

    def test_list_datasamples_AND(self, _init_data_samples):
        # Test the AND operator
        # Get sample 1 by key and correct test_only value
        client, data_sample_keys = _init_data_samples
        filters = {"key": [data_sample_keys[0]], "test_only": ["False"]}
        data_samples = client.list_data_sample(filters=filters)
        assert len(data_samples) == 1
        assert data_samples[0].key == data_sample_keys[0]

        # Get sample 1 by key and wrong test_only value (should send empty list)
        client, data_sample_keys = _init_data_samples
        filters = {"key": [data_sample_keys[0]], "test_only": ["True"]}
        data_samples = client.list_data_sample(filters=filters)
        assert len(data_samples) == 0


def test_execute_compute_plan_several_testtuples_per_train(asset_factory, monkeypatch):
    monkeypatch.setenv("DEBUG_SPAWNER", str(substra.BackendType.LOCAL_SUBPROCESS.value))
    client = substra.Client(debug=True)

    dataset_query = asset_factory.create_dataset(metadata={substra.DEBUG_OWNER: "owner_1"})
    dataset_key = client.add_dataset(dataset_query)

    data_sample_1 = asset_factory.create_data_sample(datasets=[dataset_key], test_only=False)
    sample_1_key = client.add_data_sample(data_sample_1)

    algo_query = asset_factory.create_algo(AlgoCategory.simple)
    algo_key = client.add_algo(algo_query)

    metric = asset_factory.create_algo(category=AlgoCategory.metric)
    metric_key = client.add_algo(metric)

    cp = asset_factory.create_compute_plan()

    traintuple = substra.sdk.schemas.ComputePlanTraintupleSpec(
        algo_key=algo_key,
        data_manager_key=dataset_key,
        traintuple_id=str(uuid.uuid4()),
        train_data_sample_keys=[sample_1_key],
    )

    predicttuple = substra.sdk.schemas.ComputePlanPredicttupleSpec(
        algo_key=algo_key,
        data_manager_key=dataset_key,
        traintuple_id=traintuple.traintuple_id,
        predicttuple_id=str(uuid.uuid4()),
        test_data_sample_keys=[sample_1_key],
    )

    cp.testtuples = [
        substra.sdk.schemas.ComputePlanTesttupleSpec(
            algo_key=metric_key,
            predicttuple_id=predicttuple.predicttuple_id,
            data_manager_key=dataset_key,
            test_data_sample_keys=[sample_1_key],
        )
        for _ in range(2)
    ]
    cp.traintuples = [traintuple]
    cp.predicttuples = [predicttuple]

    compute_plan = client.add_compute_plan(cp)
    assert compute_plan.done_count == 4

    testtuples = client.list_testtuple(filters={"compute_plan_key": [compute_plan.key]})
    assert len(testtuples) == 2
