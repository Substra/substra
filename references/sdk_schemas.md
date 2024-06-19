# Summary

- [DataSampleSpec](#DataSampleSpec)
- [DatasetSpec](#DatasetSpec)
- [UpdateDatasetSpec](#UpdateDatasetSpec)
- [FunctionSpec](#FunctionSpec)
- [FunctionInputSpec](#FunctionInputSpec)
- [FunctionOutputSpec](#FunctionOutputSpec)
- [TaskSpec](#TaskSpec)
- [ComputeTaskOutputSpec](#ComputeTaskOutputSpec)
- [UpdateFunctionSpec](#UpdateFunctionSpec)
- [ComputePlanSpec](#ComputePlanSpec)
- [UpdateComputePlanSpec](#UpdateComputePlanSpec)
- [UpdateComputePlanTasksSpec](#UpdateComputePlanTasksSpec)
- [ComputePlanTaskSpec](#ComputePlanTaskSpec)
- [Permissions](#Permissions)
- [PrivatePermissions](#PrivatePermissions)


# Schemas

## DataSampleSpec
Specification to create one or many data samples
To create one data sample, use the 'path' field, otherwise use
the 'paths' field.
```text
- path: typing.Optional[pathlib.Path]
- paths: typing.Optional[typing.List[pathlib.Path]]
- data_manager_keys: typing.List[str]
```

## DatasetSpec
Specification for creating a dataset

note : metadata field does not accept strings containing '__' as dict key

note : If no description markdown file is given, create an empty one on the data_opener folder.
```text
- name: <class 'str'>
- data_opener: <class 'pathlib.Path'>
- description: typing.Optional[pathlib.Path]
- permissions: <class 'substra.sdk.schemas.Permissions'>
- metadata: typing.Optional[typing.Dict[str, str]]
- logs_permission: <class 'substra.sdk.schemas.Permissions'>
```

## UpdateDatasetSpec
Specification for updating a dataset
```text
- name: <class 'str'>
```

## FunctionSpec
Specification for creating an function

note : metadata field does not accept strings containing '__' as dict key
```text
- name: <class 'str'>
- description: <class 'pathlib.Path'>
- file: <class 'pathlib.Path'>
- permissions: <class 'substra.sdk.schemas.Permissions'>
- metadata: typing.Optional[typing.Dict[str, str]]
- inputs: typing.Optional[typing.List[substra.sdk.schemas.FunctionInputSpec]]
- outputs: typing.Optional[typing.List[substra.sdk.schemas.FunctionOutputSpec]]
```

## FunctionInputSpec
Asset creation specification base class.
```text
- identifier: <class 'str'>
- multiple: <class 'bool'>
- optional: <class 'bool'>
- kind: <enum 'AssetKind'>
```

## FunctionOutputSpec
Asset creation specification base class.
```text
- identifier: <class 'str'>
- kind: <enum 'AssetKind'>
- multiple: <class 'bool'>
```

## TaskSpec
Asset creation specification base class.
```text
- key: <class 'str'>
- tag: typing.Optional[str]
- compute_plan_key: typing.Optional[str]
- metadata: typing.Optional[typing.Dict[str, str]]
- function_key: <class 'str'>
- worker: <class 'str'>
- rank: typing.Optional[int]
- inputs: typing.Optional[typing.List[substra.sdk.schemas.InputRef]]
- outputs: typing.Optional[typing.Dict[str, substra.sdk.schemas.ComputeTaskOutputSpec]]
```

## ComputeTaskOutputSpec
Specification of a compute task output
```text
- permissions: <class 'substra.sdk.schemas.Permissions'>
- is_transient: typing.Optional[bool]
```

## UpdateFunctionSpec
Specification for updating an function
```text
- name: <class 'str'>
```

## ComputePlanSpec
Specification for creating a compute plan

note : metadata field does not accept strings containing '__' as dict key
```text
- key: <class 'str'>
- tasks: typing.Optional[typing.List[substra.sdk.schemas.ComputePlanTaskSpec]]
- tag: typing.Optional[str]
- name: <class 'str'>
- metadata: typing.Optional[typing.Dict[str, str]]
```

## UpdateComputePlanSpec
Specification for updating a compute plan
```text
- name: <class 'str'>
```

## UpdateComputePlanTasksSpec
Specification for updating a compute plan's tasks
```text
- key: <class 'str'>
- tasks: typing.Optional[typing.List[substra.sdk.schemas.ComputePlanTaskSpec]]
```

## ComputePlanTaskSpec
Specification of a compute task inside a compute plan specification

note : metadata field does not accept strings containing '__' as dict key
```text
- task_id: <class 'str'>
- function_key: <class 'str'>
- worker: <class 'str'>
- tag: typing.Optional[str]
- metadata: typing.Optional[typing.Dict[str, str]]
- inputs: typing.Optional[typing.List[substra.sdk.schemas.InputRef]]
- outputs: typing.Optional[typing.Dict[str, substra.sdk.schemas.ComputeTaskOutputSpec]]
```

## Permissions
Specification for permissions. If public is False,
give the list of authorized ids.
```text
- public: <class 'bool'>
- authorized_ids: typing.List[str]
```

## PrivatePermissions
Specification for private permissions. Only the organizations whose
ids are in authorized_ids can access the asset.
```text
- authorized_ids: typing.List[str]
```

