from unittest import SkipTest

import numpy as np
import pandas as pd
from holoviews.element.comparison import ComparisonTestCase


class TestChart1D(ComparisonTestCase):
    def setUp(self):
        import hvplot.pandas  # noqa: F401

        self.dt_df = pd.DataFrame(
            np.random.rand(90), index=pd.date_range('2019-01-01', '2019-03-31')
        )
        multii_df = pd.DataFrame(
            {'A': [1, 2, 3, 4], 'B': ['a', 'a', 'b', 'b'], 'C': [0, 1, 2, 1.5]}
        )
        self.multii_df = multii_df.set_index(['A', 'B'])

    def test_table_datetime_index_displayed(self):
        table = self.dt_df.hvplot.table()
        assert table.kdims[0] == 'index'

    def test_table_multi_index_displayed(self):
        table = self.multii_df.hvplot.table()
        assert table.kdims[:2] == self.multii_df.index.names


class TestChart1DDask(TestChart1D):
    def setUp(self):
        super().setUp()
        try:
            import dask.dataframe as dd
        except ImportError:
            raise SkipTest('Dask not available')
        import hvplot.dask  # noqa: F401

        self.dt_df = dd.from_pandas(self.dt_df, npartitions=3)

    def test_table_datetime_index_displayed(self):
        raise SkipTest('Only supported for Pandas DatetimeIndex.')

    def test_table_multi_index_displayed(self):
        raise SkipTest('Dask does not support MultiIndex Dataframes.')
