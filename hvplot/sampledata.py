"""
This module provides access to sample datasets for use with hvPlot. The
``hvsampledata`` package needs to be installed for these datasets to be
available.
"""

_hvsampledata_available = False

try:
    from hvsampledata import *  # noqa: F403

    _hvsampledata_available = True
except ImportError:
    pass


def __getattr__(name):
    if not _hvsampledata_available:
        msg = (
            "Install the package 'hvsampledata' to access datasets from the "
            "'sampledata' module of hvPlot."
        )
        raise AttributeError(msg)
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
