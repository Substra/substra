# Copyright 2018 Owkin, inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import zipfile

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


def create_dir(path, root=None):
    if root:
        path = os.path.join(root, path)
    if os.path.exists(path):
        return
    os.makedirs(path)
    return path


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


def docker_run_side_effect(sandbox_path):
    def create_expected_docker_outputs(*args, **kwargs):
        name = args[1]
        if name == runner.DOCKER_ALGO_TAG:
            create_file('model/model', root=sandbox_path)
        if name == runner.DOCKER_METRICS_TAG:
            create_file('pred_test/perf.json', '{"all": 1}', root=sandbox_path)
    return create_expected_docker_outputs


def test_runner_folders(tmp_path, mocker):
    algo_path = create_dir('algo', root=tmp_path)
    train_opener_path = create_file('train/opener.py', root=tmp_path)
    test_opener_path = create_file('test/opener.py', root=tmp_path)
    metrics_path = create_dir('metrics', root=tmp_path)
    train_data_samples_path = create_dir('train_data_samples', root=tmp_path)
    test_data_samples_path = create_dir('test_data_samples_path', root=tmp_path)
    sandbox_path = create_dir('sandbox', root=tmp_path)

    mocker.patch('substra.runner.docker')
    mocker.patch('substra.runner._docker_run',
                 side_effect=docker_run_side_effect(sandbox_path))
    runner.compute(
        algo_path=algo_path,
        train_opener_file=train_opener_path,
        test_opener_file=test_opener_path,
        metrics_path=metrics_path,
        train_data_path=train_data_samples_path,
        test_data_path=test_data_samples_path,
        rank=0,
        inmodels=[],
        fake_data_samples=False,
        compute_path=sandbox_path
    )

    paths = (
        os.path.join(tmp_path, 'sandbox/model/model'),
    )
    for p in paths:
        assert os.path.exists(p)


def test_runner_archives(mocker, tmp_path):
    train_opener_path = create_file('train/opener.py', root=tmp_path)
    test_opener_path = create_file('test/opener.py', root=tmp_path)
    train_data_samples_path = create_dir('train_data_samples', root=tmp_path)
    test_data_samples_path = create_dir('test_data_samples_path', root=tmp_path)
    sandbox_path = create_dir('sandbox', root=tmp_path)

    algo_path = create_file('algo.zip', root=tmp_path)
    with zipfile.ZipFile(algo_path, 'w') as z:
        z.write(create_file('Dockerfile', root=tmp_path))
        z.write(create_file('algo.py', root=tmp_path))

    metrics_path = create_file('metrics.zip', root=tmp_path)
    with zipfile.ZipFile(metrics_path, 'w') as z:
        z.write(create_file('Dockerfile', root=tmp_path))
        z.write(create_file('metrics.py', root=tmp_path))

    mocker.patch('substra.runner.docker')
    mocker.patch('substra.runner._docker_run',
                 side_effect=docker_run_side_effect(sandbox_path))
    runner.compute(
        algo_path=algo_path,
        train_opener_file=train_opener_path,
        test_opener_file=test_opener_path,
        metrics_path=metrics_path,
        train_data_path=train_data_samples_path,
        test_data_path=test_data_samples_path,
        rank=0,
        inmodels=[],
        fake_data_samples=False,
        compute_path=sandbox_path
    )

    paths = (
        os.path.join(tmp_path, 'sandbox/model/model'),
    )
    for p in paths:
        assert os.path.exists(p)


def test_runner_invalid_archives(tmp_path):
    algo_path = create_file('algo.zip', root=tmp_path)
    train_opener_path = create_file('train/opener.py', root=tmp_path)
    test_opener_path = create_file('test/opener.py', root=tmp_path)
    metrics_path = create_file('metrics.zip', root=tmp_path)
    train_data_samples_path = create_dir('train_data_samples', root=tmp_path)
    test_data_samples_path = create_dir('test_data_samples_path', root=tmp_path)
    sandbox_path = create_dir('sandbox', root=tmp_path)

    with pytest.raises(ValueError, match="Archive must be zip or tar.gz"):
        runner.compute(
            algo_path=algo_path,
            train_opener_file=train_opener_path,
            test_opener_file=test_opener_path,
            metrics_path=metrics_path,
            train_data_path=train_data_samples_path,
            test_data_path=test_data_samples_path,
            rank=0,
            inmodels=[],
            fake_data_samples=False,
            compute_path=sandbox_path
        )
