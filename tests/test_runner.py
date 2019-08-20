import os

import pytest

from substra import runner


@pytest.fixture
def cwdir(tmpdir):
    old_cwd = os.getcwd()
    cwd = tmpdir / 'tmp'
    cwd.mkdir()
    os.chdir(str(cwd))
    yield
    os.chdir(old_cwd)


def create_dir(path):
    if os.path.exists(path):
        return
    os.makedirs(path)


def create_file(filename, content='', root=None):
    if not root:
        root = os.getcwd()
    filepath = os.path.join(root, filename)
    create_dir(os.path.dirname(filepath))
    with open(filepath, 'w') as fh:
        fh.write(content)
    return filepath


def do_algo_train_predict(*args, **kwargs):
    # create a single method doing both algo training and prediction
    create_file('model', root='sandbox/model')
    create_file('perf.json', content='{"all": 0.42}', root='sandbox/pred_train')
    create_file('pred', root='sandbox/pred_train')
    create_file('perf.json', content='{"all": 0.42}', root='sandbox/pred_test')
    create_file('pred', root='sandbox/pred_test')


@pytest.fixture
def docker_api(cwdir, mocker):
    def _run(*args, **kwargs):
        return do_algo_train_predict(*args, **kwargs)

    # create docker client instance
    client = mocker.Mock()
    client.containers.run.side_effect = _run

    # mock docker api from_env() method to return the mock docker client instance
    m = mocker.patch('substra.runner.docker', autospec=True)
    m.from_env.return_value = client


def test_runner(cwdir, docker_api):

    algo_path = create_file('algo.tar.gz')
    train_opener_path = create_file('train/opener.py')
    test_opener_path = create_file('test/opener.py')
    metrics_path = create_file('metrics.tar.gz')
    train_data_samples_path = create_dir('train_data_samples')
    test_data_samples_path = create_dir('test_data_samples_path')

    config = runner.setup(
        algo_path,
        train_opener_path,
        test_opener_path,
        metrics_path,
        train_data_samples_path,
        test_data_samples_path,
    )

    runner.compute(config, rank=0, inmodels=[], dry_run=False)

    paths = (
        'sandbox/model/model',
    )
    for p in paths:
        assert os.path.exists(p)
