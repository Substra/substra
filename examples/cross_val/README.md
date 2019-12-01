# Cross-validation

> :warning: 
> This example relies on the assets setup by the [Titanic example](../titanic/README.md). In order to run the following 
code snippets, you'll need to have run the Titanic example before 

In the Titanic example, the algos were trained on all the train data samples available and the resulting model was 
evaluated against the test data samples. 

In order to cross-validate our algos, the train data samples will have to be splitted into folds, each with a training 
part and a validation part that will change from fold to fold.

By creating traintuples for each train part and testtuples for each validation part, we'll get a bunch of scores whose 
mean and variance will inform about the robustness of the algo.


## Generating folds and submitting tasks

We will run a script that:
- retrieve exiting assets and generate folds from data samples of one node
- submit associated training and validation tasks. Note that a tag is added to these tasks in order to easily retrieve them later on.

```sh
pip install -r scripts/requirements.txt
python scripts/cross_val_algo_random_forest.py
```

It will end by providing a couple of commands you can use to track the progress of the train and test tuples.

Alternatively, you can use the frontend and get there the average score and its variance.
