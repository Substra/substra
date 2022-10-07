# Summary

- [DataSampleSpec](#DataSampleSpec)
- [DatasetSpec](#DatasetSpec)
- [UpdateDatasetSpec](#UpdateDatasetSpec)
- [AlgoSpec](#AlgoSpec)
- [AlgoInputSpec](#AlgoInputSpec)
- [AlgoOutputSpec](#AlgoOutputSpec)
- [TaskSpec](#TaskSpec)
- [UpdateAlgoSpec](#UpdateAlgoSpec)
- [ComputePlanSpec](#ComputePlanSpec)
- [UpdateComputePlanSpec](#UpdateComputePlanSpec)
- [UpdateComputePlanTuplesSpec](#UpdateComputePlanTuplesSpec)
- [ComputePlanTaskSpec](#ComputePlanTaskSpec)
- [Permissions](#Permissions)
- [PrivatePermissions](#PrivatePermissions)


# Schemas

## DataSampleSpec
Specification to create one or many data samples
To create one data sample, use the 'path' field, otherwise use
the 'paths' field.
```text
- path: Optional[Path]
- paths: Optional[List[Path]]
- test_only: bool
- data_manager_keys: List[str]
```

## DatasetSpec
Specification for creating a dataset

note : metadata field does not accept strings containing '__' as dict key
```text
- name: str
- data_opener: Path
- type: str
- description: Path
- permissions: Permissions
- metadata: Optional[Mapping[str, str]]
- logs_permission: Permissions
```

## UpdateDatasetSpec
Specification for updating a dataset
```text
- name: str
```

## AlgoSpec
Specification for creating an algo

note : metadata field does not accept strings containing '__' as dict key
```text
- name: str
- description: Path
- file: Path
- permissions: Permissions
- metadata: Optional[Mapping[str, str]]
- inputs: Optional[List[AlgoInputSpec]]
- outputs: Optional[List[AlgoOutputSpec]]
```

## AlgoInputSpec
Asset creation specification base class.
```text
- identifier: str
- multiple: bool
- optional: bool
- kind: AssetKind
```

## AlgoOutputSpec
Asset creation specification base class.
```text
- identifier: str
- kind: AssetKind
- multiple: bool
```

## TaskSpec
Asset creation specification base class.
```text
- key: str
- tag: Optional[str]
- compute_plan_key: Optional[str]
- metadata: Optional[Mapping[str, str]]
- algo_key: str
- worker: str
- rank: Optional[int]
- inputs: Optional[List[InputRef]]
- outputs: Optional[Mapping[str, ComputeTaskOutputSpec]]
```

## UpdateAlgoSpec
Specification for updating an algo
```text
- name: str
```

## ComputePlanSpec
Specification for creating a compute plan

note : metadata field does not accept strings containing '__' as dict key
```text
- key: str
- tasks: Optional[List[ComputePlanTaskSpec]]
- tag: Optional[str]
- name: str
- metadata: Optional[Mapping[str, str]]
```

## UpdateComputePlanSpec
Specification for updating a compute plan
```text
- name: str
```

## UpdateComputePlanTuplesSpec
Specification for updating a compute plan's tuples
```text
- key: str
- tasks: Optional[List[ComputePlanTaskSpec]]
```

## ComputePlanTaskSpec
Specification of a compute task inside a compute plan specification

note : metadata field does not accept strings containing '__' as dict key
```text
- task_id: str
- algo_key: str
- worker: str
- tag: Optional[str]
- metadata: Optional[Mapping[str, str]]
- inputs: Optional[List[InputRef]]
- outputs: Optional[Mapping[str, ComputeTaskOutputSpec]]
```

## Permissions
Specification for permissions. If public is False,
give the list of authorized ids.
```text
- public: bool
- authorized_ids: List[str]
```

## PrivatePermissions
Specification for private permissions. Only the organizations whose
ids are in authorized_ids can access the asset.
```text
- authorized_ids: List[str]
```

