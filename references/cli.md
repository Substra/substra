# Summary

- [substra config](#substra-config)
- [substra login](#substra-login)
- [substra describe](#substra-describe)
- [substra organization info](#substra-organization-info)
- [substra download](#substra-download)
- [substra cancel compute_plan](#substra-cancel-compute_plan)
- [substra update dataset_data_samples_link](#substra-update-dataset_data_samples_link)
- [substra update compute_plan_tuples](#substra-update-compute_plan_tuples)
- [substra logs](#substra-logs)


# Commands

## substra config

```text
Usage: substra config [OPTIONS] URL

  Add profile to config file.

Options:
  --config PATH   Config path (default ~/.substra).
  --profile TEXT  Profile name to add
  -k, --insecure  Do not verify SSL certificates
  --help          Show this message and exit.
```

## substra login

```text
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

## substra describe

```text
Usage: substra describe [OPTIONS] {algo|dataset} ASSET_KEY

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

## substra organization info

```text
Usage: substra organization info [OPTIONS]

  Display organization info.

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

```text
Usage: substra download [OPTIONS] {algo|dataset|model} KEY

  Download asset implementation.

  - algo: the algo and its dependencies
  - dataset: the opener script
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

```text
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
  --help                          Show this message and exit.
```

## substra update dataset_data_samples_link

```text
Usage: substra update dataset_data_samples_link [OPTIONS] DATA_SAMPLES_PATH

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

## substra update compute_plan_tuples

```text
Usage: substra update compute_plan_tuples [OPTIONS] COMPUTE_PLAN_KEY
                                          TUPLES_PATH

  Add tuples to compute plan.

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
  once. If the auto batching is enabled, change the `batch_size` to define the
  number of tuples uploaded in each batch (default 500).

Options:
  -n, --no-auto-batching          Disable the auto batching feature
  -b, --batch-size INTEGER        Batch size for the auto batching  [default:
                                  500]
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

```text
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

