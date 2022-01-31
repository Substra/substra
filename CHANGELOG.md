# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Speed and disk space usage improvement as datasamples are not copied to local backend folders anymore (#136)

### Added

- CLI: Add the `logs` command to display and download the logs of a failed tuple (#120)
- SDK: Add the `get_logs` and `download_logs` methods (#120)

## [0.16.0] - 2022-01-14

### Changed

- (BREAKING) Add a `logs_permission` field to Dataset schema and model (#122)

### Fixed

- CLI: Fix the display of metric key and perfs for 'substra get testtuple' (#129)

### Removed
- (BREAKING) Remove the download permissions

## [0.15.0] - 2022-01-10

### Changed

- (BREAKING) Remove the datasample.validated field as it's deprecated (#118)

### Fixed

- CLI: fix the display of the assets in yaml and json format (#115 #127)
- No more crash when running a script in local subprocess mode from a path with spaces (#99)
- Examples: add dataset logs_permission field (#130)

### Added

- Error type to traintuple, testtuple, aggregatetuple and composite_traintuple
- Expose the backend type (#119)

## [0.14.0] - 2021-12-01

### Added

- Cyclic strategy example

### Fixed

- Local mode - the substra specific assets are now saved in `/substra_internal` instead of the work dir (#53)
- Fix the display of the composite traintuple if it has no input models
- Properly prevent path traversal in archives and don't allow symbolic links

## [0.13.0] - 2021-11-02

### Added

- traintuple can take aggregatetuple as in_tuple
- Pretty print for Model and Spec
- Display orchestrator and chaincode versions in node info command
- Accept full datamanager, metrics and parent_tasks objects in get_*_tuple responses
- Add task extra information related to start_date and end_date

### Changed

- Ignore extra fields in API response (#84)
- (BREAKING) Replace objective by metric (#45)
- (BREAKING) Multiple metrics and performances per test task (#47)

### Improvements

- Local mode, execution in Docker: re-use the Docker images so that the execution is faster

## [0.11.0] - 2021-10-04

### Added

- Display backend version in node info command

### Changed

- Internal: backend now serves paginated lists of asset. Client still returns simple lists as before.
- [BREAKING CHANGE] All algos are now one single object with a category property.
- [BREAKING CHANGE] Various API changes due to the architecture change introduced by the orchestrator.

## [0.10.0] - 2021-08-05

[Unreleased]: https://github.com/owkin/substra/compare/0.10.0...HEAD
[0.10.0]: https://github.com/owkin/substra/compare/0.9.0...0.10.0
