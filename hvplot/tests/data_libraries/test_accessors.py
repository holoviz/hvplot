"""The `.hvplot` accessor of every data library hvPlot patches.

Each library has an entry in `PATCHED` (objects getting the accessor) and in `CLASSES` (the
classes patched and unpatched). Adding a library is adding its entries and nothing else.
"""

import importlib

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import hvplot
from hvplot.plotting import hvPlot, hvPlotTabular
from hvplot.plotting.core import hvPlotXugrid
from hvplot.util import _HV_VERSION

# The optional libraries are imported when the test runs, to skip it when they are missing.
pytestmark = [
    pytest.mark.filterwarnings('ignore:hvplot.intake is deprecated:FutureWarning'),
    pytest.mark.filterwarnings('ignore:streamz support has been deprecated:FutureWarning'),
]

hv_without_streamz = pytest.mark.skipif(
    _HV_VERSION >= (1, 23, 0), reason='streamz support has been removed in HoloViews >= 1.23.0'
)

DATA = {'x': [1, 3, 5], 'y': [2, 4, 6]}


def lib(name):
    return pytest.importorskip(name)


def ugrid_dataarray():
    xu = lib('xugrid')
    grid = xu.Ugrid2d(
        node_x=np.array([0.0, 1.0, 1.0, 0.0]),
        node_y=np.array([0.0, 0.0, 1.0, 1.0]),
        face_node_connectivity=np.array([[0, 1, 2], [0, 2, 3]]),
        fill_value=-1,
    )
    return xu.UgridDataArray(xr.DataArray([1.0, 2.0, 3.0, 4.0], dims=[grid.node_dimension]), grid)


def streamz_random():
    return lib('streamz.dataframe').Random()


# (library, function making an object, accessor class)
PATCHED = [
    pytest.param('pandas', lambda: pd.Series([0, 1, 2]), hvPlotTabular, id='pandas-series'),
    pytest.param('pandas', lambda: pd.DataFrame(DATA), hvPlotTabular, id='pandas-dataframe'),
    pytest.param(
        'dask',
        lambda: lib('dask.dataframe').from_pandas(pd.Series([0, 1, 2]), npartitions=2),
        hvPlotTabular,
        id='dask-series',
    ),
    pytest.param(
        'dask',
        lambda: lib('dask.dataframe').from_pandas(pd.DataFrame(DATA), npartitions=2),
        hvPlotTabular,
        id='dask-dataframe',
    ),
    pytest.param(
        'polars', lambda: lib('polars').Series([0, 1, 2]), hvPlotTabular, id='polars-series'
    ),
    pytest.param(
        'polars', lambda: lib('polars').DataFrame(DATA), hvPlotTabular, id='polars-dataframe'
    ),
    pytest.param(
        'polars', lambda: lib('polars').LazyFrame(DATA), hvPlotTabular, id='polars-lazyframe'
    ),
    pytest.param(
        'duckdb',
        lambda: lib('duckdb').sql('SELECT 1 AS x, 2 AS y'),
        hvPlotTabular,
        id='duckdb-relation',
    ),
    pytest.param(
        'duckdb',
        lambda: lib('duckdb').connect().execute('SELECT 1 AS x, 2 AS y'),
        hvPlotTabular,
        id='duckdb-connection',
    ),
    pytest.param(
        'ibis', lambda: lib('ibis').memtable(pd.DataFrame(DATA)), hvPlotTabular, id='ibis-table'
    ),
    pytest.param('cudf', lambda: lib('cudf').Series([0, 1, 2]), hvPlotTabular, id='cudf-series'),
    pytest.param('cudf', lambda: lib('cudf').DataFrame(DATA), hvPlotTabular, id='cudf-dataframe'),
    pytest.param(
        'xarray',
        lambda: xr.DataArray([[1, 2], [3, 4]], dims=('y', 'x')),
        hvPlot,
        id='xarray-dataarray',
    ),
    pytest.param(
        'xarray',
        lambda: xr.Dataset({'z': (('y', 'x'), [[1, 2], [3, 4]])}),
        hvPlot,
        id='xarray-dataset',
    ),
    pytest.param('xugrid', ugrid_dataarray, hvPlotXugrid, id='xugrid-dataarray'),
    pytest.param(
        'streamz',
        streamz_random,
        hvPlotTabular,
        marks=hv_without_streamz,
        id='streamz-dataframe',
    ),
    pytest.param(
        'streamz',
        lambda: streamz_random().x,
        hvPlotTabular,
        marks=hv_without_streamz,
        id='streamz-series',
    ),
    pytest.param(
        'streamz',
        lambda: streamz_random().groupby('x').sum(),
        hvPlotTabular,
        marks=hv_without_streamz,
        id='streamz-dataframes',
    ),
    pytest.param(
        'streamz',
        lambda: streamz_random().groupby('x').sum().y,
        hvPlotTabular,
        marks=hv_without_streamz,
        id='streamz-seriess',
    ),
]

# library: (module of the classes, names of the classes, names of the attributes added to them)
BOTH = ['hvplot', 'interactive']
CLASSES = {
    'pandas': ('pandas', ['DataFrame', 'Series'], BOTH),
    'dask': ('dask.dataframe', ['DataFrame', 'Series'], BOTH),
    'polars': ('polars', ['DataFrame', 'Series', 'LazyFrame'], ['hvplot']),
    'duckdb': ('duckdb', ['DuckDBPyRelation', 'DuckDBPyConnection'], ['hvplot']),
    'ibis': ('ibis', ['Expr'], ['hvplot']),
    'cudf': ('cudf', ['DataFrame', 'Series'], BOTH),
    'intake': ('intake.source.base', ['DataSource'], ['hvplot']),
    'streamz': (
        'streamz.dataframe',
        ['DataFrame', 'DataFrames', 'Series', 'Seriess'],
        ['hvplot'],
    ),
    'xarray': ('xarray', ['Dataset', 'DataArray'], BOTH),
    'xugrid': ('xugrid', ['UgridDataArray', 'UgridDataset'], ['hvplot']),
}


@pytest.mark.parametrize(('library', 'make_object', 'accessor'), PATCHED)
def test_accessor_patched(library, make_object, accessor):
    obj = make_object()
    importlib.import_module(f'hvplot.{library}')
    assert isinstance(obj.hvplot, accessor)


@pytest.mark.parametrize('library', CLASSES)
def test_unpatch(library):
    module, class_names, attrs = CLASSES[library]
    classes = [getattr(lib(module), name) for name in class_names]
    ext = importlib.import_module(f'hvplot.{library}')

    ext._unpatch()
    # vars() and not hasattr() as some classes inherit an `hvplot` attribute (e.g. intake).
    assert not any(attr in vars(cls) for cls in classes for attr in attrs)
    assert f'hvplot.{library}' not in hvplot._module_extensions

    # Ends patched, the _isolate_hvplot fixture unpatches it after the test.
    ext.patch()
    assert all(attr in vars(cls) for cls in classes for attr in attrs)
    assert f'hvplot.{library}' in hvplot._module_extensions
    if library == 'polars':
        # Polars also records the names of the registered accessors.
        assert all('hvplot' in cls._accessors for cls in classes)


@pytest.mark.parametrize('library', CLASSES)
def test_patch_without_library(library, block_import, monkeypatch):
    lib(library)
    ext = importlib.import_module(f'hvplot.{library}')

    block_import(library)
    # Some modules only import the library when they are not patched yet.
    monkeypatch.setattr(hvplot, '_module_extensions', set())
    with pytest.raises(ImportError, match=f'(?i){library} could not be imported'):
        ext.patch()
