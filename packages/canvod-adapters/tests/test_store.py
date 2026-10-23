"""Tests for VOD store I/O through an adapter (needs canvod-store)."""

import numpy as np
import pytest
import xarray as xr
from canvod.adapters.gnssvod import GnssvodVod, to_gnssvod_vod
from canvod.adapters.provenance import Provenance

store_module = pytest.importorskip("canvod.store")
from canvod.adapters.store import export_vod, import_vod  # noqa: E402

BANDS = {"VOD_L2": ["S2W"], "VOD_E5a": ["S5Q"]}


@pytest.fixture
def store(tmp_path):
    # Opening a store never creates one (canvodpy#236): create it the way a
    # run does, with the made-up site's metadata and settings, never the
    # user's own settings file
    from canvod.config import load_config
    from canvod.store_metadata.testing import give_test_metadata
    from canvod.utils import testing

    path = give_test_metadata(tmp_path / "vod_store", "vod_store")
    testing.write_settings(tmp_path / "settings")
    settings = load_config(config_dir=tmp_path / "settings")
    return store_module.MyIcechunkStore(path, store_type="vod_store", config=settings)


@pytest.fixture
def gnssvod_file(vod_ds, tmp_path):
    path = tmp_path / "vod.nc"
    to_gnssvod_vod(vod_ds, BANDS).to_netcdf(path)
    return path


def test_import_goes_to_the_tool_group(store, gnssvod_file, vod_ds):
    adapter = GnssvodVod(bands=BANDS, time_system="GPS")

    assert import_vod(adapter, gnssvod_file, store, "canopy_01_vs_reference_01")

    stored = store.read_group("gnssvod/canopy_01_vs_reference_01").load()
    np.testing.assert_allclose(
        stored["VOD"].values, vod_ds["VOD"].sel(sid=stored["sid"].values).values
    )
    assert Provenance.from_attrs(stored.attrs).source == "vod.nc"


def test_same_file_is_imported_once(store, gnssvod_file):
    adapter = GnssvodVod(bands=BANDS, time_system="GPS")
    import_vod(adapter, gnssvod_file, store, "a")

    assert not import_vod(adapter, gnssvod_file, store, "a")


def test_export_from_a_group(store, gnssvod_file, tmp_path):
    adapter = GnssvodVod(bands=BANDS, time_system="GPS")
    import_vod(adapter, gnssvod_file, store, "a")

    path = export_vod(adapter, store, "gnssvod/a", tmp_path / "out.nc")

    with xr.open_dataset(gnssvod_file) as original, xr.open_dataset(path) as exported:
        np.testing.assert_allclose(
            exported["VOD_L2"].values,
            original["VOD_L2"].sel(SV=exported["SV"].values).values,
        )
        prov = Provenance.from_attrs(exported.attrs)
    assert (prov.direction, prov.source) == ("export", "gnssvod/a")
