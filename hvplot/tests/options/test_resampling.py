import numpy as np
import pandas as pd
import pytest
import xarray as xr
from holoviews import Store, render
from holoviews.core.overlay import Overlay
from holoviews.core.spaces import DynamicMap
from holoviews.element import Image, Points
from holoviews.element.chart import Scatter
from holoviews.element.raster import ImageStack
from holoviews.operation.downsample import downsample1d
from holoviews.plotting.util import process_cmap

from hvplot.converter import HoloViewsConverter
from hvplot.tests._data import makeTimeDataFrame
from hvplot.tests._deps import requires

pytestmark = pytest.mark.usefixtures('hvplot_pandas')

operations = pytest.mark.parametrize('operation', ['rasterize', 'datashade'])

CATEGORICAL_CMAP = HoloViewsConverter._default_cmaps['categorical']


@pytest.fixture
def df():
    return pd.DataFrame(
        [[1, 2, 'A', 0.1], [3, 4, 'B', 0.2], [5, 6, 'C', 0.3]],
        columns=['x', 'y', 'category', 'number'],
    )


@pytest.fixture
def large_df():
    return pd.DataFrame(
        np.random.multivariate_normal((0, 0), [[0.1, 0.1], [0.1, 1.0]], (5000,)),
        columns=['x', 'y'],
    )


def _operation(dmap):
    """The resampling operation applied by a DynamicMap returned by hvPlot."""
    return dmap.callback.inputs[0].callback.operation


@requires('datashader')
@pytest.mark.slow
def test_rasterize_by_count_cat_aggregator(df):
    from datashader.reductions import count_cat

    dmap = df.hvplot.scatter('x', 'y', by='category', rasterize=True)
    agg = _operation(dmap).p.aggregator
    assert isinstance(agg, count_cat)
    assert agg.column == 'category'


@requires('datashader')
@pytest.mark.slow
def test_rasterize_by_categorical_cmap(df):
    plot = df.hvplot.scatter('x', 'y', by='category', rasterize=True)
    opts = Store.lookup_options('bokeh', plot[()], 'style').kwargs
    assert opts.get('cmap') == CATEGORICAL_CMAP
    assert _operation(plot).p.aggregator.column == 'category'


@requires('datashader')
@pytest.mark.slow
def test_rasterize_by_image_stack(df):
    plot = df.hvplot(x='x', y='y', by='category', rasterize=True, dynamic=False)
    assert isinstance(plot, ImageStack)
    assert plot.opts['cmap'] == CATEGORICAL_CMAP


@requires('datashader')
@pytest.mark.slow
def test_rasterize_c_also_an_axis_default_cmap(df):
    plot = df.hvplot.scatter('x', 'y', c='y', dynamic=False, rasterize=True)
    opts = Store.lookup_options('bokeh', plot, 'style').kwargs
    assert opts.get('cmap') == 'kbc_r'


@requires('datashader')
@pytest.mark.slow
def test_rasterize_default_cmap(df):
    plot = df.hvplot.scatter('x', 'y', dynamic=False, rasterize=True)
    opts = Store.lookup_options('bokeh', plot, 'style').kwargs
    assert opts.get('cmap') == 'kbc_r'


@requires('datashader')
@pytest.mark.slow
def test_rasterize_single_y_in_list_default_cmap(df):
    # Regression test for https://github.com/holoviz/hvplot/issues/1210
    plot = df.hvplot.line(y=['y'], rasterize=True)
    opts = Store.lookup_options('bokeh', plot[()], 'style').kwargs
    assert opts.get('cmap') == 'kbc_r'


@requires('datashader')
@pytest.mark.slow
def test_rasterize_default_colorbar(df):
    plot = df.hvplot.scatter('x', 'y', dynamic=False, rasterize=True)
    opts = Store.lookup_options('bokeh', plot, 'plot').kwargs
    assert opts.get('colorbar') is True


@requires('datashader')
@pytest.mark.slow
def test_rasterize_default_colorbar_with_cmap(df):
    plot = df.hvplot.scatter('x', 'y', dynamic=False, rasterize=True, cmap='Reds')
    opts = Store.lookup_options('bokeh', plot, 'style').kwargs
    assert opts.get('cmap') == 'Reds'
    opts = Store.lookup_options('bokeh', plot, 'plot').kwargs
    assert opts.get('colorbar') is True


