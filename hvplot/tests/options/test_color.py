import colorcet as cc
import holoviews as hv
import matplotlib as mpl
import numpy as np
import pandas as pd
import pytest
import xarray as xr
from holoviews import Store
from holoviews.testing import assert_element_equal

from hvplot.tests._deps import requires

pytestmark = pytest.mark.usefixtures('hvplot_pandas')

pandas_and_dask = pytest.mark.parametrize('tabular_lib', ['pandas', 'dask'], indirect=True)

plotly_unsupported = pytest.mark.xfail(reason='Not supported by the plotly backend')


@pytest.fixture
def df():
    return pd.DataFrame(
        [[1, 2, 'A', 0.1], [3, 4, 'B', 0.2], [5, 6, 'C', 0.3]],
        columns=['x', 'y', 'category', 'number'],
    )


@pytest.fixture
def symmetric_df():
    return pd.DataFrame([[1, 2, -1], [3, 4, 0], [5, 6, 1]], columns=['x', 'y', 'number'])


@pytest.mark.parametrize('kind', ['scatter', 'points'])
def test_c_column(df, kind, backend):
    plot = df.hvplot('x', 'y', c='number', kind=kind)
    opts = Store.lookup_options(backend, plot, 'style')
    assert opts.kwargs['color'] == 'number'
    assert 'number' in plot.vdims


@pytest.mark.parametrize('kind', ['scatter', 'points'])
def test_c_column_and_by(df, kind, backend):
    plot = df.hvplot('x', 'y', c='number', by='category', kind=kind)
    opts = Store.lookup_options(backend, plot.last, 'style')
    assert opts.kwargs['color'] == 'number'
    assert 'number' in plot.last.vdims


def test_c_alias_of_color():
    df = pd.DataFrame({'x': np.linspace(0, 4, 5), 'y': np.linspace(1, 5, 5)})
    scatter = df.hvplot.scatter('x', 'y', c='y')
    opts = Store.lookup_options('bokeh', scatter, 'style')
    assert repr(opts.kwargs['color']) == repr(hv.dim('y'))


@pandas_and_dask
def test_c_series(tabular_lib):
    pandas_df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
    df = tabular_lib(pandas_df)
    actual = df.hvplot.scatter('x', 'y', c=pandas_df['y'])
    expected = df.assign(_color=pandas_df['y']).hvplot.scatter('x', 'y', c='_color')
    assert_element_equal(actual, expected)


@pandas_and_dask
def test_c_column_named_like_a_color(tabular_lib):
    df = tabular_lib(
        pd.DataFrame([[1, 2, 'A'], [3, 4, 'B'], [5, 6, 'C']], columns=['x', 'y', 'red'])
    )
    plot = df.hvplot.scatter('x', 'y', c='red')
    opts = Store.lookup_options('bokeh', plot, 'style')
    assert isinstance(opts.kwargs['color'], hv.dim)
    assert opts.kwargs['color'].dimension.name == 'red'


def test_color_dim_expression():
    df = pd.DataFrame({'x': np.linspace(0, 4, 5), 'y': np.linspace(-2, 2, 5)})
    dim_expr = hv.dim('y') * 10
    scatter = df.hvplot.scatter('x', 'y', color=dim_expr)
    style_opts = Store.lookup_options('bokeh', scatter, 'style')
    assert repr(style_opts.kwargs['color']) == repr(dim_expr)
    plot_opts = Store.lookup_options('bokeh', scatter, 'plot')
    assert plot_opts.kwargs['colorbar'] is True


def test_cmap_default_categorical(df, backend):
    plot = df.hvplot.scatter('x', 'y', c='category')
    opts = Store.lookup_options(backend, plot, 'style')
    assert opts.kwargs['cmap'] == cc.palette['glasbey_category10']


def test_cmap_default_numerical(df, backend):
    plot = df.hvplot.scatter('x', 'y', c='number')
    opts = Store.lookup_options(backend, plot, 'style')
    assert opts.kwargs['cmap'] == 'kbc_r'


def test_cmap_by_type(df, backend):
    plot = df.hvplot.scatter('x', 'y', c='number', cmap='diverging')
    opts = Store.lookup_options(backend, plot, 'style')
    assert opts.kwargs['cmap'] == 'coolwarm'


