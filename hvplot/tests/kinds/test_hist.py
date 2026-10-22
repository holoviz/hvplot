import numpy as np
import pandas as pd
import pytest
from holoviews.element import Histogram


@pytest.fixture(scope='module')
def df():
    return pd.DataFrame({'v': [0.0, 1.0, 1.0, 2.0, 3.0, 4.0], 'w': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]})


def test_y(df, tabular_lib):
    plot = tabular_lib(df).hvplot.hist(y='v', bins=2)
    assert isinstance(plot, Histogram)
    assert plot.kdims == ['v']
    assert plot.vdims == ['v_count']
    np.testing.assert_array_equal(plot.edges, [0, 2, 4])
    np.testing.assert_array_equal(plot.dimension_values('v_count'), [3, 3])


def test_y_list(df, hvplot_pandas):
    plot = df.hvplot.hist(y=['v', 'w'])
    assert list(plot.keys()) == ['v', 'w']
    assert all(isinstance(hist, Histogram) for hist in plot)


def test_bins(df, hvplot_pandas):
    plot = df.hvplot.hist(y='v', bins=4)
    np.testing.assert_array_equal(plot.edges, [0, 1, 2, 3, 4])


def test_bins_edges(df, hvplot_pandas):
    plot = df.hvplot.hist(y='v', bins=[0, 1, 4])
    np.testing.assert_array_equal(plot.edges, [0, 1, 4])
    np.testing.assert_array_equal(plot.dimension_values('v_count'), [1, 5])


def test_bins_method(df, hvplot_pandas):
    plot = df.hvplot.hist(y='v', bins='sturges')
    np.testing.assert_array_equal(plot.edges, np.histogram_bin_edges(df['v'], 'sturges'))


def test_bin_range(df, hvplot_pandas):
    plot = df.hvplot.hist(y='v', bins=2, bin_range=(0, 8))
    np.testing.assert_array_equal(plot.edges, [0, 4, 8])
    np.testing.assert_array_equal(plot.dimension_values('v_count'), [5, 1])


@pytest.mark.parametrize(('normed', 'expected'), [(True, [0.25, 0.25]), ('height', [1, 1])])
def test_normed(df, hvplot_pandas, normed, expected):
    plot = df.hvplot.hist(y='v', bins=2, normed=normed)
    assert plot.vdims == ['v_frequency']
    np.testing.assert_array_equal(plot.dimension_values('v_frequency'), expected)


def test_cumulative(df, hvplot_pandas):
    plot = df.hvplot.hist(y='v', bins=2, cumulative=True)
    np.testing.assert_array_equal(plot.dimension_values('v_count'), [3, 6])


@pytest.mark.parametrize('tabular_lib', ['pandas', 'dask'], indirect=True)
def test_histogram_log_bins(tabular_lib):
    df = tabular_lib(pd.DataFrame({'z': [1, 1, 4, 4]}))
    plot_logx = df.hvplot.hist(bins=2, logx=True)
    plot_loglog = df.hvplot.hist(bins=2, loglog=True)
    np.testing.assert_array_equal(plot_logx.data['z'], np.array([1.0, 2.0, 4.0]))
    np.testing.assert_array_equal(plot_loglog.data['z'], np.array([1.0, 2.0, 4.0]))
