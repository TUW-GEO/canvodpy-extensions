# Start here

These packages are optional extras for canVODpy. Start here when canVODpy
already works on your data and your setup needs one of them.

Each is on PyPI and installs on its own:

| You need | Install | Read next |
|---|---|---|
| Your receiver's files don't follow the canVOD filename convention | `canvod-filemap` | [Naming recipes](../packages/filemap/overview.md) |
| A site's processing to run on a schedule | `canvod-airflow` | [Airflow DAGs](../packages/airflow/overview.md) |
| Another GNSS-T program to read or write your observations and VOD | `canvod-adapters` | [Data exchange](../packages/adapters/overview.md) |

## Install a package

Add the package to the project that uses canvodpy. Each package brings
everything it needs.

### `canvod-filemap`

```bash
uv add canvod-filemap
```

### `canvod-airflow`

Install it wherever the DAGs run. It also installs Apache Airflow 3; an
Airflow 3 that is already installed is used as it is:

```bash
uv add canvod-airflow
```

### `canvod-adapters`

```bash
uv add canvod-adapters
```

## If you don't install a package

canVODpy imports `canvod-filemap` only for a receiver whose settings set a
naming recipe (`recipe:`). Without a recipe, a run takes only the files
with canVOD filenames, even when the package is not installed. A
receiver with a recipe but without the package stops the run with an
error that says how to install it. It never guesses the filenames. See
[Optional extensions](https://canvodpy.eu/guides/extensions/).

`canvod-airflow` and `canvod-adapters` call canVODpy, not the other way
around. A run never needs them.
