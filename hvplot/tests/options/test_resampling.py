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
def test_rasterize_by_count_cat_aggregator(df):
    from datashader.reductions import count_cat

    dmap = df.hvplot.scatter('x', 'y', by='category', rasterize=True)
    agg = _operation(dmap).p.aggregator
    assert isinstance(agg, count_cat)
    assert agg.column == 'category'


@requires('datashader')
def test_rasterize_by_categorical_cmap(df):
    plot = df.hvplot.scatter('x', 'y', by='category', rasterize=True)
    opts = Store.lookup_options('bokeh', plot[()], 'style').kwargs
    assert opts.get('cmap') == CATEGORICAL_CMAP
    assert _operation(plot).p.aggregator.column == 'category'


@requires('datashader')
def test_rasterize_by_image_stack(df):
    plot = df.hvplot(x='x', y='y', by='category', rasterize=True, dynamic=False)
    assert isinstance(plot, ImageStack)
    assert plot.opts['cmap'] == CATEGORICAL_CMAP


@requires('datashader')
def test_rasterize_c_also_an_axis_default_cmap(df):
    plot = df.hvplot.scatter('x', 'y', c='y', dynamic=False, rasterize=True)
    opts = Store.lookup_options('bokeh', plot, 'style').kwargs
    assert opts.get('cmap') == 'kbc_r'


@requires('datashader')
def test_rasterize_default_cmap(df):
    plot = df.hvplot.scatter('x', 'y', dynamic=False, rasterize=True)
    opts = Store.lookup_options('bokeh', plot, 'style').kwargs
    assert opts.get('cmap') == 'kbc_r'


@requires('datashader')
def test_rasterize_single_y_in_list_default_cmap(df):
    # Regression test for https://github.com/holoviz/hvplot/issues/1210
    plot = df.hvplot.line(y=['y'], rasterize=True)
    opts = Store.lookup_options('bokeh', plot[()], 'style').kwargs
    assert opts.get('cmap') == 'kbc_r'


@requires('datashader')
def test_rasterize_default_colorbar(df):
    plot = df.hvplot.scatter('x', 'y', dynamic=False, rasterize=True)
    opts = Store.lookup_options('bokeh', plot, 'plot').kwargs
    assert opts.get('colorbar') is True


@requires('datashader')
def test_rasterize_default_colorbar_with_cmap(df):
    plot = df.hvplot.scatter('x', 'y', dynamic=False, rasterize=True, cmap='Reds')
    opts = Store.lookup_options('bokeh', plot, 'style').kwargs
    assert opts.get('cmap') == 'Reds'
    opts = Store.lookup_options('bokeh', plot, 'plot').kwargs
    assert opts.get('colorbar') is True


@requires('datashader')
def test_rasterize_clim(df):
    plot = df.hvplot.scatter('x', 'y', dynamic=False, rasterize=True, clim=(1, 4))
    opts = Store.lookup_options('bokeh', plot, 'plot').kwargs
    assert opts.get('clim') == (1, 4)


@requires('datashader')
@pytest.mark.parametrize('dynamic', [True, False])
@pytest.mark.parametrize('opt', ['aspect', 'data_aspect'])
def test_datashade_aspect(df, opt, dynamic):
    plot = df.hvplot(x='x', y='y', datashade=True, dynamic=dynamic, **{opt: 2})
    opts = Store.lookup_options('bokeh', plot[()], 'plot').kwargs
    assert opts[opt] == 2
    assert opts.get('height') is None
    assert opts.get('frame_height') is None


@requires('datashader')
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
def test_datashade_cmap_as_color_key(df):
    color_key = {'A': '#ff0000', 'B': '#00ff00', 'C': '#0000ff'}
    df.hvplot.points(x='x', y='y', by='category', cmap=color_key, datashade=True)
    with pytest.raises(TypeError):
        df.hvplot.points(
            x='x', y='y', by='category', datashade=True, cmap='kbc_r', color_key=color_key
        )


