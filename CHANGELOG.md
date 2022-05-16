# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
