from collections import OrderedDict
from unittest import SkipTest

import holoviews as hv
import numpy as np
import pandas as pd
import pytest
import xarray as xr
from holoviews import Store, dim
from holoviews.element.comparison import ComparisonTestCase

from hvplot.util import is_dask


@pytest.fixture(scope='module')
def df():
    return pd.DataFrame(
        [[1, 2, 'A', 0.1], [3, 4, 'B', 0.2], [5, 6, 'C', 0.3]],
        columns=['x', 'y', 'category', 'number'],
    )


@pytest.fixture(scope='module')
def symmetric_df():
    return pd.DataFrame([[1, 2, -1], [3, 4, 0], [5, 6, 1]], columns=['x', 'y', 'number'])


@pytest.mark.usefixtures('hvplot_pandas')
class TestOptions:
    @pytest.mark.parametrize('kind', ['scatter', 'points'])
    def test_color_dim(self, df, kind, backend):
        plot = df.hvplot('x', 'y', c='number', kind=kind)
        opts = Store.lookup_options(backend, plot, 'style')
        assert opts.kwargs['color'] == 'number'
        assert 'number' in plot.vdims

    @pytest.mark.parametrize('kind', ['scatter', 'points'])
    def test_color_dim_overlay(self, df, kind, backend):
        plot = df.hvplot('x', 'y', c='number', by='category', kind=kind)
        opts = Store.lookup_options(backend, plot.last, 'style')
        assert opts.kwargs['color'] == 'number'
        assert 'number' in plot.last.vdims

    def test_hvplot_default_cat_cmap_opts(self, df, backend):
        import colorcet as cc

        plot = df.hvplot.scatter('x', 'y', c='category')
        opts = Store.lookup_options(backend, plot, 'style')
        assert opts.kwargs['cmap'] == cc.palette['glasbey_category10']

    def test_hvplot_default_num_cmap_opts(self, df, backend):
        plot = df.hvplot.scatter('x', 'y', c='number')
        opts = Store.lookup_options(backend, plot, 'style')
        assert opts.kwargs['cmap'] == 'kbc_r'

    def test_cmap_opts_by_type(self, df, backend):
        plot = df.hvplot.scatter('x', 'y', c='number', cmap='diverging')
        opts = Store.lookup_options(backend, plot, 'style')
        assert opts.kwargs['cmap'] == 'coolwarm'

    def test_cmap_opts_by_name(self, df, backend):
        plot = df.hvplot.scatter('x', 'y', c='number', cmap='fire')
        opts = Store.lookup_options(backend, plot, 'style')
        assert opts.kwargs['cmap'] == 'fire'

    def test_colormap_opts_by_name(self, df, backend):
        plot = df.hvplot.scatter('x', 'y', c='number', colormap='fire')
        opts = Store.lookup_options(backend, plot, 'style')
        assert opts.kwargs['cmap'] == 'fire'

    def test_cmap_opts_as_a_list(self, df, backend):
        plot = df.hvplot.scatter('x', 'y', c='number', cmap=['red', 'blue', 'green'])
        opts = Store.lookup_options(backend, plot, 'style')
        assert opts.kwargs['cmap'] == ['red', 'blue', 'green']

    def test_symmetric_dataframe(self, backend):
        df = pd.DataFrame([[1, 2, -1], [3, 4, 0], [5, 6, 1]], columns=['x', 'y', 'number'])
        plot = df.hvplot.scatter('x', 'y', c='number')
        plot_opts = Store.lookup_options(backend, plot, 'plot')
        assert plot_opts.kwargs['symmetric'] is True
        style_opts = Store.lookup_options(backend, plot, 'style')
        assert style_opts.kwargs['cmap'] == 'coolwarm'

    def test_symmetric_is_deduced_dataframe(self, symmetric_df, backend):
        plot = symmetric_df.hvplot.scatter('x', 'y', c='number')
        plot_opts = Store.lookup_options(backend, plot, 'plot')
        assert plot_opts.kwargs['symmetric'] is True
        style_opts = Store.lookup_options(backend, plot, 'style')
        assert style_opts.kwargs['cmap'] == 'coolwarm'

    def test_symmetric_from_opts(self, df, backend):
        plot = df.hvplot.scatter('x', 'y', c='number', symmetric=True)
        plot_opts = Store.lookup_options(backend, plot, 'plot')
        assert plot_opts.kwargs['symmetric'] is True
        style_opts = Store.lookup_options(backend, plot, 'style')
        assert style_opts.kwargs['cmap'] == 'coolwarm'

    def test_symmetric_from_opts_does_not_deduce(self, symmetric_df, backend):
        plot = symmetric_df.hvplot.scatter('x', 'y', c='number', symmetric=False)
        plot_opts = Store.lookup_options(backend, plot, 'plot')
        assert plot_opts.kwargs['symmetric'] is False
        style_opts = Store.lookup_options(backend, plot, 'style')
        assert style_opts.kwargs['cmap'] == 'kbc_r'

    def test_if_clim_is_set_symmetric_is_not_deduced(self, symmetric_df, backend):
        plot = symmetric_df.hvplot.scatter('x', 'y', c='number', clim=(-1, 1))
        plot_opts = Store.lookup_options(backend, plot, 'plot')
        assert plot_opts.kwargs.get('symmetric') is None
        style_opts = Store.lookup_options(backend, plot, 'style')
        assert style_opts.kwargs['cmap'] == 'kbc_r'

    def test_bgcolor(self, df, backend):
        plot = df.hvplot.scatter('x', 'y', bgcolor='black')
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['bgcolor'] == 'black'


