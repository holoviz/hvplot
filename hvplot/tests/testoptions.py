from unittest import SkipTest

from parameterized import parameterized

from holoviews import Store
from holoviews.element.comparison import ComparisonTestCase
from hvplot import patch


class TestOptions(ComparisonTestCase):

    def setUp(self):
        try:
            import pandas as pd
        except:
            raise SkipTest('Pandas not available')
        patch('pandas')
        self.df = pd.DataFrame([[1, 2, 'A', 0.1], [3, 4, 'B', 0.2], [5, 6, 'C', 0.3]],
                               columns=['x', 'y', 'category', 'number'])

    def test_scatter_legend_position(self):
        plot = self.df.hvplot.scatter('x', 'y', c='category', legend='left')
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['legend_position'], 'left')

    def test_histogram_by_category_legend_position(self):
        plot = self.df.hvplot.hist('y', by='category', legend='left')
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['legend_position'], 'left')

    def test_histogram_legend_position(self):
        plot = self.df.hvplot.hist('y', legend='left')
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['legend_position'], 'left')

    @parameterized.expand(['scatter', 'points'])
    def test_logz(self, kind):
        plot = self.df.hvplot('x', 'y', c='x', logz=True, kind=kind)
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['logz'], True)

    @parameterized.expand(['scatter', 'points'])
    def test_color_dim(self, kind):
        plot = self.df.hvplot('x', 'y', c='number', kind=kind)
        opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(opts.kwargs['color'], 'number')
        self.assertIn('number', plot.vdims)

    @parameterized.expand(['scatter', 'points'])
    def test_size_dim(self, kind):
        plot = self.df.hvplot('x', 'y', s='number', kind=kind)
        opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(opts.kwargs['size'], 'number')
        self.assertIn('number', plot.vdims)

    @parameterized.expand(['scatter', 'points'])
    def test_alpha_dim(self, kind):
        plot = self.df.hvplot('x', 'y', alpha='number', kind=kind)
        opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(opts.kwargs['alpha'], 'number')
        self.assertIn('number', plot.vdims)

    @parameterized.expand(['scatter', 'points'])
    def test_marker_dim(self, kind):
        plot = self.df.hvplot('x', 'y', marker='category', kind=kind)
        opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(opts.kwargs['marker'], 'category')
        self.assertIn('category', plot.vdims)

    @parameterized.expand(['scatter', 'points'])
    def test_color_dim_overlay(self, kind):
        plot = self.df.hvplot('x', 'y', c='number', by='category', kind=kind)
        opts = Store.lookup_options('bokeh', plot.last, 'style')
        self.assertEqual(opts.kwargs['color'], 'number')
        self.assertIn('number', plot.last.vdims)

    @parameterized.expand(['scatter', 'points'])
    def test_size_dim_overlay(self, kind):
        plot = self.df.hvplot('x', 'y', s='number', by='category', kind=kind)
        opts = Store.lookup_options('bokeh', plot.last, 'style')
        self.assertEqual(opts.kwargs['size'], 'number')
        self.assertIn('number', plot.last.vdims)

    @parameterized.expand(['scatter', 'points'])
    def test_alpha_dim_overlay(self, kind):
        plot = self.df.hvplot('x', 'y', alpha='number', by='category', kind=kind)
        opts = Store.lookup_options('bokeh', plot.last, 'style')
        self.assertEqual(opts.kwargs['alpha'], 'number')
        self.assertIn('number', plot.last.vdims)

