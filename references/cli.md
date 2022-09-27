# Summary

- [substra config](#substra-config)
- [substra login](#substra-login)
- [substra organization info](#substra-organization-info)
- [substra cancel compute_plan](#substra-cancel-compute_plan)


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

## substra cancel compute_plan

```text
Usage: substra cancel compute_plan [OPTIONS] COMPUTE_PLAN_KEY

  Cancel execution of a compute plan. Nothing is printed, you can check again
  the compute plan status with `substra get compute_plan`.

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