@requires('datashader')
def test_datashade_hover_disabled_by_default(df):
    plot = df.hvplot(x='x', y='y', datashade=True)
    opts = Store.lookup_options('bokeh', plot[()], 'plot').kwargs
    assert 'hover' not in opts.get('tools')


@requires('datashader')
def test_datashade_with_hover_true(df):
    plot = df.hvplot(x='x', y='y', datashade=True, hover=True)
    opts = Store.lookup_options('bokeh', plot[()], 'plot').kwargs
    assert 'hover' in opts.get('tools')


@requires('datashader')
def test_datashade_xlim():
    data = pd.DataFrame(np.random.randn(100).cumsum())
    img = data.hvplot(xlim=(0, 20000), datashade=True, dynamic=False)
    assert img.range(0) == (0, 20000)


@requires('datashader')
@pytest.mark.parametrize('kind', ['scatter', 'line', 'area'])
def test_datashade_wide_explicit_ys_categorical(kind):
    df = makeTimeDataFrame()
    plot = df.hvplot(y=list(df.columns), datashade=True, kind=kind)
    assert _operation(plot).p.cmap == CATEGORICAL_CMAP
    assert _operation(plot).p.aggregator.column == 'Variable'


@requires('datashader')
@pytest.mark.parametrize('kind', ['scatter', 'line', 'area'])
def test_datashade_wide_implicit_ys_categorical(kind):
    plot = makeTimeDataFrame().hvplot(datashade=True, kind=kind)
    assert _operation(plot).p.cmap == CATEGORICAL_CMAP
    assert _operation(plot).p.aggregator.column == 'Variable'


@requires('datashader')
def test_datashade_by_categorical(df):
    plot = df.hvplot.scatter('x', 'y', by='category', datashade=True)
    assert _operation(plot).p.cmap == CATEGORICAL_CMAP
    assert _operation(plot).p.aggregator.column == 'category'


@requires('datashader')
def test_aggregator_count_cat(df):
    from datashader.reductions import count_cat

    dmap = df.hvplot.scatter('x', 'y', aggregator=count_cat('category'), rasterize=True)
    agg = _operation(dmap).p.aggregator
    assert isinstance(agg, count_cat)
    assert agg.column == 'category'


@requires('datashader')
def test_aggregator_count_cat_categorical_cmap(df):
    from datashader.reductions import count_cat

    plot = df.hvplot.scatter('x', 'y', aggregator=count_cat('category'), rasterize=True)
    opts = Store.lookup_options('bokeh', plot[()], 'style').kwargs
    assert opts.get('cmap') == CATEGORICAL_CMAP
    assert _operation(plot).p.aggregator.column == 'category'


@requires('datashader')
def test_aggregator_count_cat_image_stack(df):
    from datashader.reductions import count_cat

    plot = df.hvplot(
        x='x', y='y', aggregator=count_cat('category'), rasterize=True, width=999, dynamic=False
    )
    assert isinstance(plot, ImageStack)
    assert plot.opts['width'] == 999
    assert plot.opts['cmap'] == CATEGORICAL_CMAP


@requires('datashader')
@operations
def test_aggregator_default_with_c(df, operation):
    from datashader.reductions import mean

    dmap = df.hvplot.scatter('x', 'y', c='number', **{operation: True})
    agg = _operation(dmap).p.aggregator
    assert isinstance(agg, mean)
    assert agg.column == 'number'


@requires('datashader')
@operations
def test_aggregator_string_with_c(df, operation):
    from datashader.reductions import sum

    dmap = df.hvplot.scatter('x', 'y', c='number', aggregator='sum', **{operation: True})
    agg = _operation(dmap).p.aggregator
    assert isinstance(agg, sum)
    assert agg.column == 'number'


