from unittest import SkipTest

import pandas as pd
from holoviews import NdOverlay
from holoviews.core.dimension import Dimension
from holoviews.element import Area
from holoviews.element.comparison import ComparisonTestCase


class TestChart1D(ComparisonTestCase):
    def setUp(self):
        import hvplot.pandas  # noqa: F401

        self.df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])

    def test_area_stacked(self):
        plot = self.df.hvplot.area(stacked=True)
        obj = NdOverlay(
            {
                'x': Area(self.df, 'index', Dimension('x', label='value')),
                'y': Area(self.df, 'index', Dimension('y', label='value')),
            },
            'Variable',
        )
        self.assertEqual(plot, Area.stack(obj))


class TestChart1DDask(TestChart1D):
    def setUp(self):
        super().setUp()
        try:
            import dask.dataframe as dd
        except ImportError:
            raise SkipTest('Dask not available')
        import hvplot.dask  # noqa: F401

        self.df = dd.from_pandas(self.df, npartitions=2)
