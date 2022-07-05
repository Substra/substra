import os
import pathlib
import shutil
import sys
import tempfile
import uuid
import zipfile

import substra
from substra.sdk.schemas import AlgoCategory

DEFAULT_DATA_SAMPLE_FILENAME = "data.csv"


DEFAULT_SUBSTRATOOLS_VERSION = (
    f"latest-nvidiacuda11.6.0-base-ubuntu20.04-python{sys.version_info.major}.{sys.version_info.minor}-minimal"
)

DEFAULT_SUBSTRATOOLS_DOCKER_IMAGE = f"gcr.io/connect-314908/connect-tools:{DEFAULT_SUBSTRATOOLS_VERSION}"

DEFAULT_OPENER_SCRIPT = f"""
import csv
import json
import os
import substratools as tools
class TestOpener(tools.Opener):
    def get_X(self, folders):
        res = []
        for folder in folders:
            with open(os.path.join(folder, '{DEFAULT_DATA_SAMPLE_FILENAME}'), 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    res.append(int(row[0]))
        print(f'get_X: {{res}}')
        return res  # returns a list of 1's
    def get_y(self, folders):
        res = []
        for folder in folders:
            with open(os.path.join(folder, '{DEFAULT_DATA_SAMPLE_FILENAME}'), 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    res.append(int(row[1]))
        print(f'get_y: {{res}}')
        return res  # returns a list of 2's
    def fake_X(self, n_samples=None):
        if n_samples is None:
            n_samples = 1
        res = [10] * n_samples
        print(f'fake_X: {{res}}')
        return res
    def fake_y(self, n_samples=None):
        if n_samples is None:
            n_samples = 1
        res = [30] * n_samples
        print(f'fake_y: {{res}}')
        return res
    def get_predictions(self, path):
        with open(path) as f:
            return json.load(f)
    def save_predictions(self, y_pred, path):
        with open(path, 'w') as f:
            return json.dump(y_pred, f)
"""

DEFAULT_METRIC_ALGO_SCRIPT = """
import json
import substratools as tools
class TestMetrics(tools.Metrics):
    def score(self, y_true, y_pred):
        res = sum(y_pred) - sum(y_true)
        print(f'metrics, y_true: {y_true}, y_pred: {y_pred}, result: {res}')
        return res
if __name__ == '__main__':
    tools.metrics.execute(TestMetrics())
"""

DEFAULT_ALGO_SCRIPT = """
import json
import substratools as tools
class TestAlgo(tools.Algo):
    def train(self, X, y, models, rank):
        print(f'Train, get X: {X}, y: {y}, models: {models}')

        ratio = sum(y) / sum(X)
        err = 0.1 * ratio  # Add a small error

        if len(models) == 0:
            res = {'value': ratio + err }
        else:
            ratios = [m['value'] for m in models]
            avg = sum(ratios) / len(ratios)
            res = {'value': avg + err }

        print(f'Train, return {res}')
        return res

    def predict(self, X, model):
        res = [x * model['value'] for x in X]
        print(f'Predict, get X: {X}, model: {model}, return {res}')
        return res

    def load_model(self, path):
        with open(path) as f:
            return json.load(f)

    def save_model(self, model, path):
        with open(path, 'w') as f:
            return json.dump(model, f)

if __name__ == '__main__':
    tools.algo.execute(TestAlgo())
"""

DEFAULT_AGGREGATE_ALGO_SCRIPT = """
import json
import substratools as tools
class TestAggregateAlgo(tools.AggregateAlgo):
    def aggregate(self, models, rank):
        print(f'Aggregate models: {models}')
        values = [m['value'] for m in models]
        avg = sum(values) / len(values)
        res = {'value': avg}
        print(f'Aggregate result: {res}')
        return res
    def predict(self, X, model):
        predictions = 0
        return predictions
    def load_model(self, path):
        with open(path) as f:
            return json.load(f)
    def save_model(self, model, path):
        with open(path, 'w') as f:
            return json.dump(model, f)
if __name__ == '__main__':
    tools.algo.execute(TestAggregateAlgo())
"""

