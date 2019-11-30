# Titanic

*This example is based on [the similarly named Kaggle challenge](https://www.kaggle.com/c/titanic/overview)*

In this example, we consider by default two nodes: node 0 and node 1. We'll see how to:
- define and register an objective 
- define and register a dataset
- define and register an algorithm and train it on distributed datasets


## Prerequisites


### Setup 

In order to run this example, you'll need to:

* use Python 3
* have [Docker](https://www.docker.com/) installed
* [install the `substra` cli](../../README.md#install)
* [install the `substratools` library](https://github.com/substrafoundation/substra-tools)
* [pull the `substra-tools` docker images](https://github.com/substrafoundation/substra-tools#pull-from-private-docker-registry)

### Data preparation

To run this example, you will also need to generate data samples for the two nodes from
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

This will create three sub-folders in the `assets` folder:
* `train_data_samples_node0` contains 5 sub-folders, one for each train data sample and each containing a single CSV file.
    This corresponds to data samples that will be submitted to node 0.
* `train_data_samples_node1` contains 5 sub-folders, one for each train data sample and each containing a single CSV file
    This corresponds to data samples that will be submitted to node 1.
* `test_data_samples_node0` contains 2 sub-folders, one for each test data sample and each containing a single CSV file
    This corresponds to data samples that will be submitted to node 0.

This also create two sub-folders in the `assets` folder: `dataset_node0` and `dataset_node1` that store a description and 
an opener to handle data samples submitted to node 0 and node 1. 

The reason we have multiple train data samples for each node is that this way we'll be able to finely select our training set later 
on.

> :tada: **Congratulations, you are now ready to start running the example!** 

## Objective preparation by Node 0

A user of Node 0 will register an *objective* to Substra. 
An *objective* corresponds to the definition of a machine learning problem. 
It is associated with a test dataset and a metrics to evaluate models created to solve this problem. 

To prepare an objective, one needs to create:
- a markdown description `description.md`
- a metrics defined in a `metrics.py` file with its dependencies specified in a `Dockerfile`. This rely on classes imported from the `substratools` module. These classes provide a simple yet rigid structure that will make your metrics pretty easy to write. 

Those have been already been created: You can have a look at them in the folder `asset/objective`. 

## Dataset preparation by Node 0 and Node 1

Both a user of Node 0 and of Node 1 will register a *dataset*.
A *dataset* corresponds to a set of *data samples* and a *data manager*.

To prepare a *data manager*, one needs to create:
- a markdown description `description.md`
- an `opener.py` file with makes it possible to load your data samples in memory. It relies on a classe imported from the `substratools` module. This classe provides a simple yet rigid structure that will make your opener pretty easy to write. 

Those have been created: You can have a look at them in the folder `asset/dataset0` and `asset/dataset1`.


## Algorithm definition by Node 1

A user of Node 1 will register an *algorithm*. 

To prepare an *algorithm*, one needs to create:
- a markdown description `description.md`
- the algorithm itself :-) Like for a metrics you can define it through Python file and a `Dockerfile`. Like the metrics and opener scripts, it relies on a 
class imported from `substratools` that greatly simplifies the writing process. 

Those have been created: You can have a look at them in the folder `assets/algo_random_forest`.

> **Everything is now prepared and we can add the assets to Substra!**

## Adding the assets to substra

### Adding the objective, dataset and data samples to substra as a user of the Node 0

A script has been written that adds objective, data manager and data samples to substra as a user of Node 0. It uses the `substra` python 
sdk to perform actions. It's main goal is to create assets, get their keys and use these keys in the creation of other
assets.

To run it:

```sh
pip install -r scripts/requirements.txt
python scripts/add_dataset_objective.py
```

This script just generated an `assets_keys_node0.json` file in the `titanic` folder. This file contains the keys of 
all assets we've just created and organizes the keys of the train data samples in folds. 

### Adding a dataset and data samples to substra as a user of the Node 1

A script has been written that adds a data manager and data samples to substra as a user of Node 1. It uses the `substra` python 
sdk to perform actions. It's main goal is to create assets, get their keys and use these keys in the creation of other
assets.

To run it:

```sh
python scripts/add_dataset.py
```

This script just generated an `assets_keys_node1.json` file in the `titanic` folder. This file contains the keys of
all assets we've just created and organizes the keys of the train data samples in folds.


### Adding the algorithm and training it as a user of Node 1

The script `add_train_algo_random_forest.py` pushes our simple algo to substra, uses the SDK to retrieve the datasets and objective 
we just generated to train it against the dataset and objective we previously set up. It will then update the 
`assets_keys_node1.json` file with the newly created assets keys (algo, traintuple and testtuple)

To run it:

```sh
python scripts/add_train_algo_random_forest.py
```

It will end by providing a couple of commands you can use to track the progress of the train and test tuples as well 
as the associated scores. Alternatively, you can browse the frontend to look up progress and scores.


> **Congratulations! You submitted assets to Substra as being users of two different nodes!** 
> **Hopefully, everything went well.** 
> **But wait, what if you had to design all assets by yourself ?**
> **It would been nice to know how to test things before submitting them. And also how to do this when you don't have access to data.**
> **This is what is explained in the next two sections.**

## Testing our assets

### Using asset command line interfaces

#### Training task

```sh
python assets/algo_random_forest/algo.py train \
  --debug \
  --opener-path assets/dataset_node0/opener.py \
  --data-samples-path assets/train_data_samples_node0 \
  --output-predictions-path assets/pred-train.csv
  
python assets/objective/metrics.py \
  --debug \
  --opener-path assets/dataset_node0/opener.py \
  --data-samples-path assets/train_data_samples_node0 \
  --input-predictions-path assets/pred-train.csv
 ```

#### Testing task

```sh
python assets/algo_random_forest/algo.py predict \
  --debug \
  --opener-path assets/dataset_node0/opener.py \
  --data-samples-path assets/test_data_samples_node0 \
  --output-predictions-path assets/pred-test.csv model
  
python assets/objective/metrics.py \
  --debug \
  --opener-path assets/dataset_node0/opener.py \
  --data-samples-path assets/test_data_samples_node0 \
  --input-predictions-path assets/pred-test.csv
```

### Using substra cli

Before pushing our assets to the platform, we need to make sure they work well. To do so, we can run them locally. This 
way, if the training fails, we can access the logs and debug our code.

To test the assets, we'll use `substra run-local`, passing it paths to our algorithm of course, but also the opener, 
the metrics and to the data samples we want to use.

```sh
substra run-local assets/algo_random_forest \
  --train-opener=assets/dataset_node0/opener.py \
  --test-opener=assets/dataset_node0/opener.py \
  --metrics=assets/objective/ \
  --train-data-samples=assets/train_data_samples_node0 \
  --test-data-samples=assets/test_data_samples_node0
```

At the end of this step, you'll find in the newly created `sandbox/model` folder a `model` file that contains your 
trained model. There is also a `sandbox/pred_train` folder that contains both the predictions made by the model on 
train data and the associated performance.

#### Debugging

It's more than probable that your code won't run perfectly the first time. Since runs happen in dockers, you can't 
debug using prints. Instead, you should use the `logging` module from python. All logs can then be consulted at the end 
of the run in  `sandbox/model/log_model.log`.

## 

## Preparing an algorithm when you don't have access to the data samples

Now that we have a full example setup, let's imagine that we are someone else, someone whithout access to the data 
samples who want to develop an algorithm for this objective (see `assets/algo_constant` for such an algorithm).

Before pushing this new algorithm to the platform, we need to make sure it works. However we cannot use `run-local` the 
way we did before since we don't have access to the data samples. We'll therefore have to rely of fake data generated 
by the opener. **It's the responsibility of the person who wrote the data manager to provide generators of fake data 
who match perfectly the type of data the methods `get_X` and `get_y` would normally return.**

The first step is to download the `opener.py` and `metrics.zip` from the frontend. Save the `opener.py` script in the 
`dataset` folder and unzip the `metrics.zip` archive in the `objective` folder (these folders are not strictly necessary 
but they help identify the related assets).

Now we can launch the `run-local` using fake data:

```sh
substra run-local assets/algo_constant \
  --train-opener=assets/dataset/opener.py \
  --test-opener=assets/dataset/opener.py \
  --metrics=assets/objective/ \
  --fake-data-samples
```

Once again, we can use the `logging` module to debug.

Once it works as expected, we can push it to the platform by using the `add_train_algo_constant.py` script. It relies 
on the `assets_keys.json` file that was previously generated and updates it the keys of the new algo, traintuple and 
testtuple.

To run `add_train_algo_constant.py`:

```sh
python scripts/add_train_algo_constant.py
```

At the end of the training and testing, we can use the frontend to compare the performance of our algorithms.

