from unittest import SkipTest
from parameterized import parameterized

from holoviews import NdOverlay
from holoviews.element import Curve, Area, Scatter
from holoviews.element.comparison import ComparisonTestCase
from hvplot import patch


class TestChart1D(ComparisonTestCase):

    def setUp(self):
        try:
            import pandas as pd
        except:
            raise SkipTest('Pandas not available')
        patch('pandas')
        self.df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_wide_chart(self, kind, element):
        plot = self.df.hvplot(kind=kind)
        obj = NdOverlay({'x': element(self.df, 'index', 'x').redim(x='value'),
                         'y': element(self.df, 'index', 'y').redim(y='value')}, 'Variable')
        self.assertEqual(plot, obj)

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_wide_chart_labels(self, kind, element):
        plot = self.df.hvplot(kind=kind, value_label='Test', group_label='Category')
        obj = NdOverlay({'x': element(self.df, 'index', 'x').redim(x='Test'),
                         'y': element(self.df, 'index', 'y').redim(y='Test')}, 'Category')
        self.assertEqual(plot, obj)

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_tidy_chart(self, kind, element):
        plot = self.df.hvplot(x='x', y='y', kind=kind)
        self.assertEqual(plot, element(self.df, 'x', 'y'))
        
    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_tidy_chart_index(self, kind, element):
        plot = self.df.hvplot(x='index', y='y', kind=kind)
        self.assertEqual(plot, element(self.df, 'index', 'y'))

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_tidy_chart_index_by(self, kind, element):
        plot = self.df.hvplot(x='index', y='y', by='x', kind=kind)
        obj = NdOverlay({1: element(self.df[self.df.x==1], 'index', 'y'),
                         3: element(self.df[self.df.x==3], 'index', 'y'),
                         5: element(self.df[self.df.x==5], 'index', 'y')}, 'x')
        self.assertEqual(plot, obj)
        
    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_use_index_disabled(self, kind, element):
        with self.assertRaises(ValueError):
            self.df.hvplot(use_index=False, kind=kind)

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_tidy_chart_ranges(self, kind, element):
        plot = self.df.hvplot(x='x', y='y', kind=kind, xlim=(0, 3), ylim=(5, 10))
        self.assertEqual(plot.kdims[0].range, (0, 3))
        self.assertEqual(plot.vdims[0].range, (5, 10))

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_wide_chart_ranges(self, kind, element):
        plot = self.df.hvplot(kind=kind, xlim=(0, 3), ylim=(5, 10))
        self.assertEqual(plot.last.kdims[0].range, (0, 3))
        self.assertEqual(plot.last.vdims[0].range, (5, 10))

    def test_area_stacked(self):
        plot = self.df.hvplot.area(stacked=True)
        obj = NdOverlay({'x': Area(self.df, 'index', 'x').redim(x='value'),
                         'y': Area(self.df, 'index', 'y').redim(y='value')}, 'Variable')
        self.assertEqual(plot, Area.stack(obj))
