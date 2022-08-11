# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- New update_compute_plan, update_algo and update_dataset methods that allow editing names
- The local mode now uses the inputs/outputs fields to execute the tasks. The other fields are still kept up-to-date

## [0.32.0](https://github.com/owkin/substra/releases/tag/0.32.0) - 2022-08-09

### Added

- BREAKING CHANGE: drop Python 3.7 support (#246)
- add `inputs` and `outputs` fields to the Algo model (#245)

### Removed

- BREAKING CHANGE CLI: keep only the cancel, profile, login and organization commands

### Changed

- BREAKING CHANGE: Stop using legacy `_permissions` fields (#242)

## [0.31.0](https://github.com/owkin/substra/releases/tag/0.31.0) - 2022-08-01

### Added

- "inputs" field to substra.sdk.schemas.\*tupleSpec (#215)
- "inputs" field to \*tuple models (#239)
- embed models/performances in output fields of tasks (#251)

## [0.30.1](https://github.com/owkin/substra/releases/tag/0.30.1) - 2022-07-26

### Fixed

- revert: fix: `get_performances` works again in remote (#240)

## [0.30.0](https://github.com/owkin/substra/releases/tag/0.30.0) - 2022-07-25

### Fixed

- fix: `get_performances` works again in remote (#236)

### Changed

- feat: change DEFAULT_BATCH_SIZE to 500 (#226)

### Added

- "outputs" field to substra.sdk.schemas.*tupleSpec (#219)
- feat: add "outputs" field to *tuple models (#235)

### Removed

- BREAKING: "out_trunk_model_permissions" field from substra.sdk.schemas.CompositeTraintupleSpec (superseded by "outputs") (#219)

## [0.29.0](https://github.com/owkin/substra/releases/tag/0.29.0) - 2022-07-11

### Added

- feat: support two composite as input of a composite in local mode (#232)
- feat: support metadata filters in local mode (#218)

### Changed

- BREAKING: convert (test task) to (predict task + test task) (#202)

### Fixed

- fix: add mandatory cp name in cyclic strategy example (#216)

## [0.28.0](https://github.com/owkin/substra/releases/tag/0.28.0) - 2022-07-05

### Changed

- BREAKING CHANGE: Client.update_compute_plan renamed Client.add_compute_plan_tuples (#223)

### Removed

- CLI commands `add`, `get` and `list` (#224)
- BREAKING: Removed metrics APIs and types; use algo APIs and types instead (#210)

## [0.27.0](https://github.com/owkin/substra/releases/tag/0.27.0) - 2022-06-27

### Changed

- BREAKING: implement filtering and ordering for list methods in SDK (#187)

  - Removed filtering syntax `asset::key::value` in SDK and CLI
  - New filtering syntax in SDK `filters={key:["value1", "value2"]}` and ordering possibility:

    ```diff
    - list_***(self, filters=None) -> List[substra.sdk.models.***]
    + list_***(self, filters: dict = None, order_by: str = 'creation_date', ascending: bool = False) -> List[substra.sdk.models.***]
    ```

## [0.26.0](https://github.com/owkin/substra/releases/tag/0.26.0) - 2022-06-20

### Fixed

- fix: get_performance test tuples filter on local dal (#209)

## [0.25.0](https://github.com/owkin/substra/releases/tag/0.25.0) - 2022-06-14

### Fixed

- cancel_compute_plan should return nothing (#193)

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

- BREAKING CHANGE (rename node to organization) (#204):
  - SDK: `client.list_node` renamed to `client.list_organization`
  - SDK: `client.node_info` renamed to `client.organization_info`
  - CLI: the command `substra node info` is now `substra organization info`
  - CLI: the command `substra list node` is now `substra list organization`
  - local mode: when using chainkeys, the chainkey file is renamed from `node_name_id.json` to `organization_name_id.json`

## [0.24.0](https://github.com/owkin/substra/releases/tag/0.24.0) - 2022-06-07

### Added

- feat: add predict algo category (#201)

### Changes

- BREAKING CHANGE (UpdateComputePlanSpec key field): Use new register tasks endpoint (#196)

## [0.23.0](https://github.com/owkin/substra/releases/tag/0.23.0) - 2022-05-31

### Added

- feat: add empty compute plan status (#190)

### Changed

- feat: in debug mode, subprocess errors are now caught and raised as `ExecutionError` (#198)

## [0.22.0](https://github.com/owkin/substra/releases/tag/0.22.0) - 2022-05-22

### Added

- feat: add round_idx to get_performance() (#192)

### Changed

- feat: Add algo named inputs and outputs for existing task in remote mode (#191)
- feat: log level set to warning for connect-tools (#185)

## [0.21.0](https://github.com/owkin/substra/releases/tag/0.21.0) - 2022-05-16

### Changed

- BREAKING CHANGE: add mandatory name field to compute plan (#180)
- doc: update orchestrator compatibility table for the Connect release 0.11.0 (#184)

### Added

- feat: save performances in live for local mode on a json file (#178)

## [0.20.0](https://github.com/owkin/substra/releases/tag/0.20.0) - 2022-05-09

### Changed

- BREAKING CHANGE: use algo spec for metric (#164)
- BREAKING CHANGE: Cancel CP returns nothing (#177)
- BREAKING CHANGE: the user must give the key of the compute plan when creating a new compute plan (#173)

## [0.19.0](https://github.com/owkin/substra/releases/tag/0.19.0) - 2022-05-03

### Added

- feat(sdk): add `get_datasample` method (#171)
- feat: add the get_performances(compute_plan.key) function to the client (#156)

### Changed

- BREAKING CHANGE: local mode - arguments of each train, test, composite and aggregate task are passed as named inputs and outputs in a json format. Those changes are compatible with connect-tools `0.12.0`.
- Rest client supports default backend pagination, list will automatically fetch all pages (#154)
- BREAKING CHANGE: local mode - the format of the asset ids is now `uuid.UUID`, e.g. `3da0075f-360b-446d-902f-af60a38d9594` and not the hex representation.
- update connect-tools version in examples Dockerfiles (#174)

## [0.18.0](https://github.com/owkin/substra/releases/tag/0.18.0) - 2022-04-11

### Changed

- Local mode - in a compute plan, the testtuples are executed at the same time as the other tasks instead of after all of them (#150)
- Examples now use the connect-tools base Docker image 0.10.0 (#148)

### Fixed

- Local mode works with data on another disk partition than the one the code is executed on (#149)
  - In subprocess mode: the data samples are linked via a symbolic link to a temporary folder
  - In Docker mode: the data samples are copied at the task execution time to a temporary folder
- Be able to use pdb in subprocess mode (#137)

## [0.17.0](https://github.com/owkin/substra/releases/tag/0.17.0) - 2022-03-01

### Changed

- Speed and disk space usage improvement as datasamples are not copied to local backend folders anymore (#136)
- Documentation: Fix the display of the API reference (#144)

### Added

- CLI: Add the `logs` command to display and download the logs of a failed tuple (#120)
- SDK: Add the `get_logs` and `download_logs` methods (#120)
- doc: add DEBUG_SPAWNER doc (#140)
- doc: add `AlgoSpec` to documentation (#145)
- SDK: add `get_model` method

### Fixed

- Local mode should not accept test data samples for train tuples (#124)

## [0.16.0](https://github.com/owkin/substra/releases/tag/0.16.0) - 2022-01-14

### Changed

- (BREAKING) Add a `logs_permission` field to Dataset schema and model (#122)

### Fixed

- CLI: Fix the display of metric key and perfs for 'substra get testtuple' (#129)

### Removed

- (BREAKING) Remove the download permissions

## [0.15.0](https://github.com/owkin/substra/releases/tag/0.15.0) - 2022-01-10

### Changed

- (BREAKING) Remove the datasample.validated field as it's deprecated (#118)

### Fixed

- CLI: fix the display of the assets in yaml and json format (#115 #127)
- No more crash when running a script in local subprocess mode from a path with spaces (#99)
- Examples: add dataset logs_permission field (#130)

### Added

- Error type to traintuple, testtuple, aggregatetuple and composite_traintuple
- Expose the backend type (#119)

## [0.14.0](https://github.com/owkin/substra/releases/tag/0.14.0) - 2021-12-01

### Added

- Cyclic strategy example

### Fixed

- Local mode - the substra specific assets are now saved in `/substra_internal` instead of the work dir (#53)
- Fix the display of the composite traintuple if it has no input models
- Properly prevent path traversal in archives and don't allow symbolic links

## [0.13.0](https://github.com/owkin/substra/releases/tag/0.13.0) - 2021-11-02

### Added

- traintuple can take aggregatetuple as in_tuple
- Pretty print for Model and Spec
- Display orchestrator and chaincode versions in node info command
- Accept full datamanager, metrics and parent_tasks objects in get\_\*\_tuple responses
- Add task extra information related to start_date and end_date

### Changed

- Ignore extra fields in API response (#84)
- (BREAKING) Replace objective by metric (#45)
- (BREAKING) Multiple metrics and performances per test task (#47)

### Improvements

- Local mode, execution in Docker: re-use the Docker images so that the execution is faster

## [0.11.0](https://github.com/owkin/substra/releases/tag/0.11.0) - 2021-10-04

### Added

- Display backend version in node info command

### Changed

- Internal: backend now serves paginated lists of asset. Client still returns simple lists as before.
- (BREAKING CHANGE) All algos are now one single object with a category property.
- (BREAKING CHANGE) Various API changes due to the architecture change introduced by the orchestrator.

## [0.10.0](https://github.com/owkin/substra/releases/tag/0.10.0) - 2021-08-05

[0.10.0]: https://github.com/owkin/substra/compare/0.9.0...0.10.0
[unreleased]: https://github.com/owkin/substra/compare/0.10.0...HEAD
