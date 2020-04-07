# Cross-validation

> Important
> This example relies on the assets setup by the [Titanic example](../titanic/README.md). In order to run the following
code snippets, you'll need the `assets_keys.json` generated while running the Titanic example.

In the Titanic example, the algos were trained on all the train data samples available and the resulting model was
evaluated against the test data samples.

In order to cross-validate our algos, the train data samples will have to be split into folds, each with a training
part and a validation part that will change from fold to fold.

By creating traintuples for each train part and testtuples for each validation part, we'll get a bunch of scores whose
mean and variance will inform about the robustness of the algo.

## Generating folds

In this setup, we'll consider only the data already in Substra, with no access to the source material.

As a result, the only way we have to generate fold is to decide with data samples keys should be used for train and
which one should be used for test.

These folds can only be made on the data samples of one node.

To generate 4 folds from existing keys, run:

```sh
pip install -r scripts/requirements.txt
python scripts/generate_folds.py
```

## Training and validation

Now that we have our folds, the only remaining thing to do is to launch matching training/testing tasks.

We need to tag all of these train and test tuples with a same tag so that substra knows that they are part of the same
cross-validated experiment.

To launch the 4 traintuples and 4 testtuples, run:
```sh
python scripts/cross_val_algo_random_forest.py
```

It will end by providing a couple of commands you can use to track the progress of the train and test tuples.

Alternatively, you can use the frontend and get there the average score and its variance.
