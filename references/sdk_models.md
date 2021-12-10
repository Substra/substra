# Summary

- [DataSample](#DataSample)
- [Dataset](#Dataset)
- [Metric](#Metric)
- [Testtuple](#Testtuple)
- [Traintuple](#Traintuple)
- [Aggregatetuple](#Aggregatetuple)
- [CompositeTraintuple](#CompositeTraintuple)
- [Algo](#Algo)
- [ComputePlan](#ComputePlan)
- [Node](#Node)
- [Permissions](#Permissions)
- [InModel](#InModel)
- [OutModel](#OutModel)
- [_File](#_File)
- [_Metric](#_Metric)


# Models

## DataSample
Data sample
```python
- key: str
- owner: str
- data_manager_keys: Optional[List[str]]
- path: Optional[DirectoryPath]
- validated: bool
- creation_date: datetime
- test_only: bool
```

## Dataset
Dataset asset
```python
- key: str
- name: str
- owner: str
- permissions: Permissions
- type: str
- train_data_sample_keys: List[str]
- test_data_sample_keys: List[str]
- opener: _File
- description: _File
- metadata: Mapping[str, str]
- creation_date: datetime
```

## Metric
Metric
```python
- key: str
- name: str
- owner: str
- metadata: Mapping[str, str]
- permissions: Permissions
- creation_date: datetime
- description: _File
- address: _Metric
```

## Testtuple
Testtuple
```python
- key: str
- category: TaskCategory
- algo: Algo
- owner: str
- compute_plan_key: str
- metadata: Mapping[str, str]
- status: str
- worker: str
- rank: Optional[int]
- parent_task_keys: List[str]
- tag: str
- creation_date: datetime
- test: _Test
```

## Traintuple
Traintuple
```python
- key: str
- category: TaskCategory
- algo: Algo
- owner: str
- compute_plan_key: str
- metadata: Mapping[str, str]
- status: str
- worker: str
- rank: Optional[int]
- parent_task_keys: List[str]
- tag: str
- creation_date: datetime
- train: _Train
```

## Aggregatetuple
Aggregatetuple
```python
- key: str
- category: TaskCategory
- algo: Algo
- owner: str
- compute_plan_key: str
- metadata: Mapping[str, str]
- status: str
- worker: str
- rank: Optional[int]
- parent_task_keys: List[str]
- tag: str
- creation_date: datetime
- aggregate: _Aggregate
```

## CompositeTraintuple
CompositeTraintuple
```python
- key: str
- category: TaskCategory
- algo: Algo
- owner: str
- compute_plan_key: str
- metadata: Mapping[str, str]
- status: str
- worker: str
- rank: Optional[int]
- parent_task_keys: List[str]
- tag: str
- creation_date: datetime
- composite: _Composite
```

## Algo
Asset creation specification base class.
```python
- key: str
- name: str
- owner: str
- permissions: Permissions
- metadata: Mapping[str, str]
- category: AlgoCategory
- creation_date: datetime
- description: _File
- algorithm: _File
```

## ComputePlan
ComputePlan
```python
- key: str
- tag: str
- owner: str
- metadata: Mapping[str, str]
- done_count: int
- task_count: int
- failed_task: Optional[FailedTuple]
- delete_intermediary_models: bool
- status: ComputePlanStatus
- creation_date: datetime
```

## Node
Node
```python
- id: str
- is_current: bool
- creation_date: datetime
```

## Permissions
Permissions structure stored in various asset types.
```python
- process: Permission
- download: Permission
```

## InModel
In model of a traintuple, aggregate or composite traintuple
```python
- checksum: str
- storage_address: Union[pydantic.types.FilePath, pydantic.networks.AnyUrl, str]
```

## OutModel
Out model of a traintuple, aggregate tuple or out trunk
model of a composite traintuple
```python
- key: str
- category: ModelType
- compute_task_key: str
- address: Optional[InModel]
- permissions: Permissions
- owner: str
- creation_date: datetime
```

## _File
File as stored in the models
```python
- checksum: str
- storage_address: Union[pydantic.types.FilePath, pydantic.networks.AnyUrl, str]
```

## _Metric
Metric associated to a testtuple or metric
```python
- checksum: str
- storage_address: Union[pydantic.types.FilePath, pydantic.networks.AnyUrl, str]
```
