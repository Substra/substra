# Summary

- [DataSample](#DataSample)
- [Dataset](#Dataset)
- [Task](#Task)
- [Function](#Function)
- [ComputePlan](#ComputePlan)
- [Performances](#Performances)
- [Organization](#Organization)
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
```

## Dataset
Dataset asset
```text
- key: str
- name: str
- owner: str
- permissions: Permissions
- type: str
- data_sample_keys: List[str]
- opener: _File
- description: _File
- metadata: Mapping[str, str]
- creation_date: datetime
- logs_permission: Permission
```

## Task
Asset creation specification base class.
```text
- key: str
- function: Function
- owner: str
- compute_plan_key: str
- metadata: Mapping[str, str]
- status: Status
- worker: str
- rank: Optional[int]
- tag: str
- creation_date: datetime
- start_date: Optional[datetime]
- end_date: Optional[datetime]
- error_type: Optional[TaskErrorType]
- inputs: List[InputRef]
- outputs: Mapping[str, ComputeTaskOutput]
```

## Function
Asset creation specification base class.
```text
- key: str
- name: str
- owner: str
- permissions: Permissions
- metadata: Mapping[str, str]
- creation_date: datetime
- inputs: List[FunctionInput]
- outputs: List[FunctionOutput]
- description: _File
- function: _File
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
- failed_task_key: Optional[str]
- status: ComputePlanStatus
- creation_date: datetime
- start_date: Optional[datetime]
- end_date: Optional[datetime]
- estimated_end_date: Optional[datetime]
- duration: Optional[int]
- creator: Optional[str]
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
- task_key: List[str]
- function_name: List[str]
- task_rank: List[int]
- round_idx: List[int]
- performance: List[float]
```

## Organization
Organization
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
In model of a task
```text
- checksum: str
- storage_address: Union[FilePath, AnyUrl, str]
```

## OutModel
Out model of a task
```text
- key: str
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
- storage_address: Union[FilePath, AnyUrl, str]
```

