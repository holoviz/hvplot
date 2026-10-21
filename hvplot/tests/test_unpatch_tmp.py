"""
Patch/unpatch round trips of the data-library extension modules.

Temporary, to be dissolved into the data_libraries/ tests.
"""

import sys

import pytest

import hvplot
import hvplot.pandas


def _patched(classes, attrs):
    # vars() and not hasattr() as intake's DataSource inherits its own `hvplot` property.
    return all(attr in vars(cls) for cls in classes for attr in attrs)


def _unpatched(classes, attrs):
    return not any(attr in vars(cls) for cls in classes for attr in attrs)


def _round_trip(ext, classes, attrs=('hvplot',)):
    # Leave the state as found, other tests in the same process rely on it.
    was_patched = ext.__name__ in hvplot._module_extensions

    ext.patch()
    assert _patched(classes, attrs)
    assert ext.__name__ in hvplot._module_extensions

    ext._unpatch()
    assert _unpatched(classes, attrs)
    assert ext.__name__ not in hvplot._module_extensions

    ext.patch()
    assert _patched(classes, attrs)
    assert ext.__name__ in hvplot._module_extensions

    if not was_patched:
        ext._unpatch()


def test_unpatch_pandas():
    import pandas as pd

    _round_trip(hvplot.pandas, [pd.DataFrame, pd.Series], ['hvplot', 'interactive'])


def test_unpatch_dask():
    dd = pytest.importorskip('dask.dataframe')
    import hvplot.dask

    _round_trip(hvplot.dask, [dd.DataFrame, dd.Series], ['hvplot', 'interactive'])


def test_unpatch_xarray():
    xr = pytest.importorskip('xarray')
    import hvplot.xarray

    _round_trip(hvplot.xarray, [xr.Dataset, xr.DataArray], ['hvplot', 'interactive'])


def test_unpatch_polars():
    pl = pytest.importorskip('polars')
    import hvplot.polars

    classes = [pl.DataFrame, pl.Series, pl.LazyFrame]
    _round_trip(hvplot.polars, classes)

    hvplot.polars._unpatch()
    assert not any('hvplot' in cls._accessors for cls in classes)
    hvplot.polars.patch()
    assert all('hvplot' in cls._accessors for cls in classes)


def test_unpatch_duckdb():
    duckdb = pytest.importorskip('duckdb')
    import hvplot.duckdb

    _round_trip(hvplot.duckdb, [duckdb.DuckDBPyRelation, duckdb.DuckDBPyConnection])


def test_unpatch_ibis():
    ibis = pytest.importorskip('ibis')
    import hvplot.ibis

    _round_trip(hvplot.ibis, [ibis.Expr])


@pytest.mark.filterwarnings('ignore:hvplot.intake is deprecated:FutureWarning')
def test_unpatch_intake():
    intake = pytest.importorskip('intake')
    import hvplot.intake

    _round_trip(hvplot.intake, [intake.source.base.DataSource])
    # testdeprecations.py expects the import-time warning.
    sys.modules.pop('hvplot.intake', None)


@pytest.mark.filterwarnings('ignore:streamz support has been deprecated:FutureWarning')
def test_unpatch_streamz():
    sdf = pytest.importorskip('streamz.dataframe')
    import hvplot.streamz

    classes = [sdf.DataFrame, sdf.DataFrames, sdf.Series, sdf.Seriess]
    _round_trip(hvplot.streamz, classes)


def test_unpatch_xugrid():
    xu = pytest.importorskip('xugrid')
    import hvplot.xugrid

    _round_trip(hvplot.xugrid, [xu.UgridDataArray, xu.UgridDataset])