# TODO we should have a different serializer for head and trunk models

DEFAULT_COMPOSITE_ALGO_SCRIPT = """
import json
import substratools as tools
class TestCompositeAlgo(tools.CompositeAlgo):
    def train(self, X, y, head_model, trunk_model, rank):

        print(f'Composite algo train X: {X}, y: {y}, head_model: {head_model}, trunk_model: {trunk_model}')

        ratio = sum(y) / sum(X)
        err_head = 0.1 * ratio  # Add a small error
        err_trunk = 0.2 * ratio  # Add a small error

        if head_model:
            res_head = head_model['value']
        else:
            res_head = ratio

        if trunk_model:
            res_trunk = trunk_model['value']
        else:
            res_trunk = ratio

        res = {'value' : res_head + err_head }, {'value' : res_trunk + err_trunk }
        print(f'Composite algo train head, trunk result: {res}')
        return res

    def predict(self, X, head_model, trunk_model):
        print(f'Composite algo predict X: {X}, head_model: {head_model}, trunk_model: {trunk_model}')
        ratio_sum = head_model['value'] + trunk_model['value']
        res = [x * ratio_sum for x in X]
        print(f'Composite algo predict result: {res}')
        return res

    def load_head_model(self, path):
        return self._load_model(path)

    def save_head_model(self, model, path):
        return self._save_model(model, path)

    def load_trunk_model(self, path):
        return self._load_model(path)

    def save_trunk_model(self, model, path):
        return self._save_model(model, path)

    def _load_model(self, path):
        with open(path) as f:
            return json.load(f)

    def _save_model(self, model, path):
        with open(path, 'w') as f:
            return json.dump(model, f)

if __name__ == '__main__':
    tools.algo.execute(TestCompositeAlgo())
"""


DEFAULT_ALGO_SCRIPTS = {
    AlgoCategory.simple: DEFAULT_ALGO_SCRIPT,
    AlgoCategory.composite: DEFAULT_COMPOSITE_ALGO_SCRIPT,
    AlgoCategory.aggregate: DEFAULT_AGGREGATE_ALGO_SCRIPT,
    AlgoCategory.predict: DEFAULT_ALGO_SCRIPT,
    AlgoCategory.metric: DEFAULT_METRIC_ALGO_SCRIPT,
}

INVALID_ALGO_SCRIPT = DEFAULT_ALGO_SCRIPT.replace("train", "naitr")
INVALID_COMPOSITE_ALGO_SCRIPT = DEFAULT_COMPOSITE_ALGO_SCRIPT.replace("train", "naitr")
INVALID_AGGREGATE_ALGO_SCRIPT = DEFAULT_AGGREGATE_ALGO_SCRIPT.replace("aggregate", "etagergga")

DEFAULT_METRICS_DOCKERFILE = f"""
FROM {DEFAULT_SUBSTRATOOLS_DOCKER_IMAGE}
COPY metrics.py .
ENTRYPOINT ["python3", "metrics.py"]
"""

DEFAULT_ALGO_DOCKERFILE = f"""
FROM {DEFAULT_SUBSTRATOOLS_DOCKER_IMAGE}
COPY algo.py .
ENTRYPOINT ["python3", "algo.py"]
"""

BAD_ENTRYPOINT_DOCKERFILE = f"""
FROM {DEFAULT_SUBSTRATOOLS_DOCKER_IMAGE}
COPY algo.py .
ENTRYPOINT ["python3", "algo.txt"]
"""

NO_ENTRYPOINT_DOCKERFILE = f"""
FROM {DEFAULT_SUBSTRATOOLS_DOCKER_IMAGE}
COPY algo.py .
"""

DEFAULT_PERMISSIONS = substra.sdk.schemas.Permissions(public=True, authorized_ids=[])


def zip_folder(path, destination=None):
    if not destination:
        destination = os.path.join(os.path.dirname(path), os.path.basename(path) + ".zip")
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(path):
            for f in files:
                abspath = os.path.join(root, f)
                archive_path = os.path.relpath(abspath, start=path)
                zf.write(abspath, arcname=archive_path)
    return destination


