import holoviews as hv
import numpy as np
import pandas as pd
import pytest
import xarray as xr
from bokeh.models import (
    FixedTicker,
    NumeralTickFormatter,
    PrintfTickFormatter,
    SingleIntervalTicker,
)
from holoviews import Store
from matplotlib.ticker import PercentFormatter

import hvplot
from hvplot.tests._deps import pandas_and_dask, requires

pytestmark = pytest.mark.usefixtures('hvplot_pandas')


@pytest.fixture
def df():
    return pd.DataFrame(
        [[1, 2, 'A', 0.1], [3, 4, 'B', 0.2], [5, 6, 'C', 0.3]],
        columns=['x', 'y', 'category', 'number'],
    )


@pytest.fixture
def grouped_df():
    return pd.DataFrame(
        {
            'x': [1, 3, 5, 7],
            'y': [2, 4, 6, 8],
            'z': [1.0, 2.0, 3.0, 4.0],
            'g': ['a', 'a', 'b', 'b'],
        }
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
            marks=pytest.mark.render_xfail(
                reason='HoloViews: plotly does not accept xaxis=True', strict=False
            ),
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


def test_loglog_wins_over_logx_false(df, backend):
    plot = df.hvplot.scatter('x', 'y', c='category', loglog=True, logx=False)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['logx'] is True
    assert opts.kwargs['logy'] is True


only_bokeh_defaults = pytest.mark.xfail(
    reason='BUG: HoloViews defaults are only read for bokeh (converter.py)', raises=AssertionError
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


@pytest.mark.parametrize('kind', ['box', 'violin'])
@pytest.mark.parametrize(
    ('y', 'dim'),
    [('z', 'z'), (['y', 'z'], 'value')],
    ids=['single_y', 'multi_y'],
)
def test_ylim_box_violin(grouped_df, kind, y, dim):
    plot = getattr(grouped_df.hvplot, kind)(y=y, ylim=(0, 20))
    assert plot.get_dimension(dim).range == (0, 20)


def test_ylim_box_by(grouped_df):
    plot = grouped_df.hvplot.box(y='z', by='g', ylim=(0, 20))
    assert plot.get_dimension('z').range == (0, 20)


def test_xlim_kde(grouped_df):
    plot = grouped_df.hvplot.kde(y='y', xlim=(-5, 15))
    assert plot.get_dimension('y').range == (-5, 15)


def test_xlim_kde_multi_y(grouped_df):
    plot = grouped_df.hvplot.kde(y=['y', 'z'], xlim=(-5, 15))
    assert plot.last.get_dimension('value').range == (-5, 15)


def test_xlim_kde_by(grouped_df):
    plot = grouped_df.hvplot.kde(y='y', by='g', xlim=(-5, 15))
    assert plot.last.get_dimension('y').range == (-5, 15)


@requires('datashader')
@pytest.mark.slow
@pytest.mark.parametrize('operation', ['rasterize', 'datashade'])
def test_ylim_resampling(xy_df, operation):
    plot = xy_df.hvplot.scatter(
        'x', 'y', ylim=(0, 20), dynamic=False, width=20, height=20, **{operation: True}
    )
    assert plot.range(1) == (0, 20)


def test_xlim_datetime():
    index = pd.date_range('2024-01-01', periods=5)
    xlim = (pd.Timestamp('2024-01-02'), pd.Timestamp('2024-01-04'))
    plot = pd.DataFrame({'y': range(5)}, index=index).hvplot.line(xlim=xlim)
    opts = Store.lookup_options('bokeh', plot, 'plot').options
    assert opts['xlim'] == xlim
    x_range = hv.renderer('bokeh').get_plot(plot).state.x_range
    assert (x_range.start, x_range.end) == xlim


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


def test_cticks_number_of_ticks(df):
    plot = df.hvplot.scatter('x', 'y', c='number', cticks=3)
    handles = hv.renderer('bokeh').get_plot(plot).handles
    assert handles['color_colorbar'].ticker.desired_num_ticks == 3


@pytest.mark.parametrize('backend', ['matplotlib'], indirect=True)
def test_cticks_matplotlib_default_compatibility(hvplot_xarray, da2, backend):
    plot = da2.isel(other=0).hvplot(cticks=[5, 10])
    handles = hv.renderer('matplotlib').get_plot(plot).handles
    assert list(handles['cbar'].get_ticks()) == [5, 10]


@pytest.mark.xfail(
    reason='BUG: cticks is dropped on matplotlib with compatibility="bokeh" (the style key'
    ' is chosen from _backend instead of _backend_compat, converter.py)',
    raises=AssertionError,
)
def test_cticks_matplotlib_bokeh_compatibility(hvplot_xarray, da2):
    hvplot.extension('matplotlib', compatibility='bokeh')
    plot = da2.isel(other=0).hvplot(cticks=[5, 10])
    handles = hv.renderer('matplotlib').get_plot(plot).handles
    assert list(handles['cbar'].get_ticks()) == [5, 10]


@pytest.mark.parametrize('backend', ['plotly'], indirect=True)
def test_cticks_plotly_raises(hvplot_xarray, da2, backend):
    with pytest.raises(ValueError, match='cticks option is not supported for plotly'):
        da2.isel(other=0).hvplot(cticks=[5, 10])


@pytest.mark.parametrize('autorange', ['x', 'y'])
def test_autorange(df, autorange):
    plot = df.hvplot.scatter('x', 'y', autorange=autorange)
    opts = Store.lookup_options('bokeh', plot, 'plot')
    assert opts.kwargs['autorange'] == autorange


def test_autorange_default_unset(df):
    plot = df.hvplot.scatter('x', 'y')
    opts = Store.lookup_options('bokeh', plot, 'plot')
    assert 'autorange' not in opts.kwargs


@pytest.mark.parametrize(
    'backend',
    [
        'bokeh',
        'matplotlib',
        pytest.param(
            'plotly',
            marks=pytest.mark.xfail(
                reason='HoloViews: plotly has no clabel option', raises=KeyError, strict=False
            ),
        ),
    ],
    indirect=True,
)
def test_clabel(hvplot_xarray, da2, backend):
    plot = da2.isel(other=0).hvplot.image(clabel='Temperature')
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['clabel'] == 'Temperature'


def test_clabel_scatter_colorbar_title(df):
    plot = df.hvplot.scatter('x', 'y', c='number', clabel='Temperature')
    handles = hv.renderer('bokeh').get_plot(plot).handles
    assert handles['color_colorbar'].title == 'Temperature'


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


def test_framewise_groupby(grouped_df):
    # Frame 'a' only has x in 1..3, frame 'b' has x in 5..7.
    plots = {}
    for framewise in [True, False]:
        hmap = grouped_df.hvplot.scatter('x', 'y', groupby='g', dynamic=False, framewise=framewise)
        plot = hv.renderer('bokeh').get_plot(hmap)
        plot.update(('a',))
        plots[framewise] = plot.state.x_range
    assert plots[True].end < 4
    assert plots[False].end > 7


@pytest.mark.parametrize(
    ('shared_axes', 'axiswise'),
    [(True, False), (False, True)],
)
def test_shared_axes_scatter_subplots(grouped_df, shared_axes, axiswise):
    plots = grouped_df.hvplot.scatter('x', 'y', by='g', subplots=True, shared_axes=shared_axes)
    element = next(iter(plots.values()))
    assert Store.lookup_options('bokeh', element, 'norm').kwargs['axiswise'] is axiswise
    rendered = hv.renderer('bokeh').get_plot(plots)
    x_ranges = rendered.traverse(lambda p: p.state.x_range, [hv.plotting.bokeh.ElementPlot])
    assert (x_ranges[0].end == x_ranges[1].end) == shared_axes


def test_invert(df, backend):
    plot = df.hvplot.scatter('x', 'y', invert=True)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['invert_axes'] is True
    assert opts.kwargs['labelled'] == ['y', 'x']


@pytest.mark.parametrize(
    ('kwargs', 'labelled', 'labelled_inverted'),
    [
        pytest.param({'kind': 'bar', 'x': 'g', 'y': 'y'}, ['x', 'y'], ['y', 'x'], id='bar'),
        pytest.param({'kind': 'hist', 'y': 'y'}, ['x'], ['y'], id='hist'),
        pytest.param({'kind': 'box', 'y': ['y', 'z']}, ['x'], ['y'], id='box_wide'),
        pytest.param({'kind': 'violin', 'y': ['y', 'z']}, ['x'], ['y'], id='violin_wide'),
    ],
)
def test_invert_kinds(grouped_df, kwargs, labelled, labelled_inverted):
    plot = grouped_df.hvplot(**kwargs)
    opts = Store.lookup_options('bokeh', plot, 'plot').kwargs
    assert 'invert_axes' not in opts
    assert opts['labelled'] == labelled
    plot = grouped_df.hvplot(invert=True, **kwargs)
    opts = Store.lookup_options('bokeh', plot, 'plot').kwargs
    assert opts['invert_axes'] is True
    assert opts['labelled'] == labelled_inverted


def test_invert_multi_y_line(grouped_df):
    plot = grouped_df.hvplot.line(y=['y', 'z'], invert=True)
    opts = Store.lookup_options('bokeh', plot, 'plot').kwargs
    assert opts['invert_axes'] is True


def test_invert_barh_is_already_inverted(grouped_df):
    # barh already has inverted axes, invert=True does not invert them back.
    plot = grouped_df.hvplot.barh(x='g', y='y', invert=True)
    opts = Store.lookup_options('bokeh', plot, 'plot').kwargs
    assert opts['invert_axes'] is True


def test_flip_xaxis_with_invert(df):
    plot = df.hvplot.scatter('x', 'y', flip_xaxis=True, invert=True)
    opts = Store.lookup_options('bokeh', plot, 'plot').kwargs
    assert opts['invert_xaxis'] is True
    assert opts['invert_axes'] is True


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


formatter_backends = pytest.mark.parametrize(
    'backend',
    [
        'bokeh',
        'matplotlib',
        pytest.param(
            'plotly',
            marks=pytest.mark.xfail(
                reason='HoloViews: plotly has no xformatter/yformatter option',
                raises=KeyError,
                strict=False,
            ),
        ),
    ],
    indirect=True,
)


@formatter_backends
def test_xformatter(df, backend):
    plot = df.hvplot.scatter('x', 'y', xformatter='%.3f')
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['xformatter'] == '%.3f'


@formatter_backends
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


@pytest.mark.parametrize(
    ('kwargs', 'label', 'labelled'),
    [
        pytest.param({'kind': 'line', 'y': 'y'}, 'xlabel', ['y', 'x'], id='line_index_x'),
        pytest.param({'kind': 'bar', 'x': 'g', 'y': ['y', 'z']}, 'ylabel', ['x', 'y'], id='bar'),
        pytest.param({'kind': 'hist', 'y': 'y'}, 'ylabel', ['x', 'y'], id='hist'),
        pytest.param({'kind': 'box', 'y': ['y', 'z']}, 'ylabel', ['x', 'y'], id='box_wide'),
        pytest.param({'kind': 'violin', 'y': ['y', 'z']}, 'ylabel', ['x', 'y'], id='violin_wide'),
    ],
)
def test_xlabel_ylabel_are_labelled(grouped_df, kwargs, label, labelled):
    plot = grouped_df.hvplot(**{label: 'Label'}, **kwargs)
    opts = Store.lookup_options('bokeh', plot, 'plot').kwargs
    assert opts[label] == 'Label'
    assert opts['labelled'] == labelled


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


def test_xticks_ndarray(df):
    plot = df.hvplot.scatter('x', 'y', xticks=np.array([1, 3]))
    ticker = hv.renderer('bokeh').get_plot(plot).state.xaxis[0].ticker
    assert isinstance(ticker, FixedTicker)
    assert list(ticker.ticks) == [1, 3]


def test_yticks_bokeh_ticker(df):
    ticker = SingleIntervalTicker(interval=2)
    plot = df.hvplot.scatter('x', 'y', yticks=ticker)
    assert hv.renderer('bokeh').get_plot(plot).state.yaxis[0].ticker is ticker


def test_xformatter_string_is_printf_formatter(df):
    plot = df.hvplot.scatter('x', 'y', xformatter='%.3f')
    formatter = hv.renderer('bokeh').get_plot(plot).state.xaxis[0].formatter
    assert isinstance(formatter, PrintfTickFormatter)
    assert formatter.format == '%.3f'


def test_yformatter_bokeh_formatter(df):
    formatter = NumeralTickFormatter(format='0.0%')
    plot = df.hvplot.scatter('x', 'y', yformatter=formatter)
    assert hv.renderer('bokeh').get_plot(plot).state.yaxis[0].formatter is formatter


@pytest.mark.parametrize('backend', ['matplotlib'], indirect=True)
def test_xformatter_matplotlib_formatter(df, backend):
    formatter = PercentFormatter()
    plot = df.hvplot.scatter('x', 'y', xformatter=formatter)
    axis = hv.renderer('matplotlib').get_plot(plot).handles['axis']
    assert axis.xaxis.get_major_formatter() is formatter
