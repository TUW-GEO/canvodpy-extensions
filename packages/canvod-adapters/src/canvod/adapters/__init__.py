"""Adapters between canvodpy and other GNSS-T programs.

Shared by all programs:

- :mod:`~canvod.adapters.base`: one interface per kind of data canvodpy
  exchanges (:class:`ObservationsAdapter`, :class:`VodAdapter`). Imports
  are checked against canvodpy's contract for that data and carry
  provenance.
- :mod:`~canvod.adapters.provenance`: the provenance model.
- :mod:`~canvod.adapters.store`: VOD store I/O through any VOD adapter.

One subpackage per program, e.g. :mod:`canvod.adapters.gnssvod`.
"""

from importlib.metadata import version

from canvod.adapters.base import ObservationsAdapter, VodAdapter
from canvod.adapters.provenance import Provenance, Tool

__version__ = version("canvod-adapters")

__all__ = [
    "ObservationsAdapter",
    "Provenance",
    "Tool",
    "VodAdapter",
    "__version__",
]
