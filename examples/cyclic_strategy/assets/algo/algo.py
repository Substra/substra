import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import substratools as tools
from sklearn.linear_model import SGDClassifier

N_UPDATE = 1
BATCH_SIZE = 32
N_NODES = 2
N_ROUNDS = 7


def generate_batch_indexes(index, n_rounds, n_update, batch_size):
    """Generatesr n_rounds*n_update batch of `batch_size` size.

    Args:
        index (list): Index of your dataset
        n_rounds (int): The total number of rounds in your strategy
        n_update (int): The number of batches, you will perform the train method at each
        step of the compute plan
        batch_size (int): Number of data points in a batch

    Returns:
        List[List[index]]: A 2D list where each embedded list is the list of the
        indexes for a batch
    """

    my_index = index.copy().values
    np.random.seed(42)
    np.random.shuffle(my_index)

    n = len(my_index)
    total_batches = n_rounds * n_update
    batches_iloc = []
    batch_size = min(n, batch_size)
    k = 0

    for _ in range(total_batches):

        # It is needed to convert the array to list.
        # Otherwise, you store references during the for loop and everything
        # is computed at the end of the loop. So, you won't see the impact
        # of the shuffle operation
        batches_iloc.append(list(my_index[k * batch_size : (k + 1) * batch_size]))
        k += 1
        if n < (k + 1) * batch_size:
            np.random.shuffle(my_index)
            k = 0

    return batches_iloc


class Algo(tools.algo.Algo):
    def _normalize_X(self, X):
        return X

    def _predict_pandas(self, model, X):
        y_pred = model.predict(X)
        return pd.DataFrame(columns=["target"], data=y_pred)

    def train(self, X, y, models, rank):
        """Train function of the algorithm.
        To train the algorithm on different batches on each step
        we generate the list of index for each node (the first time the
        algorithm is trained on it). We save this list and for each task
        read it from the self.compute_plan_path folder which is a place
        where you can store information locally.

        Args:
            X (DataFrame): Training features
            y (DataFrame): Target
            models (List[Algo]): List of algorithm from the previous step of the compute plan
            rank (int): The rank of the task in the compute plan

        Returns:
            [Algo]: The updated algorithm after the training for this task
        """

        compute_plan_path = Path(self.compute_plan_path)

        # Since our strategy is to train our algorithm on each node one after the other,
        # if the rank is in [0, N_NODES[ it means that this is the first time we are
        # training the algorithm on this node. Therefore, the batches have not yet been
        # generated and saved.
        if rank in range(N_NODES):
            batches_loc = generate_batch_indexes(
                X.index,
                n_rounds=N_ROUNDS,
                n_update=N_UPDATE,
                batch_size=BATCH_SIZE,
            )

        else:
            batches_loc = eval((compute_plan_path / "batches_loc_node.txt").read_text())

        # Reuse or instantiate model
        if models:
            clf = models[0]

        else:
            clf = SGDClassifier(max_iter=10, warm_start=True, random_state=42)

        # Train the algorithm for each update on different data
        for _ in range(N_UPDATE):
            batch_loc = batches_loc.pop()
            X = self._normalize_X(X.loc[batch_loc])
            y = y.loc[batch_loc]
            clf.partial_fit(X, y.values.ravel(), list(range(10)))

        # Save the remaining batches indexes
        (compute_plan_path / "batches_loc_node.txt").write_text(str(batches_loc))

        # Return the classifier for it to be used on the next node
        return clf

    def predict(self, X, model):
        X = self._normalize_X(X)
        return self._predict_pandas(model, X)

    def load_model(self, path):
        with open(path, "rb") as f:
            return pickle.load(f)

    def save_model(self, model, path):
        with open(path, "wb") as f:
            pickle.dump(model, f)


if __name__ == "__main__":
    tools.algo.execute(Algo())
