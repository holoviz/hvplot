import holoviews as hv
import numpy as np
import pandas as pd
import pytest
from holoviews import Store
from holoviews.element.comparison import ComparisonTestCase


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