def test_cmap_by_name(df, backend):
    plot = df.hvplot.scatter('x', 'y', c='number', cmap='fire')
    opts = Store.lookup_options(backend, plot, 'style')
    assert opts.kwargs['cmap'] == 'fire'


def test_cmap_list(df, backend):
    plot = df.hvplot.scatter('x', 'y', c='number', cmap=['red', 'blue', 'green'])
    opts = Store.lookup_options(backend, plot, 'style')
    assert opts.kwargs['cmap'] == ['red', 'blue', 'green']


def test_cmap_matplotlib_colormap(hvplot_xarray):
    # Regression test for https://github.com/holoviz/hvplot/pull/1461
    da = xr.DataArray(np.arange(25).reshape(5, 5))
    da.hvplot.image(cmap=mpl.colormaps['viridis'])


def test_colormap_by_name(df, backend):
    plot = df.hvplot.scatter('x', 'y', c='number', colormap='fire')
    opts = Store.lookup_options(backend, plot, 'style')
    assert opts.kwargs['cmap'] == 'fire'


def test_symmetric_deduced_dataframe(symmetric_df, backend):
    plot = symmetric_df.hvplot.scatter('x', 'y', c='number')
    plot_opts = Store.lookup_options(backend, plot, 'plot')
    assert plot_opts.kwargs['symmetric'] is True
    style_opts = Store.lookup_options(backend, plot, 'style')
    assert style_opts.kwargs['cmap'] == 'coolwarm'


def test_symmetric_true(df, backend):
    plot = df.hvplot.scatter('x', 'y', c='number', symmetric=True)
    plot_opts = Store.lookup_options(backend, plot, 'plot')
    assert plot_opts.kwargs['symmetric'] is True
    style_opts = Store.lookup_options(backend, plot, 'style')
    assert style_opts.kwargs['cmap'] == 'coolwarm'


def test_symmetric_false_not_deduced(symmetric_df, backend):
    plot = symmetric_df.hvplot.scatter('x', 'y', c='number', symmetric=False)
    plot_opts = Store.lookup_options(backend, plot, 'plot')
    assert plot_opts.kwargs['symmetric'] is False
    style_opts = Store.lookup_options(backend, plot, 'style')
    assert style_opts.kwargs['cmap'] == 'kbc_r'


def test_symmetric_not_deduced_when_clim_set(symmetric_df, backend):
    plot = symmetric_df.hvplot.scatter('x', 'y', c='number', clim=(-1, 1))
    plot_opts = Store.lookup_options(backend, plot, 'plot')
    assert plot_opts.kwargs.get('symmetric') is None
    style_opts = Store.lookup_options(backend, plot, 'style')
    assert style_opts.kwargs['cmap'] == 'kbc_r'


def test_bgcolor(df, backend):
    plot = df.hvplot.scatter('x', 'y', bgcolor='black')
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['bgcolor'] == 'black'


@pytest.fixture
def symmetric_da():
    return xr.DataArray(np.arange(-2, 2).reshape((2, 2)), name='foo')


@pytest.fixture
def big_symmetric_da():
    return xr.DataArray(np.arange(-1e6, 1e6).reshape(1000, 2000))


def test_robust(hvplot_xarray):
    da = xr.DataArray(
        np.arange(8).reshape((2, 2, 2)),
        coords={'time': [0, 1], 'lat': [0, 1], 'lon': [0, 1]},
        dims=['time', 'lat', 'lon'],
    )
    img = da[0].hvplot(robust=True)
    assert img.opts['clim_percentile'] is True


def test_symmetric_deduced_image(hvplot_xarray, symmetric_da):
    plot = symmetric_da.hvplot.image()
    plot_opts = Store.lookup_options('bokeh', plot, 'plot')
    assert plot_opts.kwargs.get('symmetric') is True
    style_opts = Store.lookup_options('bokeh', plot, 'style')
    assert style_opts.kwargs['cmap'] == 'coolwarm'


def test_symmetric_false_image(hvplot_xarray, symmetric_da):
    plot = symmetric_da.hvplot.image(symmetric=False)
    plot_opts = Store.lookup_options('bokeh', plot, 'plot')
    assert plot_opts.kwargs.get('symmetric') is False
    style_opts = Store.lookup_options('bokeh', plot, 'style')
    assert style_opts.kwargs['cmap'] == 'kbc_r'


