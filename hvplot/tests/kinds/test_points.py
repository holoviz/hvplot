from unittest import SkipTest

import pandas as pd
from holoviews.element import Path, Points
from holoviews.element.comparison import ComparisonTestCase
from parameterized import parameterized


class TestChart2D(ComparisonTestCase):
    def setUp(self):
        import hvplot.pandas  # noqa: F401

        self.df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])

    @parameterized.expand([('points', Points), ('paths', Path)])
    def test_2d_defaults(self, kind, element):
        plot = self.df.hvplot(kind=kind)
        self.assertEqual(plot, element(self.df, ['x', 'y']))

    @parameterized.expand([('points', Points), ('paths', Path)])
    def test_2d_chart(self, kind, element):
        plot = self.df.hvplot(x='x', y='y', kind=kind)
        self.assertEqual(plot, element(self.df, ['x', 'y']))

    @parameterized.expand([('points', Points), ('paths', Path)])
    def test_2d_index_and_c(self, kind, element):
        plot = self.df.hvplot(x='index', y='y', c='x', kind=kind)
        self.assertEqual(plot, element(self.df, ['index', 'y'], ['x']))


class TestChart2DDask(TestChart2D):
    def setUp(self):
        super().setUp()
        try:
            import dask.dataframe as dd
        except ImportError:
            raise SkipTest('Dask not available')
        import hvplot.dask  # noqa: F401

        self.df = dd.from_pandas(self.df, npartitions=2)
