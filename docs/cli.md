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

  The path is either a directory reprensenting a data sample or a parent
  directory containing data samples directories (if --multiple option is
  set).

Options:
  --dataset-key TEXT  [required]
  --local / --remote  Data sample(s) location.
  --multiple          Add multiple data samples at once.
  --test-only         Data sample(s) used as test data only.
  --dry-run
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
      "permissions": str,
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
  --dry-run
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
      "permissions": str,
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
  --data-samples-path PATH  test data samples
  --dry-run
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
      "permissions": str,
  }

  Where:
  - name: name of the algorithm
  - description: path to a markdown file describing the algo
  - file: path to tar.gz or zip archive containing the algorithm python
    script and its Dockerfile
  - permissions: define asset access permissions

Options:
  --dry-run
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
  --data-samples-path PATH  [required]
  --dry-run
  --tag
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
  --data-samples-path PATH
  --dry-run
  --tag
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
  --expand        Display associated assets (available for dataset and
                  traintuple).
  --json          Display output as json.
  --config PATH   Config path (default ~/.substra).
  --profile TEXT  Profile name to use.
  --verbose       Enable verbose mode.
  --help          Show this message and exit.
```

## substra list

```bash
Usage: substra list [OPTIONS]
                    [algo|data_sample|dataset|objective|testtuple|traintuple]
                    [FILTERS]

  List assets.

Options:
  --is-complex    When using filters the server will return a list of assets
                  for each filter item. By default these lists are merged into
                  a single list. When set, this option disables the lists
                  aggregation.
  --json          Display output as json.
  --config PATH   Config path (default ~/.substra).
  --profile TEXT  Profile name to use.
  --verbose       Enable verbose mode.
  --help          Show this message and exit.
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

## substra run-local

```bash
Usage: substra run-local [OPTIONS] ALGO_PATH

  Run local.

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
  --train-opener PATH
  --test-opener PATH
  --metrics PATH
  --rank INTEGER
  --train-data-samples PATH
  --test-data-samples PATH
  --inmodel PATH
  --fake-data-samples
  --help                     Show this message and exit.
```

## substra update data_sample

```bash
Usage: substra update data_sample [OPTIONS] DATA_SAMPLES_PATH DATASET_KEY

  Link data samples with dataset.

  The data samples path must point to a valid JSON file with the following
  schema:

  {
      "keys": list[str],
  }

  Where:
  - keys: list of data sample keys

Options:
  --config PATH   Config path (default ~/.substra).
  --profile TEXT  Profile name to use.
  --verbose       Enable verbose mode.
  --help          Show this message and exit.
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

