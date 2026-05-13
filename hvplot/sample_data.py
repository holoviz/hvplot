"""
Deprecated. Use ``hvplot.sampledata`` instead.

This module previously loaded hvPlot sample data using an intake catalogue.
It has been replaced by ``hvplot.sampledata``, which uses the ``hvsampledata``
package and does not require intake.
"""

import warnings

from .util import _find_stack_level
from . import sampledata as _sampledata

warnings.warn(
    "The 'hvplot.sample_data' module is deprecated and will be removed in a "
    "future version. Use 'hvplot.sampledata' instead.",
    FutureWarning,
    stacklevel=_find_stack_level(),
)

from .sampledata import *  # noqa: F401, F403, E402


def __getattr__(name):
    if not _sampledata._hvsampledata_available:
        raise AttributeError(
            "Install the package 'hvsampledata' to access datasets from "
            "'hvplot.sample_data' (deprecated; use 'hvplot.sampledata' instead)."
        )
    raise AttributeError(f"module 'hvplot.sample_data' has no attribute {name!r}")
