import uuid
from pathlib import Path

import docker
import pytest

import substra
from substra.sdk import models
from substra.sdk import exceptions
from substra.sdk.backends import local

from ...fl_interface import AlgoCategory
from ...fl_interface import FLTaskInputGenerator
from ...fl_interface import FLTaskOutputGenerator
from ...fl_interface import InputIdentifiers


def test_wrong_debug_spawner():
    with pytest.raises(exceptions.SDKException) as err:
        substra.Client(backend_type="test")
    assert (
        str(err.value) == "Unknown value for the execution mode: test, valid values are: dict_values"
        "([<BackendType.REMOTE: 'remote'>, <BackendType.LOCAL_DOCKER: 'docker'>, <BackendType.LOCAL_SUBPROCESS: "
        "'subprocess'>])"
    )


def test_get_backend_type_docker(docker_clients):
    assert docker_clients[0].backend_mode == substra.BackendType.LOCAL_DOCKER


def test_get_backend_type_subprocess(subprocess_clients):
    assert subprocess_clients[0].backend_mode == substra.BackendType.LOCAL_SUBPROCESS


def test_get_backend_type_deployed():
    client = substra.Client(url="foo.com")
    assert client.backend_mode == substra.BackendType.REMOTE


class TestsDebug:
    def test_client_tmp_dir(self, clients):
        """Test the creation of a temp directory for the debug client"""
        assert clients[0].temp_directory

    @pytest.mark.parametrize("dockerfile_type", ("BAD_ENTRYPOINT", "NO_ENTRYPOINT", "NO_FUNCTION_NAME"))
    def test_client_bad_dockerfile(self, asset_factory, dockerfile_type, clients):

        client = clients[0]

        dataset_query = asset_factory.create_dataset()
        dataset_1_key = client.add_dataset(dataset_query)

        data_sample = asset_factory.create_data_sample(datasets=[dataset_1_key], test_only=False)
        sample_1_key = client.add_data_sample(data_sample)

        algo_query = asset_factory.create_algo(AlgoCategory.simple, dockerfile_type=dockerfile_type)
        algo_key = client.add_algo(algo_query)

        cp = asset_factory.create_compute_plan()
        cp.tasks = [
            substra.sdk.schemas.ComputePlanTaskSpec(
                algo_key=algo_key,
                data_manager_key=dataset_1_key,
                task_id=str(uuid.uuid4()),
                train_data_sample_keys=[sample_1_key],
                inputs=FLTaskInputGenerator.tuple(opener_key=dataset_1_key, data_sample_keys=[sample_1_key]),
                outputs=FLTaskOutputGenerator.traintuple(),
                worker=client.organization_info().organization_id,
            ),
        ]
        with pytest.raises((substra.sdk.backends.local.compute.spawner.base.ExecutionError, docker.errors.APIError)):
            client.add_compute_plan(cp)

    def test_compute_plan_add_update_tuples(self, asset_factory, clients):
        client = clients[0]
        client = substra.Client(backend_type=substra.BackendType.LOCAL_SUBPROCESS)
        compute_plan = client.add_compute_plan(
            substra.sdk.schemas.ComputePlanSpec(
                key=str(uuid.uuid4()),
                tag=None,
                name="My ultra cool compute plan",
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

        traintuple_key = client.add_task(
            substra.sdk.schemas.TaskSpec(
                algo_key=algo_key,
                compute_plan_key=compute_plan.key,
                rank=None,
                metadata=None,
                inputs=FLTaskInputGenerator.tuple(opener_key=dataset_key, data_sample_keys=[data_sample_key]),
                outputs=FLTaskOutputGenerator.traintuple(),
                worker=client.organization_info().organization_id,
            )
        )

        traintuple = substra.sdk.schemas.ComputePlanTaskSpec(
            algo_key=algo_key,
            task_id=str(uuid.uuid4()),
            inputs=FLTaskInputGenerator.tuple(opener_key=dataset_key, data_sample_keys=[data_sample_key])
            + FLTaskInputGenerator.trains_to_train([traintuple_key]),
            outputs=FLTaskOutputGenerator.traintuple(),
            worker=client.organization_info().organization_id,
        )

        compute_plan = client.add_compute_plan_tuples(
            key=compute_plan.key,
            tuples={
                "traintuples": [traintuple],
            },
        )

    def test_compute_plan_update(self, clients):
        client = clients[0]
        old_name = "My ultra cool compute plan"
        new_name = "My even cooler compute plan"

        compute_plan = client.add_compute_plan(
            substra.sdk.schemas.ComputePlanSpec(
                key=str(uuid.uuid4()),
                tag="cool-tag",
                name=old_name,
                metadata=dict(),
            )
        )

        client.update_compute_plan(
            key=compute_plan.key,
            name=new_name,
        )

        compute_plan.name = new_name
        updated_compute_plan = client.get_compute_plan(compute_plan.key)

        assert compute_plan == updated_compute_plan

    def test_tasks_extra_fields(self, asset_factory, clients):
        client = clients[0]

        # set dataset, metric and algo
        dataset_query = asset_factory.create_dataset()
        dataset_key = client.add_dataset(dataset_query)

        data_sample = asset_factory.create_data_sample(datasets=[dataset_key], test_only=False)
        data_sample_key = client.add_data_sample(data_sample)

        algo_query = asset_factory.create_algo(AlgoCategory.simple)
        algo_key = client.add_algo(algo_query)

        predict_algo_spec = asset_factory.create_algo(category=AlgoCategory.predict)
        predict_algo_key = client.add_algo(predict_algo_spec)

        composite_algo_query = asset_factory.create_algo(AlgoCategory.composite)
        composite_algo_key = client.add_algo(composite_algo_query)

        metric_query = asset_factory.create_algo(category=AlgoCategory.metric)
        metric_key = client.add_algo(metric_query)

        # test traintuple extra field

        traintuple_key = client.add_task(
            substra.sdk.schemas.TaskSpec(
                algo_key=algo_key,
                inputs=FLTaskInputGenerator.tuple(opener_key=dataset_key, data_sample_keys=[data_sample_key]),
                outputs=FLTaskOutputGenerator.traintuple(),
                worker=client.organization_info().organization_id,
            )
        )

        traintuple = client.get_task(traintuple_key)
        dataset_ref = [x for x in traintuple.inputs if x.identifier == substra.sdk.schemas.StaticInputIdentifier.opener]
        assert len(dataset_ref) == 1
        assert dataset_ref[0].asset_key == dataset_key
        assert len(traintuple.inputs) == 2  # data sample + opener

        # test predicttuple extra fields
        predicttuple_key = client.add_task(
            substra.sdk.schemas.TaskSpec(
                algo_key=predict_algo_key,
                inputs=FLTaskInputGenerator.tuple(opener_key=dataset_key, data_sample_keys=[data_sample_key])
                + FLTaskInputGenerator.train_to_predict(traintuple_key),
                outputs=FLTaskOutputGenerator.predicttuple(),
                worker=client.organization_info().organization_id,
            )
        )

        predicttuple = client.get_task(predicttuple_key)
        dataset_ref = [
            x for x in predicttuple.inputs if x.identifier == substra.sdk.schemas.StaticInputIdentifier.opener
        ]
        assert len(dataset_ref) == 1
        assert dataset_ref[0].asset_key == dataset_key

        assert len(predicttuple.inputs) == 3  # data sample + opener + input task

        model_ref = [x for x in predicttuple.inputs if x.identifier == InputIdentifiers.model]
        assert len(model_ref) == 1
        assert model_ref[0].parent_task_key == traintuple_key

        # test testtuple extra fields
        testtuple_key = client.add_task(
            substra.sdk.schemas.TaskSpec(
                algo_key=metric_key,
                inputs=FLTaskInputGenerator.tuple(opener_key=dataset_key, data_sample_keys=[data_sample_key])
                + FLTaskInputGenerator.predict_to_test(predicttuple_key),
                outputs=FLTaskOutputGenerator.testtuple(),
                worker=client.organization_info().organization_id,
            )
        )
        testtuple = client.get_task(testtuple_key)

        dataset_ref = [
            x for x in predicttuple.inputs if x.identifier == substra.sdk.schemas.StaticInputIdentifier.opener
        ]
        assert len(dataset_ref) == 1
        assert dataset_ref[0].asset_key == dataset_key
        assert len(predicttuple.inputs) == 3  # data sample + opener + input task

        model_ref = [x for x in testtuple.inputs if x.identifier == InputIdentifiers.predictions]
        assert len(model_ref) == 1
        assert model_ref[0].parent_task_key == predicttuple_key

        assert testtuple.algo
        assert testtuple.algo.key == metric_key

        # test composite extra field

        composite_traintuple_key = client.add_task(
            substra.sdk.schemas.TaskSpec(
                algo_key=composite_algo_key,
                inputs=FLTaskInputGenerator.tuple(opener_key=dataset_key, data_sample_keys=[data_sample_key]),
                outputs=FLTaskOutputGenerator.composite_traintuple(),
                worker=client.organization_info().organization_id,
            )
        )

        composite_traintuple = client.get_task(composite_traintuple_key)
        dataset_ref = [
            x for x in composite_traintuple.inputs if x.identifier == substra.sdk.schemas.StaticInputIdentifier.opener
        ]
        assert len(dataset_ref) == 1
        assert dataset_ref[0].asset_key == dataset_key
        assert len(composite_traintuple.inputs) == 2  # data sample + opener

    def test_add_two_compute_plan_with_same_cp_key(self, clients):
        client = clients[0]
        common_cp_key = str(uuid.uuid4())
        client.add_compute_plan(
            substra.sdk.schemas.ComputePlanSpec(
                key=common_cp_key,
                tag=None,
                name="My compute plan",
                metadata=dict(),
            )
        )
        with pytest.raises(exceptions.KeyAlreadyExistsError):
            client.add_compute_plan(
                substra.sdk.schemas.ComputePlanSpec(
                    key=common_cp_key,
                    tag=None,
                    name="My other compute plan",
                    metadata=dict(),
                )
            )

    def test_add_compute_plan_with_wrong_metadata(self, clients):
        client = clients[0]
        cp_key = str(uuid.uuid4())
        with pytest.raises(exceptions.InvalidRequest):
            client.add_compute_plan(
                substra.sdk.schemas.ComputePlanSpec(
                    key=cp_key,
                    tag=None,
                    name="My compute plan",
                    metadata={"wrong__key": "value"},
                )
            )

    def test_live_performances_json_file_exist(self, asset_factory, clients):
        """Assert the performances file is well created."""
        client = clients[0]

        dataset_query = asset_factory.create_dataset()
        dataset_key = client.add_dataset(dataset_query)

        data_sample = asset_factory.create_data_sample(datasets=[dataset_key], test_only=False)
        sample_key = client.add_data_sample(data_sample)

        algo_query = asset_factory.create_algo(AlgoCategory.simple)
        algo_key = client.add_algo(algo_query)

        predict_algo_spec = asset_factory.create_algo(category=AlgoCategory.predict)
        predict_algo_key = client.add_algo(predict_algo_spec)

        metric = asset_factory.create_algo(category=AlgoCategory.metric)
        metric_key = client.add_algo(metric)

        cp = asset_factory.create_compute_plan()

        traintuple = substra.sdk.schemas.ComputePlanTaskSpec(
            algo_key=algo_key,
            task_id=str(uuid.uuid4()),
            inputs=FLTaskInputGenerator.tuple(opener_key=dataset_key, data_sample_keys=[sample_key]),
            outputs=FLTaskOutputGenerator.traintuple(),
            worker=client.organization_info().organization_id,
        )

        predicttuple = substra.sdk.schemas.ComputePlanTaskSpec(
            algo_key=predict_algo_key,
            task_id=str(uuid.uuid4()),
            inputs=FLTaskInputGenerator.tuple(opener_key=dataset_key, data_sample_keys=[sample_key])
            + FLTaskInputGenerator.train_to_predict(traintuple.task_id),
            outputs=FLTaskOutputGenerator.predicttuple(),
            worker=client.organization_info().organization_id,
        )

        testtuples = [
            substra.sdk.schemas.ComputePlanTaskSpec(
                task_id=str(uuid.uuid4()),
                algo_key=metric_key,
                inputs=FLTaskInputGenerator.tuple(opener_key=dataset_key, data_sample_keys=[sample_key])
                + FLTaskInputGenerator.predict_to_test(predicttuple.task_id),
                outputs=FLTaskOutputGenerator.testtuple(),
                worker=client.organization_info().organization_id,
            )
        ]
        cp.tasks = [traintuple, predicttuple] + testtuples

        client.add_compute_plan(cp)

        json_perf_path = client.temp_directory.parent / "live_performances" / cp.key / "performances.json"

        assert json_perf_path.is_file()


class TestsList:
    "Test client.list... functions"

    @pytest.fixture()
    def _init_data_samples(self, asset_factory, docker_clients):
        client = docker_clients[0]
        data_sample_keys = []
        dataset_query = asset_factory.create_dataset()
        dataset_key = client.add_dataset(dataset_query)

        data_sample_1 = asset_factory.create_data_sample(datasets=[dataset_key], test_only=False)
        data_sample_keys.append(client.add_data_sample(data_sample_1))

        data_sample_2 = asset_factory.create_data_sample(datasets=[dataset_key], test_only=True)
        data_sample_keys.append(client.add_data_sample(data_sample_2))

        data_sample_3 = asset_factory.create_data_sample(datasets=[dataset_key], test_only=False)
        data_sample_keys.append(client.add_data_sample(data_sample_3))
        return client, data_sample_keys

    @pytest.mark.parametrize("asset_name", ["dataset", "algo"])
    def test_list_assets(self, asset_name, asset_factory, docker_clients):
        client = docker_clients[0]
        query = getattr(asset_factory, f"create_{asset_name}")()
        key = getattr(client, f"add_{asset_name}")(query)

        assets = getattr(client, f"list_{asset_name}")()

        assert assets[0].key == key

    def test_list_datasamples_all(self, _init_data_samples):
        # get all datasamples
        client, _ = _init_data_samples
        data_samples = client.list_data_sample(ascending=False)
        assert len(data_samples) >= 3
        # assert dates in descending order
        assert all(
            data_samples[i].creation_date >= data_samples[i + 1].creation_date for i in range(len(data_samples) - 1)
        )

    def test_list_datasamples_all_order_ascending(self, _init_data_samples):
        # get all datasamples
        client, _ = _init_data_samples
        data_samples = client.list_data_sample(ascending=True)
        assert len(data_samples) >= 3
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

    def test_list_filter_on_field(self, docker_clients, asset_factory):
        client = docker_clients[0]
        dataset_keys = set()

        n_datasets = 2

        for _ in range(n_datasets):
            dataset_query = asset_factory.create_dataset(name="dataset_dummy_")
            dataset_key = client.add_dataset(dataset_query)
            dataset_keys.add(dataset_key)

        # Get all samples with test_only
        filters = {"name": "dataset_dummy_"}
        datasets = client.list_dataset(filters=filters)
        assert len(datasets) == n_datasets
        assert set([d.key for d in datasets]) == dataset_keys


def test_execute_compute_plan_several_testtuples_per_train(asset_factory, subprocess_clients):
    client = subprocess_clients[0]

    dataset_query = asset_factory.create_dataset()
    dataset_key = client.add_dataset(dataset_query)

    data_sample_1 = asset_factory.create_data_sample(datasets=[dataset_key], test_only=False)
    sample_1_key = client.add_data_sample(data_sample_1)

    algo_query = asset_factory.create_algo(AlgoCategory.simple)
    algo_key = client.add_algo(algo_query)

    predict_algo_spec = asset_factory.create_algo(category=AlgoCategory.predict)
    predict_algo_key = client.add_algo(predict_algo_spec)

    metric = asset_factory.create_algo(category=AlgoCategory.metric)
    metric_key = client.add_algo(metric)

    cp = asset_factory.create_compute_plan()

    traintuple = substra.sdk.schemas.ComputePlanTaskSpec(
        algo_key=algo_key,
        task_id=str(uuid.uuid4()),
        inputs=FLTaskInputGenerator.tuple(opener_key=dataset_key, data_sample_keys=[sample_1_key]),
        outputs=FLTaskOutputGenerator.traintuple(),
        worker=client.organization_info().organization_id,
    )

    predicttuple = substra.sdk.schemas.ComputePlanTaskSpec(
        algo_key=predict_algo_key,
        task_id=str(uuid.uuid4()),
        inputs=FLTaskInputGenerator.tuple(opener_key=dataset_key, data_sample_keys=[sample_1_key])
        + FLTaskInputGenerator.train_to_predict(traintuple.task_id),
        outputs=FLTaskOutputGenerator.predicttuple(),
        worker=client.organization_info().organization_id,
    )

    testtuples = [
        substra.sdk.schemas.ComputePlanTaskSpec(
            task_id=str(uuid.uuid4()),
            algo_key=metric_key,
            inputs=FLTaskInputGenerator.tuple(opener_key=dataset_key, data_sample_keys=[sample_1_key])
            + FLTaskInputGenerator.predict_to_test(predicttuple.task_id),
            outputs=FLTaskOutputGenerator.testtuple(),
            worker=client.organization_info().organization_id,
        )
        for _ in range(2)
    ]
    cp.tasks = [traintuple, predicttuple] + testtuples

    compute_plan = client.add_compute_plan(cp)
    assert compute_plan.done_count == 4

    tasks = client.list_task(filters={"compute_plan_key": [compute_plan.key]})
    assert len(tasks) == 4


def test_two_composite_to_composite(asset_factory, subprocess_clients):
    client = subprocess_clients[0]

    dataset_query = asset_factory.create_dataset()
    dataset_key = client.add_dataset(dataset_query)

    data_sample_1 = asset_factory.create_data_sample(datasets=[dataset_key], test_only=False)
    sample_1_key = client.add_data_sample(data_sample_1)

    algo_query = asset_factory.create_algo(AlgoCategory.composite)
    algo_key = client.add_algo(algo_query)

    predict_algo_spec = asset_factory.create_algo(category=AlgoCategory.predict_composite)
    predict_algo_key = client.add_algo(predict_algo_spec)

    metric = asset_factory.create_algo(category=AlgoCategory.metric)
    metric_key = client.add_algo(metric)

    cp = asset_factory.create_compute_plan()

    authorized_ids = ["MyOrg1", "MyOrg2"]

    composite_1_key = str(uuid.uuid4())
    composite_1 = substra.sdk.schemas.ComputePlanTaskSpec(
        algo_key=algo_key,
        task_id=composite_1_key,
        inputs=FLTaskInputGenerator.tuple(opener_key=dataset_key, data_sample_keys=[sample_1_key]),
        outputs=FLTaskOutputGenerator.composite_traintuple(
            shared_authorized_ids=authorized_ids, local_authorized_ids=authorized_ids
        ),
        worker=client.organization_info().organization_id,
    )
    composite_2_key = str(uuid.uuid4())
    composite_2 = substra.sdk.schemas.ComputePlanTaskSpec(
        algo_key=algo_key,
        task_id=composite_2_key,
        inputs=FLTaskInputGenerator.tuple(opener_key=dataset_key, data_sample_keys=[sample_1_key]),
        outputs=FLTaskOutputGenerator.composite_traintuple(
            shared_authorized_ids=authorized_ids, local_authorized_ids=authorized_ids
        ),
        worker=client.organization_info().organization_id,
    )

    composite_3_key = str(uuid.uuid4())
    composite_3 = substra.sdk.schemas.ComputePlanTaskSpec(
        algo_key=algo_key,
        task_id=composite_3_key,
        inputs=FLTaskInputGenerator.tuple(opener_key=dataset_key, data_sample_keys=[sample_1_key])
        + FLTaskInputGenerator.composite_to_composite(composite_1_key, composite_2_key),
        outputs=FLTaskOutputGenerator.composite_traintuple(
            shared_authorized_ids=authorized_ids, local_authorized_ids=authorized_ids
        ),
        worker=client.organization_info().organization_id,
    )

    predicttuple_key = str(uuid.uuid4())
    predicttuple = substra.sdk.schemas.ComputePlanTaskSpec(
        algo_key=predict_algo_key,
        task_id=predicttuple_key,
        inputs=FLTaskInputGenerator.tuple(opener_key=dataset_key, data_sample_keys=[sample_1_key])
        + FLTaskInputGenerator.composite_to_predict(composite_3_key),
        outputs=FLTaskOutputGenerator.predicttuple(authorized_ids),
        worker=client.organization_info().organization_id,
    )

    testtuple = substra.sdk.schemas.ComputePlanTaskSpec(
        algo_key=metric_key,
        task_id=str(uuid.uuid4()),
        inputs=FLTaskInputGenerator.tuple(opener_key=dataset_key, data_sample_keys=[sample_1_key])
        + FLTaskInputGenerator.predict_to_test(predicttuple_key),
        outputs=FLTaskOutputGenerator.testtuple(authorized_ids),
        worker=client.organization_info().organization_id,
    )

    cp.tasks = [composite_1, composite_2, composite_3, predicttuple, testtuple]

    compute_plan = client.add_compute_plan(cp)
    assert compute_plan.done_count == 5
    assert client.get_performances(compute_plan.key).performance[0] == 32


def test_task_different_owner_dataset(asset_factory, clients):
    client = clients[0]

    # set dataset, metric and algo
    dataset_query = asset_factory.create_dataset()
    dataset_key = client.add_dataset(dataset_query)

    data_sample = asset_factory.create_data_sample(datasets=[dataset_key], test_only=False)
    data_sample_key = client.add_data_sample(data_sample)

    algo_query = asset_factory.create_algo(AlgoCategory.simple)
    algo_key = client.add_algo(algo_query)

    with pytest.raises(substra.sdk.exceptions.InvalidRequest) as err:
        client.add_task(
            substra.sdk.schemas.TaskSpec(
                algo_key=algo_key,
                inputs=[
                    substra.sdk.schemas.InputRef(identifier=InputIdentifiers.datasamples, asset_key=data_sample_key),
                    substra.sdk.schemas.InputRef(identifier=InputIdentifiers.opener, asset_key=dataset_key),
                ],
                outputs=FLTaskOutputGenerator.traintuple(),
                worker="bad_worker",
            )
        )
    assert "The task worker must be the organization that contains the data:" in str(err.value)


class TestMultipleOrgLocalClient:
    def test_local_org_info(self, docker_clients):

        org1info = docker_clients[0].organization_info()
        org2info = docker_clients[1].organization_info()

        assert org1info.organization_id != org2info.organization_id

    def test_list_org(self, docker_clients):

        org1_id = docker_clients[0].organization_info().organization_id
        org2_id = docker_clients[1].organization_info().organization_id

        orgs = docker_clients[0].list_organization()

        org1 = [x for x in orgs if x.id == org1_id]
        assert len(org1) == 1
        assert org1[0].is_current

        org2 = [x for x in orgs if x.id == org2_id]
        assert len(org2) == 1
        assert not org2[0].is_current

    def test_local_org_owner(self, asset_factory, docker_clients):

        client = docker_clients[0]
        dataset_query = asset_factory.create_dataset()
        dataset_key = client.add_dataset(dataset_query)

        dataset = client.get_dataset(dataset_key)
        assert dataset.owner == client.organization_info().organization_id

    def test_local_org_shared_db(self, asset_factory, docker_clients):

        dataset_query = asset_factory.create_dataset()
        dataset_key = docker_clients[0].add_dataset(dataset_query)

        docker_clients[1].get_dataset(dataset_key)
