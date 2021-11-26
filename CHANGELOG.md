# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

### Added

### Changed

### Improvements

### Fixed
- Properly prevent path traversal in archives and don't allow symbolic links

## [0.12.0mdy] - 2021-10-25

### Added
- Display orchestrator and chaincode versions in node info command

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
