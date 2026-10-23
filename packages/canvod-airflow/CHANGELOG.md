# Changelog

All notable changes to this package are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this package adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [canvod-airflow-v1.0.0](https://github.com/TUW-GEO/canvodpy-extensions/releases/tag/canvod-airflow-v1.0.0) - 2026-10-23

### Features

- Add canvod-airflow package with daily + backfill DAGs ([b66aae2](https://github.com/TUW-GEO/canvodpy-extensions/commit/b66aae271f5de3a48a3af8201012e1eac73cf6dd))
- Publish the packages to PyPI ([306a20d](https://github.com/TUW-GEO/canvodpy-extensions/commit/306a20d4f79da74c87fdb8e7241cc0f7660d5574))
- **Breaking:** No extras; each package brings what it needs ([8582445](https://github.com/TUW-GEO/canvodpy-extensions/commit/85824452d371b9cb9d9eee8a9f7a22f0b29d9aee))

### Bug fixes

- Pin UTF-8 encoding on DAG-source read_text() calls ([93e98ab](https://github.com/TUW-GEO/canvodpy-extensions/commit/93e98abc9e032a20c112815ce54ede78181ca808))
- Backfill parameters without defaults ([dfce93e](https://github.com/TUW-GEO/canvodpy-extensions/commit/dfce93e795883e2f784b1822ad64693fc3e64ff2))
- Say Airflow runs on POSIX systems only ([8dadac1](https://github.com/TUW-GEO/canvodpy-extensions/commit/8dadac1fb29c0858b0a6994bd69d1359d6176486))
- Update the locked packages past their known vulnerabilities ([0c40e33](https://github.com/TUW-GEO/canvodpy-extensions/commit/0c40e33ac71e8dc046451bedfa18274eff54eef8))
- Package versions from metadata, airflow needs canvod-config ([5608804](https://github.com/TUW-GEO/canvodpy-extensions/commit/5608804ef6f69b94dfee2103fa5b6f9fd97d966a))

### Refactoring

- **Breaking:** One daily DAG per site on the code of canvodpy run ([0ba0846](https://github.com/TUW-GEO/canvodpy-extensions/commit/0ba08469cab58a2156b4dcfc9922b77b693a9c00))
- Import the DAG API from airflow.sdk ([28c4cff](https://github.com/TUW-GEO/canvodpy-extensions/commit/28c4cffc1a50186baebd479a72e8604cac75a1f2))

### Documentation

- Pin all install snippets to the v0.1.0 tag, not the default branch ([d8d8c0a](https://github.com/TUW-GEO/canvodpy-extensions/commit/d8d8c0a9b1664e4ade06e4ea1fb7b25241b890e1))
- Fix stale docstring — daily_processing generates three DAGs ([bce8f3f](https://github.com/TUW-GEO/canvodpy-extensions/commit/bce8f3f18491ff85116ce0b49647e0e2f61aabb7))
- AGENTS.md and task guides for coding agents ([92c841d](https://github.com/TUW-GEO/canvodpy-extensions/commit/92c841da32370f84ba4ad1786cbe96310ee7b5f9))
- Lead agents through canvodpy's trail before changing an extension ([6cbc821](https://github.com/TUW-GEO/canvodpy-extensions/commit/6cbc821fec392972890fe06ddc948f6c7e5b5b4e))
- Host the documentation at extensions.canvodpy.eu ([3129c54](https://github.com/TUW-GEO/canvodpy-extensions/commit/3129c54fde078723c7620eec53c2756ea48a6f76))
- Package agent instructions in canvodpy's layout and words ([37bc085](https://github.com/TUW-GEO/canvodpy-extensions/commit/37bc085a06002965ab264e1e67091e6cc08727a5))
- PyPI pages for the 1.0.0 release ([76fcf9b](https://github.com/TUW-GEO/canvodpy-extensions/commit/76fcf9b20e9305648e48a5c36f79b11370e1af45))
- Drop the leftover extras wording ([19f8c5e](https://github.com/TUW-GEO/canvodpy-extensions/commit/19f8c5ed4be604af596416949efd14a74ee516f8))
- Drop the af example from the backfill docstring ([d0507a3](https://github.com/TUW-GEO/canvodpy-extensions/commit/d0507a3491cf5e15334764c7ac7214970b731dd3))
- Name the pending publisher a new package needs ([7302afd](https://github.com/TUW-GEO/canvodpy-extensions/commit/7302afdce5b811c9771ff91c98aef3716e4456fc))

### bump

- Version 0.0.0 → 0.1.0 ([9e24904](https://github.com/TUW-GEO/canvodpy-extensions/commit/9e249047772bcb94d84628b979c800c2b2b5dcd1))
