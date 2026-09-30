"""
Tests patching of supported libraries
"""

import sys
from importlib import import_module, reload
from unittest import SkipTest, TestCase

import holoviews as hv
import numpy as np
import pandas as pd
import pytest

import hvplot
from hvplot.plotting import hvPlot, hvPlotTabular
from hvplot.util import _HV_VERSION


@pytest.mark.parametrize('module_name', ['pandas', 'xarray'])
@pytest.mark.parametrize('backend', ['matplotlib', 'plotly'])
def test_import_preserves_selected_backend(module_name, backend):
    original_backend = hv.Store.current_backend
    original_compatibility = hvplot.extension.compatibility
    module = import_module(f'hvplot.{module_name}')
    try:
        hvplot.extension(backend, compatibility='bokeh')
        reload(module)
        assert hv.Store.current_backend == backend
        assert hvplot.extension.compatibility == 'bokeh'
    finally:
        hvplot.extension(original_backend, compatibility=original_compatibility)


@pytest.mark.parametrize('module_name', ['pandas', 'xarray'])
def test_patch_loads_default_backend(module_name, monkeypatch):
    original_backend = hv.Store.current_backend
    original_compatibility = hvplot.extension.compatibility
    module = import_module(f'hvplot.{module_name}')
    monkeypatch.setattr(hv.extension, '_loaded', False)
    try:
        hv.Store.set_current_backend('bokeh')
        module.patch()
        assert hv.Store.current_backend == 'bokeh'
        data = (
            pd.Series([1, 2])
            if module_name == 'pandas'
            else module.xr.DataArray([1, 2], dims=['x'], name='value')
        )
        assert hv.render(data.hvplot.line()) is not None
    finally:
        hvplot.extension(original_backend, compatibility=original_compatibility)


@pytest.mark.parametrize('module_name', ['pandas', 'xarray'])
def test_patch_honors_explicit_backend(module_name):
    original_backend = hv.Store.current_backend
    original_compatibility = hvplot.extension.compatibility
    module = import_module(f'hvplot.{module_name}')
    try:
        hvplot.extension('matplotlib')
        module.patch(extension='plotly')
        assert hv.Store.current_backend == 'plotly'
    finally:
        hvplot.extension(original_backend, compatibility=original_compatibility)


class TestPatchPandas(TestCase):
    def setUp(self):
        import hvplot.pandas  # noqa: F401

    def test_pandas_series_patched(self):
        series = pd.Series([0, 1, 2])
        self.assertIsInstance(series.hvplot, hvPlotTabular)

    def test_pandas_dataframe_patched(self):
        df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
        self.assertIsInstance(df.hvplot, hvPlotTabular)


class TestPatchDask(TestCase):
    def setUp(self):
        try:
            import dask.dataframe  # noqa: F401
        except ImportError:
            raise SkipTest('Dask not available')
        import hvplot.dask  # noqa: F401

    def test_dask_series_patched(self):
        import dask.dataframe as dd

        series = pd.Series([0, 1, 2])
        dseries = dd.from_pandas(series, 2)
        self.assertIsInstance(dseries.hvplot, hvPlotTabular)

    def test_dask_dataframe_patched(self):
        import dask.dataframe as dd

        df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
        ddf = dd.from_pandas(df, 2)
        self.assertIsInstance(ddf.hvplot, hvPlotTabular)


class TestPatchXArray(TestCase):
    def setUp(self):
        try:
            import xarray  # noqa: F401
        except ImportError:
            raise SkipTest('XArray not available')
        import hvplot.xarray  # noqa: F401

    def test_xarray_dataarray_patched(self):
        import xarray as xr

        array = np.random.rand(100, 100)
        xr_array = xr.DataArray(array, coords={'x': range(100), 'y': range(100)}, dims=('y', 'x'))
        self.assertIsInstance(xr_array.hvplot, hvPlot)

    def test_xarray_dataset_patched(self):
        import xarray as xr

        array = np.random.rand(100, 100)
        xr_array = xr.DataArray(array, coords={'x': range(100), 'y': range(100)}, dims=('y', 'x'))
        xr_ds = xr.Dataset({'z': xr_array})
        self.assertIsInstance(xr_ds.hvplot, hvPlot)


class TestPatchStreamz(TestCase):
    def setUp(self):
        if _HV_VERSION >= (1, 23, 0):
            raise SkipTest('streamz support has been removed in HoloViews >= 1.23.0')
        try:
            import streamz  # noqa: F401
        except ImportError:
            raise SkipTest('streamz not available')
        import hvplot.streamz  # noqa: F401

    def test_streamz_dataframe_patched(self):
        from streamz.dataframe import Random

        random_df = Random()
        self.assertIsInstance(random_df.hvplot, hvPlotTabular)

    def test_streamz_series_patched(self):
        from streamz.dataframe import Random

        random_df = Random()
        self.assertIsInstance(random_df.x.hvplot, hvPlotTabular)

    def test_streamz_dataframes_patched(self):
        from streamz.dataframe import Random

        random_df = Random()
        self.assertIsInstance(random_df.groupby('x').sum().hvplot, hvPlotTabular)

    def test_streamz_seriess_patched(self):
        from streamz.dataframe import Random

        random_df = Random()
        self.assertIsInstance(random_df.groupby('x').sum().y.hvplot, hvPlotTabular)


class TestPatchPolars(TestCase):
    def setUp(self):
        if sys.platform == 'win32' and sys.version_info[:2] == (3, 9):
            raise SkipTest('stack overflow error')
        try:
            import polars  # noqa: F401
        except ImportError:
            raise SkipTest('Polars not available')
        import hvplot.polars  # noqa: F401

    def test_polars_series_patched(self):
        import polars as pl

        pseries = pl.Series([0, 1, 2])
        self.assertIsInstance(pseries.hvplot, hvPlotTabular)

    def test_polars_dataframe_patched(self):
        import polars as pl

        pdf = pl.DataFrame({'x': [1, 3, 5], 'y': [2, 4, 6]})
        self.assertIsInstance(pdf.hvplot, hvPlotTabular)

    def test_polars_lazyframe_patched(self):
        import polars as pl

        pldf = pl.LazyFrame({'x': [1, 3, 5], 'y': [2, 4, 6]})
        self.assertIsInstance(pldf.hvplot, hvPlotTabular)


class TestPatchDuckDB(TestCase):
    def setUp(self):
        try:
            import duckdb  # noqa: F401
        except ImportError:
            raise SkipTest('DuckDB not available')
        import hvplot.duckdb  # noqa: F401

    def test_duckdb_relation_patched(self):
        import duckdb

        df = pd.DataFrame({'x': [1, 2, 3], 'y': [1, 2, 3]})
        connection = duckdb.connect(':memory:')
        relation = duckdb.from_df(df, connection=connection)
        self.assertIsInstance(relation.hvplot, hvPlotTabular)

    def test_duckdb_connection_patched(self):
        import duckdb

        df = pd.DataFrame({'x': [1, 2, 3], 'y': [1, 2, 3]})
        connection = duckdb.connect(':memory:')
        duckdb.from_df(df, connection=connection).to_view('test_connection')
        self.assertIsInstance(
            connection.execute('SELECT * FROM test_connection').hvplot, hvPlotTabular
        )
