# Summary

- [substra config](#substra-config)
- [substra add data_sample](#substra-add-data_sample)
- [substra add dataset](#substra-add-dataset)
- [substra add objective](#substra-add-objective)
- [substra add algo](#substra-add-algo)
- [substra add traintuple](#substra-add-traintuple)
- [substra add testtuple](#substra-add-testtuple)
- [substra get](#substra-get)
- [substra list](#substra-list)
- [substra describe](#substra-describe)
- [substra download](#substra-download)
- [substra leaderboard](#substra-leaderboard)
- [substra run-local](#substra-run-local)
- [substra update data_sample](#substra-update-data_sample)
- [substra update dataset](#substra-update-dataset)


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
  -u, --user TEXT
  -p, --password TEXT
  --help               Show this message and exit.
```

## substra add data_sample

```bash
Usage: substra add data_sample [OPTIONS] PATH

  Add data sample(s).

  The path is either a directory representing a data sample or a parent
  directory containing data samples directories (if --multiple option is
  set).

Options:
  --dataset-key TEXT  [required]
  --local / --remote  Data sample(s) location.
  --multiple          Add multiple data samples at once.
  --test-only         Data sample(s) used as test data only.
  --config PATH       Config path (default ~/.substra).
  --profile TEXT      Profile name to use.
  --verbose           Enable verbose mode.
  --help              Show this message and exit.
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
  --yaml                Display output as yaml.
  --json                Display output as json.
  --pretty              Pretty print output  [default: True]
  --config PATH         Config path (default ~/.substra).
  --profile TEXT        Profile name to use.
  --verbose             Enable verbose mode.
  --help                Show this message and exit.
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
  --data-samples-path FILE  test data samples
  --yaml                    Display output as yaml.
  --json                    Display output as json.
  --pretty                  Pretty print output  [default: True]
  --config PATH             Config path (default ~/.substra).
  --profile TEXT            Profile name to use.
  --verbose                 Enable verbose mode.
  --help                    Show this message and exit.
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
  }

  Where:
  - name: name of the algorithm
  - description: path to a markdown file describing the algo
  - file: path to tar.gz or zip archive containing the algorithm python
    script and its Dockerfile
  - permissions: define asset access permissions

Options:
  --yaml          Display output as yaml.
  --json          Display output as json.
  --pretty        Pretty print output  [default: True]
  --config PATH   Config path (default ~/.substra).
  --profile TEXT  Profile name to use.
  --verbose       Enable verbose mode.
  --help          Show this message and exit.
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
  --objective-key TEXT      [required]
  --algo-key TEXT           [required]
  --dataset-key TEXT        [required]
  --data-samples-path FILE  [required]
  --tag TEXT
  --yaml                    Display output as yaml.
  --json                    Display output as json.
  --pretty                  Pretty print output  [default: True]
  --config PATH             Config path (default ~/.substra).
  --profile TEXT            Profile name to use.
  --verbose                 Enable verbose mode.
  --help                    Show this message and exit.
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
  --dataset-key TEXT
  --traintuple-key TEXT     [required]
  --data-samples-path FILE
  --tag TEXT
  --yaml                    Display output as yaml.
  --json                    Display output as json.
  --pretty                  Pretty print output  [default: True]
  --config PATH             Config path (default ~/.substra).
  --profile TEXT            Profile name to use.
  --verbose                 Enable verbose mode.
  --help                    Show this message and exit.
```

## substra get

```bash
Usage: substra get [OPTIONS] [algo|dataset|objective|testtuple|traintuple]
                   ASSET_KEY

  Get asset definition.

Options:
  --expand        Display associated assets details
  --yaml          Display output as yaml.
  --json          Display output as json.
  --pretty        Pretty print output  [default: True]
  --config PATH   Config path (default ~/.substra).
  --profile TEXT  Profile name to use.
  --verbose       Enable verbose mode.
  --help          Show this message and exit.
```

## substra list

```bash
Usage: substra list [OPTIONS] [algo|data_sample|dataset|objective|testtuple|tr
                    aintuple|node]

  List assets.

Options:
  -f, --filter TEXT        Only display assets that exactly match this filter.
                           Valid syntax is: <asset>:<property>:<value>
  --and                    Combine filters using logical ANDs
  --or                     Combine filters using logical ORs
  --advanced-filters TEXT  Filter results using a complex search (must be a
                           JSON array of valid filters). Incompatible with the
                           --filter option
  --is-complex             When using filters using 'OR', the server will
                           return a list of matching assets for each operand.
                           By default these lists are merged into a single
                           list. When set, this option disables the lists
                           aggregation.
  --yaml                   Display output as yaml.
  --json                   Display output as json.
  --pretty                 Pretty print output  [default: True]
  --config PATH            Config path (default ~/.substra).
  --profile TEXT           Profile name to use.
  --verbose                Enable verbose mode.
  --help                   Show this message and exit.
```

## substra describe

```bash
Usage: substra describe [OPTIONS] [algo|dataset|objective] ASSET_KEY

  Display asset description.

Options:
  --config PATH   Config path (default ~/.substra).
  --profile TEXT  Profile name to use.
  --verbose       Enable verbose mode.
  --help          Show this message and exit.
```

## substra download

```bash
Usage: substra download [OPTIONS] [algo|dataset|objective] KEY

  Download asset implementation.

  - algo: the algo and its dependencies
  - dataset: the opener script
  - objective: the metrics and its dependencies

Options:
  --folder PATH   destination folder
  --config PATH   Config path (default ~/.substra).
  --profile TEXT  Profile name to use.
  --verbose       Enable verbose mode.
  --help          Show this message and exit.
```

## substra leaderboard

```bash
Usage: substra leaderboard [OPTIONS] OBJECTIVE_KEY

  Display objective leaderboard

Options:
  --expand           Display associated assets details
  --yaml             Display output as yaml.
  --json             Display output as json.
  --pretty           Pretty print output  [default: True]
  --sort [asc|desc]  Sort models by highest to lowest perf or vice versa
                     [default: desc]
  --config PATH      Config path (default ~/.substra).
  --profile TEXT     Profile name to use.
  --verbose          Enable verbose mode.
  --help             Show this message and exit.
```

## substra run-local

```bash
Usage: substra run-local [OPTIONS] ALGO

  Run local.

  Train and test the algo located in ALGO (directory or archive) locally.

  This command can be used to check that objective, dataset and algo assets
  implementations are compatible.

  It will execute sequentially 4 tasks in docker:

  - train algo using train data samples
  - get model perf
  - test model using test data samples
  - get model perf

  It will create several output files:
  - sandbox/model/model
  - sandbox/pred_train/perf.json
  - sandbox/pred_train/pred
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
  --dataset-key TEXT  [required]
  --config PATH       Config path (default ~/.substra).
  --profile TEXT      Profile name to use.
  --verbose           Enable verbose mode.
  --help              Show this message and exit.
```

## substra update dataset

```bash
Usage: substra update dataset [OPTIONS] DATASET_KEY OBJECTIVE_KEY

  Link dataset with objective.

Options:
  --config PATH   Config path (default ~/.substra).
  --profile TEXT  Profile name to use.
  --verbose       Enable verbose mode.
  --help          Show this message and exit.
```

