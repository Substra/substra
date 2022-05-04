# Summary

- [DataSampleSpec](#DataSampleSpec)
- [DatasetSpec](#DatasetSpec)
- [AlgoSpec](#AlgoSpec)
- [MetricSpec](#MetricSpec)
- [TesttupleSpec](#TesttupleSpec)
- [TraintupleSpec](#TraintupleSpec)
- [AggregatetupleSpec](#AggregatetupleSpec)
- [CompositeTraintupleSpec](#CompositeTraintupleSpec)
- [ComputePlanSpec](#ComputePlanSpec)
- [UpdateComputePlanSpec](#UpdateComputePlanSpec)
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

## AlgoSpec
Specification for creating an algo
```text
- name: str
- description: Path
- file: Path
- permissions: Permissions
- metadata: Optional[Mapping[str, str]]
- category: AlgoCategory
```

## MetricSpec
Specification for creating an metric
```text
- name: str
- description: Path
- file: Path
- permissions: Permissions
- metadata: Optional[Mapping[str, str]]
- category: AlgoCategory
```

## TesttupleSpec
Specification for creating a testtuple
```text
- metric_keys: List[str]
- traintuple_key: str
- tag: Optional[str]
- data_manager_key: str
- test_data_sample_keys: List[str]
- compute_plan_key: Optional[str]
- metadata: Optional[Mapping[str, str]]
```

## TraintupleSpec
Specification for creating a traintuple
```text
- algo_key: str
- data_manager_key: str
- train_data_sample_keys: List[str]
- in_models_keys: Optional[List[str]]
- tag: Optional[str]
- compute_plan_key: Optional[str]
- rank: Optional[int]
- metadata: Optional[Mapping[str, str]]
```

## AggregatetupleSpec
Specification for creating an aggregate tuple
```text
- algo_key: str
- worker: str
- in_models_keys: List[str]
- tag: Optional[str]
- compute_plan_key: Optional[str]
- rank: Optional[int]
- metadata: Optional[Mapping[str, str]]
```

## CompositeTraintupleSpec
Specification for creating a composite traintuple
```text
- algo_key: str
- data_manager_key: str
- train_data_sample_keys: List[str]
- in_head_model_key: Optional[str]
- in_trunk_model_key: Optional[str]
- tag: Optional[str]
- compute_plan_key: Optional[str]
- out_trunk_model_permissions: Permissions
- rank: Optional[int]
- metadata: Optional[Mapping[str, str]]
```

## ComputePlanSpec
Specification for creating a compute plan
```text
- traintuples: Optional[List[ComputePlanTraintupleSpec]]
- composite_traintuples: Optional[List[ComputePlanCompositeTraintupleSpec]]
- aggregatetuples: Optional[List[ComputePlanAggregatetupleSpec]]
- testtuples: Optional[List[ComputePlanTesttupleSpec]]
- tag: Optional[str]
- clean_models: Optional[bool]
- metadata: Optional[Mapping[str, str]]
```

## UpdateComputePlanSpec
Specification for updating a compute plan
```text
- traintuples: Optional[List[ComputePlanTraintupleSpec]]
- composite_traintuples: Optional[List[ComputePlanCompositeTraintupleSpec]]
- aggregatetuples: Optional[List[ComputePlanAggregatetupleSpec]]
- testtuples: Optional[List[ComputePlanTesttupleSpec]]
```

## ComputePlanTesttupleSpec
Specification of a testtuple inside a compute
plan specification
```text
- metric_keys: List[str]
- traintuple_id: str
- tag: Optional[str]
- data_manager_key: str
- test_data_sample_keys: List[str]
- metadata: Optional[Mapping[str, str]]
```

## ComputePlanAggregatetupleSpec
Specification of an aggregate tuple inside a compute
plan specification
```text
- aggregatetuple_id: str
- algo_key: str
- worker: str
- in_models_ids: Optional[List[str]]
- tag: Optional[str]
- metadata: Optional[Mapping[str, str]]
```

## ComputePlanCompositeTraintupleSpec
Specification of a composite traintuple inside a compute
plan specification
```text
- composite_traintuple_id: str
- algo_key: str
- data_manager_key: str
- train_data_sample_keys: List[str]
- in_head_model_id: Optional[str]
- in_trunk_model_id: Optional[str]
- tag: Optional[str]
- out_trunk_model_permissions: Permissions
- metadata: Optional[Mapping[str, str]]
```

## ComputePlanTraintupleSpec
Specification of a traintuple inside a compute
plan specification
```text
- algo_key: str
- data_manager_key: str
- train_data_sample_keys: List[str]
- traintuple_id: str
- in_models_ids: Optional[List[str]]
- tag: Optional[str]
- metadata: Optional[Mapping[str, str]]
```

## Permissions
Specification for permissions. If public is False,
give the list of authorized ids.
```text
- public: bool
- authorized_ids: List[str]
```

## PrivatePermissions
Specification for private permissions. Only the nodes whose
ids are in authorized_ids can access the asset.
```text
- authorized_ids: List[str]
```

