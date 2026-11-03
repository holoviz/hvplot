import colorcet as cc
import holoviews as hv
import matplotlib as mpl
import numpy as np
import pandas as pd
import pytest
import xarray as xr
from holoviews import Store
from holoviews.testing import assert_element_equal

from hvplot.tests._deps import pandas_and_dask, requires

pytestmark = pytest.mark.usefixtures('hvplot_pandas')


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
    assert repr(opts.kwargs['color']) == repr(hv.dim('number'))
    assert 'number' in plot.vdims


@pytest.mark.parametrize('kind', ['scatter', 'points'])
def test_c_column_and_by(df, kind, backend):
    plot = df.hvplot('x', 'y', c='number', by='category', kind=kind)
    opts = Store.lookup_options(backend, plot.last, 'style')
    assert repr(opts.kwargs['color']) == repr(hv.dim('number'))
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


@pytest.mark.parametrize(
    ('alias', 'expected'),
    [
        ('linear', 'kbc_r'),
        ('categorical', cc.palette['glasbey_category10']),
        ('cyclic', 'colorwheel'),
        ('diverging', 'coolwarm'),
    ],
)
def test_cmap_by_type(df, backend, alias, expected):
    plot = df.hvplot.scatter('x', 'y', c='number', cmap=alias)
    opts = Store.lookup_options(backend, plot, 'style')
    assert opts.kwargs['cmap'] == expected


def test_cmap_by_name(df, backend):
    plot = df.hvplot.scatter('x', 'y', c='number', cmap='fire')
    opts = Store.lookup_options(backend, plot, 'style')
    assert opts.kwargs['cmap'] == 'fire'


def test_cmap_list(df, backend):
    plot = df.hvplot.scatter('x', 'y', c='number', cmap=['red', 'blue', 'green'])
    opts = Store.lookup_options(backend, plot, 'style')
    assert opts.kwargs['cmap'] == ['red', 'blue', 'green']


def test_cmap_dict(df, backend):
    cmap = {'A': 'red', 'B': 'blue', 'C': 'green'}
    plot = df.hvplot.scatter('x', 'y', c='category', cmap=cmap)
    opts = Store.lookup_options(backend, plot, 'style')
    assert opts.kwargs['cmap'] == cmap


def test_cmap_ignored_with_by(df):
    # Documented in doc/ref/plotting_options/color_colormap.ipynb: `by` cycles through
    # a color list instead of honoring cmap.
    default = df.hvplot.line('x', 'y', by='category')
    plot = df.hvplot.line('x', 'y', by='category', cmap=['red', 'blue', 'green'])
    default_color = Store.lookup_options('bokeh', default.last, 'style').kwargs['color']
    color = Store.lookup_options('bokeh', plot.last, 'style').kwargs['color']
    assert color.values == default_color.values
    assert 'red' not in color.values


def test_cmap_matplotlib_colormap(hvplot_xarray):
    # Regression test for https://github.com/holoviz/hvplot/pull/1461
    da = xr.DataArray(np.arange(25).reshape(5, 5))
    cmap = mpl.colormaps['viridis']
    plot = da.hvplot.image(cmap=cmap)
    assert Store.lookup_options('bokeh', plot, 'style').kwargs['cmap'] is cmap


@pytest.mark.parametrize('kind', ['scatter', 'line', 'bar'])
@pytest.mark.parametrize('color', ['red', '#ff5733'])
def test_color_constant(df, backend, kind, color):
    plot = df.hvplot(x='x', y='y', kind=kind, color=color)
    style_opts = Store.lookup_options(backend, plot, 'style')
    assert style_opts.kwargs['color'] == color
    plot_opts = Store.lookup_options(backend, plot, 'plot')
    assert 'colorbar' not in plot_opts.kwargs


def test_color_list_by(df, backend):
    colors = ['red', 'blue', 'green']
    plot = df.hvplot.line('x', 'y', by='category', color=colors)
    style_opts = Store.lookup_options(backend, plot.last, 'style')
    assert style_opts.kwargs['color'].values == colors


