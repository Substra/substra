# Summary

- [substra config](#substra-config)
- [substra login](#substra-login)
- [substra add data_sample](#substra-add-data_sample)
- [substra add dataset](#substra-add-dataset)
- [substra add metric](#substra-add-metric)
- [substra add algo](#substra-add-algo)
- [substra add compute_plan](#substra-add-compute_plan)
- [substra add traintuple](#substra-add-traintuple)
- [substra add aggregatetuple](#substra-add-aggregatetuple)
- [substra add composite_traintuple](#substra-add-composite_traintuple)
- [substra add testtuple](#substra-add-testtuple)
- [substra get](#substra-get)
- [substra list](#substra-list)
- [substra describe](#substra-describe)
- [substra node info](#substra-node-info)
- [substra download](#substra-download)
- [substra cancel compute_plan](#substra-cancel-compute_plan)
- [substra update data_sample](#substra-update-data_sample)
- [substra update compute_plan](#substra-update-compute_plan)
- [substra logs](#substra-logs)


# Commands

## substra config

```
Usage: substra config [OPTIONS] URL

  Add profile to config file.

Options:
  --config PATH   Config path (default ~/.substra).
  --profile TEXT  Profile name to add
  -k, --insecure  Do not verify SSL certificates
  --help          Show this message and exit.
```

## substra login

```
Usage: substra login [OPTIONS]

  Login to the Substra platform.

Options:
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --tokens FILE                   Tokens file path to use (default ~/.substra-
                                  tokens).

  --verbose                       Enable verbose mode.
  -u, --username TEXT
  -p, --password TEXT
  --help                          Show this message and exit.
```

## substra add data_sample

```
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
  --tokens FILE                   Tokens file path to use (default ~/.substra-
                                  tokens).

  --verbose                       Enable verbose mode.
  --timeout INTEGER               Max number of seconds the operation will be
                                  retried for  [default: 300]

  --help                          Show this message and exit.
```

## substra add dataset

```
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
      "metadata": dict,
      "logs_permission": {
          "public": bool,
          "authorized_ids": list[str],
      },
  }

  Where:
  - name: name of the dataset
  - description: path to a markdown file describing the dataset
  - type: short description of the type of data that will be attached to this
    dataset (common values are 'Images', 'Tabular', 'Time series',
    'Spatial time series' and 'Hierarchical images')
  - data_opener: path to the opener python script
  - permissions: define asset access permissions
  - logs_permission: define tuple execution logs access permissions
  (in case of tuple execution failure)

Options:
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --tokens FILE                   Tokens file path to use (default ~/.substra-
                                  tokens).

  --verbose                       Enable verbose mode.
  -o, --output [pretty|yaml|json]
                                  Set output format
                                  - pretty: summarised view
                                  - yaml: full view in YAML format
                                  - json: full view in JSON format
                                  [default: pretty]

  --timeout INTEGER               Max number of seconds the operation will be
                                  retried for  [default: 300]

  --help                          Show this message and exit.
```

## substra add metric

```
Usage: substra add metric [OPTIONS] PATH

  Add metric.

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
  - name: name of the metric
  - description: path to a markdown file describing the metric
  - file: path to tar.gz or zip archive containing the metrics python
    script and its Dockerfile
  - permissions: define asset access permissions

Options:
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --tokens FILE                   Tokens file path to use (default ~/.substra-
                                  tokens).

  --verbose                       Enable verbose mode.
  -o, --output [pretty|yaml|json]
                                  Set output format
                                  - pretty: summarised view
                                  - yaml: full view in YAML format
                                  - json: full view in JSON format
                                  [default: pretty]

  --timeout INTEGER               Max number of seconds the operation will be
                                  retried for  [default: 300]

  --help                          Show this message and exit.
```

## substra add algo

```
Usage: substra add algo [OPTIONS] PATH

  Add algo.

  The path must point to a valid JSON file with the following schema:

  {
      "name": str,
      "category": str,
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
  - category: one of ALGO_SIMPLE, ALGO_COMPOSITE, ALGO_AGGREGATE
  - description: path to a markdown file describing the algo
  - file: path to tar.gz or zip archive containing the algorithm python
    script and its Dockerfile
  - permissions: define asset access permissions

Options:
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --tokens FILE                   Tokens file path to use (default ~/.substra-
                                  tokens).

  --verbose                       Enable verbose mode.
  -o, --output [pretty|yaml|json]
                                  Set output format
                                  - pretty: summarised view
                                  - yaml: full view in YAML format
                                  - json: full view in JSON format
                                  [default: pretty]

  --timeout INTEGER               Max number of seconds the operation will be
                                  retried for  [default: 300]

  --help                          Show this message and exit.
```

## substra add compute_plan

```
Usage: substra add compute_plan [OPTIONS] PATH

  Add compute plan.

  The path must point to a valid JSON file with the following schema:

  {
      "traintuples": list[{
          "algo_key": str,
          "data_manager_key": str,
          "train_data_sample_keys": list[str],
          "traintuple_id": str,
          "in_models_ids": list[str],
          "tag": str,
          "metadata": dict
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
          "metadata": dict
      }]
      "aggregatetuples": list[{
          "aggregatetuple_id": str,
          "algo_key": str,
          "worker": str,
          "in_models_ids": list[str],
          "tag": str,
          "metadata": dict
      }],
      "testtuples": list[{
          "metric_keys": list[str],
          "data_manager_key": str,
          "test_data_sample_keys": list[str],
          "traintuple_id": str,
          "tag": str,
          "metadata": dict
      }],
      "clean_models": bool,
      "tag": str,
      "metadata": dict
  }

  Disable the auto batching to upload all the tuples of the compute plan at
  once. If the auto batching is enabled, change the `batch_size` to define
  the number of tuples uploaded in each batch (default 20).

Options:
  -n, --no-auto-batching          Disable the auto batching feature
  -b, --batch-size INTEGER        Batch size for the auto batching  [default:
                                  20]

  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --tokens FILE                   Tokens file path to use (default ~/.substra-
                                  tokens).

  --verbose                       Enable verbose mode.
  -o, --output [pretty|yaml|json]
                                  Set output format
                                  - pretty: summarised view
                                  - yaml: full view in YAML format
                                  - json: full view in JSON format
                                  [default: pretty]

  --help                          Show this message and exit.
```

## substra add traintuple

```
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
  --tokens FILE                   Tokens file path to use (default ~/.substra-
                                  tokens).

  --verbose                       Enable verbose mode.
  -o, --output [pretty|yaml|json]
                                  Set output format
                                  - pretty: summarised view
                                  - yaml: full view in YAML format
                                  - json: full view in JSON format
                                  [default: pretty]

  --timeout INTEGER               Max number of seconds the operation will be
                                  retried for  [default: 300]

  --metadata-path FILE            Metadata file path
  --help                          Show this message and exit.
```

## substra add aggregatetuple

```
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
  --tokens FILE                   Tokens file path to use (default ~/.substra-
                                  tokens).

  --verbose                       Enable verbose mode.
  -o, --output [pretty|yaml|json]
                                  Set output format
                                  - pretty: summarised view
                                  - yaml: full view in YAML format
                                  - json: full view in JSON format
                                  [default: pretty]

  --timeout INTEGER               Max number of seconds the operation will be
                                  retried for  [default: 300]

  --metadata-path FILE            Metadata file path
  --help                          Show this message and exit.
```

## substra add composite_traintuple

```
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
  --tokens FILE                   Tokens file path to use (default ~/.substra-
                                  tokens).

  --verbose                       Enable verbose mode.
  -o, --output [pretty|yaml|json]
                                  Set output format
                                  - pretty: summarised view
                                  - yaml: full view in YAML format
                                  - json: full view in JSON format
                                  [default: pretty]

  --timeout INTEGER               Max number of seconds the operation will be
                                  retried for  [default: 300]

  --metadata-path FILE            Metadata file path
  --help                          Show this message and exit.
```

## substra add testtuple

```
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
  --metric-key TEXT               [required]
  --dataset-key TEXT
  --traintuple-key TEXT           [required]
  --data-samples-path FILE
  --tag TEXT
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --tokens FILE                   Tokens file path to use (default ~/.substra-
                                  tokens).

  --verbose                       Enable verbose mode.
  -o, --output [pretty|yaml|json]
                                  Set output format
                                  - pretty: summarised view
                                  - yaml: full view in YAML format
                                  - json: full view in JSON format
                                  [default: pretty]

  --timeout INTEGER               Max number of seconds the operation will be
                                  retried for  [default: 300]

  --metadata-path FILE            Metadata file path
  --help                          Show this message and exit.
```

## substra get

```
Usage: substra get [OPTIONS] [algo|compute_plan|dataset|metric|testtuple|train
                   tuple|composite_traintuple|aggregatetuple] ASSET_KEY

  Get asset definition.

Options:
  --expand                        Display associated assets details
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --tokens FILE                   Tokens file path to use (default ~/.substra-
                                  tokens).

  --verbose                       Enable verbose mode.
  -o, --output [pretty|yaml|json]
                                  Set output format
                                  - pretty: summarised view
                                  - yaml: full view in YAML format
                                  - json: full view in JSON format
                                  [default: pretty]

  --help                          Show this message and exit.
```

## substra list

```
Usage: substra list [OPTIONS] [algo|compute_plan|data_sample|dataset|metric|te
                    sttuple|traintuple|composite_traintuple|aggregatetuple|nod
                    e]

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
  --tokens FILE                   Tokens file path to use (default ~/.substra-
                                  tokens).

  --verbose                       Enable verbose mode.
  -o, --output [pretty|yaml|json]
                                  Set output format
                                  - pretty: summarised view
                                  - yaml: full view in YAML format
                                  - json: full view in JSON format
                                  [default: pretty]

  --help                          Show this message and exit.
```

## substra describe

```
Usage: substra describe [OPTIONS] [algo|dataset|metric] ASSET_KEY

  Display asset description.

Options:
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --tokens FILE                   Tokens file path to use (default ~/.substra-
                                  tokens).

  --verbose                       Enable verbose mode.
  --help                          Show this message and exit.
```

## substra node info

```
Usage: substra node info [OPTIONS]

  Display node info.

Options:
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --tokens FILE                   Tokens file path to use (default ~/.substra-
                                  tokens).

  --verbose                       Enable verbose mode.
  -o, --output [pretty|yaml|json]
                                  Set output format
                                  - pretty: summarised view
                                  - yaml: full view in YAML format
                                  - json: full view in JSON format
                                  [default: pretty]

  --help                          Show this message and exit.
```

## substra download

```
Usage: substra download [OPTIONS] [algo|dataset|metric|model] KEY

  Download asset implementation.

  - algo: the algo and its dependencies
  - dataset: the opener script
  - metric: the metrics and its dependencies
  - model: the output model

Options:
  --folder PATH                   destination folder
  --from-traintuple               (model download only) if this option is set,
                                  the KEY argument refers to a traintuple key

  --from-aggregatetuple           (model download only) if this option is set,
                                  the KEY argument refers to an aggregatetuple
                                  key

  --from-composite-head           (model download only) if this option is set,
                                  the KEY argument refers to a composite
                                  traintuple key

  --from-composite-trunk          (model download only) if this option is set,
                                  the KEY argument refers to a composite
                                  traintuple key

  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --tokens FILE                   Tokens file path to use (default ~/.substra-
                                  tokens).

  --verbose                       Enable verbose mode.
  --help                          Show this message and exit.
```

## substra cancel compute_plan

```
Usage: substra cancel compute_plan [OPTIONS] COMPUTE_PLAN_KEY

  Cancel execution of a compute plan.

Options:
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --tokens FILE                   Tokens file path to use (default ~/.substra-
                                  tokens).

  --verbose                       Enable verbose mode.
  -o, --output [pretty|yaml|json]
                                  Set output format
                                  - pretty: summarised view
                                  - yaml: full view in YAML format
                                  - json: full view in JSON format
                                  [default: pretty]

  --help                          Show this message and exit.
```

## substra update data_sample

```
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
  --tokens FILE                   Tokens file path to use (default ~/.substra-
                                  tokens).

  --verbose                       Enable verbose mode.
  --help                          Show this message and exit.
```

## substra update compute_plan

```
Usage: substra update compute_plan [OPTIONS] COMPUTE_PLAN_KEY TUPLES_PATH

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
          "metadata": dict,
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
          "metadata": dict,
      }]
      "aggregatetuples": list[{
          "aggregatetuple_id": str,
          "algo_key": str,
          "worker": str,
          "in_models_ids": list[str],
          "tag": str,
          "metadata": dict,
      }],
      "testtuples": list[{
          "metric_keys": list[str],
          "data_manager_key": str,
          "test_data_sample_keys": list[str],
          "traintuple_id": str,
          "tag": str,
          "metadata": dict,
      }]
  }

  Disable the auto batching to upload all the tuples of the compute plan at
  once. If the auto batching is enabled, change the `batch_size` to define
  the number of tuples uploaded in each batch (default 20).

Options:
  -n, --no-auto-batching          Disable the auto batching feature
  -b, --batch-size INTEGER        Batch size for the auto batching  [default:
                                  20]

  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --tokens FILE                   Tokens file path to use (default ~/.substra-
                                  tokens).

  --verbose                       Enable verbose mode.
  -o, --output [pretty|yaml|json]
                                  Set output format
                                  - pretty: summarised view
                                  - yaml: full view in YAML format
                                  - json: full view in JSON format
                                  [default: pretty]

  --help                          Show this message and exit.
```

## substra logs

```
Usage: substra logs [OPTIONS] TUPLE_KEY

  Display or download the logs of a failed tuple.

  When an output directory is set, the logs are saved in the directory to a
  file named 'tuple_logs_{tuple_key}.txt'. Otherwise, the logs are outputted
  to stdout.

  Logs are only available for tuples that experienced an execution failure.
  Attempting to retrieve logs for tuples in any other states or for non-
  existing tuples will result in an error.

Options:
  -o, --output-dir DIRECTORY      The directory the logs must be downloaded
                                  to. If not set, the logs are outputted to
                                  stdout.

  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Enable logging and set log level
  --config PATH                   Config path (default ~/.substra).
  --profile TEXT                  Profile name to use.
  --tokens FILE                   Tokens file path to use (default ~/.substra-
                                  tokens).

  --verbose                       Enable verbose mode.
  --help                          Show this message and exit.
```
