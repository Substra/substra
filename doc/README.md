# Summary

- [substra add algo](#substra-add-algo)
- [substra add data_sample](#substra-add-data_sample)
- [substra add dataset](#substra-add-dataset)
- [substra add objective](#substra-add-objective)
- [substra add testtuple](#substra-add-testtuple)
- [substra add traintuple](#substra-add-traintuple)
- [substra config](#substra-config)
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
      "name": str [required],
      "description": path [required],
      "file": path [required],
      "objective_key": str,
  }

  Where:
  - name: name of the algorithm
  - description: path to a markdown file describing the algo
  - file: path to tar.gz archive containing the algorithm python script and
    its Dockerfile
  - objective_key: optional objective key

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

Options:
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

Options:
  --dataset-key TEXT
  --data-samples-path PATH
  --dry-run
  --config PATH             Config path (default ~/.substra).
  --profile TEXT            Profile name to use.
  --help                    Show this message and exit.
```

## substra add testtuple

```bash
Usage: substra add testtuple [OPTIONS]

  Add testtuple.

Options:
  --dataset-key TEXT
  --traintuple-key TEXT
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

Options:
  --objective-key TEXT
  --algo-key TEXT
  --dataset-key TEXT
  --data-samples-path PATH
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

Options:
  --config PATH   Config path (default ~/.substra).
  --profile TEXT  Profile name to use.
  --help          Show this message and exit.
```

## substra update dataset

```bash
Usage: substra update dataset [OPTIONS] DATASET_KEY OBJECTIVE_KEY

  Update dataset.

Options:
  --config PATH   Config path (default ~/.substra).
  --profile TEXT  Profile name to use.
  --help          Show this message and exit.
```