def test_color_over_c(df):
    plot = df.hvplot.scatter('x', 'y', c='number', color='red')
    style_opts = Store.lookup_options('bokeh', plot, 'style')
    assert style_opts.kwargs['color'] == 'red'


def test_c_ndarray(df):
    plot = df.hvplot.scatter('x', 'y', c=df['number'].to_numpy())
    expected = df.assign(_color=df['number']).hvplot.scatter('x', 'y', c='_color')
    assert_element_equal(plot, expected)


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


def test_colormap_and_cmap_error(df):
    with pytest.raises(TypeError, match='Specify at most one of'):
        df.hvplot.scatter('x', 'y', c='number', cmap='fire', colormap='fire')


def test_symmetric_deduced_use_dask_skipped(symmetric_df):
    # With use_dask=True the data is not checked, as it could be loaded lazily.
    plot = symmetric_df.hvplot.scatter('x', 'y', c='number', use_dask=True)
    plot_opts = Store.lookup_options('bokeh', plot, 'plot')
    assert plot_opts.kwargs.get('symmetric') is None
    style_opts = Store.lookup_options('bokeh', plot, 'style')
    assert style_opts.kwargs['cmap'] == 'kbc_r'


@pandas_and_dask
@pytest.mark.lib_xfail(
    'dask', reason='BUG: _process_symmetric raises TypeError on a dask DataFrame, swallowed'
)
def test_symmetric_deduced_tabular_lib(tabular_lib, symmetric_df):
    plot = tabular_lib(symmetric_df).hvplot.scatter('x', 'y', c='number')
    plot_opts = Store.lookup_options('bokeh', plot, 'plot')
    assert plot_opts.kwargs['symmetric'] is True
    style_opts = Store.lookup_options('bokeh', plot, 'style')
    assert style_opts.kwargs['cmap'] == 'coolwarm'


@pandas_and_dask
@pytest.mark.lib_xfail(
    'dask', reason='BUG: _process_symmetric raises TypeError on a dask DataFrame, swallowed'
)
def test_robust_tabular_lib(tabular_lib, symmetric_df):
    plot = tabular_lib(symmetric_df).hvplot.scatter('x', 'y', c='number', robust=True)
    plot_opts = Store.lookup_options('bokeh', plot, 'plot')
    assert plot_opts.kwargs['clim_percentile'] is True


@pytest.mark.xfail(
    reason='BUG: check_symmetric_max is ignored for tabular data, only used for xarray',
)
def test_check_symmetric_max_tabular():
    df = pd.DataFrame({'x': np.arange(100.0), 'y': np.arange(100.0)})
    df['number'] = np.linspace(-1, 1, len(df))
    plot = df.hvplot.scatter('x', 'y', c='number', check_symmetric_max=10)
    plot_opts = Store.lookup_options('bokeh', plot, 'plot')
    assert not plot_opts.kwargs.get('symmetric')


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


def test_robust(gridded_lib):
    da = xr.DataArray(
        np.arange(8).reshape((2, 2, 2)),
        coords={'time': [0, 1], 'lat': [0, 1], 'lon': [0, 1]},
        dims=['time', 'lat', 'lon'],
    )
    img = gridded_lib(da[0]).hvplot(robust=True)
    assert img.opts['clim_percentile'] is True


@pytest.mark.lib_skip('dask', reason='Symmetry is not checked on lazy data')
def test_symmetric_deduced_image(gridded_lib, symmetric_da):
    plot = gridded_lib(symmetric_da).hvplot.image()
    plot_opts = Store.lookup_options('bokeh', plot, 'plot')
    assert plot_opts.kwargs.get('symmetric') is True
    style_opts = Store.lookup_options('bokeh', plot, 'style')
    assert style_opts.kwargs['cmap'] == 'coolwarm'