def test_symmetric_deduced_image_with_cmap(hvplot_xarray, symmetric_da):
    plot = symmetric_da.hvplot.image(cmap='fire')
    plot_opts = Store.lookup_options('bokeh', plot, 'plot')
    assert plot_opts.kwargs.get('symmetric') is True
    style_opts = Store.lookup_options('bokeh', plot, 'style')
    assert style_opts.kwargs['cmap'] == 'fire'


def test_check_symmetric_max_default_skips_big_image(hvplot_xarray, big_symmetric_da):
    plot = big_symmetric_da.hvplot.image()
    plot_opts = Store.lookup_options('bokeh', plot, 'plot')
    assert plot_opts.kwargs.get('symmetric') is False
    style_opts = Store.lookup_options('bokeh', plot, 'style')
    assert style_opts.kwargs['cmap'] == 'kbc_r'


def test_check_symmetric_max_big_image(hvplot_xarray, big_symmetric_da):
    plot = big_symmetric_da.hvplot.image(check_symmetric_max=int(1e7))
    plot_opts = Store.lookup_options('bokeh', plot, 'plot')
    assert plot_opts.kwargs.get('symmetric') is True
    style_opts = Store.lookup_options('bokeh', plot, 'style')
    assert style_opts.kwargs['cmap'] == 'coolwarm'


def _operation(dmap):
    """The resampling operation applied by a DynamicMap returned by hvPlot."""
    return dmap.callback.inputs[0].callback.operation


def test_clim_image(hvplot_xarray, symmetric_da):
    plot = symmetric_da.hvplot.image(clim=(-5, 5))
    assert plot.get_dimension('foo').range == (-5, 5)


def test_clim_one_bound_unset(hvplot_xarray, symmetric_da):
    plot = symmetric_da.hvplot.image(clim=(None, 5))
    assert plot.get_dimension('foo').range == (None, 5)


def test_colorbar_default_line(df, backend):
    plot = df.hvplot.line('x', 'y')
    opts = Store.lookup_options(backend, plot, 'plot')
    assert 'colorbar' not in opts.kwargs


def test_colorbar_default_scatter_numeric_c(df, backend):
    plot = df.hvplot.scatter('x', 'y', c='number')
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['colorbar'] is True


def test_colorbar_false_scatter_numeric_c(df, backend):
    plot = df.hvplot.scatter('x', 'y', c='number', colorbar=False)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['colorbar'] is False


def test_colorbar_default_image(hvplot_xarray, symmetric_da, backend):
    plot = symmetric_da.hvplot.image()
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['colorbar'] is True


def test_colorbar_false_image(hvplot_xarray, symmetric_da, backend):
    plot = symmetric_da.hvplot.image(colorbar=False)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['colorbar'] is False


def test_color_key_by_name(df, backend):
    plot = df.hvplot.scatter('x', 'y', c='number', color_key='fire')
    opts = Store.lookup_options(backend, plot, 'style')
    assert opts.kwargs['cmap'] == 'fire'


@pytest.mark.parametrize('other', ['cmap', 'colormap'])
def test_color_key_with_other_cmap_option_error(df, other):
    with pytest.raises(TypeError, match='Specify at most one of'):
        df.hvplot.scatter('x', 'y', c='number', color_key='fire', **{other: 'fire'})


@requires('datashader')
def test_color_key_dict_datashade(df):
    color_key = {'A': '#ff0000', 'B': '#00ff00', 'C': '#0000ff'}
    plot = df.hvplot.points('x', 'y', by='category', color_key=color_key, datashade=True)
    assert _operation(plot).p.color_key == color_key


@pytest.mark.parametrize(
    'backend',
    ['bokeh', 'matplotlib', pytest.param('plotly', marks=plotly_unsupported)],
    indirect=True,
)
def test_cnorm(df, backend):
    plot = df.hvplot.scatter('x', 'y', c='number', cnorm='log')
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['cnorm'] == 'log'


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


@pytest.mark.parametrize(
    'backend',
    ['bokeh', 'matplotlib', pytest.param('plotly', marks=plotly_unsupported)],
    indirect=True,
)
def test_rescale_discrete_levels(df, backend):
    plot = df.hvplot.scatter('x', 'y', c='number', cnorm='eq_hist', rescale_discrete_levels=False)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['rescale_discrete_levels'] is False
