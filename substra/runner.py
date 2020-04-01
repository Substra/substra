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

import contextlib
import os
import json
import shutil
import tarfile
import tempfile
import time
import hashlib
import zipfile

import docker

USER = os.getuid()

METRICS_NO_FAKE_Y = "DISABLED"
METRICS_FAKE_Y = "FAKE_Y"

VOLUME_OUTPUT_MODEL = {'bind': '/sandbox/model', 'mode': 'rw'}
VOLUME_OPENER = {'bind': '/sandbox/opener/__init__.py', 'mode': 'ro'}
VOLUME_PRED = {'bind': '/sandbox/pred', 'mode': 'rw'}
VOLUME_DATA = {'bind': '/sandbox/data', 'mode': 'ro'}
VOLUME_LOCAL = {'bind': '/sandbox/local', 'mode': 'rw'}

DOCKER_ALGO_TAG = 'algo_run_local'
DOCKER_METRICS_TAG = 'metrics_run_local'
MODEL_FILENAME = 'model'


def _create_directory(directory):
    if not os.path.exists(directory):
        print(f'Create path : {directory}')
        os.makedirs(directory)


def _get_metrics_command(fake_data_samples=False):
    mode = METRICS_FAKE_Y if fake_data_samples else METRICS_NO_FAKE_Y
    return f"--fake-data-mode {mode}"


def _get_abspath(path):
    if path:  # path may be None
        path = os.path.abspath(path)
    return path


def clean_sandbox(compute_path, local_path, test_pred_path, outmodel_path):
    print(f'Clean run local sandbox {compute_path}')

    try:
        shutil.rmtree(compute_path)
    except FileNotFoundError:
        pass

    _create_directory(compute_path)
    _create_directory(local_path)
    _create_directory(test_pred_path)
    _create_directory(outmodel_path)


def _docker_build(docker_client, dockerfile_path, name, rm=False):
    print(f'Creating docker {name}', end=' ', flush=True)
    start = time.time()
    docker_client.images.build(path=dockerfile_path,
                               tag=name,
                               rm=rm)
    elaps = time.time() - start
    print(f'(duration {elaps:.2f} s )')


def _docker_run(docker_client, name, command, volumes, remove=True):
    print(f'Running docker {name}', end=' ', flush=True)
    start = time.time()
    try:
        # Setting userns_mode to "host" effectively turns off user namespaces
        # (see https://github.com/moby/moby/issues/25492#issuecomment-239173095).
        # Turning it off prevents permission issues when accessing the host
        # filesystem from the container.
        # It is safe to do because we also use the user=USER option: the `UID`
        # in the container is set to the `UID` of the current process.
        docker_client.containers.run(name, command=command,
                                     volumes=volumes, remove=remove, user=USER,
                                     userns_mode="host")
    except docker.errors.ContainerError as e:
        # try to pretty print traceback
        try:
            err = e.stderr.decode('utf-8')
        except Exception:
            raise e
        msg = (
            f"Command '{command}' in image '{name}' returned non-zero exit "
            f"status {e.exit_status}:\n{err}"
        )
        raise Exception(msg)

    elaps = time.time() - start
    print(f'(duration {elaps:.2f} s )')


def compute_train(docker_client, train_data_path, algo_path, fake_data_samples, outmodel_path,
                  local_path, train_opener_file, rank, inmodels, outmodel_file):

    print('Training starts')

    _docker_build(docker_client, algo_path, DOCKER_ALGO_TAG)

    if not fake_data_samples:
        print(f'Training algo on {train_data_path}')
    else:
        print('Training algo fake data samples')

    volumes = {outmodel_path: VOLUME_OUTPUT_MODEL,
               local_path: VOLUME_LOCAL,
               train_opener_file: VOLUME_OPENER}

    if not fake_data_samples:
        volumes[train_data_path] = VOLUME_DATA

    command = 'train'
    if fake_data_samples:
        command += " --fake-data"

    if rank is not None:
        command += f" --rank {rank}"

    if inmodels:
        model_keys = []

        for inmodel in inmodels:
            src = os.path.abspath(inmodel)
            model_hash = hashlib.sha256(src.encode()).hexdigest()
            dst = os.path.join(outmodel_path, model_hash)
            os.link(src, dst)
            print(f"Creating model symlink from {src} to {dst}")
            model_keys.append(model_hash)

        if model_keys:
            models_command = ' '.join(model_keys)
            command += f" {models_command}"

    _docker_run(docker_client, DOCKER_ALGO_TAG, command=command,
                volumes=volumes)

    if not os.path.exists(outmodel_file):
        raise Exception(f"Model {outmodel_file} doesn't exist")


def compute_test(docker_client, algo_path, test_data_path, test_pred_path, outmodel_path,
                 test_opener_file, fake_data_samples, metrics_path):
    print('Testing starts')

    _docker_build(docker_client, algo_path, DOCKER_METRICS_TAG)

    print('Testing model')

    test_data_path_str = test_data_path or 'fake'
    print(f'Testing model on {test_data_path_str} labels with {MODEL_FILENAME} '
          f'saved in {test_pred_path}')

    volumes = {outmodel_path: VOLUME_OUTPUT_MODEL,
               test_pred_path: VOLUME_PRED,
               test_opener_file: VOLUME_OPENER}
    if not fake_data_samples:
        volumes[test_data_path] = VOLUME_DATA

    command = f"predict {MODEL_FILENAME}"
    if fake_data_samples:
        command += " --fake-data"
    _docker_run(docker_client, DOCKER_ALGO_TAG, command=command,
                volumes=volumes)

    _docker_build(docker_client, metrics_path, DOCKER_METRICS_TAG)