@requires('datashader')
@pytest.mark.slow
def test_rasterize_clim(df):
    plot = df.hvplot.scatter('x', 'y', dynamic=False, rasterize=True, clim=(1, 4))
    opts = Store.lookup_options('bokeh', plot, 'plot').kwargs
    assert opts.get('clim') == (1, 4)


@requires('datashader')
@pytest.mark.slow
@pytest.mark.parametrize('dynamic', [True, False])
@pytest.mark.parametrize('opt', ['aspect', 'data_aspect'])
def test_datashade_aspect(df, opt, dynamic):
    plot = df.hvplot(x='x', y='y', datashade=True, dynamic=dynamic, **{opt: 2})
    opts = Store.lookup_options('bokeh', plot[()], 'plot').kwargs
    assert opts[opt] == 2
    assert opts.get('height') is None
    assert opts.get('frame_height') is None


@requires('datashader')
@pytest.mark.slow
@pytest.mark.parametrize('dynamic', [True, False])
@pytest.mark.parametrize('opt', ['aspect', 'data_aspect'])
def test_datashade_aspect_and_frame_height(df, opt, dynamic):
    plot = df.hvplot(x='x', y='y', frame_height=150, datashade=True, dynamic=dynamic, **{opt: 2})
    opts = Store.lookup_options('bokeh', plot[()], 'plot').kwargs
    assert opts[opt] == 2
    assert opts.get('frame_height') == 150
    assert opts.get('height') is None
    assert opts.get('frame_width') is None


@requires('datashader')
@pytest.mark.slow
def test_datashade_cmap_as_color_key(df):
    color_key = {'A': '#ff0000', 'B': '#00ff00', 'C': '#0000ff'}
    plot = df.hvplot.points(x='x', y='y', by='category', cmap=color_key, datashade=True)
    assert _operation(plot).p.color_key == color_key


@requires('datashader')
@pytest.mark.slow
def test_datashade_cmap_name(df):
    plot = df.hvplot.points(x='x', y='y', datashade=True, cmap='fire')
    assert _operation(plot).p.cmap == process_cmap('fire')


@requires('datashader')
@pytest.mark.slow
def test_datashade_hover_disabled_by_default(df):
    plot = df.hvplot(x='x', y='y', datashade=True)
    opts = Store.lookup_options('bokeh', plot[()], 'plot').kwargs
    assert 'hover' not in opts.get('tools')


@requires('datashader')
@pytest.mark.slow
def test_datashade_with_hover_true(df):
    plot = df.hvplot(x='x', y='y', datashade=True, hover=True)
    opts = Store.lookup_options('bokeh', plot[()], 'plot').kwargs
    assert 'hover' in opts.get('tools')


@requires('datashader')
@pytest.mark.slow
def test_datashade_xlim():
    data = pd.DataFrame(np.random.randn(100).cumsum())
    img = data.hvplot(xlim=(0, 20000), datashade=True, dynamic=False)
    assert img.range(0) == (0, 20000)


@requires('datashader')
@pytest.mark.slow
@operations
def test_xlim_ylim_ranges(df, operation):
    plot = df.hvplot.points('x', 'y', xlim=(1, 5), ylim=(0, 10), **{operation: True})
    assert _operation(plot).p.x_range == (1, 5)
    assert _operation(plot).p.y_range == (0, 10)


@requires('datashader')
@pytest.mark.slow
@pytest.mark.parametrize('kind', ['scatter', 'line', 'area'])
def test_datashade_wide_explicit_ys_categorical(kind):
    df = makeTimeDataFrame()
    plot = df.hvplot(y=list(df.columns), datashade=True, kind=kind)
    assert _operation(plot).p.cmap == CATEGORICAL_CMAP
    assert _operation(plot).p.aggregator.column == 'Variable'


@requires('datashader')
@pytest.mark.slow
@pytest.mark.parametrize('kind', ['scatter', 'line', 'area'])
def test_datashade_wide_implicit_ys_categorical(kind):
    plot = makeTimeDataFrame().hvplot(datashade=True, kind=kind)
    assert _operation(plot).p.cmap == CATEGORICAL_CMAP
    assert _operation(plot).p.aggregator.column == 'Variable'


