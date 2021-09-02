"""
=======
Titanic
=======

This example is based on `the similarly named Kaggle challenge <https://www.kaggle.com/c/titanic/overview>`_

We will be training and testing with only one :term:`node`.

Authors:
  |    Romain Goussault :fa:`github` `RomainGoussault <https://github.com/RomainGoussault>`_
  |    Maria Telenczuk, :fa:`github` `maikia <https://github.com/maikia>`_

"""

# %%
# Import all the dependencies
# ---------------------------

from pathlib import Path
import os
import zipfile

# %%
# You should have already Substra installed, if not follow the instructions here: :ref:`Installation`
#

import substra

# %%
# Next, we need to link to the already defined assets. You can download them from here:
#
# TODO: add a link and the instructions on how to get the assets folder and update the path if necessary
#
# TODO: in the assets directory you can find XXX files including datafiles which we will use next
# TODO: a link to some example on how to prepare your own assets + each file explained??
#

assets_directory = Path("../code_examples") / "titanic" / "assets"

# %%
# Registering data samples and dataset
# ------------------------------------
#
# Now we need to register the data samples on the client (also called :term:`node`). This is usually done by a data
# scientists working on a given node. Here we set debug to True... TODO: explain
#
# To do that we also need to set the permissions.
# TODO: explain what are the pemissions/ possible permissions/ and/or link to more
#

client = substra.Client(debug=True)

permissions = {
            'public': False,
            'authorized_ids': []
}

DATASET = {
    'name': 'Titanic dataset - Node 1',
    'type': 'csv',
    'data_opener': assets_directory / 'dataset' / 'opener.py',
    'description': assets_directory / 'dataset' / 'description.md',
    'permissions': permissions
}

dataset_key_1 = client.add_dataset(DATASET)
print(f'Dataset key {dataset_key_1}')

# %%
# Adding train data samples
# ^^^^^^^^^^^^^^^^^^^^^^^^
#
# TODO: explain
#

train_data_sample_folder = assets_directory / 'train_data_samples'
train_data_sample_paths = list(train_data_sample_folder.glob('*'))
train_data_sample_keys = list()

for path in train_data_sample_paths:
    data_sample_key = client.add_data_sample({
        'data_manager_keys': [dataset_key_1],
        'test_only': False,
        'path': path,
    }, local=True)
    train_data_sample_keys.append(data_sample_key)

print(f"{len(train_data_sample_keys)} data samples were registered")

# %%
# Adding test data samples
# ^^^^^^^^^^^^^^^^^^^^^^^^
#
# TODO: explain
#

test_data_sample_folder = assets_directory / 'test_data_samples'
test_data_sample_paths = list(test_data_sample_folder.glob('*'))
test_data_sample_keys = list()

for path in test_data_sample_paths:
    data_sample_key = client.add_data_sample({
        'data_manager_keys': [dataset_key_1],
        'test_only': True,
        'path': path,
    }, local=True)
    test_data_sample_keys.append(data_sample_key)

print(f"{len(test_data_sample_keys)} data samples were registered")

# %%
# Adding objective
# ----------------
#
# TODO: explain
#

OBJECTIVE = {
    'name': 'Titanic: Machine Learning From Disaster',
    'description': assets_directory / 'objective' / 'description.md',
    'metrics_name': 'accuracy',
    'metrics': assets_directory / 'objective' / 'metrics.zip',
    'permissions': {
        'public': False,
        'authorized_ids': []
    },
}

METRICS_DOCKERFILE_FILES = [
    assets_directory / 'objective' / 'metrics.py',
    assets_directory / 'objective' / 'Dockerfile'
]

archive_path = OBJECTIVE['metrics']
with zipfile.ZipFile(archive_path, 'w') as z:
    for filepath in METRICS_DOCKERFILE_FILES:
        z.write(filepath, arcname=os.path.basename(filepath))

objective_key = client.add_objective({
    'name': OBJECTIVE['name'],
    'description': OBJECTIVE['description'],
    'metrics_name': OBJECTIVE['metrics_name'],
    'metrics': OBJECTIVE['metrics'],
    'test_data_sample_keys': test_data_sample_keys,
    'test_data_manager_key': dataset_key_1,
    'permissions': OBJECTIVE['permissions'],
})
assert objective_key, 'Missing objective key'

# %%
# Adding algo
# -----------
#
# TODO: explain
#

ALGO_KEYS_JSON_FILENAME = 'algo_random_forest_keys.json'

ALGO = {
    'name': 'Titanic: Random Forest',
    'description': assets_directory / 'algo_random_forest' / 'description.md',
    'permissions': {
        'public': False,
        'authorized_ids': []
    },
}

ALGO_DOCKERFILE_FILES = [
        assets_directory / 'algo_random_forest/algo.py',
        assets_directory / 'algo_random_forest/Dockerfile',
]

archive_path = assets_directory / 'algo_random_forest' / 'algo_random_forest.zip'
with zipfile.ZipFile(archive_path, 'w') as z:
    for filepath in ALGO_DOCKERFILE_FILES:
        z.write(filepath, arcname=os.path.basename(filepath))
ALGO['file'] = archive_path


algo_key = client.add_algo({
    'name': ALGO['name'],
    'file': ALGO['file'],
    'description': ALGO['description'],
    'permissions': ALGO['permissions'],
})

# %%
# Registering tasks
# -----------------
#
# TODO: explain
#

traintuple_key = client.add_traintuple({
    'algo_key': algo_key,
    'data_manager_key': dataset_key_1,
    'rank': 0,    
    'train_data_sample_keys': train_data_sample_keys
})
assert traintuple_key, 'Missing traintuple key'

testtuple_key = client.add_testtuple({
    'objective_key': objective_key,
    'traintuple_key': traintuple_key
})
assert testtuple_key, 'Missing testtuple key'

# %%
# Results
# -------
#
# TODO: explain
#

testtuple = client.get_testtuple(testtuple_key)
testtuple.status
testtuple.dataset.perf

# %%
# TODO: in the examples gallery it is always nice if there is some kind of summary figure, not necessary, just nice :-)
