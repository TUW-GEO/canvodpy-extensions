[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.21359005-blue)](https://doi.org/10.5281/zenodo.21359005)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/)
[![REUSE](https://img.shields.io/badge/REUSE-3.3-blue)](https://reuse.software/)
[![fair-software.eu](https://img.shields.io/badge/fair--software.eu-%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8B%20%20%E2%97%8F%20%20%E2%97%8B-orange)](https://fair-software.eu)

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/TUW-GEO/canvodpy/main/docs/assets/logo/canvodpy_logo_dark_mode.svg">
    <img alt="canVODpy logo" src="https://raw.githubusercontent.com/TUW-GEO/canvodpy/main/docs/assets/logo/canvodpy_logo_bright_mode.svg" width="312">
  </picture>
</p>

# canvodpy-extensions

Optional extension packages for [canVODpy](https://github.com/TUW-GEO/canvodpy).
They are add-ons to an installed canvodpy, not part of the core monorepo.
Each package is on PyPI and installs on its own.

## Packages

| Package | Purpose | Status |
|---|---|---|
| [`canvod-filemap`](packages/canvod-filemap) | Recipe-based filename mapping for non-canonical GNSS filenames | Available |
| [`canvod-airflow`](packages/canvod-airflow) | Airflow DAGs for canvodpy: one daily DAG per site, plus backfill | Available |
| [`canvod-adapters`](packages/canvod-adapters) | Data exchange between canvodpy and other GNSS-T programs (gnssvod) | Available |

## Installation

Add a package to the project that uses canvodpy:

```bash
uv add canvod-filemap
uv add canvod-airflow
uv add canvod-adapters
```

Each package brings everything it needs; `canvod-airflow` also installs
Apache Airflow 3. Each package is released on its own, under the tag
`<package>-v<version>`, and published to PyPI from that tag. See
"Releasing" in [CONTRIBUTING.md](CONTRIBUTING.md).

## Development Setup

```bash
git clone https://github.com/TUW-GEO/canvodpy-extensions.git
cd canvodpy-extensions

uv sync
just hooks
```

### Common Commands

```bash
just --list       # Show all commands
just test         # Run all tests
just check        # Lint + format + type-check
just docs         # Preview documentation locally
```

## Documentation

Full documentation is available at **[extensions.canvodpy.eu](https://extensions.canvodpy.eu/)**.

## Contributing

Contributions of all kinds are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

First-time contributors: add yourself to [CONTRIBUTORS.md](CONTRIBUTORS.md) in your PR.

## License

Licensed under the [Apache License 2.0](LICENSE).

This software is provided "as is" without warranty of any kind.

## Affiliation

Founded by **Nicolas François Bader**

[Climate and Environmental Remote Sensing Research Unit (CLIMERS)](https://www.tuwien.at/en/mg/geo/climers)
Department of Geodesy and Geoinformation, TU Wien
