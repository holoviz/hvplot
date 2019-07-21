from unittest import SkipTest

from holoviews import NdOverlay, Store
from holoviews.element import Curve, Area, Scatter
from holoviews.element.comparison import ComparisonTestCase
from hvplot import patch


class TestOptions(ComparisonTestCase):

    def setUp(self):
        try:
            import pandas as pd
        except:
            raise SkipTest('Pandas not available')
        patch('pandas')
        self.df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
        self.cat_df = pd.DataFrame([[1, 2, 'A'], [3, 4, 'B'], [5, 6, 'C']], columns=['x', 'y', 'category'])

    def test_scatter_legend_position(self):
        plot = self.cat_df.hvplot.scatter('x', 'y', c='category', legend='left')
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['legend_position'], 'left')

    def test_histogram_by_category_legend_position(self):
        plot = self.cat_df.hvplot.hist('y', by='category', legend='left')
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['legend_position'], 'left')

    def test_histogram_legend_position(self):
        plot = self.cat_df.hvplot.hist('y', legend='left')
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['legend_position'], 'left')

    def test_scatter_logz(self):
        plot = self.df.hvplot.scatter('x', 'y', c='x', logz=True)
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['logz'], True)

