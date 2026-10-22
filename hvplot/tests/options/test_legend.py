from unittest import SkipTest

import pandas as pd
import pytest
from holoviews import Store
from holoviews.element import Area, Curve, Scatter
from holoviews.element.comparison import ComparisonTestCase
from parameterized import parameterized


@pytest.fixture(scope='module')
def df():
    return pd.DataFrame(
        [[1, 2, 'A', 0.1], [3, 4, 'B', 0.2], [5, 6, 'C', 0.3]],
        columns=['x', 'y', 'category', 'number'],
    )


@pytest.mark.usefixtures('hvplot_pandas')
class TestOptions:
    def test_scatter_legend_position(self, df, backend):
        if backend == 'matplotlib':
            pytest.xfail('legend_position not supported w/ matplotlib for scatter')
        if backend == 'plotly':
            pytest.xfail('legend_position not supported w/ plotly for scatter')

        plot = df.hvplot.scatter('x', 'y', c='category', legend='left')
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['legend_position'] == 'left'

    def test_histogram_by_category_legend_position(self, df, backend):
        if backend == 'plotly':
            pytest.xfail('legend_position not supported w/ plotly for hist')

        plot = df.hvplot.hist('y', by='category', legend='left')
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['legend_position'] == 'left'

    def test_legend_cols(self, df, backend):
        if backend == 'plotly':
            pytest.skip('legend_cols not supported w/ plotly')

        plot = df.hvplot.scatter('x', 'y', by='category', legend_cols=2)
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['legend_cols'] == 2

    def test_legend_opts(self, df, backend):
        if backend == 'plotly':
            pytest.skip('legend_opts not supported w/ plotly')

        if backend == 'bokeh':
            lo = {'spacing': 20}
        elif backend == 'matplotlib':
            lo = {'labelspacing': 2}

        plot = df.hvplot.scatter('x', 'y', by='category', legend_opts=lo)
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['legend_opts'] == lo


class TestChart1D(ComparisonTestCase):
    def setUp(self):
        import hvplot.pandas  # noqa: F401

        self.df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
        self.cat_df = pd.DataFrame(
            [[1, 2, 'A'], [3, 4, 'B'], [5, 6, 'C']], columns=['x', 'y', 'category']
        )

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_wide_chart_legend_position(self, kind, element):
        plot = self.df.hvplot(kind=kind, value_label='Test', group_label='Category', legend='left')
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['legend_position'], 'left')

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_tidy_chart_index_by_legend_position(self, kind, element):
        plot = self.df.hvplot(x='index', y='y', by='x', kind=kind, legend='left')
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['legend_position'], 'left')

    def test_scatter_color_by_legend_position(self):
        plot = self.cat_df.hvplot.scatter('x', 'y', c='category', legend='left')
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['legend_position'], 'left')

    def test_histogram_by_category_legend_position(self):
        plot = self.cat_df.hvplot.hist('y', by='category', legend='left')
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['legend_position'], 'left')


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
