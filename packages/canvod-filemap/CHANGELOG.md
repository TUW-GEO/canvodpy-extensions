# Changelog

All notable changes to this package are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this package adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [canvod-filemap-v1.0.0](https://github.com/TUW-GEO/canvodpy-extensions/releases/tag/canvod-filemap-v1.0.0) - 2026-10-24

### Features

- **Breaking:** Require canvod-preflight and canvod-utils 1.0.0 from PyPI ([f695940](https://github.com/TUW-GEO/canvodpy-extensions/commit/f695940a09b30042c91811a0cfd8e2a31b4e3620))
- Find recipe files per site and create them from a template ([753db56](https://github.com/TUW-GEO/canvodpy-extensions/commit/753db564850611e4e43671f10ef51c0e71beb322))
- Read a naming recipe from a pinned URL ([ecec4ae](https://github.com/TUW-GEO/canvodpy-extensions/commit/ecec4aedc1e2d6b8c608dec787c5ae19bd166fbe))
- **Breaking:** Fetch recipe URLs in every run, accept branch links ([c5c1d53](https://github.com/TUW-GEO/canvodpy-extensions/commit/c5c1d53f80aadd56a6ffe3dc19e340e98240c9e0))
- Publish the packages to PyPI ([306a20d](https://github.com/TUW-GEO/canvodpy-extensions/commit/306a20d4f79da74c87fdb8e7241cc0f7660d5574))
- **Breaking:** No extras; each package brings what it needs ([8582445](https://github.com/TUW-GEO/canvodpy-extensions/commit/85824452d371b9cb9d9eee8a9f7a22f0b29d9aee))

### Bug fixes

- Resolve ty type errors blocking pre-push hook ([c70aeae](https://github.com/TUW-GEO/canvodpy-extensions/commit/c70aeae9f137cb4d54d8ca597e6678dfb673fef6))
- Relock after merging main and escape the recipe path in a test ([40975aa](https://github.com/TUW-GEO/canvodpy-extensions/commit/40975aa5f2e33c4c7e25056b8ed62eb44bef2d9e))
- RINEX 2 daily session "0" gives a daily file ([b61bb75](https://github.com/TUW-GEO/canvodpy-extensions/commit/b61bb75735db4ba54d7996ee45e76a852154b1e1))
- Keep a parallel fetch's cached recipe on Windows ([deaf1dd](https://github.com/TUW-GEO/canvodpy-extensions/commit/deaf1ddd241f24d5d4e73236bacba6dd94c8e99b))
- A failed cache write is a RecipeFetchError; test both branches ([2541a37](https://github.com/TUW-GEO/canvodpy-extensions/commit/2541a3720961b718e1ef8d885a2665dc4dae2093))
- Read `__version__` from the package metadata ([5608804](https://github.com/TUW-GEO/canvodpy-extensions/commit/5608804ef6f69b94dfee2103fa5b6f9fd97d966a))

### Refactoring

- **Breaking:** Remove the mapper, validator and pattern registry ([5d00897](https://github.com/TUW-GEO/canvodpy-extensions/commit/5d008972c4283d51af362f6b9422aa55b7e98f06))
- **Breaking:** Use the canVOD naming convention of canvod-preflight ([8edc239](https://github.com/TUW-GEO/canvodpy-extensions/commit/8edc239d2fb289412a2cebeac045217884629b7c))
- Break the import cycle between recipe_files and remote ([5ec6eeb](https://github.com/TUW-GEO/canvodpy-extensions/commit/5ec6eebd9a0d41a1b58b77258363eea76028bd35))
- Fetch URL recipes with canvod.utils.pinned ([84176ee](https://github.com/TUW-GEO/canvodpy-extensions/commit/84176eeb21e6fff6444b7322666408d416b08a16))

### Documentation

- AGENTS.md and task guides for coding agents ([92c841d](https://github.com/TUW-GEO/canvodpy-extensions/commit/92c841da32370f84ba4ad1786cbe96310ee7b5f9))
- Lead agents through canvodpy's trail before changing an extension ([6cbc821](https://github.com/TUW-GEO/canvodpy-extensions/commit/6cbc821fec392972890fe06ddc948f6c7e5b5b4e))
- Host the documentation at extensions.canvodpy.eu ([3129c54](https://github.com/TUW-GEO/canvodpy-extensions/commit/3129c54fde078723c7620eec53c2756ea48a6f76))
- Link canvodpy's docs at canvodpy.eu ([f8a15b2](https://github.com/TUW-GEO/canvodpy-extensions/commit/f8a15b2aeb0a571c28cbc28b4ac93f641704515a))
- Package agent instructions in canvodpy's layout and words ([37bc085](https://github.com/TUW-GEO/canvodpy-extensions/commit/37bc085a06002965ab264e1e67091e6cc08727a5))
- Describe recipes read from a pinned URL ([05ae9dd](https://github.com/TUW-GEO/canvodpy-extensions/commit/05ae9dd6a093caf779ce33cde74ab05b3e3a366c))
- The recipe example uses the Fangorn test site ([e0a10e9](https://github.com/TUW-GEO/canvodpy-extensions/commit/e0a10e9721f12173026b2176a7a09c1e155f9656))
- README, overview and recipe template use the Fangorn test site ([a0f9c93](https://github.com/TUW-GEO/canvodpy-extensions/commit/a0f9c93bbf41c45fe0809ae26a2bee502a0767ec))
- The run folder is removed when its process ends ([124ff82](https://github.com/TUW-GEO/canvodpy-extensions/commit/124ff82471164c108540290be7cb3f389b171335))
- PyPI pages for the 1.0.0 release ([76fcf9b](https://github.com/TUW-GEO/canvodpy-extensions/commit/76fcf9b20e9305648e48a5c36f79b11370e1af45))
