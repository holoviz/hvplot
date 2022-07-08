import pandas as pd
import panel as pn

from holoviews.util.transform import dim

from hvplot import bind
from hvplot.interactive import Interactive
from hvplot.xarray import XArrayInteractive


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

def test_interactive_xarray_dataarray():
    import xarray as xr
    ds = xr.tutorial.load_dataset('air_temperature')

    dsi = Interactive(ds.air)

    assert type(dsi) is XArrayInteractive
    assert (dsi._obj == ds.air).all()
    assert dsi._fn is None
    assert dsi._transform == dim('air')

def test_interactive_xarray_dataset():
    import xarray as xr
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

def test_interactive_xarray_function():
    import xarray as xr
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
