# Start here

These packages are optional extras for canVODpy. Start here when canVODpy
already works on your data and your setup needs one of them.

They live on GitHub only, not on PyPI, and each installs on its
own:

| You need | Install | Read next |
|---|---|---|
| Your receiver's files don't follow the canVOD filename convention | `canvod-filemap` | [Naming recipes](../packages/filemap/overview.md) |
| A site's processing to run on a schedule | `canvod-airflow` | [Airflow DAGs](../packages/airflow/overview.md) |
| Another GNSS-T program to read or write your observations and VOD | `canvod-adapters` | [Data exchange](../packages/adapters/overview.md) |

## Install a package

Each package is a `uv` package, installed from a git source because these
packages are not on PyPI. The `@v0.1.0` is the tag of the release.

### `canvod-filemap`

```bash
uv add "canvod-filemap @ git+https://github.com/nfb2021/canvodpy-extensions.git@v0.1.0#subdirectory=packages/canvod-filemap"
```

### `canvod-airflow`

`canvod-airflow` depends on canvodpy. Install it directly wherever the
DAGs run. The `[airflow]` extra installs `apache-airflow`:

```bash
uv add "canvod-airflow[airflow] @ git+https://github.com/nfb2021/canvodpy-extensions.git@v0.1.0#subdirectory=packages/canvod-airflow"
```

### `canvod-adapters`

The `[store]` extra adds the VOD store read and write:

```bash
uv add "canvod-adapters[store] @ git+https://github.com/nfb2021/canvodpy-extensions.git@v0.1.0#subdirectory=packages/canvod-adapters"
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
