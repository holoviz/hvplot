from unittest import SkipTest

import holoviews as hv
import numpy as np
import pandas as pd
import pytest
from holoviews import Store
from holoviews.element.comparison import ComparisonTestCase

from hvplot.util import is_dask


@pytest.fixture(scope='module')
def df():
    return pd.DataFrame(
        [[1, 2, 'A', 0.1], [3, 4, 'B', 0.2], [5, 6, 'C', 0.3]],
        columns=['x', 'y', 'category', 'number'],
    )


@pytest.mark.usefixtures('hvplot_pandas')
class TestOptions:
    @pytest.mark.parametrize('kind', ['scatter', 'points'])
    def test_logz(self, df, kind, backend):
        plot = df.hvplot('x', 'y', c='x', logz=True, kind=kind)
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['logz'] is True

    @pytest.mark.parametrize('kind', ['scatter', 'points'])
    def test_size_dim(self, df, kind, backend):
        plot = df.hvplot('x', 'y', s='number', kind=kind)
        opts = Store.lookup_options(backend, plot, 'style')
        if backend in ['bokeh', 'plotly']:
            param = 'size'
        elif backend == 'matplotlib':
            param = 's'
        assert opts.kwargs[param] == 'number'
        assert 'number' in plot.vdims

    @pytest.mark.parametrize('kind', ['scatter', 'points'])
    def test_alpha_dim(self, df, kind, backend):
        if backend != 'bokeh':
            pytest.xfail(f'cannot map a dim to alpha w/ {backend}')

        plot = df.hvplot('x', 'y', alpha='number', kind=kind)
        opts = Store.lookup_options(backend, plot, 'style')
        assert opts.kwargs['alpha'] == 'number'
        assert 'number' in plot.vdims
        # Special matplotlib code to trigger an error that happens on render
        if backend == 'matplotlib':
            mpl_renderer = hv.Store.renderers['matplotlib']
            mpl_renderer.get_plot(plot)

    @pytest.mark.parametrize('kind', ['scatter', 'points'])
    def test_marker_dim(self, df, kind, backend):
        plot = df.hvplot('x', 'y', marker='category', kind=kind)
        opts = Store.lookup_options(backend, plot, 'style')
        assert opts.kwargs['marker'] == 'category'
        assert 'category' in plot.vdims

    @pytest.mark.parametrize('kind', ['scatter', 'points'])
    def test_size_dim_overlay(self, df, kind, backend):
        plot = df.hvplot('x', 'y', s='number', by='category', kind=kind)
        opts = Store.lookup_options(backend, plot.last, 'style')
        if backend in ['bokeh', 'plotly']:
            param = 'size'
        elif backend == 'matplotlib':
            param = 's'
        assert opts.kwargs[param] == 'number'
        assert 'number' in plot.last.vdims

    @pytest.mark.parametrize('kind', ['scatter', 'points'])
    def test_alpha_dim_overlay(self, df, kind, backend):
        if backend == 'plotly':
            pytest.xfail('cannot map a dim to alpha w/ plotly')

        plot = df.hvplot('x', 'y', alpha='number', by='category', kind=kind)
        opts = Store.lookup_options(backend, plot.last, 'style')
        assert opts.kwargs['alpha'] == 'number'
        assert 'number' in plot.last.vdims


class TestPandasTransforms(ComparisonTestCase):
    def setUp(self):
        import hvplot.pandas  # noqa: F401

    def test_pandas_dim_size_alias(self):
        df = pd.DataFrame({'x': np.linspace(0, 4, 5), 'y': np.linspace(1, 5, 5)})
        dim_expr = hv.dim('y') * 10
        scatter = df.hvplot.scatter('x', 'y', s=dim_expr)
        plot_opts = scatter.opts.get().kwargs
        assert repr(plot_opts.get('size')) == repr(dim_expr)

    # def test_pandas_dim_size_matplotlib_backend(self):
    #     hv.extension('matplotlib')

    #     df = pd.DataFrame({'x': np.linspace(0, 4, 5), 'y': np.linspace(1, 5, 5)})
    #     dim_expr = hv.dim('y') * 10

    #     scatter = df.hvplot.scatter('x', 'y', size=dim_expr)
    #     plot_opts = scatter.opts.get().kwargs
    #     # Matplotlib uses 's' not 'size'
    #     assert 's' in plot_opts


class TestChart1D(ComparisonTestCase):
    def setUp(self):
        import hvplot.pandas  # noqa: F401

        self.df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])

    def test_scatter_size_set_to_series(self):
        if is_dask(self.df['y']):
            y = self.df['y'].compute()
        else:
            y = self.df['y']
        plot = self.df.hvplot.scatter('x', 'y', s=y)
        opts = Store.lookup_options('bokeh', plot, 'style')
        assert '_size' in plot.data.columns
        self.assertEqual(opts.kwargs['size'], '_size')


class TestChart1DDask(TestChart1D):
    def setUp(self):
        super().setUp()
        try:
            import dask.dataframe as dd
        except ImportError:
            raise SkipTest('Dask not available')
        import hvplot.dask  # noqa: F401

        self.df = dd.from_pandas(self.df, npartitions=2)
