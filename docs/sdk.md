# substra.sdk

# Client
```python
Client(self, config_path=None, profile_name=None)
```

## set_profile
```python
Client.set_profile(self, profile_name)
```
Set profile from profile name.

If profiles has not been defined through the `add_profile` method, it is loaded
from the config file.

## add_profile
```python
Client.add_profile(self, profile_name, url, version='0.0', insecure=False, user=None, password=None)
```
Add new profile (in-memory only).
## add_data_sample
```python
Client.add_data_sample(self, data, local=True, dryrun=False, timeout=False)
```
Create new data sample asset(s).
## add_dataset
```python
Client.add_dataset(self, data, dryrun=False, timeout=False)
```
Create new dataset asset.
## add_objective
```python
Client.add_objective(self, data, dryrun=False, timeout=False)
```
Create new objective asset.
## add_algo
```python
Client.add_algo(self, data, dryrun=False, timeout=False)
```
Create new algo asset.
## add_traintuple
```python
Client.add_traintuple(self, data, dryrun=False, timeout=False)
```
Create new traintuple asset.
## add_testtuple
```python
Client.add_testtuple(self, data, dryrun=False, timeout=False)
```
Create new testtuple asset.
## get_algo
```python
Client.get_algo(self, algo_key)
```
Get algo by key.
## get_dataset
```python
Client.get_dataset(self, dataset_key)
```
Get dataset by key.
## get_objective
```python
Client.get_objective(self, objective_key)
```
Get objective by key.
## get_testtuple
```python
Client.get_testtuple(self, testtuple_key)
```
Get testtuple by key.
## get_traintuple
```python
Client.get_traintuple(self, traintuple_key)
```
Get traintuple by key.
## list_algo
```python
Client.list_algo(self, filters=None, is_complex=False)
```
List algos.
## list_data_sample
```python
Client.list_data_sample(self, filters=None, is_complex=False)
```
List data samples.
## list_dataset
```python
Client.list_dataset(self, filters=None, is_complex=False)
```
List datasets.
## list_objective
```python
Client.list_objective(self, filters=None, is_complex=False)
```
List objectives.
## list_testtuple
```python
Client.list_testtuple(self, filters=None, is_complex=False)
```
List testtuples.
## list_traintuple
```python
Client.list_traintuple(self, filters=None, is_complex=False)
```
List traintuples.
## update_dataset
```python
Client.update_dataset(self, dataset_key, data)
```
Update dataset.
## link_dataset_with_objective
```python
Client.link_dataset_with_objective(self, dataset_key, objective_key)
```
Link dataset with objective.
## link_dataset_with_data_samples
```python
Client.link_dataset_with_data_samples(self, dataset_key, data_sample_keys)
```
Link dataset with data samples.
## download_dataset
```python
Client.download_dataset(self, asset_key, destination_folder)
```
Download data manager resource.

Download opener script in destination folder.

## download_algo
```python
Client.download_algo(self, asset_key, destination_folder)
```
Download algo resource.

Download algo package in destination folder.

## download_objective
```python
Client.download_objective(self, asset_key, destination_folder)
```
Download objective resource.

Download metrics script in destination folder.

## describe_algo
```python
Client.describe_algo(self, asset_key)
```
Get algo description.
## describe_dataset
```python
Client.describe_dataset(self, asset_key)
```
Get dataset description.
## describe_objective
```python
Client.describe_objective(self, asset_key)
```
Get objective description.