def test_symmetric_false_image(gridded_lib, symmetric_da):
    plot = gridded_lib(symmetric_da).hvplot.image(symmetric=False)
    plot_opts = Store.lookup_options('bokeh', plot, 'plot')
    assert plot_opts.kwargs.get('symmetric') is False
    style_opts = Store.lookup_options('bokeh', plot, 'style')
    assert style_opts.kwargs['cmap'] == 'kbc_r'


@pytest.mark.lib_skip('dask', reason='Symmetry is not checked on lazy data')
def test_symmetric_deduced_image_with_cmap(gridded_lib, symmetric_da):
    plot = gridded_lib(symmetric_da).hvplot.image(cmap='fire')
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


@pytest.mark.lib_skip('dask', reason='Symmetry is not checked on lazy data')
def test_check_symmetric_max_big_image(gridded_lib, big_symmetric_da):
    plot = gridded_lib(big_symmetric_da).hvplot.image(check_symmetric_max=int(1e7))
    plot_opts = Store.lookup_options('bokeh', plot, 'plot')
    assert plot_opts.kwargs.get('symmetric') is True
    style_opts = Store.lookup_options('bokeh', plot, 'style')
    assert style_opts.kwargs['cmap'] == 'coolwarm'


def test_symmetric_not_deduced_not_in_memory(hvplot_xarray, tmp_path):
    da = xr.DataArray(
        np.arange(-100, 100).reshape(10, 10, 2),
        dims=['x', 'y', 'z'],
        coords={'x': np.arange(10), 'y': np.arange(10), 'z': np.arange(2)},
        name='value',
    )
    # Saved to and loaded from a netCDF file to get a DataArray not in memory.
    fpath = tmp_path / 'data.nc'
    da.to_netcdf(fpath)
    with xr.open_dataarray(fpath) as da:
        plot = da.hvplot(x='x', y='y', check_symmetric_max=da.size + 1)
        plot[0]
        plot_opts = Store.lookup_options('bokeh', plot.last, 'plot')
        # If a DataArray is not in memory, computing whether it's symmetric should
        # not be done and return False.
        assert not plot_opts.kwargs['symmetric']


def _operation(dmap):
    """The resampling operation applied by a DynamicMap returned by hvPlot."""
    return dmap.callback.inputs[0].callback.operation


def test_clim_image(gridded_lib, symmetric_da):
    plot = gridded_lib(symmetric_da).hvplot.image(clim=(-5, 5))
    assert plot.get_dimension('foo').range == (-5, 5)


def test_clim_one_bound_unset(hvplot_xarray, symmetric_da):
    plot = symmetric_da.hvplot.image(clim=(None, 5))
    assert plot.get_dimension('foo').range == (None, 5)


def test_clim_points_c_column(df):
    plot = df.hvplot.points('x', 'y', c='number', clim=(0, 1))
    assert plot.get_dimension('number').range == (0, 1)


@pytest.mark.xfail(reason='BUG: clim is ignored by scatter with c, points honors it')
def test_clim_scatter_c_column(df):
    plot = df.hvplot.scatter('x', 'y', c='number', clim=(0, 1))
    assert plot.get_dimension('number').range == (0, 1)


@pytest.mark.parametrize('kind', ['image', 'quadmesh', 'contour', 'contourf'])
def test_clim_gridded(gridded_lib, symmetric_da, kind):
    plot = gridded_lib(symmetric_da).hvplot(kind=kind, clim=(-5, 5))
    assert plot.vdims[0].range == (-5, 5)


def test_clim_heatmap(df):
    plot = df.hvplot.heatmap('x', 'y', C='number', clim=(0, 1))
    assert plot.get_dimension('number').range == (0, 1)


def test_clim_hexbin(df):
    plot = df.hvplot.hexbin('x', 'y', C='number', clim=(0, 1))
    assert plot.get_dimension('number').range == (0, 1)


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


def test_colorbar_true_without_c(df, backend):
    plot = df.hvplot.scatter('x', 'y', colorbar=True)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['colorbar'] is True


def test_colorbar_default_categorical_c(df, backend):
    plot = df.hvplot.scatter('x', 'y', c='category')
    opts = Store.lookup_options(backend, plot, 'plot')
    assert 'colorbar' not in opts.kwargs


