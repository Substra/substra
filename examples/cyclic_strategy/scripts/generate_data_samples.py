# Copyright 2018 Owkin, inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
from typing import List

import numpy as np
import pandas as pd
from sklearn import datasets
from sklearn.model_selection import train_test_split

"""
Script to generate data to be registered to Substra
cyclic example
"""
# number of data samples for the train and test sets
# 2 training data samples as we are training on 2 nodes
# 1 testing data sample (on the last node)
# You can generate as many training data samples as you want by changing the value
# of N_NOES
N_NODES = 2


folds = range(N_NODES)

root_path = os.path.dirname(__file__)
asset_path = os.path.join(root_path, "../assets")
data_path = os.path.join(root_path, "../data")


def load_sklearn_mnnist() -> pd.DataFrame:
    """Loading mnist dataset from scikit-learn

    Returns:
        pd.DataFrame: each row contains all the digits from one image
        and the target
    """

    print("Downloading dataset")
    # load Mnist data from sklearn dataset
    digits = datasets.load_digits()

    # flatten the images
    n_samples = len(digits.images)
    data = digits.images.reshape((n_samples, -1))
    data = pd.DataFrame(data, columns=[f"pixel_{k}" for k in range(data.shape[1])])
    data.loc[:, "target"] = digits.target

    return data


def custom_split(data: pd.DataFrame, n_split: int = N_NODES) -> List[pd.DataFrame]:
    """Splits a dataset into n unbalanced splits both in target
    distribution and size.

    Args:
        data (pd.DataFrame): input data (must contains a 'target' column)
        n_split (int, optional): Number of siplits. Defaults to N_NODES.

    Returns:
        List[pd.DataFrame]: List of dataframe
    """
    rng = np.random.default_rng(42)

    repartition = {
        y: list(rng.dirichlet(np.ones(n_split), size=1)[0]) for y in data.target.unique()
    }

    # generate unbalance train data samples
    data.loc[:, "node"] = data.target.apply(
        lambda k: rng.choice(range(n_split), 1, replace=False, p=repartition[k])[0]
    )

    data = data.groupby("node")
    data = [data.get_group(split).drop(columns="node") for split in range(n_split)]

    return data


def main():
    mnist = load_sklearn_mnnist()
    # Split data into 60% train and 40% test subsets
    train, test = train_test_split(mnist, test_size=0.4, shuffle=True, random_state=42)

    # Split the train set between nodes with:
    #   an unbalanced target repartition
    #   different size
    trains = custom_split(train, n_split=N_NODES)

    for node, train in enumerate(trains):
        os.makedirs(os.path.join(asset_path, f"node_{node+1}/train"), exist_ok=True)
        filename = os.path.join(asset_path, f"node_{node+1}/train/train.csv")
        train.to_csv(filename)

    os.makedirs(os.path.join(asset_path, "node_algo/test"), exist_ok=True)
    test.to_csv(os.path.join(asset_path, "node_algo/test/test.csv"))


if __name__ == "__main__":
    main()
