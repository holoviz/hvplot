import pandas as pd
from hvplot import HvPlot, patch
from holoviews import Store, Scatter
from holoviews.element.comparison import ComparisonTestCase


class TestDefaults(ComparisonTestCase):

    def setUp(self):
        patch('pandas')
        self.df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])

    def test_define_default_options(self):
        hvplot = HvPlot(self.df, width=42, height=42)
        curve = hvplot(y='y')
        opts = Store.lookup_options('bokeh', curve, 'plot')
        self.assertEqual(opts.options.get('width'), 42)
        self.assertEqual(opts.options.get('height'), 42)

    def test_define_custom_method(self):
        hvplot = HvPlot(self.df, {'custom_scatter': {'width': 42, 'height': 42}})
        custom_scatter = hvplot.custom_scatter(y='y')
        scatter = hvplot.scatter(y='y')
        custom_opts = Store.lookup_options('bokeh', custom_scatter, 'plot')
        opts = Store.lookup_options('bokeh', scatter, 'plot')
        self.assertEqual(custom_opts.options.get('width'), 42)
        self.assertEqual(custom_opts.options.get('height'), 42)
        self.assertNotEqual(opts.options.get('width'), 42)
        self.assertNotEqual(opts.options.get('height'), 42)

    def test_define_customize_method(self):
        hvplot = HvPlot(self.df, {'scatter': {'width': 42, 'height': 42}})
        custom_scatter = hvplot.scatter(y='y')
        curve = hvplot.line(y='y')
        custom_opts = Store.lookup_options('bokeh', custom_scatter, 'plot')
        opts = Store.lookup_options('bokeh', curve, 'plot')
        self.assertEqual(custom_opts.options.get('width'), 42)
        self.assertEqual(custom_opts.options.get('height'), 42)
        self.assertNotEqual(opts.options.get('width'), 42)
        self.assertNotEqual(opts.options.get('height'), 42)

    def test_attempt_to_override_kind_on_method(self):
        hvplot = HvPlot(self.df, {'scatter': {'kind': 'line'}})
        self.assertIsInstance(hvplot.scatter(y='y'), Scatter)