def test_colorbar_default_contour_hides_legend(hvplot_xarray, symmetric_da):
    plot = symmetric_da.hvplot.contour()
    opts = Store.lookup_options('bokeh', plot, 'plot')
    assert opts.kwargs['colorbar'] is True
    assert opts.kwargs['show_legend'] is False


def test_color_key_by_name(df, backend):
    plot = df.hvplot.scatter('x', 'y', c='number', color_key='fire')
    opts = Store.lookup_options(backend, plot, 'style')
    assert opts.kwargs['cmap'] == 'fire'


@pytest.mark.parametrize('other', ['cmap', 'colormap'])
def test_color_key_with_other_cmap_option_error(df, other):
    with pytest.raises(TypeError, match='Specify at most one of'):
        df.hvplot.scatter('x', 'y', c='number', color_key='fire', **{other: 'fire'})


@requires('datashader')
@pytest.mark.slow
def test_color_key_dict_datashade(df):
    color_key = {'A': '#ff0000', 'B': '#00ff00', 'C': '#0000ff'}
    plot = df.hvplot.points('x', 'y', by='category', color_key=color_key, datashade=True)
    assert _operation(plot).p.color_key == color_key


@pytest.mark.parametrize(
    'backend',
    [
        'bokeh',
        'matplotlib',
        pytest.param(
            'plotly',
            marks=pytest.mark.xfail(
                reason='HoloViews: plotly has no cnorm option', raises=KeyError, strict=False
            ),
        ),
    ],
    indirect=True,
)
@pytest.mark.parametrize('cnorm', ['linear', 'log', 'eq_hist'])
def test_cnorm(df, backend, cnorm):
    plot = df.hvplot.scatter('x', 'y', c='number', cnorm=cnorm)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['cnorm'] == cnorm


def test_cnorm_image(hvplot_xarray):
    da = xr.DataArray(np.arange(1, 5).reshape(2, 2), name='foo')
    plot = da.hvplot.image(cnorm='log')
    opts = Store.lookup_options('bokeh', plot, 'plot')
    assert opts.kwargs['cnorm'] == 'log'


@requires('datashader')
@pytest.mark.slow
def test_cnorm_rasterize(df):
    plot = df.hvplot(x='x', y='y', rasterize=True, cnorm='eq_hist')
    opts = Store.lookup_options('bokeh', plot[()], 'plot').kwargs
    assert opts.get('cnorm') == 'eq_hist'


@requires('datashader')
@pytest.mark.slow
def test_cnorm_datashade(df):
    plot = df.hvplot(x='x', y='y', datashade=True, cnorm='log')
    assert _operation(plot).p['cnorm'] == 'log'


@requires('datashader')
@pytest.mark.slow
def test_rescale_discrete_levels_rasterize(df):
    plot = df.hvplot(x='x', y='y', rasterize=True, cnorm='eq_hist', rescale_discrete_levels=False)
    opts = Store.lookup_options('bokeh', plot[()], 'plot').kwargs
    assert opts.get('rescale_discrete_levels') is False


@requires('datashader')
@pytest.mark.slow
def test_rescale_discrete_levels_datashade(df):
    plot = df.hvplot(x='x', y='y', datashade=True, cnorm='eq_hist', rescale_discrete_levels=False)
    assert _operation(plot).p['rescale_discrete_levels'] is False


@pytest.mark.parametrize(
    'backend',
    [
        'bokeh',
        'matplotlib',
        pytest.param(
            'plotly',
            marks=pytest.mark.xfail(
                reason='HoloViews: plotly has no rescale_discrete_levels option',
                raises=KeyError,
                strict=False,
            ),
        ),
    ],
    indirect=True,
)
def test_rescale_discrete_levels(df, backend):
    plot = df.hvplot.scatter('x', 'y', c='number', cnorm='eq_hist', rescale_discrete_levels=False)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['rescale_discrete_levels'] is False
