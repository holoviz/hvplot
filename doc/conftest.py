import os
import sys

from importlib.util import find_spec

import dask

from packaging.version import Version, parse
from bokeh.io.webdriver import webdriver_control

# Examples that are slow to run and/or download large files.
SLOW_EXAMPLES = [
    'gallery/geospatial/datashade_map.ipynb',
]

collect_ignore_glob = [
    'user_guide/Streaming.ipynb',
]

# Slow examples are excluded by default.
if os.getenv('HVPLOT_INCLUDE_SLOW_EXAMPLES'):
    collect_ignore_glob.extend(SLOW_EXAMPLES)

# On MacOs, Python 3.12 and 3.13, got the following error running this:
# `pos = layout(G)`
# => OSError: Format: "dot" not recognized. No formats found.
# Fixed locally by running `dot -c`
if not find_spec('pygraphviz') or (
    sys.platform == 'darwin' and sys.version_info[:2] in [(3, 12), (3, 13)]
):
    collect_ignore_glob += [
        'user_guide/NetworkX.ipynb',
    ]

if not find_spec('geoviews'):
    collect_ignore_glob += [
        'tutorials/getting_started.ipynb',
        'gallery/geospatial/*.ipynb',
        'gallery/gridded/rgb_satellite_imagery.ipynb',
        'user_guide/Explorer.ipynb',
        'user_guide/Geographic_Data.ipynb',
        'user_guide/Integrations.ipynb',
    ]

try:
    import ibis
    import duckdb

    # 'Ibis <= 10.8.0 is incompatible with DuckDB >= 1.4')
    if parse(ibis.__version__) <= parse('10.8.0') and parse(duckdb.__version__) >= parse('1.4'):
        collect_ignore_glob += ['doc/ref/data_libraries.ipynb']
except ImportError:
    pass

try:
    webdriver_control.create()
except RuntimeError:
    # hvplot.save() with bokeh
    collect_ignore_glob += [
        'user_guide/Viewing.ipynb',
        'user_guide/NetworkX.ipynb',
    ]
finally:
    webdriver_control.cleanup()


if Version(dask.__version__).release < (2025, 1, 0):
    # From Dask 2024.3.0 they now use `dask_expr` by default
    # https://github.com/dask/dask/issues/10995
    dask.config.set({'dataframe.query-planning': False})


# https://github.com/pydata/xarray/pull/9182
try:
    import xarray as xr
except ImportError:
    pass
else:
    import numpy as np

    if Version(np.__version__) >= Version('2.0.0') and Version(xr.__version__) <= Version(
        '2024.6.0'
    ):
        collect_ignore_glob += [
            'user_guide/Gridded_Data.ipynb',
        ]


def pytest_runtest_makereport(item, call):
    """
    Skip tests that fail because "the kernel died before replying to kernel_info"
    this is a common error when running the example tests in CI.

    Inspired from: https://stackoverflow.com/questions/32451811

    """
    from _pytest.runner import pytest_runtest_makereport

    tr = pytest_runtest_makereport(item, call)

    if call.excinfo is not None:
        msgs = [
            'Kernel died before replying to kernel_info',
            "Kernel didn't respond in 60 seconds",
        ]
        for msg in msgs:
            if call.excinfo.type is RuntimeError and call.excinfo.value.args[0] in msg:
                tr.outcome = 'skipped'
                tr.wasxfail = f'reason: {msg}'

    return tr
