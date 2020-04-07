# Titanic - Node 2

This dataset comes from Kaggle's ["Titanic: Machine Learning from Disaster" challenge](https://www.kaggle.com/c/titanic/data).

## Test and train data samples

Since Kaggle doesn't provide the ground truth for its test set, all data samples attached to this dataset are extracted from Kaggle's train set.

Out of the 891 records of the train set:
* 20% were kept aside as the test data sample
* the remaining 80% were split among 4 train data samples

This way it is possible to demonstrate cross-validation strategies using these assets.

These splits were generated using the following code:

```python
import os
import pandas as pd
from sklearn.model_selection import KFold, train_test_split

data = pd.read_csv('train.csv')

# generate splits
train_data, test_data_sample = train_test_split(data, test_size=0.2)
kf = KFold(n_splits=4)
splits = kf.split(train_data)
train_data_samples = []
for train_index, test_index in splits:
    train_data_samples.append(train_data.iloc[test_index])

# save splits
DATA_SAMPLES_ROOT = '../assets'

filename = os.path.join(DATA_SAMPLES_ROOT, 'test_data_sample/test.csv')
os.makedirs(os.path.dirname(filename), exist_ok=True)
with open(filename, 'w') as f:
    test_data_sample.to_csv(f)

for i, train_data_sample in enumerate(train_data_samples):
    filename = os.path.join(DATA_SAMPLES_ROOT, f'../assets/train_data_samples/train{i}/train{i}.csv')
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        train_data_sample.to_csv(f)
```


## Data samples structure

All data samples have the same exact structure. They all contain a single CSV files with the following fields (description are extracted from Kaggle):

| Field | Type | Description | Values |
| ----- | ---- | ----------- | ------- |
| `PassengerId` | integer | Type should be integers | `1`, `2`, `3`... |
| `Survived` | bool | Survived or not | either `0` or `1` |
| `Pclass` | integer | Class of Travel | either `1`, `2` or `3` |
| `Name` | string | Name of Passenger| `Braund, Mr. Owen Harris` |
| `Sex` | string | Gender | either `male` or `female` |
| `Age` | integer | Age of Passengers | `24` |
| `SibSp` | integer | Number of Sibling/Spouse aboard | `0` |
| `Parch` | integer | Number of Parent/Child aboard | `0` |
| `Ticket` | string | Ticket number | `A/5 21171` |
| `Fare` | float | Price of the ticket | `71.2833` |
| `Cabin` | string | Cabin number | `C85` |
| `Embarked` | string | The port in which a passenger has embarked | either `C` for Cherbourg, `S` for Southampton or `Q` for Queenstown  |

## Opener usage

The opener exposes 4 methods:
* `get_X` returns all data but the `Survived` field
* `get_y` returns only the `Survived` field
* `save_pred` saves a pandas DataFrame as csv,
* `get_pred` loads the csv saved with `save_pred` and returns a pandas DataFrame