@requires('datashader')
@pytest.mark.slow
def test_datashade_by_categorical(df):
    plot = df.hvplot.scatter('x', 'y', by='category', datashade=True)
    assert _operation(plot).p.cmap == CATEGORICAL_CMAP
    assert _operation(plot).p.aggregator.column == 'category'


@requires('datashader')
@pytest.mark.slow
def test_aggregator_count_cat(df):
    from datashader.reductions import count_cat

    dmap = df.hvplot.scatter('x', 'y', aggregator=count_cat('category'), rasterize=True)
    agg = _operation(dmap).p.aggregator
    assert isinstance(agg, count_cat)
    assert agg.column == 'category'


@requires('datashader')
@pytest.mark.slow
def test_aggregator_count_cat_categorical_cmap(df):
    from datashader.reductions import count_cat

    plot = df.hvplot.scatter('x', 'y', aggregator=count_cat('category'), rasterize=True)
    opts = Store.lookup_options('bokeh', plot[()], 'style').kwargs
    assert opts.get('cmap') == CATEGORICAL_CMAP
    assert _operation(plot).p.aggregator.column == 'category'


@requires('datashader')
@pytest.mark.slow
def test_aggregator_count_cat_image_stack(df):
    from datashader.reductions import count_cat

    plot = df.hvplot(
        x='x', y='y', aggregator=count_cat('category'), rasterize=True, width=999, dynamic=False
    )
    assert isinstance(plot, ImageStack)
    assert plot.opts['width'] == 999
    assert plot.opts['cmap'] == CATEGORICAL_CMAP


@requires('datashader')
@pytest.mark.slow
@operations
def test_aggregator_string_without_c(df, operation):
    dmap = df.hvplot.scatter('x', 'y', aggregator='max', **{operation: True})
    assert _operation(dmap).p.aggregator == 'max'


@requires('datashader')
@pytest.mark.slow
def test_aggregator_count_cat_string(df):
    from datashader.reductions import count_cat

    plot = df.hvplot.scatter('x', 'y', c='category', aggregator='count_cat', rasterize=True)
    agg = _operation(plot).p.aggregator
    assert isinstance(agg, count_cat)
    assert agg.column == 'category'
    assert Store.lookup_options('bokeh', plot[()], 'style').kwargs['cmap'] == CATEGORICAL_CMAP


@requires('datashader')
@pytest.mark.slow
@operations
def test_aggregator_default_with_c(df, operation):
    from datashader.reductions import mean

    dmap = df.hvplot.scatter('x', 'y', c='number', **{operation: True})
    agg = _operation(dmap).p.aggregator
    assert isinstance(agg, mean)
    assert agg.column == 'number'


@requires('datashader')
@pytest.mark.slow
@operations
def test_aggregator_string_with_c(df, operation):
    from datashader.reductions import sum

    dmap = df.hvplot.scatter('x', 'y', c='number', aggregator='sum', **{operation: True})
    agg = _operation(dmap).p.aggregator
    assert isinstance(agg, sum)
    assert agg.column == 'number'


@requires('datashader')
@pytest.mark.slow
@operations
def test_aggregator_default_with_c_also_an_axis(df, operation):
    from datashader.reductions import mean

    original_data = df.copy(deep=True)
    dmap = df.hvplot.scatter('x', 'y', c='y', **{operation: True})
    agg = _operation(dmap).p.aggregator
    assert isinstance(agg, mean)
    assert agg.column == '_color'
    assert original_data.equals(df)


@requires('datashader')
@pytest.mark.slow
@operations
def test_pixel_ratio(df, operation):
    plot = df.hvplot(x='x', y='y', pixel_ratio=0.5, **{operation: True})
    assert _operation(plot).p['pixel_ratio'] == 0.5


@requires('datashader')
@pytest.mark.slow
@operations
def test_dynspread(df, operation):
    from holoviews.operation.datashader import dynspread

    plot = df.hvplot.points('x', 'y', dynspread=True, **{operation: True})
    assert isinstance(_operation(plot), dynspread)
    # The resampling operation is applied first, then spread.
    resampled = plot.callback.inputs[0].callback.inputs[0]
    assert type(resampled.callback.operation).__name__ == operation


