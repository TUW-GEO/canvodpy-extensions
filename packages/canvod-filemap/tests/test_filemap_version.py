from importlib.metadata import version

import canvod.filemap


def test_version_is_the_installed_package_version() -> None:
    # A version written into the code goes stale at the next release
    assert canvod.filemap.__version__ == version("canvod-filemap")
