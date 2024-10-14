# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- towncrier release notes start -->

## [1.0.0](https://github.com/Substra/substra/releases/tag/1.0.0) - 2024-10-14

### Removed

- Drop Python 3.9 support. ([#428](https://github.com/Substra/substra/pull/428))


## [0.54.0](https://github.com/Substra/substra/releases/tag/0.54.0) - 2024-09-12

### Added

- Python 3.12 support ([#418](https://github.com/Substra/substra/pull/418))

### Changed

- `description.md` are now `Optional` in `DatasampleSpec`. If no description file is given, `Substra` will generate a template indicating how to add a custom description file during dataset registration. ([#417](https://github.com/Substra/substra/pull/417))


## [0.53.0](https://github.com/Substra/substra/releases/tag/0.53.0) - 2024-06-03


### Added

- A warning indicates when a `Client` is set in hybrid mode ([#413](https://github.com/Substra/substra/pull/413))

### Changed

- Exclude `requests` 2.32.* due to bug introduction in these version. ([#415](https://github.com/Substra/substra/pull/415))


## [0.52.0](https://github.com/Substra/substra/releases/tag/0.52.0) - 2024-03-27


### Changed

- - BREAKING: Remove `type` from `DatasetSpec` ([#405](https://github.com/Substra/substra/pull/405))
- - Depreciate `setup.py` in favour of `pyproject.toml` ([#407](https://github.com/Substra/substra/pull/407))


## [0.51.0](https://github.com/Substra/substra/releases/tag/0.51.0) - 2024-03-07

### Changed

- Dropped Python 3.8 support ([#404](https://github.com/Substra/substra/pull/404))
- Compute task status `DOING` is renamed `EXECUTING` ([#401](https://github.com/Substra/substra/pull/401))
- Compute plan statuses `EMPTY`, `WAITING` ansd `TODO` are merged into new status `CREATED` ([#401](https://github.com/Substra/substra/pull/401))

## [0.50.0](https://github.com/Substra/substra/releases/tag/0.50.0) - 2024-02-26

### Changed

- BREAKING: Renamed `function` field of the Function pydantic model to `archive`([#393](https://github.com/Substra/substra/pull/393))
- BREAKING: Renamed ComputeTask status values ([#397](https://github.com/Substra/substra/pull/397))
- `download_logs` uses the new endpoint ([#398](https://github.com/Substra/substra/pull/398))
- BREAKING: Renamed Status to ComputeTaskStatus ([#399](https://github.com/Substra/substra/pull/399))

### Added

- Paths are now resolved on DatasampleSpec objects. Which means that users can pass relative paths ([#392](https://github.com/Substra/substra/pull/392))
- Added FunctionStatus ([#399](https://github.com/Substra/substra/pull/399))

## [0.49.0](https://github.com/Substra/substra/releases/tag/0.49.0) - 2023-10-18

### Added

- Support on Python 3.11 ([#388](https://github.com/Substra/substra/pull/388))

## [0.48.1](https://github.com/Substra/substra/releases/tag/0.48.1) - 2023-10-06

### Changed

- Use substra-tools base docker image (not minimal) in tests ([#389](https://github.com/Substra/substra/pull/389))

### Fixed

- Convert `round_idx` from metadata to `int` when creating `Performances` to fix Pydantic warning ([#387](https://github.com/Substra/substra/pull/387))

## [0.48.0](https://github.com/Substra/substra/releases/tag/0.48.0) - 2023-09-08

### Changed

- Update to pydantic 2.3.0 ([#375](https://github.com/Substra/substra/pull/375))

## [0.47.0](https://github.com/Substra/substra/releases/tag/0.47.0) - 2023-09-07

### Added

- `wait_completion` param on `get_performances`, `list_task_output_assets` and `get_task_output_asset` to block execution until execution is over ([#368](https://github.com/Substra/substra/pull/368))
- `list_task_output_assets` and `get_task_output_asset` wait that the compute task is over before getting assets ([#369](https://github.com/Substra/substra/pull/369))
- warning and help message when logging in with username/password rather than token ([#378](https://github.com/Substra/substra/pull/378))
- new `Client.logout` function, mirroring `Client.login` ([#381](https://github.com/Substra/substra/pull/381))
- `Client` can now be used within a context manager ([#381](https://github.com/Substra/substra/pull/381))

  ```python
  with Client(
      client_name="org-1",
      backend_type="remote",
      url="http://substra-backend.org-1.com:8000",
      username="org-1",
      password="p@sswr0d44",
  ) as client:
      pass
  ```

### Changed

- change how API responses are parsed to match server changes ([#379](https://github.com/Substra/substra/pull/379))
- `Client` will now terminate the sessions it starts when given username & password ([#381](https://github.com/Substra/substra/pull/381))

### Fixed

- typo in exception ([#377](https://github.com/Substra/substra/pull/377))
- Client.login breaking when Client was instanciated with `insecure=True` ([#384](https://github.com/Substra/substra/pull/384))

## [0.46.0](https://github.com/Substra/substra/releases/tag/0.46.0) - 2023-07-25

### Added

- `wait_task` and `wait_compute_plan` to block execution until execution is over ([#368](https://github.com/Substra/substra/pull/368))
- Configuration file path can be set with env var `SUBSTRA_CLIENTS_CONFIGURATION_FILE_PATH` ([#370](https://github.com/Substra/substra/pull/370))

### Changed

- Remove `model` and `models` for input and output identifiers in tests. Replace by `shared` instead. ([#367](https://github.com/Substra/substra/pull/367))
- Remove pagination on `get_performances` to remove limitation on 1000 first points ([#372](https://github.com/Substra/substra/pull/372))

### Fixed

- Pin `pydantic` to `>=1.9.0` & `<2.0.0` as `pydantic` v `2.0.0` has been released with a lot of non backward compatible changes. ([#371](https://github.com/Substra/substra/pull/371))

## [0.45.0](https://github.com/Substra/substra/releases/tag/0.45.0) - 2023-06-12

### Added

- Concepts `InputAsset` and `OutputAsset` have been introduced, mirroring concept in `substra-backend`([#361](https://github.com/Substra/substra/pull/361))
- Utils to get `input / output assets` for a specific task (`get_task_output_asset`, `list_task_output_assets`, `list_task_input_assets`) ([#361](https://github.com/Substra/substra/pull/361))

### Changed

- `Task`(including `inputs` and `outputs` without linked assets) replace `SummaryTask` ([#361](https://github.com/Substra/substra/pull/361))
- Fix the ordering when filtering on a remote client ([#363](https://github.com/Substra/substra/pull/363))

### Removed

- `SummaryTask` ([#361](https://github.com/Substra/substra/pull/361))

## [0.44.0](https://github.com/Substra/substra/releases/tag/0.44.0) - 2023-05-11

### Added

- Client can now be configured using environment variables or a configuration Yaml file ([#353](https://github.com/Substra/substra/pull/353))

### Changed

- BREAKING: default backend type for Client is now "subprocess" ([#353](https://github.com/Substra/substra/pull/353))
- Add identifier to performance view when calling `client.get_performances` ([#357](https://github.com/Substra/substra/pull/357))

### Removed

- Function name from the Performance model ([#358](https://github.com/Substra/substra/pull/358))
- BREAKING: `substra.cli` module ([#362](https://github.com/Substra/substra/pull/362))
- BREAKING: `Client.from_config_file()`. The recommended way is to use the new config file format or env vars ([#362](https://github.com/Substra/substra/pull/362))

## [0.43.0](https://github.com/Substra/substra/releases/tag/0.43.0) - 2023-03-31

### Added

- Add `SummaryTask` Pydantic validator to match the new API behavior (returning compute tasks without details in list view) ([#350](https://github.com/Substra/substra/pull/350/))

### Changed

- BREAKING: rename Algo to Function ([#341](https://github.com/Substra/substra/pull/341))
- Rename fields in Performances model ([#344](https://github.com/Substra/substra/pull/344))

### Fixed

- Permissions inconsistency in local mode ([#348](https://github.com/Substra/substra/pull/348))

## [0.42.0](https://github.com/Substra/substra/releases/tag/0.42.0) - 2023-02-20

### Added

- Creator field in Compute Plan model (#331)
- Contributing, contributors & code of conduct files (#333)

### Removed

- BREAKING CHANGE: failed task category (#309)
- BREAKING: DataSampleSpec don't have a `test_only` field anymore (#332)

### Changed

- BREAKING: rename tuple to task (#337)

## [0.41.0](https://github.com/Substra/substra/releases/tag/0.41.0) - 2022-12-19

### Changed

- Adapt hybrid mode to pass the rank in a task property argument to match backend behavior (#329)

### Fixed

- Pass the Python Github Actions on ubuntu 20.04 to be compatible with docker rootless mode (#325)

## [0.40.0](https://github.com/Substra/substra/releases/tag/0.40.0) - 2022-11-22

### Changed

- BREAKING CHANGE: replace the tasks `traintuple`, `aggregatetuple`, `predicttuple`, `testtuple`, `composite_traintuple` with a single `task` (#299)

```python
task_key = client.add_task(
    substra.schemas.TaskSpec(
        algo_key=algo_key,
        worker=client.organization_info().organization_id,  # org on which the task is executed
        inputs=[
            {
                'identifier': 'datasamples',
                'asset_key': datasample_key
            },
            {
                'identifier': 'opener',
                'asset_key': dataset_key
            }
        ],
        outputs= {
            'example_output': {
                'permissions': {
                    'public': False,
                    'authorized_ids': ['org1'],
                },
                'is_transient': True,
            }
        }
    )
)

task = client.get_task(task_key)
tasks = client.list_task()

# Compute plan changes
compute_plan = client.add_compute_plan(
    substra.schemas.ComputePlanSpec(
        name = 'my compute plan',
        tasks = [
            schemas.ComputePlanTaskSpec(
                task_id=uuid.uuid4(),
                algo_key=algo_key,
                worker=client.organization_info().organization_id,  # org on which the task is executed
                inputs=[
                    {
                        'identifier': 'datasamples',
                        'asset_key': datasample_key
                    },
                    {
                        'identifier': 'opener',
                        'asset_key': dataset_key
                    }
                ],
                outputs= {
                    'example_output': {
                        'permissions': {
                            'public': False,
                            'authorized_ids': ['org1'],
                        },
                        'is_transient': True,
                    }
                }
            )
        ]
    )
)
```

- Update substratools Docker image name (#316)

### Fixed

- Remove depreciated `pytest-runner` from setup.py (#320)
- link_dataset_with_data_samples return value in remote mode
- Fix the compute plan rank calculation in local mode (#299)
- Windows compatibility on `pathlib` usage for a Docker argument (#317)

### Changed

- Apply changes from algo to function in substratools (#303)
- Register functions in substratools using decorator `@tools.register` (#310)
- Update README image (#318)

## [0.39.0](https://github.com/Substra/substra/releases/tag/0.39.0) - 2022-10-03

### Removed

- BREAKING CHANGE: remove category from substra.schema.AlgoSpec and substra.models.Algo
- Remove '# substra.sdk' from sdk documentation (#315)

### Added

- Prevent use of `__` in asset metadata keys in local mode
- docker: add build logs to container image build exception messages
- At compute plan submission by batch, continue the submission after a timeout error

## [0.38.0](https://github.com/Substra/substra/releases/tag/0.38.0) - 2022-09-26

### Tests

- used openers within the library only exposes `get_data` and `fake_data` methods due to breaking changes within
  substra-tools
- a third argument `task_properties` (containing the `rank` of a task) has been added to all algo methods relying on substra-tools
- substra tools metrics `tools.Metrics` become `tools.MetricAlgo` and `tools.metrics.execute` becomes `tools.algo.execute` (#290)

### Changed

- Algo categories are not checked anymore in local mode. Validations based on inputs and outputs are sufficient.
- BREAKING CHANGE: the backend type is now set in the Client, the env variable `DEBUG_SPAWNER` is not used anymore. Default value is deployed (#287)

API before

```sh
export DEBUG_SPAWNER=subprocess
```

```python
client = substra.Client(debug=True)
```

API after

```python
client = substra.Client(backend_type=substra.BackendType.LOCAL_SUBPROCESS)
```

- Pass substra-tools arguments via a file instead of the command line
- internal change: the metrics algo CLI is the same as the other algos (#290)

### Removed

- BREAKING CHANGE: Model.category field

## [0.37.0](https://github.com/Substra/substra/releases/tag/0.37.0) - 2022-09-19

### Fixed

tests: fix algo inputs and task code consistency

### Changed

- BREAKING CHANGE: `schemas.ComputePlanSpec` `clean_models` property is now removed, the transient property on tasks outputs should be used instead.

## [0.36.0](https://github.com/Substra/substra/releases/tag/0.36.0) - 2022-09-12

### Added

- input multiplicity within the cli in debug mode
- `list_model` to the SDK client

### Removed

- chore: remove the `examples` section, and references to them

### Changed

- BREAKING CHANGE: opener input identifier must be `opener`
- BREAKING CHANGE: datasample input identifier must be `datasamples`
- BREAKING CHANGE: `chainkeys`, `opener` and `datasamples` are forbidden identifier for inputs and outputs
  of kind `artifact` and `performance`
- BREAKING CHANGE: pass the algo method to execute under the `--method-name` argument within the CLI.
  If the interface between substra and the backend is handled via substratools, there are no changes to apply
  within the the `substra` code but algo and metric Dockerfiles should expose a `--method-name` argument in
  the `ENTRYPOINT` (#266)
- test tasks now have an higher rank than their parent train task
- chore: remove close source for CHANGELOG, README and cyclic-example
- chore: rename connect-tools to substra-tools.
- BREAKING CHANGE: remove the shared local folder of the compute plan
- feat: download function of the client return the path of downloaded file.

### Feature

- Local mode: add a check, a task output of type performance must have public permissions

### Fixes

- Filters: Fix the filters on status for compute plans and tasks

This fix also introduces some changes: the value for the filters on status must now be a list (like for other filters, there is a OR condition between elements of the list) and its value must be
`substra.models.ComputePlanStatus.{name of the status}.value` for compute plans and `substra.models.Status.{name of the status}.value` for tasks.

Example:

```python
# Return all the compute plans that are not finished
client.list_compute_plan(filters={'status':[substra.models.ComputePlanStatus.todo.value, substra.models.ComputePlanStatus.waiting.value, substra.models.ComputePlanStatus.doing.value]})

# Return all the composite traintuples with the status "doing"
client.list_composite_traintuple(filters={"status": [substra.models.Status.doing.value]})
```

### Documentation

- Add the filters documentation to the references

## [0.35.0](https://github.com/Substra/substra/releases/tag/0.35.0) - 2022-08-29

### Changed

- chore: change the `metrics` and `algo` definition relying on substra tools. All the methods of those objects now takes `inputs` and `outputs` as arguments; which are `TypedDict`.

## [0.34.0](https://github.com/Substra/substra/releases/tag/0.34.0) - 2022-08-22

### Changed

- BREAKING CHANGE:in local mode, each client has its own `organization_id`. Removed the `DEBUG_OWNER` mechanism.

Instead of:

```python
client = substra.Client(debug=True)
clients = [client] * 2
```

do:

```python
clients = [substra.Client(debug=True) for _ in range(2)]
client1_org_id = clients[0].organization_info().organization_id
```

- The `Client.organization_info` function now returns a model `OrganizationInfo` instead of a dict

## [0.33.0](https://github.com/Substra/substra/releases/tag/0.33.0) - 2022-08-17

### Added

- New update_compute_plan, update_algo and update_dataset methods that allow editing names
- The local mode now uses the inputs/outputs fields to execute the tasks. The other fields are still kept up-to-date
- Support for the `transient` flag on tasks outputs

### Changed

- BREAKING CHANGE: rename `schemas.ComputeTaskOutput` to `schemas.ComputeTaskOutputSpec`

### Removed

- BREAKING CHANGE: remove the chainkey feature

## [0.32.0](https://github.com/Substra/substra/releases/tag/0.32.0) - 2022-08-09

### Added

- BREAKING CHANGE: drop Python 3.7 support
- add `inputs` and `outputs` fields to the Algo model

### Removed

- BREAKING CHANGE CLI: keep only the cancel, profile, login and organization commands

### Changed

- BREAKING CHANGE: Stop using legacy `_permissions` fields

## [0.31.0](https://github.com/Substra/substra/releases/tag/0.31.0) - 2022-08-01

### Added

- "inputs" field to substra.sdk.schemas.\*tupleSpec
- "inputs" field to \*tuple models
- embed models/performances in output fields of tasks

## [0.30.1](https://github.com/Substra/substra/releases/tag/0.30.1) - 2022-07-26

### Fixed

- revert: fix: `get_performances` works again in remote

## [0.30.0](https://github.com/Substra/substra/releases/tag/0.30.0) - 2022-07-25

### Fixed

- fix: `get_performances` works again in remote

### Changed

- feat: change DEFAULT_BATCH_SIZE to 500

### Added

- "outputs" field to substra.sdk.schemas.\*tupleSpec
- feat: add "outputs" field to \*tuple models

### Removed

- BREAKING: "out_trunk_model_permissions" field from substra.sdk.schemas.CompositeTraintupleSpec (superseded by "outputs")

## [0.29.0](https://github.com/Substra/substra/releases/tag/0.29.0) - 2022-07-11

### Added

- feat: support two composite as input of a composite in local mode
- feat: support metadata filters in local mode

### Changed

- BREAKING: convert (test task) to (predict task + test task)

### Fixed

- fix: add mandatory cp name in cyclic strategy example

## [0.28.0](https://github.com/Substra/substra/releases/tag/0.28.0) - 2022-07-05

### Changed

- BREAKING CHANGE: Client.update_compute_plan renamed Client.add_compute_plan_tuples

### Removed

- CLI commands `add`, `get` and `list`
- BREAKING: Removed metrics APIs and types; use algo APIs and types instead

## [0.27.0](https://github.com/Substra/substra/releases/tag/0.27.0) - 2022-06-27

### Changed

- BREAKING: implement filtering and ordering for list methods in SDK

  - Removed filtering syntax `asset::key::value` in SDK and CLI
  - New filtering syntax in SDK `filters={key:["value1", "value2"]}` and ordering possibility:

    ```diff
    - list_***(self, filters=None) -> List[substra.sdk.models.***]
    + list_***(self, filters: dict = None, order_by: str = 'creation_date', ascending: bool = False) -> List[substra.sdk.models.***]
    ```

## [0.26.0](https://github.com/Substra/substra/releases/tag/0.26.0) - 2022-06-20

### Fixed

- fix: get_performance test tuples filter on local dal

## [0.25.0](https://github.com/Substra/substra/releases/tag/0.25.0) - 2022-06-14

### Fixed

- cancel_compute_plan should return nothing

  SDK:

  ```diff
  - cancel_compute_plan(self, key: str) -> substra.sdk.models.ComputePlan
  + cancel_compute_plan(self, key: str) -> None

  - Cancel execution of compute plan, the returned object is described in the [models.ComputePlan](sdk_models.md#ComputePlan) model
  + Cancel execution of compute plan. Nothing is returned by this method
  ```

  CLI:

  ```diff
  substra cancel compute_plan [OPTIONS] COMPUTE_PLAN_KEY
  -  Cancel execution of a compute plan.
  +  Cancel execution of a compute plan. Nothing is printed, you can check again the compute plan status with `substra get compute_plan`.
  ```

### Changes

- BREAKING CHANGE (rename node to organization)
  - SDK: `client.list_node` renamed to `client.list_organization`
  - SDK: `client.node_info` renamed to `client.organization_info`
  - CLI: the command `substra node info` is now `substra organization info`
  - CLI: the command `substra list node` is now `substra list organization`
  - local mode: when using chainkeys, the chainkey file is renamed from `node_name_id.json` to `organization_name_id.json`

## [0.24.0](https://github.com/Substra/substra/releases/tag/0.24.0) - 2022-06-07

### Added

- feat: add predict algo category

### Changes

- BREAKING CHANGE (UpdateComputePlanSpec key field): Use new register tasks endpoint

## [0.23.0](https://github.com/Substra/substra/releases/tag/0.23.0) - 2022-05-31

### Added

- feat: add empty compute plan status

### Changed

- feat: in debug mode, subprocess errors are now caught and raised as `ExecutionError`

## [0.22.0](https://github.com/Substra/substra/releases/tag/0.22.0) - 2022-05-22

### Added

- feat: add round_idx to get_performance()

### Changed

- feat: Add algo named inputs and outputs for existing task in remote mode
- feat: log level set to warning for substra-tools

## [0.21.0](https://github.com/Substra/substra/releases/tag/0.21.0) - 2022-05-16

### Changed

- BREAKING CHANGE: add mandatory name field to compute plan
- doc: update orchestrator compatibility table for the Substra release 0.11.0

### Added

- feat: save performances in live for local mode on a json file

## [0.20.0](https://github.com/Substra/substra/releases/tag/0.20.0) - 2022-05-09

### Changed

- BREAKING CHANGE: use algo spec for metric
- BREAKING CHANGE: Cancel CP returns nothing
- BREAKING CHANGE: the user must give the key of the compute plan when creating a new compute plan

## [0.19.0](https://github.com/Substra/substra/releases/tag/0.19.0) - 2022-05-03

### Added

- feat(sdk): add `get_datasample` method
- feat: add the get_performances(compute_plan.key) function to the client

### Changed

- BREAKING CHANGE: local mode - arguments of each train, test, composite and aggregate task are passed as named inputs and outputs in a json format. Those changes are compatible with substra-tools `0.12.0`.
- Rest client supports default backend pagination, list will automatically fetch all pages
- BREAKING CHANGE: local mode - the format of the asset ids is now `uuid.UUID`, e.g. `3da0075f-360b-446d-902f-af60a38d9594` and not the hex representation.
- update substra-tools version in examples Dockerfiles

## [0.18.0](https://github.com/Substra/substra/releases/tag/0.18.0) - 2022-04-11

### Changed

- Local mode - in a compute plan, the testtuples are executed at the same time as the other tasks instead of after all of them
- Examples now use the substra-tools base Docker image 0.10.0

### Fixed

- Local mode works with data on another disk partition than the one the code is executed on
  - In subprocess mode: the data samples are linked via a symbolic link to a temporary folder
  - In Docker mode: the data samples are copied at the task execution time to a temporary folder
- Be able to use pdb in subprocess mode

## [0.17.0](https://github.com/Substra/substra/releases/tag/0.17.0) - 2022-03-01

### Changed

- Speed and disk space usage improvement as datasamples are not copied to local backend folders anymore
- Documentation: Fix the display of the API reference

### Added

- CLI: Add the `logs` command to display and download the logs of a failed tuple
- SDK: Add the `get_logs` and `download_logs` methods
- doc: add DEBUG_SPAWNER doc
- doc: add `AlgoSpec` to documentation
- SDK: add `get_model` method

### Fixed

- Local mode should not accept test data samples for train tuples

## [0.16.0](https://github.com/Substra/substra/releases/tag/0.16.0) - 2022-01-14

### Changed

- (BREAKING) Add a `logs_permission` field to Dataset schema and model

### Fixed

- CLI: Fix the display of metric key and perfs for 'substra get testtuple'

### Removed

- (BREAKING) Remove the download permissions

## [0.15.0](https://github.com/Substra/substra/releases/tag/0.15.0) - 2022-01-10

### Changed

- (BREAKING) Remove the datasample.validated field as it's deprecated

### Fixed

- CLI: fix the display of the assets in yaml and json format
- No more crash when running a script in local subprocess mode from a path with spaces
- Examples: add dataset logs_permission field

### Added

- Error type to traintuple, testtuple, aggregatetuple and composite_traintuple
- Expose the backend type

## [0.14.0](https://github.com/Substra/substra/releases/tag/0.14.0) - 2021-12-01

### Added

- Cyclic strategy example

### Fixed

- Local mode - the substra specific assets are now saved in `/substra_internal` instead of the work dir
- Fix the display of the composite traintuple if it has no input models
- Properly prevent path traversal in archives and don't allow symbolic links

## [0.13.0](https://github.com/Substra/substra/releases/tag/0.13.0) - 2021-11-02

### Added

- traintuple can take aggregatetuple as in_tuple
- Pretty print for Model and Spec
- Display orchestrator and chaincode versions in node info command
- Accept full datamanager, metrics and parent_tasks objects in get\_\*\_tuple responses
- Add task extra information related to start_date and end_date

### Changed

- Ignore extra fields in API response
- (BREAKING) Replace objective by metric
- (BREAKING) Multiple metrics and performances per test task

### Improvements

- Local mode, execution in Docker: re-use the Docker images so that the execution is faster

## [0.11.0](https://github.com/Substra/substra/releases/tag/0.11.0) - 2021-10-04

### Added

- Display backend version in node info command

### Changed

- Internal: backend now serves paginated lists of asset. Client still returns simple lists as before.
- (BREAKING CHANGE) All algos are now one single object with a category property.
- (BREAKING CHANGE) Various API changes due to the architecture change introduced by the orchestrator.

## [0.10.0](https://github.com/Substra/substra/releases/tag/0.10.0) - 2021-08-05

- [unreleased]: https://github.com/Substra/substra/compare/0.10.0...HEAD
