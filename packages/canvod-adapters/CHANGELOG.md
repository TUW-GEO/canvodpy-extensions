# Changelog

All notable changes to this package are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this package adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [canvod-adapters-v1.0.0](https://github.com/TUW-GEO/canvodpy-extensions/releases/tag/canvod-adapters-v1.0.0) - 2026-10-24

### Features

- **Breaking:** Require canvod-readers, canvod-utils and canvod-store 1.0.0 from PyPI ([f695940](https://github.com/TUW-GEO/canvodpy-extensions/commit/f695940a09b30042c91811a0cfd8e2a31b4e3620))
- Add canvod-adapters package with gnssvod converter ([ce77b5c](https://github.com/TUW-GEO/canvodpy-extensions/commit/ce77b5c1196b4550e2da459e3aabbc35d627f1b4))
- **Breaking:** One interface per kind of data, checked against canvodpy's contracts ([e16c394](https://github.com/TUW-GEO/canvodpy-extensions/commit/e16c39457b3a36f12edcd00538e65854dc42387c))
- Publish the packages to PyPI ([306a20d](https://github.com/TUW-GEO/canvodpy-extensions/commit/306a20d4f79da74c87fdb8e7241cc0f7660d5574))
- **Breaking:** No extras; each package brings what it needs ([8582445](https://github.com/TUW-GEO/canvodpy-extensions/commit/85824452d371b9cb9d9eee8a9f7a22f0b29d9aee))

### Bug fixes

- Sort data_vars by str key to satisfy type checker ([9a2ad07](https://github.com/TUW-GEO/canvodpy-extensions/commit/9a2ad07ac8fa3b36745af854e987f410a63db93f))
- Gnssvod epochs must be GPS time ([6637e2f](https://github.com/TUW-GEO/canvodpy-extensions/commit/6637e2ff07021db7c923cbee01de73e5f91b3ff9))
- Read `__version__` from the package metadata ([5608804](https://github.com/TUW-GEO/canvodpy-extensions/commit/5608804ef6f69b94dfee2103fa5b6f9fd97d966a))

### Refactoring

- Import VOD through the batch VOD write ([2d1b227](https://github.com/TUW-GEO/canvodpy-extensions/commit/2d1b227635eccfb09276673ee5da09815e4ef6f0))

### Documentation

- AGENTS.md and task guides for coding agents ([92c841d](https://github.com/TUW-GEO/canvodpy-extensions/commit/92c841da32370f84ba4ad1786cbe96310ee7b5f9))
- Lead agents through canvodpy's trail before changing an extension ([6cbc821](https://github.com/TUW-GEO/canvodpy-extensions/commit/6cbc821fec392972890fe06ddc948f6c7e5b5b4e))
- Host the documentation at extensions.canvodpy.eu ([3129c54](https://github.com/TUW-GEO/canvodpy-extensions/commit/3129c54fde078723c7620eec53c2756ea48a6f76))
- Package agent instructions in canvodpy's layout and words ([37bc085](https://github.com/TUW-GEO/canvodpy-extensions/commit/37bc085a06002965ab264e1e67091e6cc08727a5))
- List model fields under Attributes ([a6874dd](https://github.com/TUW-GEO/canvodpy-extensions/commit/a6874ddef41ce41638c2b6fbe292c22d93a28873))
- PyPI pages for the 1.0.0 release ([76fcf9b](https://github.com/TUW-GEO/canvodpy-extensions/commit/76fcf9b20e9305648e48a5c36f79b11370e1af45))
- Drop the leftover extras wording ([19f8c5e](https://github.com/TUW-GEO/canvodpy-extensions/commit/19f8c5ed4be604af596416949efd14a74ee516f8))