@requires('datashader')
@pytest.mark.slow
@operations
def test_dynspread_default_disabled(df, operation):
    from holoviews.operation.datashader import dynspread

    plot = df.hvplot.points('x', 'y', **{operation: True})
    assert not isinstance(_operation(plot), dynspread)


@requires('datashader')
@pytest.mark.slow
@operations
def test_max_px(df, operation):
    plot = df.hvplot.points('x', 'y', dynspread=True, max_px=5, **{operation: True})
    assert _operation(plot).p.max_px == 5


@requires('datashader')
@pytest.mark.slow
@operations
def test_threshold(df, operation):
    plot = df.hvplot.points('x', 'y', dynspread=True, threshold=0.8, **{operation: True})
    assert _operation(plot).p.threshold == 0.8


@requires('datashader')
@pytest.mark.slow
@operations
def test_precompute(df, operation):
    plot = df.hvplot.points('x', 'y', precompute=True, **{operation: True})
    assert _operation(plot).p.precompute is True


def test_resample_when_without_operation_error(df):
    with pytest.raises(ValueError, match='At least one resampling operation'):
        df.hvplot(x='x', y='y', resample_when=10)


@requires('datashader')
@pytest.mark.slow
@operations
def test_resample_when(large_df, operation):
    dmap = large_df.hvplot.scatter('x', 'y', resample_when=1000, **{operation: True})
    assert isinstance(dmap, DynamicMap)

    render(dmap)  # trigger dynamicmap
    overlay = dmap.items()[0][1]
    assert isinstance(overlay, Overlay)

    image = overlay.get(0)
    assert isinstance(image, Image)
    assert len(image) > 0

    scatter = overlay.get(1)
    assert isinstance(scatter, Scatter)
    assert len(scatter.data) == 0


@pytest.mark.parametrize(('kind', 'eltype'), [('points', Points), ('scatter', Scatter)])
def test_resample_when_downsample(large_df, kind, eltype):
    dmap = large_df.hvplot(kind=kind, x='x', y='y', resample_when=1000, downsample=True)
    assert isinstance(dmap, DynamicMap)

    render(dmap)  # trigger dynamicmap
    overlay = dmap.items()[0][1]
    assert isinstance(overlay, Overlay)

    downsampled = overlay.get(0)
    assert isinstance(downsampled, eltype)
    assert len(downsampled) > 0

    element = overlay.get(1)
    assert isinstance(element, eltype)
    assert len(element) == 0


@pytest.fixture
def small_df():
    return pd.DataFrame({'x': np.linspace(0, 1, 50), 'y': np.linspace(0, 1, 50)})


@requires('datashader')
@pytest.mark.slow
@pytest.mark.parametrize(
    'resampling',
    [
        pytest.param(
            {'rasterize': True},
            marks=pytest.mark.xfail(
                reason='HoloViews: apply_when with rasterize empties the raw element', strict=False
            ),
        ),
        {'datashade': True},
        {'downsample': True},
    ],
)
def test_resample_when_below_threshold(small_df, resampling):
    dmap = small_df.hvplot.scatter('x', 'y', resample_when=1000, **resampling)

    render(dmap)  # trigger dynamicmap
    resampled, raw = dmap.items()[0][1]
    assert len(resampled) == 0
    assert len(raw) == len(small_df)


def test_selector_without_operation_error(df):
    with pytest.raises(
        ValueError, match='rasterize or datashade must be enabled when selector is set'
    ):
        df.hvplot.points('x', 'y', selector='first')


@requires('datashader')
@pytest.mark.parametrize('selector', ['bad', ('bad', 'number')])
def test_selector_invalid_value(df, selector):
    with pytest.raises(ValueError, match='Invalid selector value'):
        df.hvplot.points('x', 'y', rasterize=True, selector=selector)


@requires('datashader')
@pytest.mark.slow
@operations
def test_selector(df, operation):
    from datashader.reductions import first, min

    test_cases = [
        ('first', first()),
        (('min', 'number'), min('number')),
    ]
    for selector, expected in test_cases:
        plot = df.hvplot.points('x', 'y', selector=selector, **{operation: True})
        assert _operation(plot).p['selector'] == expected, selector


