# Titanic

*This example is based on [the similarly named Kaggle challenge](https://www.kaggle.com/c/titanic/overview)*

In this example, we'll see how to setup an objective with cross-validation in mind and how to train algorithms.

## Prerequisites

In order to run this example, you'll need to:

* use Python 3
* have [Docker](https://www.docker.com/) installed
* [install the `substra` cli](../../README.md#install)
* [install the `substratools` library](https://github.com/substrafoundation/substra-tools)
* [pull the `substra-tools` docker images](https://github.com/substrafoundation/substra-tools#pull-from-private-docker-registry)
* create a substra profile to define the substra network to target, for instance:
    ```sh
    substra config --profile node-1 http://substra-backend.node-1.com
    substra login --profile node-1 --username node-1 --password 'p@$swr0d44'
    ```
* checkout this repository

All commands in this example are run from the `substra/examples/titanic/` folder.

## Data preparation

The first step will be to generate train and test data samples from the
[Kaggle challenge source](https://www.kaggle.com/c/titanic/data). The raw `train.csv` file is available in the `data`
directory.

> This file can be obtained straight from Kaggle by creating an account there and either downloading it manually or
> running the following command using
>[kaggle CLI tool](https://www.kaggle.com/docs/api#getting-started-installation-&-authentication):
> ```sh
> kaggle competitions download -c titanic -p scripts
> ```

To generate the data samples, run:
```sh
pip install -r scripts/requirements.txt
python scripts/generate_data_samples.py
```

This will create two sub-folders in the `assets` folder:
* `train_data_samples` contains 10 sub-folders, one for each train data sample and each containing a single CSV file
* `test_data_samples` contains 2 sub-folders, one for each test data sample and each containing a single CSV file

The reason we have multiple train data samples is that this way we'll be able to finely select our training set later
on.

## Writing the objective and data manager

Both objective and data manager will need a proper markdown description, you can check them out in their respective
folders. Notice that the data manager's description includes a formal description of the data structure.

Notice also that the `metrics.py` and `opener.py` module both rely on classes imported from the `substratools` module.
These classes provide a simple yet rigid structure that will make algorithms pretty easy to write.

## Writing a simple algorithm

You'll find under `assets/algo_random_forest` a simple algorithm. Like the metrics and opener scripts, it relies on a
class imported from `substratools` that greatly simplifies the writing process. You'll notice that it handles not only
the train and predict tasks but also a lot of data preprocessing.

## Adding the assets to substra

### Adding the objective, dataset and data samples to substra

A script has been written that adds objective, data manager and data samples to substra. It uses the `substra` python
sdk to perform actions. It's main goal is to create assets, get their keys and use these keys in the creation of other
assets.

To run it:

```sh
pip install -r scripts/requirements.txt
python scripts/add_dataset_objective.py
```

This script just generated an `assets_keys.json` file in the `titanic` folder. This file contains the keys of all assets
we've just created and organizes the keys of the train data samples in folds. This file will be used as input when
adding an algorithm so that we can automatically launch all training and testing tasks.


### Adding the algorithm and training it

The script `add_train_algo_random_forest.py` pushes our simple algo to substra and then uses the `assets_keys.json` file
we just generated to train it against the dataset and objective we previously set up. It will then update the
`assets_keys.json` file with the newly created assets keys (algo, traintuple and testtuple)

To run it:

```sh
python scripts/add_train_algo_random_forest.py
```

It will end by providing a couple of commands you can use to track the progress of the train and test tuples as well
as the associated scores. Alternatively, you can browse the frontend to look up progress and scores.


## Testing our assets

### Manually

#### Training task

```sh
python assets/algo_random_forest/algo.py train \
  --debug \
  --opener-path assets/dataset/opener.py \
  --data-samples-path assets/train_data_samples \
  --output-model-path assets/model/model \
  --log-path assets/logs/train.log

python assets/algo_random_forest/algo.py predict \
  --debug \
  --opener-path assets/dataset/opener.py \
  --data-samples-path assets/train_data_samples \
  --output-predictions-path assets/pred-train.csv \
  --models-path assets/model/ \
  --log-path assets/logs/train_predict.log \
  model

python assets/objective/metrics.py \
  --debug \
  --opener-path assets/dataset/opener.py \
  --data-samples-path assets/train_data_samples \
  --input-predictions-path assets/pred-train.csv \
  --output-perf-path assets/perf-train.json \
  --log-path assets/logs/train_metrics.log
 ```

#### Testing task

```sh
python assets/algo_random_forest/algo.py predict \
  --debug \
  --opener-path assets/dataset/opener.py \
  --data-samples-path assets/test_data_samples \
  --output-predictions-path assets/pred-test.csv \
  --models-path assets/model/ \
  --log-path assets/logs/test_predict.log \
  model

python assets/objective/metrics.py \
  --debug \
  --opener-path assets/dataset/opener.py \
  --data-samples-path assets/test_data_samples \
  --input-predictions-path assets/pred-test.csv \
  --output-perf-path assets/perf-test.json \
  --log-path assets/logs/test_metrics.log
```

### Using the debug mode

Substra provides a very handy debug mode that will simulate the workings of a node right on your machine.

For more information, have a look at the [debugging example](../debugging/READMEmd).
