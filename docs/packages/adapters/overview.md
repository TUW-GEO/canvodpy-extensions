# canvod-adapters

`canvod-adapters` exchanges data between canvodpy and other GNSS-T
programs. Every import is checked against canvodpy's contract for that
data, and every conversion records where the data came from. The package
adapts [gnssvod](https://github.com/vincenthumphrey/gnssvod).

## When you need it

You need it when another GNSS-T program writes your observations or VOD,
or when you want to give yours to it. You don't need it when you only
read and write canvodpy's own readers and stores.

## Install

```bash
uv add "canvod-adapters[store] @ git+https://github.com/TUW-GEO/canvodpy-extensions.git@v0.1.0#subdirectory=packages/canvod-adapters"
```

The package lives on GitHub only. The `[store]` extra adds the VOD store
read and write.

## A minimal example

gnssvod works on datasets whose axes are the epoch and the satellite,
with one variable per RINEX observation code (`S1C`, `C1C`) or per VOD
band, and angles in degrees. canvodpy works on the epoch and the Signal
ID, for example `G01|L1|C`, and angles in radians. The adapter maps one
to the other.

Import a gnssvod VOD file into the VOD store, and export one back:

```python
from canvod.adapters.gnssvod import GnssvodVod
from canvod.adapters.store import export_vod, import_vod

adapter = GnssvodVod(bands={"VOD_L1": ["S1C", "S1W", "S1X"], "VOD_L2": ["S2W"]}, time_system="GPS")

import_vod(adapter, "vod_rosalia.nc", site.vod_store, "canopy_01_vs_reference_01")

export_vod(
    adapter,
    site.vod_store,
    "tau_omega_zeroth_order/canopy_01_vs_reference_01",
    "vod_canvodpy.nc",
)
```

## How it fits into a run

The package separates what every program shares from what is specific to
one program, behind one interface per kind of data.

**One interface per kind of data.** Programs exchange different data with
canvodpy: one writes observations, another only VOD. A program's adapter
implements the interfaces of the data it exchanges, and only those.

**canvodpy's contracts guard everything that comes in.** canvodpy defines
what its data looks like, and the interfaces check every import against
it:

| Data | Contract |
|------|----------|
| Observations | `canvod.readers.validate_dataset`, the contract of every canvodpy reader |
| VOD | `canvod.readers.validate_vod_dataset` |

Observations come in through a reader of the program's files (a
`canvod.readers.GNSSDataReader`), so they carry the same file hash,
attributes and epoch time scale as observations read from RINEX or SBF
files. See [Building a reader](https://canvodpy.eu/packages/readers/building-a-reader/).

**Settings are Pydantic models.** An adapter is a frozen Pydantic model
whose fields are the program's settings, checked when the adapter is
created, for example the bands of `GnssvodVod`.

**Provenance.** Every conversion records the program, its URL and
installed version, the canvod-adapters version, the direction, the source
and the time in the dataset attributes (`conversion_*`), read back with
`Provenance.from_attrs`.

## Limits and known issues

- gnssvod's `calc_vod` merges the observation codes of a band. Imported
  VOD of a band with one code gets the Signal IDs of that code (`S2W` →
  `G01|L2|W`). A band with several codes gets canvodpy's marker for an
  unknown tracking code (`G01|L1|u`).
- `calc_vod` reports the reference receiver's Azimuth and Elevation.
  canvodpy reports the canopy receiver's. Imported VOD keeps gnssvod's
  angles.
- The VOD store keeps imported VOD under the program's name, apart from
  the VOD canvodpy computed. Importing the same file again is skipped.
- gnssvod keeps the epochs of the RINEX files it read, in observation
  and in VOD files, so the files' time scale is a required setting
  (`time_system`). canvodpy stores every epoch in GPS time, so a file in
  another time scale is refused rather than converted.

## Another program

To add an adapter for another program:

1. Create a subpackage `canvod.adapters.<program>`.
2. Describe the program with a `Tool` (name, Python distribution, URL).
3. Implement the interfaces of the data it exchanges: `VodAdapter`
   (`open`, `save`, `convert_to_canvodpy`, `convert_from_canvodpy`) or
   `ObservationsAdapter` (`reader`, `convert_from_canvodpy`, `save`).
4. Put the program's settings in fields of the adapter.

Contract checks, provenance and store I/O come with the interfaces.

## API

See the [API reference](../../api/canvod-adapters.md) for the full public
API.
