import pandas as pd
import panel as pn
import pytest

from holoviews.util.transform import dim

import hvplot.pandas  # noqa
from hvplot import bind
from hvplot.interactive import Interactive
from hvplot.xarray import XArrayInteractive

try:
    import xarray as xr
    import hvplot.xarray  # noqa
except ImportError:
    xr = None

xr_available = pytest.mark.skipif(xr is None, reason="requires xarray")

def test_interactive_pandas_dataframe():
    df = pd._testing.makeMixedDataFrame()

    dfi = Interactive(df)

    assert type(dfi) is Interactive
    assert dfi._obj is df
    assert dfi._fn is None
    assert dfi._transform == dim('*')

def test_interactive_pandas_series():
    df = pd._testing.makeMixedDataFrame()

    dfi = Interactive(df.A)

    assert type(dfi) is Interactive
    assert dfi._obj is df.A
    assert dfi._fn is None
    assert dfi._transform == dim('*')

@xr_available
def test_interactive_xarray_dataarray():
    ds = xr.tutorial.load_dataset('air_temperature')

    dsi = Interactive(ds.air)

    assert type(dsi) is XArrayInteractive
    assert (dsi._obj == ds.air).all()
    assert dsi._fn is None
    assert dsi._transform == dim('air')

@xr_available
def test_interactive_xarray_dataset():
    ds = xr.tutorial.load_dataset('air_temperature')

    dsi = Interactive(ds)

    assert type(dsi) is XArrayInteractive
    assert dsi._obj is ds
    assert dsi._fn is None
    assert dsi._transform == dim('*')

def test_interactive_pandas_function():
    df = pd._testing.makeMixedDataFrame()

    select = pn.widgets.Select(options=list(df.columns))

    def sel_col(col):
        return df[col]

    dfi = Interactive(bind(sel_col, select))
    assert type(dfi) is Interactive
    assert dfi._obj is df.A
    assert isinstance(dfi._fn, pn.param.ParamFunction)
    assert dfi._transform == dim('*')

    select.value = 'B'
    assert dfi._obj is df.B

@xr_available
def test_interactive_xarray_function():
    ds = xr.tutorial.load_dataset('air_temperature')
    ds['air2'] = ds.air*2

    select = pn.widgets.Select(options=list(ds))

    def sel_col(sel):
        return ds[sel]

    dsi = Interactive(bind(sel_col, select))

    assert type(dsi) is XArrayInteractive
    assert isinstance(dsi._fn, pn.param.ParamFunction)
    assert dsi._transform == dim('air')

    select.value = 'air2'
    assert (dsi._obj == ds.air2).all()
    assert dsi._transform == dim('air2')


def test_interactive_pandas_dataframe_accessor():
    df = pd._testing.makeMixedDataFrame()
    dfi = df.interactive()

    assert dfi.hvplot(kind="scatter")._transform == dfi.hvplot.scatter()._transform

    with pytest.raises(TypeError):
        dfi.hvplot.scatter(kind="area")


@xr_available
def test_interactive_xarray_dataset_accessor():
    ds = xr.tutorial.load_dataset('air_temperature')
    dsi = ds.air.interactive

    assert dsi.hvplot(kind="line")._transform == dsi.hvplot.line()._transform

    with pytest.raises(TypeError):
        dsi.hvplot.line(kind="area")
