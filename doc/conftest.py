from importlib.util import find_spec

import dask

from packaging.version import Version
from bokeh.io.webdriver import webdriver_control


collect_ignore_glob = [
    'user_guide/Streaming.ipynb',
]

if not find_spec('pygraphviz'):
    collect_ignore_glob += [
        'user_guide/NetworkX.ipynb',
    ]

if not find_spec('geoviews'):
    collect_ignore_glob += [
        'getting_started/hvplot.ipynb',
        'reference/geopandas/*.ipynb',
        'reference/xarray/contour.ipynb',
        'reference/xarray/contourf.ipynb',
        'reference/xarray/image.ipynb',
        'reference/xarray/quadmesh.ipynb',
        'reference/xarray/vectorfield.ipynb',
        'user_guide/Explorer.ipynb',
        'user_guide/Geographic_Data.ipynb',
        'user_guide/Integrations.ipynb',
    ]

if not find_spec('ibis'):
    collect_ignore_glob += [
        'user_guide/Integrations.ipynb',
    ]

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
