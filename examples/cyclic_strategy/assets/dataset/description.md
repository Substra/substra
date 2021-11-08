# Mnist hand's written digits

This dataset is a simplification of the [THE MNIST DATABASE of handwritten digits](http://yann.lecun.com/exdb/mnist/). It can be downloaded from scikit-learn.

All the images have been flatten into a vector.
The structure of our dataset is now:

* pixel_0
* pixel_1
* ...
* pixel_k
* ...
* pixel_63
* target

Were all pixels are integer between 0 and 16 and the target is the number (0 -> 9) represented by the pixels.

## Data repartition

### Train and test

When running `generate_data_samples.py` we'll split the data into two equals part for the training and the testing phases.

### Split data between nodes

This example runs from two nodes. Hence we have split the train data into two different folds.

To demonstrate the relevance of Federated learning we have unbalanced the folds both in volume and distribution of the target.

## Opener usage

The opener exposes 6 methods:

* `get_X` returns all data but the `target` field
* `get_y` returns only the `target` field
* `fake_X` returns a fake data sample of all data but the `target`field
* `fake_y`returns a fake data sample of the `target`field
* `save_pred` saves a pandas DataFrame as csv,
* `get_pred` loads the csv saved with `save_pred` and returns a pandas DataFrame
