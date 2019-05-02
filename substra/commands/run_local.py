import os
import json
import docker
import time
import shutil
import hashlib

from .base import Base

metrics_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../run_local_materials/metrics')


USER = os.getuid()


def create_directory(directory):
    if not os.path.exists(directory):
        print(f'Create path : {directory}')
        os.makedirs(directory)


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
        if not os.path.exists(config[key]):
            raise Exception(f"Cannot launch local run: {key.replace('_', ' ')} {config[key]} doesn't exist")

    # docker
    config['algo_docker'] = 'algo_run_local'
    config['metrics_docker'] = 'metrics_run_local'

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


def compute_local(docker_client, config, rank, inmodels, dryrun=False):

    print('Training starts')

    print('Creating docker for train', end=' ', flush=True)
    start = time.time()
    docker_client.images.build(path=config['algo_path'],
                               tag=config['algo_docker'],
                               rm=False)
    print('(duration %.2f s )' % (time.time() - start))

    if not dryrun:
        print('Training algo on %s' % (config['train_data_path'],), end=' ', flush=True)
    else:
        print('Training algo fake data samples', end='', flush=True)

    start = time.time()
    volumes = {config['train_data_path']: {'bind': '/sandbox/data', 'mode': 'ro'},
               config['outmodel_path']: {'bind': '/sandbox/model', 'mode': 'rw'},
               config['train_pred_path']: {'bind': '/sandbox/pred', 'mode': 'rw'},
               config['local_path']: {'bind': '/sandbox/local', 'mode': 'rw'},
               config['train_opener_file']: {'bind': '/sandbox/opener/__init__.py', 'mode': 'ro'}}

    command = 'train'
    if dryrun:
        command += " --dry-run"

    if rank is not None:
        command += f" --rank {rank}"

    if inmodels:
        model_keys = []

        for inmodel in inmodels:
            src = os.abspath(inmodel)
            model_key = hashlib.sha256(src)
            dst = os.path.join(config['outmodel_path'], model_key)
            os.symlink(src, dst)
            model_keys.append(model_key)

        command += ' '.join(model_keys)

    docker_client.containers.run(config['algo_docker'], command=command, volumes=volumes, remove=True, user=USER)
    print('(duration %.2f s )' % (time.time() - start))

    model_key = 'model'
    if not os.path.exists(os.path.join(config['outmodel_path'], model_key)):
        raise Exception(f"Model ({os.path.join(config['outmodel_path'], model_key)}) doesn't exist")

    print('Evaluating performance - creating docker', end=' ', flush=True)
    start = time.time()
    docker_client.images.build(path=metrics_path,
                               tag=config['metrics_docker'],
                               rm=True)
    print('(duration %.2f s )' % (time.time() - start))

    print('Evaluating performance - compute metrics with %s predictions against %s labels' % (config['train_pred_path'],
                                                                                              config['train_data_path']), end=' ', flush=True)
    start = time.time()

    volumes = {config['train_data_path']: {'bind': '/sandbox/data', 'mode': 'ro'},
               config['train_pred_path']: {'bind': '/sandbox/pred', 'mode': 'rw'},
               config['metrics_file']: {'bind': '/sandbox/metrics/__init__.py', 'mode': 'ro'},
               config['train_opener_file']: {'bind': '/sandbox/opener/__init__.py', 'mode': 'ro'}}
    docker_client.containers.run(config['metrics_docker'], volumes=volumes, remove=True, user=USER)
    print('(duration %.2f s )' % (time.time() - start))

    model_key = 'model'

    # load performance
    with open(os.path.join(config['train_pred_path'], 'perf.json'), 'r') as perf_file:
        perf = json.load(perf_file)
    train_perf = perf['all']

    print('Successfully train model %s with a score of %s on train data' % (os.path.join(config['outmodel_path'], model_key), train_perf))

    print('Testing starts')

    print('Creating docker for test', end=' ', flush=True)
    start = time.time()
    docker_client.images.build(path=config['algo_path'],
                               tag=config['algo_docker'],
                               rm=False)
    print('(duration %.2f s )' % (time.time() - start))

    print('Testing model')

    print('Testing model on %s with %s saved in %s' % (config['test_data_path'],
                                                       model_key, config['test_pred_path']), end=' ', flush=True)
    start = time.time()
    volumes = {config['test_data_path']: {'bind': '/sandbox/data', 'mode': 'ro'},
               config['outmodel_path']: {'bind': '/sandbox/model', 'mode': 'rw'},
               config['test_pred_path']: {'bind': '/sandbox/pred', 'mode': 'rw'},
               config['test_opener_file']: {'bind': '/sandbox/opener/__init__.py', 'mode': 'ro'}}
    docker_client.containers.run(config['algo_docker'], command=f"predict {model_key}", volumes=volumes, remove=True, user=USER)
    print('(duration %.2f s )' % (time.time() - start))

    print('Evaluating performance - creating docker', end=' ', flush=True)
    start = time.time()
    docker_client.images.build(path=metrics_path,
                               tag=config['metrics_docker'],
                               rm=False)
    print('(duration %.2f s )' % (time.time() - start))

    print('Evaluating performance - compute metric with %s predictions against %s labels' % (config['test_pred_path'],
                                                                                             config['test_data_path']), end=' ', flush=True)

    volumes = {config['test_data_path']: {'bind': '/sandbox/data', 'mode': 'ro'},
               config['test_pred_path']: {'bind': '/sandbox/pred', 'mode': 'rw'},
               config['metrics_file']: {'bind': '/sandbox/metrics/__init__.py', 'mode': 'ro'},
               config['test_opener_file']: {'bind': '/sandbox/opener/__init__.py', 'mode': 'ro'}}
    docker_client.containers.run(config['metrics_docker'], volumes=volumes, remove=True, user=USER)
    print('(duration %.2f s )' % (time.time() - start))

    # load performance
    with open(os.path.join(config['test_pred_path'], 'perf.json'), 'r') as perf_file:
        perf = json.load(perf_file)
    test_perf = perf['all']

    print('Successfully test model %s with a score of %s on test data' % (os.path.join(config['outmodel_path'], model_key), test_perf))