@requires('datashader')
@pytest.mark.slow
@pytest.mark.render_xfail(
    reason='datashader: first() of a pandas string column fails', strict=False
)
@operations
def test_selector_reduction_of_string_column(df, operation):
    from datashader.reductions import first

    selector = first('category')
    plot = df.hvplot.points('x', 'y', selector=selector, **{operation: True})
    assert _operation(plot).p['selector'] == selector


@requires('datashader')
@pytest.mark.slow
def test_selector_datashade_enables_hover(df):
    plot = df.hvplot(x='x', y='y', datashade=True, selector='first')
    opts = Store.lookup_options('bokeh', plot[()], 'plot').kwargs
    assert 'hover' in opts.get('tools')


@pytest.fixture
def da():
    data = np.arange(0, 60).reshape(6, 10)
    return xr.DataArray(data, coords={'y': np.arange(6), 'x': np.arange(10)}, dims=('y', 'x'))


@pytest.mark.parametrize('kind', ['image', 'quadmesh'])
def test_rasterize_false_keeps_resolution(hvplot_xarray, da, kind):
    plot = da.hvplot(kind=kind)
    assert all(plot.data.x.diff('x').round(0) == 1)
    assert all(plot.data.y.diff('y').round(0) == 1)


@requires('datashader')
@pytest.mark.slow
@pytest.mark.parametrize('kind', ['image', 'quadmesh'])
def test_x_sampling(gridded_lib, da, kind):
    plot = gridded_lib(da).hvplot(kind=kind, dynamic=False, rasterize=True, x_sampling=5)
    assert all(plot.data.x.diff('x').round(0) == 5)


@requires('datashader')
@pytest.mark.slow
@pytest.mark.parametrize('kind', ['image', 'quadmesh'])
def test_y_sampling(hvplot_xarray, da, kind):
    plot = da.hvplot(kind=kind, dynamic=False, rasterize=True, y_sampling=2)
    assert all(plot.data.y.diff('y').round(0) == 2)


@pytest.fixture
def line_df():
    return pd.DataFrame(np.random.random(100))


def test_downsample_true(line_df):
    plot = line_df.hvplot.line(downsample=True)
    assert isinstance(plot.callback.operation, downsample1d)


def test_downsample_opts(line_df):
    plot = line_df.hvplot.line(downsample=True, width=100, height=50, x_sampling=5, xlim=(0, 5))
    assert plot.callback.operation.p.width == 100
    assert plot.callback.operation.p.height == 50
    assert plot.callback.operation.p.x_sampling == 5
    assert plot.callback.operation.p.x_range == (0, 5)


@pytest.mark.parametrize('algorithm', ['lttb', 'minmax', 'm4', 'minmax-lttb'])
def test_downsample_algorithm(line_df, algorithm):
    plot = line_df.hvplot.line(downsample=algorithm)
    assert isinstance(plot.callback.operation, downsample1d)
    assert plot.callback.operation_kwargs['algorithm'] == algorithm


@pytest.mark.parametrize('operation', ['rasterize', 'datashade'])
def test_rasterize_datashade_without_datashader(block_import, hvplot_pandas, operation):
    block_import('datashader', 'holoviews.operation.datashader')
    df = pd.DataFrame({'x': [0, 1], 'y': [0, 1]})
    with pytest.raises(ModuleNotFoundError, match='`datashader` package must be installed'):
        df.hvplot.points('x', 'y', **{operation: True})


@requires('datashader')
@pytest.mark.slow
@pytest.mark.parametrize('backend', ['matplotlib', 'plotly'], indirect=True)
def test_rasterize_cmap_clim_colorbar_other_backends(df, backend):
    plot = df.hvplot.points('x', 'y', c='number', rasterize=True, cmap='fire', clim=(0, 1))
    style_opts = Store.lookup_options(backend, plot[()], 'style').kwargs
    assert style_opts['cmap'] == 'fire'
    plot_opts = Store.lookup_options(backend, plot[()], 'plot').kwargs
    assert plot_opts['clim'] == (0, 1)
    assert plot_opts['colorbar'] is True
