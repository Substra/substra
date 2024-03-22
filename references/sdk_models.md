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


# Models

## DataSample
Data sample
```text
- key: <class 'str'>
- owner: <class 'str'>
- data_manager_keys: typing.Optional[typing.List[str]]
- path: typing.Optional[typing.Annotated[pathlib.Path, PathType(path_type='dir')]]
- creation_date: <class 'datetime.datetime'>
```

## Dataset
Dataset asset
```text
- key: <class 'str'>
- name: <class 'str'>
- owner: <class 'str'>
- permissions: <class 'substra.sdk.models.Permissions'>
- data_sample_keys: typing.List[str]
- opener: <class 'substra.sdk.models._File'>
- description: <class 'substra.sdk.models._File'>
- metadata: typing.Dict[str, str]
- creation_date: <class 'datetime.datetime'>
- logs_permission: <class 'substra.sdk.models.Permission'>
```

## Task
Asset creation specification base class.
```text
- key: <class 'str'>
- function: <class 'substra.sdk.models.Function'>
- owner: <class 'str'>
- compute_plan_key: <class 'str'>
- metadata: typing.Dict[str, str]
- status: <enum 'ComputeTaskStatus'>
- worker: <class 'str'>
- rank: typing.Optional[int]
- tag: <class 'str'>
- creation_date: <class 'datetime.datetime'>
- start_date: typing.Optional[datetime.datetime]
- end_date: typing.Optional[datetime.datetime]
- error_type: typing.Optional[substra.sdk.models.TaskErrorType]
- inputs: typing.List[substra.sdk.models.InputRef]
- outputs: typing.Dict[str, substra.sdk.models.ComputeTaskOutput]
```

## Function
Asset creation specification base class.
```text
- key: <class 'str'>
- name: <class 'str'>
- owner: <class 'str'>
- permissions: <class 'substra.sdk.models.Permissions'>
- metadata: typing.Dict[str, str]
- creation_date: <class 'datetime.datetime'>
- inputs: typing.List[substra.sdk.models.FunctionInput]
- outputs: typing.List[substra.sdk.models.FunctionOutput]
- status: <enum 'FunctionStatus'>
- description: <class 'substra.sdk.models._File'>
- archive: <class 'substra.sdk.models._File'>
```

## ComputePlan
ComputePlan
```text
- key: <class 'str'>
- tag: <class 'str'>
- name: <class 'str'>
- owner: <class 'str'>
- metadata: typing.Dict[str, str]
- task_count: <class 'int'>
- waiting_builder_slot_count: <class 'int'>
- building_count: <class 'int'>
- waiting_parent_tasks_count: <class 'int'>
- waiting_executor_slot_count: <class 'int'>
- executing_count: <class 'int'>
- canceled_count: <class 'int'>
- failed_count: <class 'int'>
- done_count: <class 'int'>
- failed_task_key: typing.Optional[str]
- status: <enum 'ComputePlanStatus'>
- creation_date: <class 'datetime.datetime'>
- start_date: typing.Optional[datetime.datetime]
- end_date: typing.Optional[datetime.datetime]
- estimated_end_date: typing.Optional[datetime.datetime]
- duration: typing.Optional[int]
- creator: typing.Optional[str]
```

## Performances
Performances of the different compute tasks of a compute plan
```text
- compute_plan_key: typing.List[str]
- compute_plan_tag: typing.List[str]
- compute_plan_status: typing.List[str]
- compute_plan_start_date: typing.List[datetime.datetime]
- compute_plan_end_date: typing.List[datetime.datetime]
- compute_plan_metadata: typing.List[dict]
- worker: typing.List[str]
- task_key: typing.List[str]
- task_rank: typing.List[int]
- round_idx: typing.List[int]
- identifier: typing.List[str]
- performance: typing.List[float]
```

## Organization
Organization
```text
- id: <class 'str'>
- is_current: <class 'bool'>
- creation_date: <class 'datetime.datetime'>
```

## Permissions
Permissions structure stored in various asset types.
```text
- process: <class 'substra.sdk.models.Permission'>
```

## InModel
In model of a task
```text
- checksum: <class 'str'>
- storage_address: typing.Union[typing.Annotated[pathlib.Path, PathType(path_type='file')], pydantic_core._pydantic_core.Url, str]
```

## OutModel
Out model of a task
```text
- key: <class 'str'>
- compute_task_key: <class 'str'>
- address: typing.Optional[substra.sdk.models.InModel]
- permissions: <class 'substra.sdk.models.Permissions'>
- owner: <class 'str'>
- creation_date: <class 'datetime.datetime'>
```

