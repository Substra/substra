# substra_sdk_py

# Client
```python
Client(self)
```

## create_config
```python
Client.create_config(self, profile, url='http://127.0.0.1:8000', version='0.0', auth=False, insecure=False)
```
Create new config profile.
## set_config
```python
Client.set_config(self, profile='default')
```
Set config profile.
## get_config
```python
Client.get_config(self)
```
Get current config.
## add
```python
Client.add(self, asset, data, dryrun=False, timeout=False)
```
Add asset.
## register
```python
Client.register(self, asset, data, dryrun=False, timeout=False)
```
Register asset.
## get
```python
Client.get(self, asset, pkhash)
```
Get asset by key.
## options
```python
Client.options(self, asset, pkhash=None)
```
Options asset by key.
## list
```python
Client.list(self, asset, filters=None, is_complex=False)
```
List assets.
## path
```python
Client.path(self, asset, pkhash, path)
```
Get asset path.
## update
```python
Client.update(self, asset, pkhash, data)
```
Update asset by key.
## bulk_update
```python
Client.bulk_update(self, asset, data)
```
Update several assets.
## download_dataset
```python
Client.download_dataset(self, pkhash, destination_folder)
```
Download data manager resource.

Download opener script in destination folder.

## download_algo
```python
Client.download_algo(self, pkhash, destination_folder)
```
Download algo resource.

Download algo package in destination folder.

## download_objective
```python
Client.download_objective(self, pkhash, destination_folder)
```
Download objective resource.

Download metrics script in destination folder.

## download
```python
Client.download(self, asset, pkhash, destination_folder='.')
```
Download asset.