@requires('datashader')
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
def test_cnorm_rasterize(df):
    plot = df.hvplot(x='x', y='y', rasterize=True, cnorm='eq_hist')
    opts = Store.lookup_options('bokeh', plot[()], 'plot').kwargs
    assert opts.get('cnorm') == 'eq_hist'


@requires('datashader')
def test_cnorm_datashade(df):
    plot = df.hvplot(x='x', y='y', datashade=True, cnorm='eq_hist')
    assert _operation(plot).p['cnorm'] == 'eq_hist'


@requires('datashader')
@operations
def test_pixel_ratio(df, operation):
    plot = df.hvplot(x='x', y='y', pixel_ratio=0.5, **{operation: True})
    assert _operation(plot).p['pixel_ratio'] == 0.5


@requires('datashader')
def test_rescale_discrete_levels_rasterize(df):
    plot = df.hvplot(x='x', y='y', rasterize=True, cnorm='eq_hist', rescale_discrete_levels=False)
    opts = Store.lookup_options('bokeh', plot[()], 'plot').kwargs
    assert opts.get('rescale_discrete_levels') is False


@requires('datashader')
def test_rescale_discrete_levels_datashade(df):
    plot = df.hvplot(x='x', y='y', datashade=True, cnorm='eq_hist', rescale_discrete_levels=False)
    assert _operation(plot).p['rescale_discrete_levels'] is False


@requires('datashader')
def test_rescale_discrete_levels_datashade_default_true(df):
    plot = df.hvplot(x='x', y='y', datashade=True, cnorm='eq_hist')
    assert _operation(plot).p['rescale_discrete_levels'] is True


def test_resample_when_without_operation_error(df):
    with pytest.raises(ValueError, match='At least one resampling operation'):
        df.hvplot(x='x', y='y', resample_when=10)


@requires('datashader')
@operations
def test_resample_when(large_df, operation):
    dmap = large_df.hvplot.scatter('x', 'y', resample_when=1000, **{operation: True})
    assert isinstance(dmap, DynamicMap)

    render(dmap)  # trigger dynamicmap
    overlay = dmap.items()[0][1]
    assert isinstance(overlay, Overlay)

    image = overlay.get(0)
    assert isinstance(image, Image)
    assert len(image.data) > 0

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
@operations
def test_selector(df, operation):
    from datashader.reductions import first, min

    test_cases = [
        ('first', first()),
        (('min', 'number'), min('number')),
        (first('category'), first('category')),
    ]
    for selector, expected in test_cases:
        plot = df.hvplot.points('x', 'y', selector=selector, **{operation: True})
        assert _operation(plot).p['selector'] == expected, selector


@requires('datashader')
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
@pytest.mark.parametrize('kind', ['image', 'quadmesh'])
def test_x_sampling_y_sampling(hvplot_xarray, da, kind):
    plot = da.hvplot(kind=kind, dynamic=False, rasterize=True, x_sampling=5, y_sampling=2)
    assert all(plot.data.x.diff('x').round(0) == 5)
    assert all(plot.data.y.diff('y').round(0) == 2)


@pytest.fixture
def line_df():
    return pd.DataFrame(np.random.random(100))


def test_downsample_default(line_df):
    plot = line_df.hvplot.line(downsample=True)
    assert isinstance(plot.callback.operation, downsample1d)
    assert plot.callback.operation.algorithm == 'lttb'


def test_downsample_opts(line_df):
    plot = line_df.hvplot.line(downsample=True, width=100, height=50, x_sampling=5, xlim=(0, 5))
    assert plot.callback.operation.p.width == 100
    assert plot.callback.operation.p.height == 50
    assert plot.callback.operation.p.x_sampling == 5
    assert plot.callback.operation.p.x_range == (0, 5)


def test_downsample_minmax(line_df):
    plot = line_df.hvplot.line(downsample='minmax')
    assert isinstance(plot.callback.operation, downsample1d)
    assert plot.callback.operation_kwargs['algorithm'] == 'minmax'
