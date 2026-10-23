from importlib.metadata import version

import canvod.adapters


def test_version_is_the_installed_package_version() -> None:
    # A version written into the code goes stale at the next release
    assert canvod.adapters.__version__ == version("canvod-adapters")
