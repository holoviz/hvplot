import numpy as np
import pandas as pd
import pytest
from holoviews import NdLayout, NdOverlay
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


def test_y_list_shared_bins(hvplot_pandas):
    # The columns have disjoint ranges, but share the bins to be comparable.
    df = pd.DataFrame({'a': [0.0, 1.0, 2.0, 3.0], 'b': [10.0, 11.0, 12.0, 13.0]})
    plot = df.hvplot.hist(y=['a', 'b'], bins=2)
    for hist in plot:
        np.testing.assert_array_equal(hist.edges, [0, 6.5, 13])
    np.testing.assert_array_equal(plot['a'].dimension_values('a_count'), [4, 0])
    np.testing.assert_array_equal(plot['b'].dimension_values('b_count'), [0, 4])


def test_y_list_bin_range(hvplot_pandas):
    df = pd.DataFrame({'a': [0.0, 1.0, 2.0, 3.0], 'b': [10.0, 11.0, 12.0, 13.0]})
    plot = df.hvplot.hist(y=['a', 'b'], bins=2, bin_range=(0, 20))
    for hist in plot:
        np.testing.assert_array_equal(hist.edges, [0, 10, 20])


def test_y_list_shared_axes_false(hvplot_pandas):
    # Without shared axes each column gets its own bins.
    df = pd.DataFrame({'a': [0.0, 1.0, 2.0, 3.0], 'b': [10.0, 11.0, 12.0, 13.0]})
    plot = df.hvplot.hist(y=['a', 'b'], bins=2, shared_axes=False)
    np.testing.assert_array_equal(plot['a'].edges, [0, 1.5, 3])
    np.testing.assert_array_equal(plot['b'].edges, [10, 11.5, 13])


def test_by(hvplot_pandas):
    df = pd.DataFrame({'v': [0.0, 1.0, 2.0, 10.0, 11.0, 12.0], 'g': list('aaabbb')})
    plot = df.hvplot.hist(y='v', by='g', bins=2)
    assert isinstance(plot, NdOverlay)
    assert list(plot.keys()) == ['a', 'b']
    # One histogram per group, on the same bins.
    for hist in plot:
        np.testing.assert_array_equal(hist.edges, [0, 6, 12])
    np.testing.assert_array_equal(plot['a'].dimension_values('v_count'), [3, 0])
    np.testing.assert_array_equal(plot['b'].dimension_values('v_count'), [0, 3])


def test_by_subplots(hvplot_pandas):
    df = pd.DataFrame({'v': [0.0, 1.0, 2.0, 10.0, 11.0, 12.0], 'g': list('aaabbb')})
    plot = df.hvplot.hist(y='v', by='g', bins=2, subplots=True)
    assert isinstance(plot, NdLayout)
    assert list(plot.keys()) == ['a', 'b']


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


@pytest.mark.parametrize(
    ('normed', 'expected'), [(True, [0.25, 0.25]), ('integral', [0.25, 0.25]), ('height', [1, 1])]
)
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
