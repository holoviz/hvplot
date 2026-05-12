"""
Deprecated. Use ``hvplot.sampledata`` instead.

Loads hvPlot sample data using intake catalogue.
"""

import os
import warnings

from .util import _find_stack_level

warnings.warn(
    "The 'hvplot.sample_data' module is deprecated and will be removed in a "
    "future version. Use 'hvplot.sampledata' instead.",
    FutureWarning,
    stacklevel=_find_stack_level(),
)

warnings.warn(
    "The 'hvplot.sample_data' module is deprecated and will be removed in a "
    "future version. Use 'hvplot.sampledata' instead.",
    FutureWarning,
    stacklevel=_find_stack_level(),
)

from .sampledata import *  # noqa: F401, F403, E402
from .sampledata import __getattr__  # noqa: F401, E402
