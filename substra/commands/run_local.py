import os
import json
import docker
import time
import shutil
import hashlib

from .base import Base

metrics_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../run_local_materials/metrics')


USER = os.getuid()

METRICS_NO_DRY_RUN = 0
METRICS_FAKE_Y = 1

VOLUME_OUTPUT_MODEL = {'bind': '/sandbox/model', 'mode': 'rw'}
VOLUME_OPENER = {'bind': '/sandbox/opener/__init__.py', 'mode': 'ro'}
VOLUME_METRICS = {'bind': '/sandbox/metrics/__init__.py', 'mode': 'ro'}
VOLUME_PRED = {'bind': '/sandbox/pred', 'mode': 'rw'}
VOLUME_DATA = {'bind': '/sandbox/data', 'mode': 'ro'}
VOLUME_LOCAL = {'bind': '/sandbox/local', 'mode': 'rw'}


def create_directory(directory):
    if not os.path.exists(directory):
        print(f'Create path : {directory}')
        os.makedirs(directory)


def get_metrics_command(dry_run=False):
    mode = METRICS_FAKE_Y if dry_run else METRICS_NO_DRY_RUN
    return '-c "import substratools as tools; tools.metrics.execute(dry_run={})"' \
        .format(mode)


def setup_local(algo_path,
                train_opener_path, test_opener_path,
                metric_file_path,
                train_data_sample_path, test_data_sample_path,
                outmodel_path='./',
                compute_path='./sandbox',
                local_path='local'):

    config = {}

    # setup config
    config['algo_path'] = os.path.abspath(algo_path)

    config['train_opener_file'] = os.path.abspath(train_opener_path)
    config['test_opener_file'] = os.path.abspath(test_opener_path)
    config['train_data_path'] = train_data_sample_path
    config['test_data_path'] = test_data_sample_path
    config['metrics_file'] = os.path.abspath(metric_file_path)

    # check config values
    for key in config.keys():
        path = config[key]
        if path and not os.path.exists(path):
            raise Exception(f"Cannot launch local run: {key.replace('_', ' ')} {path} doesn't exist")

    # sandbox
    config['run_local_path'] = os.path.abspath(compute_path)

    print('Run local results will be in sandbox : %s' % config['run_local_path'])
    print('Clean run local sandbox %s' % config['run_local_path'])

    try:
        shutil.rmtree(config['run_local_path'])
    except FileNotFoundError:
        pass

    config['local_path'] = os.path.join(config['run_local_path'], local_path)
    config['train_pred_path'] = os.path.join(config['run_local_path'], 'pred_train')
    config['test_pred_path'] = os.path.join(config['run_local_path'], 'pred_test')
    config['outmodel_path'] = os.path.join(config['run_local_path'], outmodel_path)

    create_directory(config['run_local_path'])
    create_directory(config['local_path'])
    create_directory(config['train_pred_path'])
    create_directory(config['test_pred_path'])
    create_directory(config['outmodel_path'])

    return config


def _docker_build(docker_client, dockerfile_path, name, rm=False):
    print('Creating docker {}'.format(name), end=' ', flush=True)
    start = time.time()
    docker_client.images.build(path=dockerfile_path,
                               tag=name,
                               rm=rm)
    print('(duration %.2f s )' % (time.time() - start))


def _docker_run(docker_client, name, command, volumes, remove=True):
    print('Running docker {}'.format(name), end=' ', flush=True)
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
        else:
            msg = ("Command '{}' in image '{}' returned non-zero exit "
                   "status {}:\n{}").format(command, name, e.exit_status, err)
            raise Exception(msg)

    print('(duration %.2f s )' % (time.time() - start))