def compute_perf(pred_path, opener_file, fake_data_samples, data_path, docker_client):
    volumes = {pred_path: VOLUME_PRED,
               opener_file: VOLUME_OPENER}
    if not fake_data_samples:
        volumes[data_path] = VOLUME_DATA

    command = _get_metrics_command(fake_data_samples)
    _docker_run(docker_client, DOCKER_METRICS_TAG, command=command,
                volumes=volumes)

    with open(os.path.join(pred_path, 'perf.json'), 'r') as perf_file:
        perf = json.load(perf_file)

    return perf['all']


class PathTraversalException(Exception):

    def __init__(self, archive_path, issue_path):
        self.msg = (
            f'Path Traversal Error : archive {archive_path} contains '
            f'{issue_path} which is not safe.'
        )
        super().__init__(self.msg)
        self.archive_path = archive_path
        self.issue_path = issue_path

    def __repr__(self):
        return self.msg


def raise_if_path_traversal(requested_paths, to_directory, archive_path):
    # Inspired from https://stackoverflow.com/a/45188896

    # Get real path and ensure there is a suffix /
    # at the end of the path
    safe_directory = os.path.join(
        os.path.realpath(to_directory),
        ''
    )

    if not isinstance(requested_paths, list):
        raise TypeError(f'requested_paths argument should be a list not a {type(requested_paths)}')

    for requested_path in requested_paths:
        real_requested_path = os.path.realpath(requested_path)
        is_traversal = os.path.commonprefix([real_requested_path,
                                             safe_directory]) != safe_directory

        if is_traversal:
            raise PathTraversalException(
                archive_path,
                requested_path.replace(to_directory, '')
            )


def _extract_archive(archive_path, to_directory):
    if zipfile.is_zipfile(archive_path):
        with zipfile.ZipFile(archive_path, 'r') as zf:

            # Check no path traversal
            filenames = [os.path.join(to_directory, filename)
                         for filename in zf.namelist()]
            raise_if_path_traversal(filenames, to_directory, archive_path)

            zf.extractall(to_directory)

    elif tarfile.is_tarfile(archive_path):
        with tarfile.open(archive_path, 'r:*') as tf:

            # Check no path traversal
            filenames = [os.path.join(to_directory, filename)
                         for filename in tf.getnames()]
            raise_if_path_traversal(filenames, to_directory, archive_path)

            tf.extractall(to_directory)
    else:
        raise ValueError('Archive must be zip or tar.gz')


@contextlib.contextmanager
def extract_archive_if_needed(path):
    if os.path.isdir(path):
        yield path
    else:
        with tempfile.TemporaryDirectory() as tmp_dir:
            _extract_archive(path, tmp_dir)
            yield tmp_dir


def _compute(algo_path,
             train_opener_file,
             test_opener_file,
             metrics_path,
             train_data_path,
             test_data_path,
             fake_data_samples,
             rank,
             inmodels,
             outmodel_path='model',
             compute_path='./sandbox',
             local_path='local'):

    # assets absolute paths
    algo_path = _get_abspath(algo_path)
    train_opener_file = _get_abspath(train_opener_file)
    test_opener_file = _get_abspath(test_opener_file)
    train_data_path = _get_abspath(train_data_path)
    test_data_path = _get_abspath(test_data_path)
    metrics_path = _get_abspath(metrics_path)

    # substra/docker absolute paths
    compute_path = _get_abspath(compute_path)
    local_path = os.path.join(compute_path, local_path)
    test_pred_path = os.path.join(compute_path, 'pred_test')
    outmodel_path = os.path.join(compute_path, outmodel_path)
    outmodel_file = os.path.join(outmodel_path, MODEL_FILENAME)

    print(f'Run local results will be in sandbox : {compute_path}')

    clean_sandbox(compute_path, local_path, test_pred_path, outmodel_path)

    docker_client = docker.from_env()

    compute_train(docker_client,
                  train_data_path,
                  algo_path,
                  fake_data_samples,
                  outmodel_path,
                  local_path,
                  train_opener_file,
                  rank,
                  inmodels,
                  outmodel_file)

    print(f'Successfully train model {outmodel_file}')

    compute_test(docker_client,
                 algo_path,
                 test_data_path,
                 test_pred_path,
                 outmodel_path,
                 test_opener_file,
                 fake_data_samples,
                 metrics_path)

    print(f'Evaluating performance - compute metric with {test_pred_path} '
          f'predictions against {test_data_path or "fake"} labels')
    test_perf = compute_perf(pred_path=test_pred_path,
                             opener_file=test_opener_file,
                             fake_data_samples=fake_data_samples,
                             data_path=test_data_path,
                             docker_client=docker_client)
    print(f'Successfully test model {outmodel_file} with a score of {test_perf} on test data')


def compute(algo_path,
            train_opener_file,
            test_opener_file,
            metrics_path,
            train_data_path,
            test_data_path,
            fake_data_samples,
            rank,
            inmodels,
            outmodel_path='model',
            compute_path='./sandbox',
            local_path='local'):

    with extract_archive_if_needed(algo_path) as algo_path, \
            extract_archive_if_needed(metrics_path) as metrics_path:
        _compute(algo_path,
                 train_opener_file,
                 test_opener_file,
                 metrics_path,
                 train_data_path,
                 test_data_path,
                 fake_data_samples,
                 rank,
                 inmodels,
                 outmodel_path,
                 compute_path,
                 local_path)
