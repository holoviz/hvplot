"""
Tests patching of supported libraries
"""

import sys

import numpy as np
import pandas as pd
import pytest

from hvplot.plotting import hvPlot, hvPlotTabular
from hvplot.util import _HV_VERSION


class TestPatchPandas:
    def setup_method(self):
        import hvplot.pandas  # noqa: F401

    def test_pandas_series_patched(self):
        series = pd.Series([0, 1, 2])
        assert isinstance(series.hvplot, hvPlotTabular)

    def test_pandas_dataframe_patched(self):
        df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
        assert isinstance(df.hvplot, hvPlotTabular)


class TestPatchDask:
    def setup_method(self):
        pytest.importorskip('dask.dataframe', reason='Dask not available')
        import hvplot.dask  # noqa: F401

    def test_dask_series_patched(self):
        import dask.dataframe as dd

        series = pd.Series([0, 1, 2])
        dseries = dd.from_pandas(series, 2)
        assert isinstance(dseries.hvplot, hvPlotTabular)

    def test_dask_dataframe_patched(self):
        import dask.dataframe as dd

        df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
        ddf = dd.from_pandas(df, 2)
        assert isinstance(ddf.hvplot, hvPlotTabular)


class TestPatchXArray:
    def setup_method(self):
        pytest.importorskip('xarray', reason='XArray not available')
        import hvplot.xarray  # noqa: F401

    def test_xarray_dataarray_patched(self):
        import xarray as xr

        array = np.random.rand(100, 100)
        xr_array = xr.DataArray(array, coords={'x': range(100), 'y': range(100)}, dims=('y', 'x'))
        assert isinstance(xr_array.hvplot, hvPlot)

    def test_xarray_dataset_patched(self):
        import xarray as xr

        array = np.random.rand(100, 100)
        xr_array = xr.DataArray(array, coords={'x': range(100), 'y': range(100)}, dims=('y', 'x'))
        xr_ds = xr.Dataset({'z': xr_array})
        assert isinstance(xr_ds.hvplot, hvPlot)


class TestPatchStreamz:
    def setup_method(self):
        if _HV_VERSION >= (1, 23, 0):
            pytest.skip('streamz support has been removed in HoloViews >= 1.23.0')
        pytest.importorskip('streamz', reason='streamz not available')
        import hvplot.streamz  # noqa: F401

    def test_streamz_dataframe_patched(self):
        from streamz.dataframe import Random

        random_df = Random()
        assert isinstance(random_df.hvplot, hvPlotTabular)

    def test_streamz_series_patched(self):
        from streamz.dataframe import Random

        random_df = Random()
        assert isinstance(random_df.x.hvplot, hvPlotTabular)

    def test_streamz_dataframes_patched(self):
        from streamz.dataframe import Random

        random_df = Random()
        assert isinstance(random_df.groupby('x').sum().hvplot, hvPlotTabular)

    def test_streamz_seriess_patched(self):
        from streamz.dataframe import Random

        random_df = Random()
        assert isinstance(random_df.groupby('x').sum().y.hvplot, hvPlotTabular)


class TestPatchPolars:
    def setup_method(self):
        if sys.platform == 'win32' and sys.version_info[:2] == (3, 9):
            pytest.skip('stack overflow error')
        pytest.importorskip('polars', reason='Polars not available')
        import hvplot.polars  # noqa: F401

    def test_polars_series_patched(self):
        import polars as pl

        pseries = pl.Series([0, 1, 2])
        assert isinstance(pseries.hvplot, hvPlotTabular)

    def test_polars_dataframe_patched(self):
        import polars as pl

        pdf = pl.DataFrame({'x': [1, 3, 5], 'y': [2, 4, 6]})
        assert isinstance(pdf.hvplot, hvPlotTabular)

    def test_polars_lazyframe_patched(self):
        import polars as pl

        pldf = pl.LazyFrame({'x': [1, 3, 5], 'y': [2, 4, 6]})
        assert isinstance(pldf.hvplot, hvPlotTabular)


class TestPatchDuckDB:
    def setup_method(self):
        pytest.importorskip('duckdb', reason='DuckDB not available')
        import hvplot.duckdb  # noqa: F401

    def test_duckdb_relation_patched(self):
        import duckdb

        df = pd.DataFrame({'x': [1, 2, 3], 'y': [1, 2, 3]})
        connection = duckdb.connect(':memory:')
        relation = duckdb.from_df(df, connection=connection)
        assert isinstance(relation.hvplot, hvPlotTabular)

    def test_duckdb_connection_patched(self):
        import duckdb

        df = pd.DataFrame({'x': [1, 2, 3], 'y': [1, 2, 3]})
        connection = duckdb.connect(':memory:')
        duckdb.from_df(df, connection=connection).to_view('test_connection')
        assert isinstance(
            connection.execute('SELECT * FROM test_connection').hvplot, hvPlotTabular
        )
