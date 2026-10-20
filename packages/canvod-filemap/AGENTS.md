# canvod-filemap

Naming recipes: a recipe translates the file names one receiver writes to
canVOD file names, without renaming files on disk. canvodpy does the file
discovery; this package only answers "which canVOD file name does this
file have?" and "where is the recipe file?".

Before changing it, read the canvodpy side: root `AGENTS.md`, section
"canvodpy: read it before changing an extension".

## Where things live

- `src/canvod/filemap/recipe.py`: `NamingRecipe`, the recipe model and the
  left-to-right field walk over a file name.
- `src/canvod/filemap/recipe_files.py`: where recipe files live,
  `<config dir>/recipes/<site>/<name>.yaml`, and creating one from
  `src/canvod/filemap/templates/recipe.yaml`.
- `src/canvod/filemap/remote.py`: a recipe read from a pinned raw GitHub
  URL (commit or `refs/tags/<tag>`), the cache in the system temp folder,
  the token from `GH_TOKEN`/`GITHUB_TOKEN`. `find_recipe` calls it when
  the `recipe:` setting is a URL.
- `src/canvod/filemap/mapping.py`: `VirtualFile`, a physical file with its
  canVOD file name.
- The canVOD file name itself (`CanVODFilename`) is canvod-preflight's
  (`canvod.preflight.convention`). Never redefine it here.

## How canvodpy uses it

`canvodpy.orchestrator.discovery` (canvodpy repo) calls `find_recipe`,
`NamingRecipe.load` and `to_virtual_file` for a receiver with a `recipe:`
setting. A file belongs to the recipe if its name matches `glob` **and**
`NamingRecipe.matches` (exact length, all fields parse). canvodpy's
`just naming-init SITE NAME` creates a recipe from the template; `just
config-check-data SITE` shows which files it recognizes. Changing a public
name here breaks canvodpy: search the canvodpy repo for it first.

## Traps

- `matches` requires the file name length to equal the sum of the field
  widths. A recipe for compressed files (`.gz`) must count the suffix.
- A recipe without an `hour`/`hour_letter` field produces daily files
  (`period` becomes `01D`).
- `yy` resolves 80-99 to 19xx and 00-79 to 20xx.
- Local recipe files are user data in the config directory, never in a
  repository. `find_recipe` refuses a recipe placed directly in the
  `recipes` folder and says where to move it. A shared recipe is read by
  URL instead.
- Unknown recipe fields are ignored, not refused:
  `NamingRecipe.unrecognized_fields` names them, and canvodpy prints them.
- The token never goes into a URL, a message, a log or provenance, and is
  sent only to `raw.githubusercontent.com`, never on a redirect
  (`add_unredirected_header`; urllib forwards normal headers).

## Removed

`FilenameMapper`, `DataDirectoryValidator`, the pattern registry,
`SiteNamingConfig`/`ReceiverNamingConfig`, the convention module (now in
canvod-preflight) and the recipe field `layout` were removed, not
deprecated. An old recipe with `layout:` still loads; the field is
ignored and reported as unrecognized. This was before the extensions took canvodpy's rule
"deprecate, don't delete" (`CODING_STANDARDS.md`); public code that goes
away from now on is deprecated first.

## Tests

`just test-package canvod-filemap`. Test files in `tests/test_data/` use
canVOD file names; other names are built in `tmp_path`.
