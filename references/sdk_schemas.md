# Summary

- [DataSampleSpec](#DataSampleSpec)
- [DatasetSpec](#DatasetSpec)
- [UpdateDatasetSpec](#UpdateDatasetSpec)
- [AlgoSpec](#AlgoSpec)
- [AlgoInputSpec](#AlgoInputSpec)
- [AlgoOutputSpec](#AlgoOutputSpec)
- [PredicttupleSpec](#PredicttupleSpec)
- [UpdateAlgoSpec](#UpdateAlgoSpec)
- [TesttupleSpec](#TesttupleSpec)
- [TraintupleSpec](#TraintupleSpec)
- [AggregatetupleSpec](#AggregatetupleSpec)
- [CompositeTraintupleSpec](#CompositeTraintupleSpec)
- [ComputePlanSpec](#ComputePlanSpec)
- [UpdateComputePlanSpec](#UpdateComputePlanSpec)
- [UpdateComputePlanTuplesSpec](#UpdateComputePlanTuplesSpec)
- [ComputePlanPredicttupleSpec](#ComputePlanPredicttupleSpec)
- [ComputePlanTesttupleSpec](#ComputePlanTesttupleSpec)
- [ComputePlanAggregatetupleSpec](#ComputePlanAggregatetupleSpec)
- [ComputePlanCompositeTraintupleSpec](#ComputePlanCompositeTraintupleSpec)
- [ComputePlanTraintupleSpec](#ComputePlanTraintupleSpec)
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
```text
- name: str
- description: Path
- file: Path
- permissions: Permissions
- metadata: Optional[Mapping[str, str]]
- category: AlgoCategory
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

## PredicttupleSpec
Specification for creating a predict tuple
```text
- key: str
- tag: Optional[str]
- compute_plan_key: Optional[str]
- metadata: Optional[Mapping[str, str]]
- algo_key: str
- inputs: Optional[List[InputRef]]
- outputs: Optional[Mapping[str, ComputeTaskOutputSpec]]
- traintuple_key: str
- data_manager_key: str
- test_data_sample_keys: List[str]
- category: TaskCategory
```

## UpdateAlgoSpec
Specification for updating an algo
```text
- name: str
```

## TesttupleSpec
Specification for creating a testtuple
```text
- key: str
- tag: Optional[str]
- compute_plan_key: Optional[str]
- metadata: Optional[Mapping[str, str]]
- algo_key: str
- inputs: Optional[List[InputRef]]
- outputs: Optional[Mapping[str, ComputeTaskOutputSpec]]
- predicttuple_key: str
- data_manager_key: str
- test_data_sample_keys: List[str]
- category: TaskCategory
```

## TraintupleSpec
Specification for creating a traintuple
```text
- key: str
- tag: Optional[str]
- compute_plan_key: Optional[str]
- metadata: Optional[Mapping[str, str]]
- algo_key: str
- inputs: Optional[List[InputRef]]
- outputs: Optional[Mapping[str, ComputeTaskOutputSpec]]
- data_manager_key: str
- train_data_sample_keys: List[str]
- in_models_keys: Optional[List[str]]
- rank: Optional[int]
- category: TaskCategory
```

## AggregatetupleSpec
Specification for creating an aggregate tuple
```text
- key: str
- tag: Optional[str]
- compute_plan_key: Optional[str]
- metadata: Optional[Mapping[str, str]]
- algo_key: str
- inputs: Optional[List[InputRef]]
- outputs: Optional[Mapping[str, ComputeTaskOutputSpec]]
- worker: str
- in_models_keys: List[str]
- rank: Optional[int]
- category: TaskCategory
```

## CompositeTraintupleSpec
Specification for creating a composite traintuple
```text
- key: str
- tag: Optional[str]
- compute_plan_key: Optional[str]
- metadata: Optional[Mapping[str, str]]
- algo_key: str
- inputs: Optional[List[InputRef]]
- outputs: Optional[Mapping[str, ComputeTaskOutputSpec]]
- data_manager_key: str
- train_data_sample_keys: List[str]
- in_head_model_key: Optional[str]
- in_trunk_model_key: Optional[str]
- rank: Optional[int]
- category: TaskCategory
```

## ComputePlanSpec
Specification for creating a compute plan
```text
- key: str
- traintuples: Optional[List[ComputePlanTraintupleSpec]]
- composite_traintuples: Optional[List[ComputePlanCompositeTraintupleSpec]]
- aggregatetuples: Optional[List[ComputePlanAggregatetupleSpec]]
- predicttuples: Optional[List[ComputePlanPredicttupleSpec]]
- testtuples: Optional[List[ComputePlanTesttupleSpec]]
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
- traintuples: Optional[List[ComputePlanTraintupleSpec]]
- composite_traintuples: Optional[List[ComputePlanCompositeTraintupleSpec]]
- aggregatetuples: Optional[List[ComputePlanAggregatetupleSpec]]
- predicttuples: Optional[List[ComputePlanPredicttupleSpec]]
- testtuples: Optional[List[ComputePlanTesttupleSpec]]
```

## ComputePlanPredicttupleSpec
Specification of a predict tuple inside a compute
plan specification
```text
- algo_key: str
- tag: Optional[str]
- metadata: Optional[Mapping[str, str]]
- inputs: Optional[List[InputRef]]
- outputs: Optional[Mapping[str, ComputeTaskOutputSpec]]
- predicttuple_id: str
- traintuple_id: str
- data_manager_key: str
- test_data_sample_keys: List[str]
```

## ComputePlanTesttupleSpec
Specification of a testtuple inside a compute
plan specification
```text
- algo_key: str
- tag: Optional[str]
- metadata: Optional[Mapping[str, str]]
- inputs: Optional[List[InputRef]]
- outputs: Optional[Mapping[str, ComputeTaskOutputSpec]]
- predicttuple_id: str
- data_manager_key: str
- test_data_sample_keys: List[str]
```

## ComputePlanAggregatetupleSpec
Specification of an aggregate tuple inside a compute
plan specification
```text
- algo_key: str
- tag: Optional[str]
- metadata: Optional[Mapping[str, str]]
- inputs: Optional[List[InputRef]]
- outputs: Optional[Mapping[str, ComputeTaskOutputSpec]]
- aggregatetuple_id: str
- worker: str
- in_models_ids: Optional[List[str]]
```

## ComputePlanCompositeTraintupleSpec
Specification of a composite traintuple inside a compute
plan specification
```text
- algo_key: str
- tag: Optional[str]
- metadata: Optional[Mapping[str, str]]
- inputs: Optional[List[InputRef]]
- outputs: Optional[Mapping[str, ComputeTaskOutputSpec]]
- composite_traintuple_id: str
- data_manager_key: str
- train_data_sample_keys: List[str]
- in_head_model_id: Optional[str]
- in_trunk_model_id: Optional[str]
```

## ComputePlanTraintupleSpec
Specification of a traintuple inside a compute
plan specification
```text
- algo_key: str
- tag: Optional[str]
- metadata: Optional[Mapping[str, str]]
- inputs: Optional[List[InputRef]]
- outputs: Optional[Mapping[str, ComputeTaskOutputSpec]]
- data_manager_key: str
- train_data_sample_keys: List[str]
- traintuple_id: str
- in_models_ids: Optional[List[str]]
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

