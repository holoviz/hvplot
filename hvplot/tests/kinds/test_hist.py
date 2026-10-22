import numpy as np
import pandas as pd
import pytest


@pytest.mark.parametrize('tabular_lib', ['pandas', 'dask'], indirect=True)
def test_histogram_log_bins(tabular_lib):
    df = tabular_lib(pd.DataFrame({'z': [1, 1, 4, 4]}))
    plot_logx = df.hvplot.hist(bins=2, logx=True)
    plot_loglog = df.hvplot.hist(bins=2, loglog=True)
    np.testing.assert_array_equal(plot_logx.data['z'], np.array([1.0, 2.0, 4.0]))
    np.testing.assert_array_equal(plot_loglog.data['z'], np.array([1.0, 2.0, 4.0]))
