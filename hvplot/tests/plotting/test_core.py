import numpy as np
import pandas as pd
import pytest
import xarray as xr
from holoviews import Scatter, Store

from hvplot.plotting import hvPlot, hvPlotTabular

DF = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
DA_IMG_BY_TIME = xr.DataArray(
    np.arange(8).reshape((2, 2, 2)),
    {'time': [0, 1], 'lat': [0, 1], 'lon': [0, 1]},
    ['time', 'lat', 'lon'],
).assign_coords(lat1=xr.DataArray([2, 3], dims=['lat']))


def test_define_default_options(hvplot_pandas):
    hvplot = hvPlotTabular(DF, width=42, height=42)
    curve = hvplot(y='y')
    opts = Store.lookup_options('bokeh', curve, 'plot')
    assert opts.options.get('width') == 42
    assert opts.options.get('height') == 42


def test_define_custom_method(hvplot_pandas):
    hvplot = hvPlotTabular(DF, {'custom_scatter': {'width': 42, 'height': 42}})
    custom_scatter = hvplot.custom_scatter(y='y')
    scatter = hvplot.scatter(y='y')
    custom_opts = Store.lookup_options('bokeh', custom_scatter, 'plot')
    opts = Store.lookup_options('bokeh', scatter, 'plot')
    assert custom_opts.options.get('width') == 42
    assert custom_opts.options.get('height') == 42
    assert opts.options.get('width') != 42
    assert opts.options.get('height') != 42


def test_define_customize_method(hvplot_pandas):
    hvplot = hvPlotTabular(DF, {'scatter': {'width': 42, 'height': 42}})
    custom_scatter = hvplot.scatter(y='y')
    curve = hvplot.line(y='y')
    custom_opts = Store.lookup_options('bokeh', custom_scatter, 'plot')
    opts = Store.lookup_options('bokeh', curve, 'plot')
    assert custom_opts.options.get('width') == 42
    assert custom_opts.options.get('height') == 42
    assert opts.options.get('width') != 42
    assert opts.options.get('height') != 42


@pytest.mark.usefixtures('hvplot_pandas', 'disable_param_warnings_as_exceptions')
def test_attempt_to_override_kind_on_method():
    hvplot = hvPlotTabular(DF, {'scatter': {'kind': 'line'}})
    assert isinstance(hvplot.scatter(y='y'), Scatter)


def test_pandas_query_metadata(hvplot_pandas):
    hvplot = hvPlotTabular(DF, query='x>2')
    assert len(hvplot._data) == 2


def test_xarray_isel_scalar_metadata():
    hvplot = hvPlot(DA_IMG_BY_TIME, isel={'time': 1})
    assert hvplot._data.ndim == 2


def test_xarray_isel_nonscalar_metadata():
    hvplot = hvPlot(DA_IMG_BY_TIME, isel={'time': [1]})
    assert hvplot._data.ndim == 3
    assert len(hvplot._data.time) == 1


def test_xarray_sel_metadata():
    hvplot = hvPlot(DA_IMG_BY_TIME, sel={'time': 1})
    assert hvplot._data.ndim == 2
