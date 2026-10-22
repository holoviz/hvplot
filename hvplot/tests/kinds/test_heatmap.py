from unittest import SkipTest, expectedFailure

import numpy as np
import pandas as pd
from holoviews.element import HeatMap
from holoviews.element.comparison import ComparisonTestCase


class TestChart2D(ComparisonTestCase):
    def setUp(self):
        import hvplot.pandas  # noqa: F401

        self.df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
        self.time_df = pd.DataFrame(
            {
                'time': pd.date_range('1/1/2000', periods=5 * 24, freq='1h', tz='UTC'),
                'temp': np.sin(np.linspace(0, 5 * 2 * np.pi, 5 * 24)).cumsum(),
            }
        )

    def test_heatmap_2d_index_columns(self):
        plot = self.df.hvplot.heatmap()
        self.assertEqual(
            plot, HeatMap((['x', 'y'], [0, 1, 2], self.df.values), ['columns', 'index'], 'value')
        )

    def test_heatmap_2d_derived_x_and_y(self):
        plot = self.time_df.hvplot.heatmap(x='time.hour', y='time.day', C='temp')
        assert plot.kdims == ['time.hour', 'time.day']
        assert plot.vdims == ['temp']


class TestChart2DDask(TestChart2D):
    def setUp(self):
        super().setUp()
        try:
            import dask.dataframe as dd
        except ImportError:
            raise SkipTest('Dask not available')
        import hvplot.dask  # noqa: F401

        self.df = dd.from_pandas(self.df, npartitions=2)

    @expectedFailure
    def test_heatmap_2d_index_columns(self):
        self.df.hvplot.heatmap()
