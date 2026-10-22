# canvod-filemap

`canvod-filemap` gives a receiver a naming recipe: a description of how
the receiver's own filenames translate to canVOD filenames. A run then
finds the receiver's files without you renaming anything on disk.

## When you need it

`canvodpy run` processes files whose names follow the canVOD filename
convention, in any folder layout. If your receiver writes files with
other names, for example Septentrio SBF files, legacy RINEX v2 short
names, or a custom layout, set a naming recipe on the receiver.

You don't need it when your files already follow the convention, or when
a run already finds them.

## Install

```bash
uv add "canvod-filemap @ git+https://github.com/nfb2021/canvodpy-extensions.git@v0.1.0#subdirectory=packages/canvod-filemap"
```

The package lives on GitHub only, not on PyPI.

## A minimal example

A naming recipe is a YAML file, kept per site in the configuration
directory at `<config dir>/recipes/<site>/<name>.yaml`. Load it, then map
one file:

```python
from pathlib import Path

from canvod.filemap import NamingRecipe

recipe = NamingRecipe.load(Path("config/recipes/fangorn/fangorn_reference.yaml"))
vf = recipe.to_virtual_file(Path("rref001a15.25o"))
print(vf.canonical_str)  # the canVOD filename; the file on disk keeps its name
```

The recipe reads the receiver identity, the date, and the sampling
from the receiver's own filename and writes them as a canVOD filename.
`CanVODFilename` of `canvod-preflight` parses and builds the names, the
same class a run uses. Before a run, check which files it would process:

```bash
canvodpy config validate --site fangorn
```

## How it fits into a run

A run uses the naming recipe only for a receiver whose settings set a
recipe. Reference it on the receiver in `canvod-settings.yaml`:

```yaml
sites:
  my_site:
    receivers:
      reference_01:
        recipe: my_site_reference
```

A run finds the files in any folder layout and takes each file's day from
its name. See the canVOD [file naming convention](https://canvodpy.eu/packages/naming/overview/)
and [Configuration](https://canvodpy.eu/guides/configuration/).

## Recipes from a URL

A recipe can live in a GitHub repository, so that every machine uses the
same one. Set the raw link of the file, pinned to a commit or a tag:

```yaml
        recipe: https://raw.githubusercontent.com/<account>/<recipes-repo>/<commit>/my_site/my_site_reference.yaml
```

- **Pinned only.** The link names a full 40-character commit, or a tag as
  `refs/tags/<tag>`. A branch, or a bare name such as `v1` that could be a
  branch, is refused, and the message shows both pinned forms. A commit is
  the only pin that never changes: a tag can be moved.
- **Checked like a local recipe.** The recipe's `name` must match the file
  name at the end of the link. A `github.com/.../blob/...` link is refused,
  and the message names the raw link.
- **Provenance.** The store records the link and the sha256 of the file it
  was made with.
- **Cache.** A fetched recipe is kept in a folder of the system's temporary
  folder, one per user, and used without a new fetch. A run without network
  access therefore works once the recipe was fetched; otherwise it stops
  and names the link. A cached recipe whose tag was moved keeps its old
  content until the system empties the temporary folder.
- **Private repositories.** Public recipes need nothing more. A recipe in a
  private repository needs a GitHub token that can read it, in `GH_TOKEN`
  or `GITHUB_TOKEN`; a fine-grained, read-only token for that one
  repository is enough. A variable that holds no valid token stops the
  run with a message that names the variable, not its value. canvodpy
  never stores the token, sends it only to
  `raw.githubusercontent.com`, and refuses a link that holds a user name,
  password, query or fragment. Keep the token where you keep other secrets (the
  system keychain, a password manager, the secrets store of your
  scheduler), and start the run with it in the environment.

## Limits and known issues

- A recipe has no `layout` field: a run finds the files in any folder
  layout and takes each file's day from its name. An older recipe that
  still sets `layout` loads, and the field has no effect.
- Fields a recipe holds that canvod-filemap does not know are ignored.
  `canvodpy config validate` lists them as unrecognized, and a run logs
  them.
- Recipes from a URL are read only from `raw.githubusercontent.com`.
- A recipe saved directly in `<config dir>/recipes/` is not used. The
  error says where to move it. It belongs in
  `<config dir>/recipes/<site>/`.
- A recipe does not change that compressed files are never processed.
- `DataDirMatcher` and `PairDataDirMatcher` in canvod-readers are
  obsolete and the next major version removes them.

## API

See the [API reference](../../api/canvod-filemap.md) for the full public
API.