class RunLocal(Base):
    """Run-local asset"""

    def getOption(self, option, default):
        if option is None:
            return default
        return option

    def run(self):

        algo_path = self.options['<algo-path>']
        train_opener = self.getOption(self.options.get('--train-opener'), os.path.abspath(os.path.join(algo_path, '../dataset/opener.py')))
        test_opener = self.getOption(self.options.get('--test-opener'), os.path.abspath(os.path.join(algo_path, '../objective/opener.py')))
        metrics = self.getOption(self.options.get('--metrics'), os.path.abspath(os.path.join(algo_path, '../objective/metrics.py')))
        rank = self.getOption(self.options.get('--rank'), 0)
        train_data = self.getOption(self.options.get('--train-data-sample'), os.path.abspath(os.path.join(algo_path, '../dataset/data-samples/')))
        test_data = self.getOption(self.options.get('--test-data-sample'), os.path.abspath(os.path.join(algo_path, '../objective/data-samples/')))
        inmodel = self.options.get('--inmodel')
        outmodel = self.getOption(self.options.get('--outmodels'), os.path.abspath(os.path.join(algo_path, '../model/')))
        fake_data_samples = self.options.get('--fake-data-samples', False)

        try:
            config = setup_local(algo_path,
                                 train_opener, test_opener, metrics,
                                 train_data, test_data,
                                 outmodel_path=outmodel,
                                 compute_path='./sandbox',
                                 local_path='local')

            client = docker.from_env()

            compute_local(client, config, rank, inmodel, dryrun=fake_data_samples)
        except Exception as e:
            self.handle_exception(e)
