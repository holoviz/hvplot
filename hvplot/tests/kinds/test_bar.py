from unittest import SkipTest

import pandas as pd
from holoviews.element.comparison import ComparisonTestCase


class TestChart1D(ComparisonTestCase):
    def setUp(self):
        import hvplot.pandas  # noqa: F401

        cat_df = pd.DataFrame(
            [[1, 2, 'A'], [3, 4, 'B'], [5, 6, 'C']], columns=['x', 'y', 'category']
        )
        self.cat_df_index_y = cat_df.set_index('y')

    def test_bar_y_from_index_with_by(self):
        # Testing a somewhat silly plot but that seemed to be supported
        # https://github.com/holoviz/hvplot/blob/6c96c7e9abcd44380d2122e3d86827dedab32dea/hvplot/converter.py#L1996-L1999
        plot = self.cat_df_index_y.hvplot.bar(x='x', y='y', by='category')
        assert plot.kdims == ['x', 'category']
        assert plot.vdims == ['y']


class TestChart1DDask(TestChart1D):
    def setUp(self):
        super().setUp()
        try:
            import dask.dataframe as dd
        except ImportError:
            raise SkipTest('Dask not available')
        import hvplot.dask  # noqa: F401

        self.cat_df_index_y = dd.from_pandas(self.cat_df_index_y, npartitions=3)
