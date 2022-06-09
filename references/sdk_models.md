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
- [Performances](#Performances)
- [Node](#Node)
- [Permissions](#Permissions)
- [InModel](#InModel)
- [OutModel](#OutModel)
- [_File](#_File)


# Models

## DataSample
Data sample
```text
- key: str
- owner: str
- data_manager_keys: Optional[List[str]]
- path: Optional[DirectoryPath]
- creation_date: datetime
- test_only: bool
```

## Dataset
Dataset asset
```text
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
- logs_permission: Permission
```

## Metric
Metric
```text
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

## Testtuple
Testtuple
```text
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
- parent_tasks: Optional[List[Union[ForwardRef('Traintuple'), ForwardRef('CompositeTraintuple'), ForwardRef('Aggregatetuple')]]]
- tag: str
- creation_date: datetime
- start_date: Optional[datetime]
- end_date: Optional[datetime]
- error_type: Optional[TaskErrorType]
- test: _Test
```

## Traintuple
Traintuple
```text
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
- parent_tasks: Optional[List[Union[ForwardRef('Traintuple'), ForwardRef('CompositeTraintuple'), ForwardRef('Aggregatetuple')]]]
- tag: str
- creation_date: datetime
- start_date: Optional[datetime]
- end_date: Optional[datetime]
- error_type: Optional[TaskErrorType]
- train: _Train
```

## Aggregatetuple
Aggregatetuple
```text
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
- parent_tasks: Optional[List[Union[ForwardRef('Traintuple'), ForwardRef('CompositeTraintuple'), ForwardRef('Aggregatetuple')]]]
- tag: str
- creation_date: datetime
- start_date: Optional[datetime]
- end_date: Optional[datetime]
- error_type: Optional[TaskErrorType]
- aggregate: _Aggregate
```

## CompositeTraintuple
CompositeTraintuple
```text
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
- parent_tasks: Optional[List[Union[ForwardRef('Traintuple'), ForwardRef('CompositeTraintuple'), ForwardRef('Aggregatetuple')]]]
- tag: str
- creation_date: datetime
- start_date: Optional[datetime]
- end_date: Optional[datetime]
- error_type: Optional[TaskErrorType]
- composite: _Composite
```

## Algo
Asset creation specification base class.
```text
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
```text
- key: str
- tag: str
- name: str
- owner: str
- metadata: Mapping[str, str]
- task_count: int
- waiting_count: int
- todo_count: int
- doing_count: int
- canceled_count: int
- failed_count: int
- done_count: int
- failed_task: Optional[FailedTuple]
- delete_intermediary_models: bool
- status: ComputePlanStatus
- creation_date: datetime
- start_date: Optional[datetime]
- end_date: Optional[datetime]
- estimated_end_date: Optional[datetime]
- duration: Optional[int]
```

## Performances
Performances of the different compute tasks of a compute plan
```text
- compute_plan_key: List[str]
- compute_plan_tag: List[str]
- compute_plan_status: List[str]
- compute_plan_start_date: List[datetime]
- compute_plan_end_date: List[datetime]
- compute_plan_metadata: List[dict]
- worker: List[str]
- testtuple_key: List[str]
- metric_name: List[str]
- testtuple_rank: List[int]
- round_idx: List[int]
- performance: List[float]
```

## Node
Node
```text
- id: str
- is_current: bool
- creation_date: datetime
```

## Permissions
Permissions structure stored in various asset types.
```text
- process: Permission
```

## InModel
In model of a traintuple, aggregate or composite traintuple
```text
- checksum: str
- storage_address: Union[pydantic.types.FilePath, pydantic.networks.AnyUrl, str]
```

## OutModel
Out model of a traintuple, aggregate tuple or out trunk
model of a composite traintuple
```text
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
```text
- checksum: str
- storage_address: Union[pydantic.types.FilePath, pydantic.networks.AnyUrl, str]
```

