# Summary

- [substra config](#substra-config)
- [substra login](#substra-login)
- [substra add data_sample](#substra-add-data_sample)
- [substra add dataset](#substra-add-dataset)
- [substra add objective](#substra-add-objective)
- [substra add algo](#substra-add-algo)
- [substra add compute_plan](#substra-add-compute_plan)
- [substra add aggregate_algo](#substra-add-aggregate_algo)
- [substra add composite_algo](#substra-add-composite_algo)
- [substra add traintuple](#substra-add-traintuple)
- [substra add aggregatetuple](#substra-add-aggregatetuple)
- [substra add composite_traintuple](#substra-add-composite_traintuple)
- [substra add testtuple](#substra-add-testtuple)
- [substra get](#substra-get)
- [substra list](#substra-list)
- [substra describe](#substra-describe)
- [substra download](#substra-download)
- [substra leaderboard](#substra-leaderboard)
- [substra run-local](#substra-run-local)
- [substra cancel compute_plan](#substra-cancel-compute_plan)
- [substra update data_sample](#substra-update-data_sample)
- [substra update dataset](#substra-update-dataset)
- [substra update compute_plan](#substra-update-compute_plan)


# Commands

## substra config

```bash
Usage: substra config [OPTIONS] URL

  Add profile to config file.

Options:
  --config PATH        Config path (default ~/.substra).
  --profile TEXT       Profile name to add
  -k, --insecure       Do not verify SSL certificates
  -v, --version TEXT
  -u, --username TEXT  [required]
  -p, --password TEXT  [required]
  --help               Show this message and exit.
```

## substra login

```bash
Usage: substra login [OPTIONS]

  Login to the Substra platform.

Options:
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --user FILE                     User file path to use (default ~/.substra-
                                  user).

  --verbose                       Enable verbose mode.
  --help                          Show this message and exit.
```

## substra add data_sample

```bash
Usage: substra add data_sample [OPTIONS] PATH

  Add data sample(s).

  The path is either a directory representing a data sample or a parent
  directory containing data samples directories (if --multiple option is
  set).

Options:
  --dataset-key TEXT              [required]
  --local / --remote              Data sample(s) location.
  --multiple                      Add multiple data samples at once.
  --test-only                     Data sample(s) used as test data only.
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --user FILE                     User file path to use (default ~/.substra-
                                  user).

  --verbose                       Enable verbose mode.
  --help                          Show this message and exit.
```

## substra add dataset

```bash
Usage: substra add dataset [OPTIONS] PATH

  Add dataset.

  The path must point to a valid JSON file with the following schema:

  {
      "name": str,
      "description": path,
      "type": str,
      "data_opener": path,
      "permissions": {
          "public": bool,
          "authorized_ids": list[str],
      },
      "metadata": dict
  }

  Where:
  - name: name of the dataset
  - description: path to a markdown file describing the dataset
  - type: short description of the type of data that will be attached to this
    dataset (common values are 'Images', 'Tabular', 'Time series',
    'Spatial time series' and 'Hierarchical images')
  - data_opener: path to the opener python script
  - permissions: define asset access permissions

Options:
  --objective-key TEXT
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --user FILE                     User file path to use (default ~/.substra-
                                  user).

  --verbose                       Enable verbose mode.
  -o, --output [pretty|yaml|json]
                                  Set output format  [default: pretty]
  --help                          Show this message and exit.
```

## substra add objective

```bash
Usage: substra add objective [OPTIONS] PATH

  Add objective.

  The path must point to a valid JSON file with the following schema:

  {
      "name": str,
      "description": path,
      "metrics_name": str,
      "metrics": path,
      "permissions": {
          "public": bool,
          "authorized_ids": list[str],
      },
      "metadata": dict
  }

  Where:
  - name: name of the objective
  - description: path to a markdown file describing the objective
  - metrics_name: name of the metrics
  - metrics: path to tar.gz or zip archive containing the metrics python
    script and its Dockerfile
  - permissions: define asset access permissions

  The option --data-samples-path must point to a valid JSON file with the
  following schema:

  {
      "keys": list[str],
  }

  Where:
  - keys: list of test only data sample keys

Options:
  --dataset-key TEXT
  --data-samples-path FILE        Test data samples.
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --user FILE                     User file path to use (default ~/.substra-
                                  user).

  --verbose                       Enable verbose mode.
  -o, --output [pretty|yaml|json]
                                  Set output format  [default: pretty]
  --help                          Show this message and exit.
```

## substra add algo

```bash
Usage: substra add algo [OPTIONS] PATH

  Add algo.

  The path must point to a valid JSON file with the following schema:

  {
      "name": str,
      "description": path,
      "file": path,
      "permissions": {
          "public": bool,
          "authorized_ids": list[str],
      },
      "metadata": dict
  }

  Where:
  - name: name of the algorithm
  - description: path to a markdown file describing the algo
  - file: path to tar.gz or zip archive containing the algorithm python
    script and its Dockerfile
  - permissions: define asset access permissions

Options:
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --user FILE                     User file path to use (default ~/.substra-
                                  user).

  --verbose                       Enable verbose mode.
  -o, --output [pretty|yaml|json]
                                  Set output format  [default: pretty]
  --help                          Show this message and exit.
```

## substra add compute_plan

```bash
Usage: substra add compute_plan [OPTIONS] TUPLES_PATH

  Add compute plan.

  The tuples path must point to a valid JSON file with the following schema:

  {
      "traintuples": list[{
          "algo_key": str,
          "data_manager_key": str,
          "train_data_sample_keys": list[str],
          "traintuple_id": str,
          "in_models_ids": list[str],
          "tag": str,
      }],
      "composite_traintuples": list[{
          "composite_traintuple_id": str,
          "algo_key": str,
          "data_manager_key": str,
          "train_data_sample_keys": list[str],
          "in_head_model_id": str,
          "in_trunk_model_id": str,
          "out_trunk_model_permissions": {
              "authorized_ids": list[str],
          },
          "tag": str,
      }]
      "aggregatetuples": list[{
          "aggregatetuple_id": str,
          "algo_key": str,
          "worker": str,
          "in_models_ids": list[str],
          "tag": str,
      }],
      "testtuples": list[{
          "objective_key": str,
          "data_manager_key": str,
          "test_data_sample_keys": list[str],
          "traintuple_id": str,
          "tag": str,
      }]
  }

Options:
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --user FILE                     User file path to use (default ~/.substra-
                                  user).

  --verbose                       Enable verbose mode.
  -o, --output [pretty|yaml|json]
                                  Set output format  [default: pretty]
  --help                          Show this message and exit.
```

## substra add aggregate_algo

```bash
Usage: substra add aggregate_algo [OPTIONS] PATH

  Add aggregate algo.

  The path must point to a valid JSON file with the following schema:

  {
      "name": str,
      "description": path,
      "file": path,
      "permissions": {
          "public": bool,
          "authorized_ids": list[str],
      },
      "metadata": dict
  }

  Where:
  - name: name of the algorithm
  - description: path to a markdown file describing the algo
  - file: path to tar.gz or zip archive containing the algorithm python
    script and its Dockerfile
  - permissions: define asset access permissions

Options:
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --user FILE                     User file path to use (default ~/.substra-
                                  user).

  --verbose                       Enable verbose mode.
  -o, --output [pretty|yaml|json]
                                  Set output format  [default: pretty]
  --help                          Show this message and exit.
```

## substra add composite_algo

```bash
Usage: substra add composite_algo [OPTIONS] PATH

  Add composite algo.

  The path must point to a valid JSON file with the following schema:

  {
      "name": str,
      "description": path,
      "file": path,
      "permissions": {
          "public": bool,
          "authorized_ids": list[str],
      },
      "metadata": dict
  }

  Where:
  - name: name of the algorithm
  - description: path to a markdown file describing the algo
  - file: path to tar.gz or zip archive containing the algorithm python
    script and its Dockerfile
  - permissions: define asset access permissions

Options:
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --user FILE                     User file path to use (default ~/.substra-
                                  user).

  --verbose                       Enable verbose mode.
  -o, --output [pretty|yaml|json]
                                  Set output format  [default: pretty]
  --help                          Show this message and exit.
```

## substra add traintuple

```bash
Usage: substra add traintuple [OPTIONS]

  Add traintuple.

  The option --data-samples-path must point to a valid JSON file with the
  following schema:

  {
      "keys": list[str],
  }

  Where:
  - keys: list of data sample keys

Options:
  --algo-key TEXT                 [required]
  --dataset-key TEXT              [required]
  --data-samples-path FILE        [required]
  --in-model-key TEXT             In model traintuple key.
  --tag TEXT
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --user FILE                     User file path to use (default ~/.substra-
                                  user).

  --verbose                       Enable verbose mode.
  -o, --output [pretty|yaml|json]
                                  Set output format  [default: pretty]
  --metadata-path FILE            Metadata file path
  --help                          Show this message and exit.
```

## substra add aggregatetuple

```bash
Usage: substra add aggregatetuple [OPTIONS]

  Add aggregatetuple.

Options:
  --algo-key TEXT                 Aggregate algo key.  [required]
  --in-model-key TEXT             In model traintuple key.
  --worker TEXT                   Node ID for worker execution.  [required]
  --rank INTEGER
  --tag TEXT
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --user FILE                     User file path to use (default ~/.substra-
                                  user).

  --verbose                       Enable verbose mode.
  -o, --output [pretty|yaml|json]
                                  Set output format  [default: pretty]
  --metadata-path FILE            Metadata file path
  --help                          Show this message and exit.
```

## substra add composite_traintuple

```bash
Usage: substra add composite_traintuple [OPTIONS]

  Add composite traintuple.

  The option --data-samples-path must point to a valid JSON file with the
  following schema:

  {
      "keys": list[str],
  }

  Where:
  - keys: list of data sample keys

  The option --out-trunk-model-permissions-path must point to a valid JSON
  file with the following schema:

  {
      "authorized_ids": list[str],
  }

Options:
  --algo-key TEXT                 [required]
  --dataset-key TEXT              [required]
  --data-samples-path FILE        [required]
  --head-model-key TEXT           Must be used with --trunk-model-key option.
  --trunk-model-key TEXT          Must be used with --head-model-key option.
  --out-trunk-model-permissions-path FILE
                                  Load a permissions file.
  --tag TEXT
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --user FILE                     User file path to use (default ~/.substra-
                                  user).

  --verbose                       Enable verbose mode.
  -o, --output [pretty|yaml|json]
                                  Set output format  [default: pretty]
  --metadata-path FILE            Metadata file path
  --help                          Show this message and exit.
```

## substra add testtuple

```bash
Usage: substra add testtuple [OPTIONS]

  Add testtuple.

  The option --data-samples-path must point to a valid JSON file with the
  following schema:

  {
      "keys": list[str],
  }

  Where:
  - keys: list of data sample keys

Options:
  --objective-key TEXT            [required]
  --dataset-key TEXT
  --traintuple-key TEXT           [required]
  --data-samples-path FILE
  --tag TEXT
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --user FILE                     User file path to use (default ~/.substra-
                                  user).

  --verbose                       Enable verbose mode.
  -o, --output [pretty|yaml|json]
                                  Set output format  [default: pretty]
  --metadata-path FILE            Metadata file path
  --help                          Show this message and exit.
```

## substra get

```bash
Usage: substra get [OPTIONS] [algo|compute_plan|composite_algo|aggregate_algo|
                   dataset|objective|testtuple|traintuple|composite_traintuple
                   |aggregatetuple] ASSET_KEY

  Get asset definition.

Options:
  --expand                        Display associated assets details
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --user FILE                     User file path to use (default ~/.substra-
                                  user).

  --verbose                       Enable verbose mode.
  -o, --output [pretty|yaml|json]
                                  Set output format  [default: pretty]
  --help                          Show this message and exit.
```

## substra list

```bash
Usage: substra list [OPTIONS] [algo|compute_plan|composite_algo|aggregate_algo
                    |data_sample|dataset|objective|testtuple|traintuple|compos
                    ite_traintuple|aggregatetuple|node]

  List assets.

Options:
  -f, --filter TEXT               Only display assets that exactly match this
                                  filter. Valid syntax is:
                                  <asset>:<property>:<value>

  --and                           Combine filters using logical ANDs
  --or                            Combine filters using logical ORs
  --advanced-filters TEXT         Filter results using a complex search (must
                                  be a JSON array of valid filters).
                                  Incompatible with the --filter option

  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --user FILE                     User file path to use (default ~/.substra-
                                  user).

  --verbose                       Enable verbose mode.
  -o, --output [pretty|yaml|json]
                                  Set output format  [default: pretty]
  --help                          Show this message and exit.
```

## substra describe

```bash
Usage: substra describe [OPTIONS]
                        [algo|composite_algo|aggregate_algo|dataset|objective]
                        ASSET_KEY

  Display asset description.

Options:
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --user FILE                     User file path to use (default ~/.substra-
                                  user).

  --verbose                       Enable verbose mode.
  --help                          Show this message and exit.
```

## substra download

```bash
Usage: substra download [OPTIONS]
                        [algo|composite_algo|aggregate_algo|dataset|objective]
                        KEY

  Download asset implementation.

  - algo: the algo and its dependencies
  - dataset: the opener script
  - objective: the metrics and its dependencies

Options:
  --folder PATH                   destination folder
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --user FILE                     User file path to use (default ~/.substra-
                                  user).

  --verbose                       Enable verbose mode.
  --help                          Show this message and exit.
```

## substra leaderboard

```bash
Usage: substra leaderboard [OPTIONS] OBJECTIVE_KEY

  Display objective leaderboard

Options:
  --expand                        Display associated assets details
  --sort [asc|desc]               Sort models by highest to lowest perf or
                                  vice versa  [default: desc]

  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --user FILE                     User file path to use (default ~/.substra-
                                  user).

  --verbose                       Enable verbose mode.
  -o, --output [pretty|yaml|json]
                                  Set output format  [default: pretty]
  --help                          Show this message and exit.
```

## substra run-local

```bash
Usage: substra run-local [OPTIONS] ALGO

  Run local.

  Train and test the algo located in ALGO (directory or archive) locally.

  This command can be used to check that objective, dataset and algo assets
  implementations are compatible.

  It will execute sequentially 3 tasks in docker:

  - train algo using train data samples
  - test model using test data samples
  - get model perf

  It will create several output files:
  - sandbox/model/model
  - sandbox/pred_test/perf.json
  - sandbox/pred_test/pred

Options:
  --train-opener FILE             opener.py file to use during training.
                                  [required]

  --test-opener FILE              opener.py file to use during testing.
                                  [required]

  --metrics PATH                  metrics directory or archive to use during
                                  both training and testing.  [required]

  --rank INTEGER                  will be passed to the algo during training.
  --train-data-samples DIRECTORY  directory of data samples directories to use
                                  during training.

  --test-data-samples DIRECTORY   directory of data samples directories to use
                                  during testing.

  --inmodel FILE                  model to use as input during training.
  --fake-data-samples             use fake data samples during both training
                                  and testing.

  --help                          Show this message and exit.
```

## substra cancel compute_plan

```bash
Usage: substra cancel compute_plan [OPTIONS] COMPUTE_PLAN_ID

  Cancel execution of a compute plan.

Options:
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --user FILE                     User file path to use (default ~/.substra-
                                  user).

  --verbose                       Enable verbose mode.
  -o, --output [pretty|yaml|json]
                                  Set output format  [default: pretty]
  --help                          Show this message and exit.
```

## substra update data_sample

```bash
Usage: substra update data_sample [OPTIONS] DATA_SAMPLES_PATH

  Link data samples with dataset.

  The data samples path must point to a valid JSON file with the following
  schema:

  {
      "keys": list[str],
  }

  Where:
  - keys: list of data sample keys

Options:
  --dataset-key TEXT              [required]
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --user FILE                     User file path to use (default ~/.substra-
                                  user).

  --verbose                       Enable verbose mode.
  --help                          Show this message and exit.
```

## substra update dataset

```bash
Usage: substra update dataset [OPTIONS] DATASET_KEY OBJECTIVE_KEY

  Link dataset with objective.

Options:
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --user FILE                     User file path to use (default ~/.substra-
                                  user).

  --verbose                       Enable verbose mode.
  --help                          Show this message and exit.
```

## substra update compute_plan

```bash
Usage: substra update compute_plan [OPTIONS] COMPUTE_PLAN_ID TUPLES_PATH

  Update compute plan.

  The tuples path must point to a valid JSON file with the following schema:

  {
      "traintuples": list[{
          "algo_key": str,
          "data_manager_key": str,
          "train_data_sample_keys": list[str],
          "traintuple_id": str,
          "in_models_ids": list[str],
          "tag": str,
      }],
      "composite_traintuples": list[{
          "composite_traintuple_id": str,
          "algo_key": str,
          "data_manager_key": str,
          "train_data_sample_keys": list[str],
          "in_head_model_id": str,
          "in_trunk_model_id": str,
          "out_trunk_model_permissions": {
              "authorized_ids": list[str],
          },
          "tag": str,
      }]
      "aggregatetuples": list[{
          "aggregatetuple_id": str,
          "algo_key": str,
          "worker": str,
          "in_models_ids": list[str],
          "tag": str,
      }],
      "testtuples": list[{
          "objective_key": str,
          "data_manager_key": str,
          "test_data_sample_keys": list[str],
          "traintuple_id": str,
          "tag": str,
      }]
  }

Options:
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --user FILE                     User file path to use (default ~/.substra-
                                  user).

  --verbose                       Enable verbose mode.
  -o, --output [pretty|yaml|json]
                                  Set output format  [default: pretty]
  --help                          Show this message and exit.
```

