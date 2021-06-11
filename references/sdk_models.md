# Summary

- [DataSample](#DataSample)
- [Dataset](#Dataset)
- [Objective](#Objective)
- [Testtuple](#Testtuple)
- [Traintuple](#Traintuple)
- [Aggregatetuple](#Aggregatetuple)
- [CompositeTraintuple](#CompositeTraintuple)
- [Algo](#Algo)
- [CompositeAlgo](#CompositeAlgo)
- [AggregateAlgo](#AggregateAlgo)
- [ComputePlan](#ComputePlan)
- [Node](#Node)
- [Permissions](#Permissions)
- [InModel](#InModel)
- [InHeadModel](#InHeadModel)
- [OutModel](#OutModel)
- [OutHeadModel](#OutHeadModel)
- [OutCompositeTrunkModel](#OutCompositeTrunkModel)
- [OutCompositeHeadModel](#OutCompositeHeadModel)
- [_File](#_File)
- [_ObjectiveDataset](#_ObjectiveDataset)
- [_Metric](#_Metric)
- [_TraintupleAlgo](#_TraintupleAlgo)
- [_TraintupleDataset](#_TraintupleDataset)
- [_TesttupleDataset](#_TesttupleDataset)
- [_TesttupleObjective](#_TesttupleObjective)


# Models

## DataSample
Data sample
```python
- key: str
- owner: str
- data_manager_keys: Optional[List[str]]
- path: Optional[DirectoryPath]
- validated: bool
- test_only: bool
```

## Dataset
Dataset asset
```python
- key: str
- name: str
- owner: str
- objective_key: Optional[str]
- permissions: Permissions
- type: str
- train_data_sample_keys: List[str]
- test_data_sample_keys: List[str]
- opener: _File
- description: _File
- metadata: Mapping[str, str]
```

## Objective
Objective
```python
- key: str
- name: str
- owner: str
- test_dataset: Optional[_ObjectiveDataset]
- metadata: Mapping[str, str]
- permissions: Permissions
- description: _File
- metrics: _Metric
```

## Testtuple
Testtuple
```python
- key: str
- creator: str
- algo: _TraintupleAlgo
- objective: _TesttupleObjective
- traintuple_key: str
- certified: bool
- dataset: _TesttupleDataset
- tag: Optional[str]
- log: str
- status: str
- compute_plan_key: str
- rank: int
- traintuple_type: Type
- metadata: Mapping[str, str]
```

## Traintuple
Traintuple
```python
- key: str
- creator: str
- algo: _TraintupleAlgo
- dataset: _TraintupleDataset
- permissions: Permissions
- tag: str
- compute_plan_key: str
- rank: int
- status: str
- log: str
- in_models: Optional[List[InModel]]
- out_model: Optional[OutModel]
- metadata: Mapping[str, str]
```

## Aggregatetuple
Aggregatetuple
```python
- key: str
- creator: str
- worker: str
- algo: _TraintupleAlgo
- permissions: Permissions
- tag: str
- compute_plan_key: str
- rank: Optional[int]
- status: str
- log: str
- in_models: List[InModel]
- out_model: Optional[OutModel]
- metadata: Mapping[str, str]
```

## CompositeTraintuple
CompositeTraintuple
```python
- key: str
- creator: str
- algo: _TraintupleAlgo
- dataset: _TraintupleDataset
- tag: str
- compute_plan_key: str
- rank: Optional[int]
- status: str
- log: str
- in_head_model: Optional[InHeadModel]
- in_trunk_model: Optional[InModel]
- out_head_model: OutCompositeHeadModel
- out_trunk_model: OutCompositeTrunkModel
- metadata: Mapping[str, str]
```

## Algo
Algo
```python
- key: str
- name: str
- owner: str
- permissions: Permissions
- metadata: Mapping[str, str]
- description: _File
- content: _File
```

## CompositeAlgo
CompositeAlgo
```python
- key: str
- name: str
- owner: str
- permissions: Permissions
- metadata: Mapping[str, str]
- description: _File
- content: _File
```

## AggregateAlgo
AggregateAlgo
```python
- key: str
- name: str
- owner: str
- permissions: Permissions
- metadata: Mapping[str, str]
- description: _File
- content: _File
```

## ComputePlan
ComputePlan
```python
- key: str
- status: str
- failed_tuple: FailedTuple
- traintuple_keys: Optional[List[str]]
- composite_traintuple_keys: Optional[List[str]]
- aggregatetuple_keys: Optional[List[str]]
- testtuple_keys: Optional[List[str]]
- id_to_key: Mapping[str, str]
- tag: str
- tuple_count: int
- done_count: int
- metadata: Mapping[str, str]
- clean_models: bool
```

## Node
Node
```python
- id: str
- is_current: bool
```

## Permissions
Permissions structure stored in various asset types.
```python
- process: Permission
```

## InModel
In model of a traintuple, aggregate tuple or in trunk
model of a composite traintuple
```python
- key: str
- checksum: str
- storage_address: Union[pydantic.types.FilePath, pydantic.networks.AnyUrl, str]
- traintuple_key: Optional[str]
```

## InHeadModel
In head model of a composite traintuple
```python
- key: str
- checksum: str
- storage_address: Union[pydantic.types.FilePath, pydantic.networks.AnyUrl, str, NoneType]
- traintuple_key: Optional[str]
```

## OutModel
Out model of a traintuple, aggregate tuple or out trunk
model of a composite traintuple
```python
- key: str
- checksum: str
- storage_address: Union[pydantic.types.FilePath, pydantic.networks.AnyUrl, str]
```

## OutHeadModel
Out head model of a composite traintuple
```python
- key: str
- checksum: str
- storage_address: Optional[FilePath]
```

## OutCompositeTrunkModel
Out trunk model of a composite traintuple with permissions
```python
- permissions: Permissions
- out_model: Optional[OutModel]
```

## OutCompositeHeadModel
Out head model of a composite traintuple with permissions
```python
- permissions: Permissions
- out_model: Optional[OutHeadModel]
```

## _File
File as stored in the models
```python
- checksum: str
- storage_address: Union[pydantic.types.FilePath, pydantic.networks.AnyUrl, str]
```

## _ObjectiveDataset
Dataset as stored in the Objective asset
```python
- data_manager_key: str
- data_sample_keys: List[str]
- metadata: Mapping[str, str]
- worker: str
```

## _Metric
Metric associated to a testtuple or objective
```python
- name: Optional[str]
- checksum: str
- storage_address: Union[pydantic.types.FilePath, pydantic.networks.AnyUrl, str]
```

## _TraintupleAlgo
Algo associated to a traintuple
```python
- key: str
- checksum: str
- storage_address: Union[pydantic.types.FilePath, pydantic.networks.AnyUrl, str]
- name: str
```

## _TraintupleDataset
Dataset as stored in a traintuple or composite traintuple
```python
- key: str
- opener_checksum: str
- data_sample_keys: List[str]
- worker: str
- metadata: Optional[Mapping[str, str]]
```

## _TesttupleDataset
Dataset of a testtuple
```python
- key: str
- opener_checksum: str
- perf: float
- data_sample_keys: List[str]
- worker: str
```

## _TesttupleObjective
Objective of a testtuple
```python
- key: str
- metrics: _Metric
```

