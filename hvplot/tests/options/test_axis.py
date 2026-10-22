import holoviews as hv
import numpy as np
import pandas as pd
import pytest
import xarray as xr
from bokeh.models import NumeralTickFormatter
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
def test_xaxis_hidden(df, backend, value):
    plot = df.hvplot.scatter('x', 'y', c='category', xaxis=value)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['xaxis'] is None
    assert 'yaxis' not in opts.kwargs


@pytest.mark.parametrize('value', [None, False])
def test_yaxis_hidden(df, backend, value):
    plot = df.hvplot.scatter('x', 'y', c='category', yaxis=value)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['yaxis'] is None
    assert 'xaxis' not in opts.kwargs


def test_xaxis_position(df, backend):
    plot = df.hvplot.scatter('x', 'y', c='category', xaxis='top')
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['xaxis'] == 'top'


def test_yaxis_position(df, backend):
    plot = df.hvplot.scatter('x', 'y', c='category', yaxis='right')
    opts = Store.lookup_options(backend, plot, 'plot')
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


@pytest.mark.parametrize(
    'backend',
    [
        'bokeh',
        'matplotlib',
        pytest.param(
            'plotly',
            marks=pytest.mark.render_xfail(reason='HoloViews: plotly does not accept xaxis=True'),
        ),
    ],
    indirect=True,
)
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


only_bokeh_defaults = pytest.mark.xfail(
    reason='BUG: HoloViews defaults are only read for bokeh (converter.py)'
)


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


@pytest.mark.parametrize('ylim', [(None, 10), (5, None)])
def test_ylim_one_bound_unset(xy_df, ylim, backend):
    plot = xy_df.hvplot.scatter('x', 'y', ylim=ylim)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['ylim'] == ylim


@pandas_and_dask
def test_shared_axes_false_hist_subplots(tabular_lib, xy_df):
    df = tabular_lib(xy_df)
    plots = df.hvplot.hist(subplots=True, shared_axes=False)
    plot_0 = plots.grid_items()[0, 0][1]
    plot_1 = plots.grid_items()[0, 1][1]
    assert plot_0.opts['axiswise']
    assert plot_0.range('x') == (1, 5)
    assert plot_1.range('y') == (2, 6)


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


def test_autorange(df):
    plot = df.hvplot.scatter('x', 'y', autorange='y')
    opts = Store.lookup_options('bokeh', plot, 'plot')
    assert opts.kwargs['autorange'] == 'y'


def test_autorange_default_unset(df):
    plot = df.hvplot.scatter('x', 'y')
    opts = Store.lookup_options('bokeh', plot, 'plot')
    assert 'autorange' not in opts.kwargs


plotly_unsupported = pytest.mark.xfail(reason='Not supported by the plotly backend')


@pytest.mark.parametrize(
    'backend',
    ['bokeh', 'matplotlib', pytest.param('plotly', marks=plotly_unsupported)],
    indirect=True,
)
def test_clabel(hvplot_xarray, da2, backend):
    plot = da2.isel(other=0).hvplot.image(clabel='Temperature')
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['clabel'] == 'Temperature'


def test_flip_xaxis(df, backend):
    plot = df.hvplot.scatter('x', 'y', flip_xaxis=True)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['invert_xaxis'] is True
    assert 'invert_yaxis' not in opts.kwargs


def test_flip_yaxis(df, backend):
    plot = df.hvplot.scatter('x', 'y', flip_yaxis=True)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['invert_yaxis'] is True
    assert 'invert_xaxis' not in opts.kwargs


def test_framewise_default(df, backend):
    plot = df.hvplot.scatter('x', 'y')
    opts = Store.lookup_options(backend, plot, 'norm')
    assert opts.kwargs['framewise'] is True


def test_framewise_false(df, backend):
    plot = df.hvplot.scatter('x', 'y', framewise=False)
    opts = Store.lookup_options(backend, plot, 'norm')
    assert opts.kwargs['framewise'] is False


def test_invert(df, backend):
    plot = df.hvplot.scatter('x', 'y', invert=True)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['invert_axes'] is True
    assert opts.kwargs['labelled'] == ['y', 'x']


def test_rot(df, backend):
    plot = df.hvplot.scatter('x', 'y', rot=45)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['xrotation'] == 45
    assert 'yrotation' not in opts.kwargs


def test_rot_with_invert(df, backend):
    plot = df.hvplot.scatter('x', 'y', rot=45, invert=True)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['yrotation'] == 45
    assert 'xrotation' not in opts.kwargs


@pytest.mark.parametrize(
    'backend',
    ['bokeh', 'matplotlib', pytest.param('plotly', marks=plotly_unsupported)],
    indirect=True,
)
def test_xformatter(df, backend):
    plot = df.hvplot.scatter('x', 'y', xformatter='%.3f')
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['xformatter'] == '%.3f'


@pytest.mark.parametrize(
    'backend',
    ['bokeh', 'matplotlib', pytest.param('plotly', marks=plotly_unsupported)],
    indirect=True,
)
def test_yformatter(df, backend):
    plot = df.hvplot.scatter('x', 'y', yformatter='%.3f')
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['yformatter'] == '%.3f'


def test_xformatter_bokeh_formatter(df):
    formatter = NumeralTickFormatter(format='0.0%')
    plot = df.hvplot.scatter('x', 'y', xformatter=formatter)
    opts = Store.lookup_options('bokeh', plot, 'plot')
    assert opts.kwargs['xformatter'] is formatter


def test_xlabel(df, backend):
    plot = df.hvplot.scatter('x', 'y', xlabel='Distance')
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['xlabel'] == 'Distance'


def test_ylabel(df, backend):
    plot = df.hvplot.scatter('x', 'y', ylabel='Height')
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['ylabel'] == 'Height'


@pytest.mark.parametrize('ticks', [3, [1, 3], [(1, 'one'), (3, 'three')]])
def test_xticks(df, backend, ticks):
    plot = df.hvplot.scatter('x', 'y', xticks=ticks)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['xticks'] == ticks


@pytest.mark.parametrize('ticks', [3, [2, 4], [(2, 'two'), (4, 'four')]])
def test_yticks(df, backend, ticks):
    plot = df.hvplot.scatter('x', 'y', yticks=ticks)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['yticks'] == ticks
