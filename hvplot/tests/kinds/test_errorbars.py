from unittest import SkipTest

import pandas as pd
from holoviews import Store
from holoviews.element.comparison import ComparisonTestCase


class TestChart1D(ComparisonTestCase):
    def setUp(self):
        import hvplot.pandas  # noqa: F401

        df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
        self.df_desc = df.describe().transpose().sort_values('mean')

    def test_errorbars_no_hover(self):
        plot = self.df_desc.hvplot.errorbars(y='mean', yerr1='std')
        assert list(plot.dimensions()) == ['index', 'mean', 'std']
        bkplot = Store.renderers['bokeh'].get_plot(plot)
        assert not bkplot.tools


class TestChart1DDask(TestChart1D):
    def setUp(self):
        super().setUp()
        try:
            import dask.dataframe  # noqa: F401
        except ImportError:
            raise SkipTest('Dask not available')
        import hvplot.dask  # noqa: F401
