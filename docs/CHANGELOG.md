# Changelog

This changelog records changes that are apparent to the user. Changes with no intended impact on input or output are to be recorded in the changelogs of other repositories.

## [Unreleased]

This release bundles the API v0.0.4 and the CLI v1.2.2

### Added
* [API] Added validation on the `dataset_keys` property
* [API] Added pkhash in error message when adding a traintuple or testtuple that already exists
* [API] Add validation on algo and data archives: make sure they are archives and contain the required files
* [CLI] Added missing bulk_update command

### Changed
* [API] Fixed filtering on `list` commands
* [API & CLI] Remove incorrect `list data` command and endpoint
* [CLI] Fixed flattening of non-nested lists and error messages

## 2019-02-28

Changes prior to this version were not recorded.