class TestPandasTransforms(ComparisonTestCase):
    def setUp(self):
        import hvplot.pandas  # noqa: F401

    def test_pandas_dim_color_expression(self):
        df = pd.DataFrame({'x': np.linspace(0, 4, 5), 'y': np.linspace(-2, 2, 5)})
        dim_expr = hv.dim('y') * 10
        scatter = df.hvplot.scatter('x', 'y', color=dim_expr)
        plot_opts = scatter.opts.get().kwargs
        assert repr(plot_opts.get('color')) == repr(dim_expr)
        assert plot_opts.get('colorbar') is True

    def test_pandas_color_alias_column(self):
        df = pd.DataFrame({'x': np.linspace(0, 4, 5), 'y': np.linspace(1, 5, 5)})
        scatter = df.hvplot.scatter('x', 'y', c='y')
        plot_opts = scatter.opts.get().kwargs
        assert repr(plot_opts.get('color')) == repr(hv.dim('y'))


class TestChart1D(ComparisonTestCase):
    def setUp(self):
        import hvplot.pandas  # noqa: F401

        self.df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
        self.cat_df = pd.DataFrame(
            [[1, 2, 'A'], [3, 4, 'B'], [5, 6, 'C']], columns=['x', 'y', 'category']
        )

    def test_scatter_color_set_to_series(self):
        if is_dask(self.df['y']):
            y = self.df['y'].compute()
        else:
            y = self.df['y']
        actual = self.df.hvplot.scatter('x', 'y', c=y)
        altered_df = self.df.assign(_color=y)
        expected = altered_df.hvplot.scatter('x', 'y', c='_color')
        self.assertEqual(actual, expected)

    def test_scatter_color_internally_set_to_dim(self):
        altered_df = self.cat_df.copy().rename(columns={'category': 'red'})
        plot = altered_df.hvplot.scatter('x', 'y', c='red')
        opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertIsInstance(opts.kwargs['color'], dim)
        self.assertEqual(opts.kwargs['color'].dimension.name, 'red')


class TestChart1DDask(TestChart1D):
    def setUp(self):
        super().setUp()
        try:
            import dask.dataframe as dd
        except ImportError:
            raise SkipTest('Dask not available')
        import hvplot.dask  # noqa: F401

        self.df = dd.from_pandas(self.df, npartitions=2)
        self.cat_df = dd.from_pandas(self.cat_df, npartitions=3)


def test_cmap_LinearSegmentedColormap():
    # test for https://github.com/holoviz/hvplot/pull/1461
    xr = pytest.importorskip('xarray')
    mpl = pytest.importorskip('matplotlib')
    import hvplot.xarray  # noqa: F401

    data = np.arange(25).reshape(5, 5)
    xr_da = xr.DataArray(data)
    xr_da.hvplot.image(cmap=mpl.colormaps['viridis'])


@pytest.mark.usefixtures('hvplot_xarray')
class TestGridPlots(ComparisonTestCase):
    def setUp(self):
        coords = OrderedDict([('time', [0, 1]), ('lat', [0, 1]), ('lon', [0, 1])])
        self.da_img_by_time = xr.DataArray(
            np.arange(8).reshape((2, 2, 2)), coords, ['time', 'lat', 'lon']
        ).assign_coords(lat1=xr.DataArray([2, 3], dims=['lat']))
        self.da_img = xr.DataArray(np.arange(-2, 2).reshape((2, 2)), name='foo')

    def test_img_dataarray_robust_to_clim_percentile(self):
        img = self.da_img_by_time[0].hvplot(robust=True)
        assert img.opts['clim_percentile'] is True

    def test_symmetric_img_deduces_symmetric(self):
        plot = self.da_img.hvplot.image()
        plot_opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(plot_opts.kwargs.get('symmetric'), True)
        style_opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(style_opts.kwargs['cmap'], 'coolwarm')

    def test_symmetric_img_with_symmetric_set_to_false(self):
        plot = self.da_img.hvplot.image(symmetric=False)
        plot_opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(plot_opts.kwargs.get('symmetric'), False)
        style_opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(style_opts.kwargs['cmap'], 'kbc_r')

    def test_symmetric_img_with_cmap_set(self):
        plot = self.da_img.hvplot.image(cmap='fire')
        plot_opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(plot_opts.kwargs.get('symmetric'), True)
        style_opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(style_opts.kwargs['cmap'], 'fire')

    def test_symmetric_with_big_img_sets_symmetric_to_false_without_calculating(self):
        big_img = xr.DataArray(np.arange(-1e6, 1e6).reshape(1000, 2000))
        plot = big_img.hvplot.image()
        plot_opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(plot_opts.kwargs.get('symmetric'), False)
        style_opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(style_opts.kwargs['cmap'], 'kbc_r')

    def test_symmetric_with_big_img_and_check_symmetric_max_calculates_symmetric(self):
        big_img = xr.DataArray(np.arange(-1e6, 1e6).reshape(1000, 2000))
        plot = big_img.hvplot.image(check_symmetric_max=int(1e7))
        plot_opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(plot_opts.kwargs.get('symmetric'), True)
        style_opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(style_opts.kwargs['cmap'], 'coolwarm')