def compute_local(docker_client, config, rank, inmodels, dry_run=False):
    docker_algo_tag = 'algo_run_local'
    docker_metrics_tag = 'metrics_run_local'

    print('Training starts')

    _docker_build(docker_client, config['algo_path'], docker_algo_tag)

    if not dry_run:
        print('Training algo on %s' % (config['train_data_path'],))
    else:
        print('Training algo fake data samples')

    volumes = {config['outmodel_path']: VOLUME_OUTPUT_MODEL,
               config['train_pred_path']: VOLUME_PRED,
               config['local_path']: VOLUME_LOCAL,
               config['train_opener_file']: VOLUME_OPENER}
    if not dry_run:
        volumes[config['train_data_path']] = VOLUME_DATA

    command = 'train'
    if dry_run:
        command += " --dry-run"

    if rank is not None:
        command += f" --rank {rank}"

    if inmodels:
        model_keys = []

        for inmodel in inmodels:
            src = os.abspath(inmodel)
            model_hash = hashlib.sha256(src)
            dst = os.path.join(config['outmodel_path'], model_hash)
            os.symlink(src, dst)
            model_keys.append(model_hash)

        command += ' '.join(model_keys)
    _docker_run(docker_client, docker_algo_tag, command=command,
                volumes=volumes)

    model_key = 'model'
    if not os.path.exists(os.path.join(config['outmodel_path'], model_key)):
        raise Exception(f"Model ({os.path.join(config['outmodel_path'], model_key)}) doesn't exist")

    _docker_build(docker_client, metrics_path, docker_metrics_tag, rm=True)

    print('Evaluating performance - compute metrics with %s predictions against %s labels' % (
        config['train_pred_path'], config['train_data_path']))

    volumes = {config['train_pred_path']: VOLUME_PRED,
               config['metrics_file']: VOLUME_METRICS,
               config['train_opener_file']: VOLUME_OPENER}
    if not dry_run:
        volumes[config['train_data_path']] = VOLUME_DATA
    command = get_metrics_command(dry_run)
    _docker_run(docker_client, docker_metrics_tag, command=command,
                volumes=volumes)

    model_key = 'model'

    # load performance
    with open(os.path.join(config['train_pred_path'], 'perf.json'), 'r') as perf_file:
        perf = json.load(perf_file)
    train_perf = perf['all']

    print('Successfully train model %s with a score of %s on train data' % (os.path.join(config['outmodel_path'], model_key), train_perf))

    print('Testing starts')

    _docker_build(docker_client, config['algo_path'], docker_algo_tag)

    print('Testing model')

    print('Testing model on %s with %s saved in %s' % (
        config['test_data_path'], model_key, config['test_pred_path']))
    volumes = {config['outmodel_path']: VOLUME_OUTPUT_MODEL,
               config['test_pred_path']: VOLUME_PRED,
               config['test_opener_file']: VOLUME_OPENER}
    if not dry_run:
        volumes[config['test_data_path']] = VOLUME_DATA

    command = f"predict {model_key}"
    if dry_run:
        command += " --dry-run"
    _docker_run(docker_client, docker_algo_tag, command=command,
                volumes=volumes)

    _docker_build(docker_client, metrics_path, docker_metrics_tag)

    print('Evaluating performance - compute metric with %s predictions against %s labels' % (
        config['test_pred_path'], config['test_data_path']))

    volumes = {config['test_pred_path']: VOLUME_PRED,
               config['metrics_file']: VOLUME_METRICS,
               config['test_opener_file']: VOLUME_OPENER}
    if not dry_run:
        volumes[config['test_data_path']] = VOLUME_DATA

    command = get_metrics_command(dry_run)
    _docker_run(docker_client, docker_metrics_tag, command=command,
                volumes=volumes)

    # load performance
    with open(os.path.join(config['test_pred_path'], 'perf.json'), 'r') as perf_file:
        perf = json.load(perf_file)
    test_perf = perf['all']

    print('Successfully test model %s with a score of %s on test data' % (os.path.join(config['outmodel_path'], model_key), test_perf))


class RunLocal(Base):
    """Run-local asset"""

    def run(self):

        def _get_option(option_name, default):
            option = self.options.get(option_name)
            if option is None:
                return default
            return option

        def _get_path(base_path, relpath):
            return os.path.abspath(os.path.join(base_path, relpath))

        algo_path = self.options['<algo-path>']

        train_opener = _get_option('--train-opener',
                                   _get_path(algo_path, '../dataset/opener.py'))

        test_opener = _get_option('--test-opener',
                                  _get_path(algo_path, '../objective/opener.py'))

        metrics = _get_option('--metrics',
                              _get_path(algo_path, '../objective/metrics.py'))

        rank = _get_option('--rank', 0)

        train_data = _get_option('--train-data-sample',
                                 _get_path(algo_path, '../dataset/data-samples/'))

        test_data = _get_option('--test-data-sample',
                                _get_path(algo_path, '../objective/data-samples/'))

        inmodel = self.options.get('--inmodel')

        outmodel = _get_option('--outmodels',
                               _get_path(algo_path, '../model/'))

        fake_data_samples = self.options.get('--fake-data-samples', False)

        if fake_data_samples:
            train_data = None
            test_data = None

        config = setup_local(algo_path,
                             train_opener, test_opener, metrics,
                             train_data, test_data,
                             outmodel_path=outmodel,
                             compute_path='./sandbox',
                             local_path='local')

        client = docker.from_env()

        compute_local(client, config, rank, inmodel, dry_run=fake_data_samples)
