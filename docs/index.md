---
title: canvodpy-extensions
description: Optional packages for the canVODpy ecosystem
hide:
  - navigation
  - toc
---

<div class="hero" markdown>

<h1 class="hero-lockup">
  <img src="https://raw.githubusercontent.com/nfb2021/canvodpy/main/docs/assets/logo/canvodpy_logo_bright_mode.svg#only-light" alt="canVODpy">
  <img src="https://raw.githubusercontent.com/nfb2021/canvodpy/main/docs/assets/logo/canvodpy_logo_dark_mode.svg#only-dark" alt="canVODpy">
  <span class="hero-lockup__word">extensions</span>
</h1>

**Optional packages for the [canVODpy](https://canvodpy.eu/) ecosystem**

Each of these packages does one job alongside canVODpy. Install only the
one you need: a naming recipe for the files your receiver writes, an
Airflow DAG for a site's daily runs, or an adapter to exchange data with
another GNSS-T program.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![REUSE](https://img.shields.io/badge/REUSE-3.3-blue)](https://reuse.software/)

[Start here :fontawesome-solid-arrow-right:](users/index.md){ .md-button .md-button--primary }
[Contribute :fontawesome-solid-arrow-right:](CONTRIBUTING.md){ .md-button }

</div>

---

## Packages

<div class="grid cards" markdown>

-   :fontawesome-solid-tag: &nbsp; **canvod-filemap**

    ---

    Maps the files your receiver writes to their canVOD file names, so a
    run finds your data without you renaming anything on disk.

    [:octicons-arrow-right-24: Naming recipes](packages/filemap/overview.md)

-   :fontawesome-solid-diagram-project: &nbsp; **canvod-airflow**

    ---

    One daily DAG per site, plus one to backfill a date range. The tasks
    run the code of `canvodpy run`.

    [:octicons-arrow-right-24: Airflow DAGs](packages/airflow/overview.md)

-   :fontawesome-solid-arrows-turn-to-dots: &nbsp; **canvod-adapters**

    ---

    Reads and writes observations and VOD for another GNSS-T program, for
    example gnssvod, and checks each import against canvodpy's contracts.

    [:octicons-arrow-right-24: Data exchange](packages/adapters/overview.md)

</div>

---

canVODpy is a lean core that works fully without any of these packages.
Each one is optional, installs on its own, and follows its own release
cadence. For the packages canVODpy ships and how to set a site up,
see [canVODpy](https://canvodpy.eu/).

---

## Affiliation

**Climate and Environmental Remote Sensing Research Unit (CLIMERS)**
Department of Geodesy and Geoinformation, TU Wien

[tuwien.at/en/mg/geo/climers](https://www.tuwien.at/en/mg/geo/climers){ .md-button }
