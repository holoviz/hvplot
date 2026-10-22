import holoviews as hv
import numpy as np
import pandas as pd
import pytest
import xarray as xr
from holoviews import Store

pytestmark = pytest.mark.usefixtures('hvplot_pandas')

pandas_and_dask = pytest.mark.parametrize('tabular_lib', ['pandas', 'dask'], indirect=True)


@pytest.fixture
def df():
    return pd.DataFrame(
        [[1, 2, 'A', 0.1], [3, 4, 'B', 0.2], [5, 6, 'C', 0.3]],
        columns=['x', 'y', 'category', 'number'],
    )


@pytest.fixture
def xy_df():
    return pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])


def test_xaxis_yaxis_visible_by_default(df, backend):
    plot = df.hvplot.scatter('x', 'y', c='category')
    opts = Store.lookup_options(backend, plot, 'plot')
    assert 'xaxis' not in opts.kwargs
    assert 'yaxis' not in opts.kwargs


@pytest.mark.parametrize('value', [None, False])
def test_xaxis_yaxis_hidden(df, backend, value):
    plot = df.hvplot.scatter('x', 'y', c='category', xaxis=value, yaxis=value)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['xaxis'] is None
    assert opts.kwargs['yaxis'] is None


def test_xaxis_yaxis_position(df, backend):
    plot = df.hvplot.scatter('x', 'y', c='category', xaxis='top', yaxis='right')
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['xaxis'] == 'top'
    assert opts.kwargs['yaxis'] == 'right'


def test_xaxis_yaxis_none_from_holoviews_defaults(df, backend):
    hv.opts.defaults(hv.opts.Scatter(xaxis=None, yaxis=None))
    plot = df.hvplot.scatter('x', 'y', c='category')
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['xaxis'] is None
    assert opts.kwargs['yaxis'] is None


def test_xaxis_yaxis_position_from_holoviews_defaults(df, backend):
    hv.opts.defaults(hv.opts.Scatter(xaxis='top', yaxis='right'))
    plot = df.hvplot.scatter('x', 'y', c='category')
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['xaxis'] == 'top'
    assert opts.kwargs['yaxis'] == 'right'


def test_xaxis_yaxis_override_holoviews_defaults_none(df, backend):
    hv.opts.defaults(hv.opts.Scatter(xaxis=None, yaxis=None))
    plot = df.hvplot.scatter('x', 'y', c='category', xaxis=True, yaxis=True)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['xaxis'] is True
    assert opts.kwargs['yaxis'] is True


def test_xaxis_yaxis_override_holoviews_defaults_position(df, backend):
    hv.opts.defaults(hv.opts.Scatter(xaxis='top', yaxis='right'))
    plot = df.hvplot.scatter('x', 'y', c='category', xaxis='top-bare', yaxis='right-bare')
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['xaxis'] == 'top-bare'
    assert opts.kwargs['yaxis'] == 'right-bare'


def test_loglog(df, backend):
    plot = df.hvplot.scatter('x', 'y', c='category', loglog=True)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['logx'] is True
    assert opts.kwargs['logy'] is True
    assert opts.kwargs.get('logz') is None


def test_logy(df, backend):
    plot = df.hvplot.scatter('x', 'y', c='category', logy=True)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['logx'] is False
    assert opts.kwargs['logy'] is True
    assert opts.kwargs.get('logz') is None


only_bokeh_defaults = pytest.mark.xfail(reason='hvPlot only reads the bokeh HoloViews defaults')


@pytest.mark.parametrize(
    'backend',
    [
        'bokeh',
        pytest.param('matplotlib', marks=only_bokeh_defaults),
        pytest.param('plotly', marks=only_bokeh_defaults),
    ],
    indirect=True,
)
def test_logx_from_holoviews_defaults(df, backend):
    hv.opts.defaults(hv.opts.Scatter(logx=True))
    plot = df.hvplot.scatter('x', 'y', c='category')
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['logx'] is True
    assert opts.kwargs['logy'] is False
    assert opts.kwargs.get('logz') is None


def test_logx_override_holoviews_defaults(df, backend):
    hv.opts.defaults(hv.opts.Scatter(logx=True))
    plot = df.hvplot.scatter('x', 'y', c='category', logx=False)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['logx'] is False
    assert opts.kwargs['logy'] is False
    assert opts.kwargs.get('logz') is None


@pandas_and_dask
@pytest.mark.parametrize('kind', ['line', 'area', 'scatter'])
def test_xlim_ylim_tidy(tabular_lib, xy_df, kind):
    df = tabular_lib(xy_df)
    plot = df.hvplot(x='x', y='y', kind=kind, xlim=(0, 3), ylim=(5, 10))
    opts = Store.lookup_options('bokeh', plot, 'plot').options
    assert opts['xlim'] == (0, 3)
    assert opts['ylim'] == (5, 10)


