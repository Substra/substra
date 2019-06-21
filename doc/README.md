# Summary

- [substra add algo](#substra-add-algo)
- [substra add data_sample](#substra-add-data_sample)
- [substra add dataset](#substra-add-dataset)
- [substra add objective](#substra-add-objective)
- [substra add testtuple](#substra-add-testtuple)
- [substra add traintuple](#substra-add-traintuple)
- [substra config](#substra-config)
- [substra describe](#substra-describe)
- [substra download](#substra-download)
- [substra get](#substra-get)
- [substra list](#substra-list)
- [substra run-local](#substra-run-local)
- [substra update data-sample](#substra-update-data-sample)
- [substra update dataset](#substra-update-dataset)


# Commands

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
  --help          Show this message and exit.
```

## substra add data_sample

```bash
Usage: substra add data_sample [OPTIONS] PATH

  Add data sample.

  The path must point to a valid JSON file with the following schema:

  {
      "paths": list[path],
  }

  Where:
  - paths: list of paths pointing to data sample archives (if local option)
    or to data sample directories (if remote option)

Options:
  --dataset-key TEXT  [required]
  --local / --remote
  --test-only
  --dry-run
  --config PATH       Config path (default ~/.substra).
  --profile TEXT      Profile name to use.
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
  - metrics: path to the metrics python script
  - permissions: define asset access permissions

  The data samples path must point to a valid JSON file with the following
  schema:

  {
      "keys": list[str],
  }

  Where:
  - keys: list of data sample keys

Options:
  --dataset-key TEXT        [required]
  --data-samples-path PATH  test data samples
  --dry-run
  --config PATH             Config path (default ~/.substra).
  --profile TEXT            Profile name to use.
  --help                    Show this message and exit.
```

## substra add testtuple

```bash
Usage: substra add testtuple [OPTIONS]

  Add testtuple.

  The data samples path must point to a valid JSON file with the following
  schema:

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
  --config PATH             Config path (default ~/.substra).
  --profile TEXT            Profile name to use.
  --help                    Show this message and exit.
```

## substra add traintuple

```bash
Usage: substra add traintuple [OPTIONS]

  Add traintuple.

  The data samples path must point to a valid JSON file with the following
  schema:

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
  --config PATH             Config path (default ~/.substra).
  --profile TEXT            Profile name to use.
  --help                    Show this message and exit.
```

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

## substra describe

```bash
Usage: substra describe [OPTIONS] [algo|dataset|objective] ASSET_KEY

  Download and print asset description

Options:
  --config PATH   Config path (default ~/.substra).
  --profile TEXT  Profile name to use.
  --help          Show this message and exit.
```

## substra download

```bash
Usage: substra download [OPTIONS] [algo|dataset|objective] KEY

  Download asset.

Options:
  --folder PATH   destination folder
  --config PATH   Config path (default ~/.substra).
  --profile TEXT  Profile name to use.
  --help          Show this message and exit.
```

## substra get

```bash
Usage: substra get [OPTIONS] [algo|dataset|objective|testtuple|traintuple]
                   ASSET_KEY

  Get asset by key.

Options:
  --expand
  --json          Display output as json
  --config PATH   Config path (default ~/.substra).
  --profile TEXT  Profile name to use.
  --help          Show this message and exit.
```

## substra list

```bash
Usage: substra list [OPTIONS]
                    [algo|data_sample|dataset|objective|testtuple|traintuple]
                    [FILTERS]

  List asset.

Options:
  --is-complex
  --json          Display output as json
  --config PATH   Config path (default ~/.substra).
  --profile TEXT  Profile name to use.
  --help          Show this message and exit.
```

## substra run-local

```bash
Usage: substra run-local [OPTIONS] ALGO_PATH

  Run local.

Options:
  --train-opener PATH
  --test-opener PATH
  --metrics PATH
  --rank INTEGER
  --train-data-samples PATH
  --test-data-samples PATH
  --inmodel PATH
  --outmodel PATH
  --fake-data-samples
  --help                     Show this message and exit.
```

## substra update data-sample

```bash
Usage: substra update data-sample [OPTIONS] DATA_SAMPLES_PATH DATASET_KEY

  Update data samples.

  Link data samples with a dataset through thier keys.

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
  --help          Show this message and exit.
```

## substra update dataset

```bash
Usage: substra update dataset [OPTIONS] DATASET_KEY OBJECTIVE_KEY

  Update dataset.

  Link dataset with obective.

Options:
  --config PATH   Config path (default ~/.substra).
  --profile TEXT  Profile name to use.
  --help          Show this message and exit.
```

