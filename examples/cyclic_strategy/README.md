# Cyclic Federate Learning example

*This example is based on the [Recognizing hand-written digits](https://scikit-learn.org/stable/auto_examples/classification/plot_digits_classification.html) example from sklearn documentation*

In this example, we'll see how to train a multi-class classifier with a federated learning cyclic strategy.

It consists in training our algorithm on each dataset one after the other thanks to incremental learning.

In this example, we will train our algorithm on two separated datasets hosted on two different substra organizations.

All the instructions are in [plot_cyclic_strategy.py](./scripts/plot_cyclic_strategy.py)
