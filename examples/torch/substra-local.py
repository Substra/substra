import contextlib
import importlib
import logging
from pathlib import Path
import shutil
import tarfile
import tempfile

import torchvision

DATASET_ROOT = './data'
CURRENT_DIR = Path(__file__).parent
_CIFAR10_ARCHIVE_NAME = 'cifar-10-python.tar.gz'
_OPENER_PATH = Path(CURRENT_DIR, 'assets/dataset/opener.py')
_ALGO_PATH = Path(CURRENT_DIR, 'assets/algo/algo.py')
_METRICS_PATH = Path(CURRENT_DIR, 'assets/objective/metrics.py')


def _load_module(path, module_name):
    """Import dynamically a python module."""
    assert path.exists(), "path '{}' not found".format(path)
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec, "could not load spec from path '{}'".format(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _untar(archive_path):
    """Untar archive in its current folder."""
    with tarfile.open(archive_path) as tar:
        tar.extractall(archive_path.parent)


@contextlib.contextmanager
def _to_datasamples_tree(filepaths):
    """Create a temporary data sample folders structure from input files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        folders = []
        for index, src in enumerate(filepaths):
            folder = Path(tmpdir, f'data_{index}/')
            folder.mkdir()
            # opener requires a filename data_batch_*
            dst = Path(folder, f'data_batch_{index}')
            shutil.copy(str(src), str(dst))

            folders.append(str(folder))
        yield folders


def run():
    """Run workflow in memory."""
    # download data
    torchvision.datasets.CIFAR10(root=DATASET_ROOT, download=True)
    _untar(Path(DATASET_ROOT, _CIFAR10_ARCHIVE_NAME))

    # load opener, algo and metrics from path
    Opener = _load_module(_OPENER_PATH, 'opener').TorchOpener
    algo = _load_module(_ALGO_PATH, 'algo').TorchClassifier()
    metrics = _load_module(_METRICS_PATH, 'algo').ClassifierMetrics()

    num_epochs = 2
    num_cifar10_batches = 5
    model = None
    data_root = Path(DATASET_ROOT, 'cifar-10-batches-py')

    # training
    rank = 0
    for epoch in range(num_epochs):  # loop over the dataset multiple times
        print(f'Epoch {epoch + 1}')
        datasample_paths = [
            Path(data_root, f'data_batch_{i + 1}') for i in range(num_cifar10_batches)
        ]
        with _to_datasamples_tree(datasample_paths) as tmp_datasamples_folders:
            # TODO randomize paths
            # load datasamples
            opener = Opener()
            X = opener.get_X(tmp_datasamples_folders)
            y = opener.get_y(tmp_datasamples_folders)

        # train algo
        input_models = [model] if model else []
        print('Executing training task')
        model = algo.train(X, y, models=input_models, rank=rank)
        rank += 1

    # testing
    datasample_path = Path(data_root, 'test_batch')
    with _to_datasamples_tree([datasample_path]) as test_folders:
        # load datasamples
        opener = Opener()
        X_test = opener.get_X(test_folders)
        y_test = opener.get_y(test_folders)

    print('Executing testing task')
    y_pred = algo.predict(X_test, model)
    score = metrics.score(y_test, y_pred)
    print(score)


if __name__ == '__main__':
    logging.basicConfig()
    run()
