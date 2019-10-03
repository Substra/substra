import os
import json
import shutil
import time
import hashlib

import docker

USER = os.getuid()

METRICS_NO_FAKE_Y = "DISABLED"
METRICS_FAKE_Y = "FAKE_Y"

VOLUME_OUTPUT_MODEL = {'bind': '/sandbox/model', 'mode': 'rw'}
VOLUME_OPENER = {'bind': '/sandbox/opener/__init__.py', 'mode': 'ro'}
VOLUME_PRED = {'bind': '/sandbox/pred', 'mode': 'rw'}
VOLUME_DATA = {'bind': '/sandbox/data', 'mode': 'ro'}
VOLUME_LOCAL = {'bind': '/sandbox/local', 'mode': 'rw'}


def _create_directory(directory):
    if not os.path.exists(directory):
        print(f'Create path : {directory}')
        os.makedirs(directory)


def _get_metrics_command(fake_data_samples=False):
    mode = METRICS_FAKE_Y if fake_data_samples else METRICS_NO_FAKE_Y
    return f"--dry-run-mode {mode}"


def setup(algo_path,
          train_opener_path,
          test_opener_path,
          metrics_path,
          train_data_samples_path,
          test_data_samples_path,
          outmodel_path='model',
          compute_path='./sandbox',
          local_path='local'):

    config = {}

    def _get_relpath(base_path, relpath):
        return os.path.abspath(os.path.join(base_path, relpath))

    # default values
    train_opener_path = train_opener_path or \
        _get_relpath(algo_path, '../dataset/opener.py')
    test_opener_path = test_opener_path or \
        _get_relpath(algo_path, '../objective/opener.py')
    metrics_path = metrics_path or \
        _get_relpath(algo_path, '../objective/')
    train_data_samples_path = train_data_samples_path or \
        _get_relpath(algo_path, '../dataset/data-samples/')
    test_data_samples_path = test_data_samples_path or \
        _get_relpath(algo_path, '../objective/data-samples/')

    def _get_abspath(path):
        if path:  # path may be None
            path = os.path.abspath(path)
        return path

    # setup config
    config['algo_path'] = _get_abspath(algo_path)
    config['train_opener_file'] = _get_abspath(train_opener_path)
    config['test_opener_file'] = _get_abspath(test_opener_path)
    config['train_data_path'] = _get_abspath(train_data_samples_path)
    config['test_data_path'] = _get_abspath(test_data_samples_path)
    config['metrics_path'] = _get_abspath(metrics_path)

    # sandbox
    run_local_path = _get_abspath(compute_path)

    print(f'Run local results will be in sandbox : {run_local_path}')
    print(f'Clean run local sandbox {run_local_path}')

    try:
        shutil.rmtree(run_local_path)
    except FileNotFoundError:
        pass

    config['local_path'] = os.path.join(run_local_path, local_path)
    config['train_pred_path'] = os.path.join(run_local_path, 'pred_train')
    config['test_pred_path'] = os.path.join(run_local_path, 'pred_test')
    config['outmodel_path'] = os.path.join(run_local_path, outmodel_path)

    _create_directory(run_local_path)
    _create_directory(config['local_path'])
    _create_directory(config['train_pred_path'])
    _create_directory(config['test_pred_path'])
    _create_directory(config['outmodel_path'])

    return config


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
        docker_client.containers.run(name, command=command,
                                     volumes=volumes, remove=remove, user=USER)
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


def compute(config, rank, inmodels, fake_data_samples=False):
    docker_client = docker.from_env()
    docker_algo_tag = 'algo_run_local'
    docker_metrics_tag = 'metrics_run_local'

    outmodel_path = config['outmodel_path']
    train_pred_path = config['train_pred_path']
    algo_path = config['algo_path']
    local_path = config['local_path']
    train_opener_file = config['train_opener_file']
    metrics_path = config['metrics_path']
    test_pred_path = config['test_pred_path']
    test_opener_file = config['test_opener_file']
    test_data_path = config['test_data_path']
    train_data_path = config['train_data_path']

    train_data_path_str = train_data_path or 'fake'

    model_key = 'model'
    outmodel_file = os.path.join(outmodel_path, model_key)

    print('Training starts')

    _docker_build(docker_client, algo_path, docker_algo_tag)

    if not fake_data_samples:
        print(f'Training algo on {train_data_path}')
    else:
        print('Training algo fake data samples')

    volumes = {outmodel_path: VOLUME_OUTPUT_MODEL,
               train_pred_path: VOLUME_PRED,
               local_path: VOLUME_LOCAL,
               train_opener_file: VOLUME_OPENER}

    if not fake_data_samples:
        volumes[train_data_path] = VOLUME_DATA

    command = 'train'
    if fake_data_samples:
        command += " --dry-run"

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

    _docker_run(docker_client, docker_algo_tag, command=command,
                volumes=volumes)

    if not os.path.exists(outmodel_file):
        raise Exception(f"Model {outmodel_file} doesn't exist")

    _docker_build(docker_client, metrics_path, docker_metrics_tag, rm=True)

    print(f'Evaluating performance - compute metrics with {train_pred_path} '
          f'predictions against {train_data_path_str} labels')

    volumes = {train_pred_path: VOLUME_PRED,
               train_opener_file: VOLUME_OPENER}
    if not fake_data_samples:
        volumes[train_data_path] = VOLUME_DATA
    command = _get_metrics_command(fake_data_samples)
    _docker_run(docker_client, docker_metrics_tag, command=command,
                volumes=volumes)

    # load performance
    with open(os.path.join(train_pred_path, 'perf.json'), 'r') as perf_file:
        perf = json.load(perf_file)
    train_perf = perf['all']

    print(f'Successfully train model {outmodel_file} with a score of '
          f'{train_perf} on train data')

    print('Testing starts')

    _docker_build(docker_client, algo_path, docker_algo_tag)

    print('Testing model')

    test_data_path_str = test_data_path or 'fake'
    print(f'Testing model on {test_data_path_str} labels with {model_key} '
          f'saved in {test_pred_path}')

    volumes = {outmodel_path: VOLUME_OUTPUT_MODEL,
               test_pred_path: VOLUME_PRED,
               test_opener_file: VOLUME_OPENER}
    if not fake_data_samples:
        volumes[test_data_path] = VOLUME_DATA

    command = f"predict {model_key}"
    if fake_data_samples:
        command += " --dry-run"
    _docker_run(docker_client, docker_algo_tag, command=command,
                volumes=volumes)

    _docker_build(docker_client, metrics_path, docker_metrics_tag)

    print(f'Evaluating performance - compute metric with {test_pred_path} '
          f'predictions against {test_data_path_str} labels')

    volumes = {test_pred_path: VOLUME_PRED,
               test_opener_file: VOLUME_OPENER}
    if not fake_data_samples:
        volumes[test_data_path] = VOLUME_DATA

    command = _get_metrics_command(fake_data_samples)
    _docker_run(docker_client, docker_metrics_tag, command=command,
                volumes=volumes)

    # load performance
    with open(os.path.join(test_pred_path, 'perf.json'), 'r') as perf_file:
        perf = json.load(perf_file)
    test_perf = perf['all']

    print(f'Successfully test model {outmodel_file} with a score of {test_perf} on test data')