def create_archive(tmpdir, *files):
    tmpdir.mkdir()
    for path, content in files:
        with open(tmpdir / path, "w") as f:
            f.write(content)
    return zip_folder(str(tmpdir))


def random_uuid():
    return str(uuid.uuid4())


def _shorten_name(name):
    """Format asset name to ensure they match the backend requirements."""
    if len(name) < 100:
        return name
    return name[:75] + "..." + name[:20]


def _get_key(obj, field="key"):
    """Get key from asset/spec or key."""
    if isinstance(obj, str):
        return obj
    return getattr(obj, field)


def _get_keys(obj, field="key"):
    """Get keys from asset/spec or key.

    This is particularly useful for data samples to accept as input args a list of keys
    and a list of data samples.
    """
    if not obj:
        return []
    return [_get_key(x, field=field) for x in obj]


class Counter:
    def __init__(self):
        self._idx = -1

    def inc(self):
        self._idx += 1
        return self._idx


class AssetsFactory:
    def __init__(self, name):
        self._data_sample_counter = Counter()
        self._dataset_counter = Counter()
        self._metric_counter = Counter()
        self._algo_counter = Counter()
        self._workdir = pathlib.Path(tempfile.mkdtemp(prefix="/tmp/"))
        self._uuid = name

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        shutil.rmtree(str(self._workdir), ignore_errors=True)

    def create_data_sample(self, content=None, datasets=None, test_only=False):
        idx = self._data_sample_counter.inc()
        tmpdir = self._workdir / f"data-{idx}"
        tmpdir.mkdir()

        content = content or "10,20"
        content = content.encode("utf-8")

        data_filepath = tmpdir / DEFAULT_DATA_SAMPLE_FILENAME
        with open(data_filepath, "wb") as f:
            f.write(content)

        datasets = datasets or []

        return substra.sdk.schemas.DataSampleSpec(
            path=str(tmpdir),
            test_only=test_only,
            data_manager_keys=datasets,
        )

    def create_dataset(self, permissions=None, metadata=None, py_script=None, logs_permission=None):
        idx = self._dataset_counter.inc()
        tmpdir = self._workdir / f"dataset-{idx}"
        tmpdir.mkdir()
        name = _shorten_name(f"{self._uuid} - Dataset {idx}")

        description_path = tmpdir / "description.md"
        description_content = name
        with open(description_path, "w") as f:
            f.write(description_content)

        opener_path = tmpdir / "opener.py"
        with open(opener_path, "w") as f:
            f.write(py_script or DEFAULT_OPENER_SCRIPT)

        return substra.sdk.schemas.DatasetSpec(
            name=name,
            data_opener=str(opener_path),
            type="Test",
            metadata=metadata,
            description=str(description_path),
            permissions=permissions or DEFAULT_PERMISSIONS,
            logs_permission=logs_permission or DEFAULT_PERMISSIONS,
        )

    def create_algo(
        self,
        category=AlgoCategory.simple,
        py_script=None,
        permissions=None,
        metadata=None,
        algo_spec=substra.sdk.schemas.AlgoSpec,
        dockerfile_type=None,
    ):
        idx = self._algo_counter.inc()
        tmpdir = self._workdir / f"algo-{idx}"
        tmpdir.mkdir()
        name = _shorten_name(f"{self._uuid} - Algo {idx}")

        description_path = tmpdir / "description.md"
        description_content = name
        with open(description_path, "w") as f:
            f.write(description_content)

        try:
            algo_content = py_script or DEFAULT_ALGO_SCRIPTS[category]
        except KeyError:
            raise Exception("Invalid algo category: ", category)

        algo_zip = create_archive(
            tmpdir / "algo",
            ("algo.py", algo_content),
            (
                "Dockerfile",
                (
                    BAD_ENTRYPOINT_DOCKERFILE
                    if dockerfile_type == "BAD_ENTRYPOINT"
                    else NO_ENTRYPOINT_DOCKERFILE
                    if dockerfile_type == "NO_ENTRYPOINT"
                    else DEFAULT_ALGO_DOCKERFILE
                ),
            ),
        )

        return algo_spec(
            name=name,
            category=category,
            description=str(description_path),
            file=str(algo_zip),
            permissions=permissions or DEFAULT_PERMISSIONS,
            metadata=metadata,
        )

    def create_traintuple(
        self,
        algo_key=None,
        data_manager_key=None,
        train_data_sample_keys=None,
        traintuples=None,
        tag=None,
        compute_plan_key=None,
        rank=None,
        metadata=None,
    ):
        train_data_sample_keys = train_data_sample_keys or []
        traintuples = traintuples or []

        for t in traintuples:
            assert isinstance(t, substra.sdk.models.Traintuple)

        return substra.sdk.schemas.TraintupleSpec(
            algo_key=algo_key,
            data_manager_key=data_manager_key,
            train_data_sample_keys=train_data_sample_keys,
            in_models_keys=traintuples,
            tag=tag,
            metadata=metadata,
            compute_plan_key=compute_plan_key,
            rank=rank,
        )

    def create_aggregatetuple(
        self,
        algo=None,
        worker=None,
        traintuples=None,
        tag=None,
        compute_plan_key=None,
        rank=None,
        metadata=None,
    ):
        traintuples = traintuples or []

        for t in traintuples:
            assert isinstance(t, (substra.sdk.models.Traintuple, substra.sdk.models.CompositeTraintuple))

        return substra.sdk.schemas.AggregatetupleSpec(
            algo_key=algo.key if algo else None,
            worker=worker,
            in_models_keys=[t.key for t in traintuples],
            tag=tag,
            metadata=metadata,
            compute_plan_key=compute_plan_key,
            rank=rank,
        )

    def create_composite_traintuple(
        self,
        algo=None,
        dataset=None,
        data_samples=None,
        head_traintuple=None,
        trunk_traintuple=None,
        tag=None,
        compute_plan_key=None,
        rank=None,
        permissions=None,
        metadata=None,
    ):
        data_samples = data_samples or []

        if head_traintuple and trunk_traintuple:
            assert isinstance(head_traintuple, substra.sdk.models.CompositeTraintuple)
            assert isinstance(
                trunk_traintuple,
                (substra.sdk.models.CompositeTraintuple, substra.sdk.models.Aggregatetuple),
            )
            in_head_model_key = head_traintuple.key
            in_trunk_model_key = trunk_traintuple.key
        else:
            in_head_model_key = None
            in_trunk_model_key = None

        return substra.sdk.schemas.CompositeTraintupleSpec(
            algo_key=algo.key if algo else None,
            data_manager_key=dataset.key if dataset else None,
            train_data_sample_keys=_get_keys(data_samples),
            in_head_model_key=in_head_model_key,
            in_trunk_model_key=in_trunk_model_key,
            tag=tag,
            metadata=metadata,
            compute_plan_key=compute_plan_key,
            rank=rank,
            out_trunk_model_permissions=permissions or DEFAULT_PERMISSIONS,
        )

    def create_testtuple(self, metric=None, traintuple=None, tag=None, dataset=None, data_samples=None, metadata=None):
        return substra.sdk.schemas.TesttupleSpec(
            metric_keys=[metric.key] if metric else [],
            traintuple_key=traintuple.key if traintuple else None,
            data_manager_key=dataset.key if dataset else None,
            test_data_sample_keys=_get_keys(data_samples),
            tag=tag,
            metadata=metadata,
        )

    def create_compute_plan(self, key=None, tag="", name="Test compute plan", clean_models=False, metadata=None):
        return substra.sdk.schemas.ComputePlanSpec(
            key=key or random_uuid(),
            traintuples=[],
            composite_traintuples=[],
            aggregatetuples=[],
            predicttuples=[],
            testtuples=[],
            tag=tag,
            name=name,
            metadata=metadata,
            clean_models=clean_models,
        )

    def add_compute_plan_tuples(self, compute_plan):
        return substra.sdk.schemas.UpdateComputePlanSpec(
            traintuples=[],
            composite_traintuples=[],
            aggregatetuples=[],
            predicttuples=[],
            testtuples=[],
            key=compute_plan.key,
        )
