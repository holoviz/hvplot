from unittest import SkipTest

import numpy as np
import pandas as pd
from holoviews.element.comparison import ComparisonTestCase


class TestChart1D(ComparisonTestCase):
    def setUp(self):
        import hvplot.pandas  # noqa: F401

    def test_histogram_log_bins(self):
        df = pd.DataFrame({'z': [1, 1, 4, 4]})
        plot_logx = df.hvplot.hist(bins=2, logx=True)
        plot_loglog = df.hvplot.hist(bins=2, loglog=True)
        np.testing.assert_array_equal(plot_logx.data['z'], np.array([1.0, 2.0, 4.0]))
        np.testing.assert_array_equal(plot_loglog.data['z'], np.array([1.0, 2.0, 4.0]))


class TestChart1DDask(TestChart1D):
    def setUp(self):
        super().setUp()
        try:
            import dask.dataframe  # noqa: F401
        except ImportError:
            raise SkipTest('Dask not available')
        import hvplot.dask  # noqa: F401
