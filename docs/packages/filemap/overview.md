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

recipe = NamingRecipe.load(Path("config/recipes/rosalia/rosalia_reference.yaml"))
vf = recipe.to_virtual_file(Path("rref001a15.25o"))
print(vf.canonical_str)  # the canVOD filename; the file on disk keeps its name
```

The recipe reads the receiver identity, the date, and the sampling
from the receiver's own filename and writes them as a canVOD filename.
`CanVODFilename` of `canvod-preflight` parses and builds the names, the
same class a run uses. Before a run, check which files it would process:

```bash
canvodpy config validate --site rosalia
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

## Limits and known issues

- A recipe has no `layout` field: a run finds the files in any folder
  layout and takes each file's day from its name. An older recipe that
  still sets `layout` loads, and the field has no effect.
- A recipe saved directly in `<config dir>/recipes/` is not used. The
  error says where to move it. It belongs in
  `<config dir>/recipes/<site>/`.
- A recipe does not change that compressed files are never processed.
- `DataDirMatcher` and `PairDataDirMatcher` in canvod-readers are
  obsolete and the next major version removes them.

## API

See the [API reference](../../api/canvod-filemap.md) for the full public
API.