@pandas_and_dask
@pytest.mark.parametrize('kind', ['line', 'area', 'scatter'])
def test_xlim_ylim_wide(tabular_lib, xy_df, kind):
    df = tabular_lib(xy_df)
    plot = df.hvplot(kind=kind, xlim=(0, 3), ylim=(5, 10))
    opts = Store.lookup_options('bokeh', plot.last, 'plot').options
    assert opts['xlim'] == (0, 3)
    assert opts['ylim'] == (5, 10)


@pandas_and_dask
def test_shared_axes_false_hist_subplots(tabular_lib, xy_df):
    df = tabular_lib(xy_df)
    plots = df.hvplot.hist(subplots=True, shared_axes=False)
    plot_0 = plots.grid_items()[0, 0][1]
    plot_1 = plots.grid_items()[0, 1][1]
    assert plot_0.opts['axiswise']
    assert plot_0.range('x') == (1, 5)
    assert plot_1.range('y') == (2, 6)


@pandas_and_dask
def test_shared_axes_true_hist_subplots(tabular_lib, xy_df):
    df = tabular_lib(xy_df)
    plots = df.hvplot.hist(subplots=True, shared_axes=True)
    plot_0 = plots.grid_items()[0, 0][1]
    plot_1 = plots.grid_items()[0, 1][1]
    assert not plot_0.opts['axiswise']
    assert plot_0.range('x') == (1, 6)
    assert plot_1.range('y') == (1, 6)


def test_subcoordinate_y_bool():
    df = pd.DataFrame(np.random.random((10, 3)), columns=list('ABC'))
    plot = df.hvplot.line(subcoordinate_y=True)
    opts = Store.lookup_options('bokeh', plot, 'plot')
    assert opts.kwargs['subcoordinate_y'] is True


def test_subcoordinate_y_dict():
    df = pd.DataFrame(np.random.random((10, 3)), columns=list('ABC'))
    plot = df.hvplot.line(subcoordinate_y={'subcoordinate_scale': 2})
    opts = Store.lookup_options('bokeh', plot, 'plot')
    assert opts.kwargs['subcoordinate_y'] is True
    assert opts.kwargs['subcoordinate_scale'] == 2


@pytest.fixture
def da():
    return xr.DataArray(
        data=np.arange(16).reshape((2, 2, 2, 2)),
        coords={'time': [0, 1], 'y': [0, 1], 'x': [0, 1], 'band': [0, 1]},
        dims=['time', 'y', 'x', 'band'],
        name='test',
    )


@pytest.fixture
def da2():
    return xr.DataArray(
        data=np.arange(27).reshape((3, 3, 3)),
        coords={'y': [0, 1, 2], 'x': [0, 1, 2]},
        dims=['y', 'x', 'other'],
        name='test2',
    )


def test_title_dataarray_2d(hvplot_xarray, da, backend):
    plot = da.sel(time=0, band=0).hvplot()  # Image plot
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['title'] == 'time = 0, band = 0'


def test_title_dataarray_1d(hvplot_xarray, da, backend):
    plot = da.sel(time=0, band=0, x=0).hvplot()  # Line plot
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['title'] == 'time = 0, x = 0, band = 0'


def test_title_dataarray_1d_and_by(hvplot_xarray, da, backend):
    plot = da.sel(time=0, band=0, x=[0, 1]).hvplot(by='x')  # Line plot with hue/by
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['title'] == 'time = 0, band = 0'


def test_title_override(hvplot_xarray, da, backend):
    plot = da.sel(time=0, band=0).hvplot(title='title')  # Image plot
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['title'] == 'title'


def test_title_dataarray_4d_line_none(hvplot_xarray, da, backend):
    plot = da.hvplot.line(dynamic=False)  # Line plot with widgets
    opts = Store.lookup_options(backend, plot.last, 'plot')
    assert 'title' not in opts.kwargs


def test_title_dataarray_3d_histogram(hvplot_xarray, da, backend):
    plot = da.sel(time=0).hvplot()  # Histogram and no widgets
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['title'] == 'time = 0'


def test_title_dataset_one_var_like_dataarray(hvplot_xarray, da, backend):
    ds = xr.Dataset({'foo': da})
    plot = ds.sel(time=0, band=0).hvplot()  # Image plot
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['title'] == 'time = 0, band = 0'


def test_title_dataset_scatter(hvplot_xarray, da, da2, backend):
    ds = xr.Dataset({'foo': da, 'bar': da2})
    plot = ds.sel(time=0, band=0, x=0, y=0).hvplot.scatter(x='foo', y='bar')
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['title'] == 'time = 0, y = 0, x = 0, band = 0'


def test_cticks(hvplot_xarray, da2):
    plot = da2.isel(other=0).hvplot(cticks=[5, 10])
    handles = hv.renderer('bokeh').get_plot(plot).handles
    assert handles['colorbar'].ticker.ticks == [5, 10]
