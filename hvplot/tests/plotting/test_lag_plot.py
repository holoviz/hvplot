import holoviews as hv
import pandas as pd
import pytest
from holoviews import Store

from hvplot.plotting import lag_plot


def test_lag_plot_series():
    plot = lag_plot(pd.Series([1, 2, 3, 4, 5]))
    assert isinstance(plot, hv.Scatter)
    assert plot.kdims == ['y(t)']
    assert plot.vdims == ['y(t + 1)']
    assert plot.array().tolist() == [[1, 2], [2, 3], [3, 4], [4, 5]]


def test_lag_plot_lag():
    plot = lag_plot(pd.Series([1, 2, 3, 4, 5]), lag=2)
    assert plot.vdims == ['y(t + 2)']
    assert plot.array().tolist() == [[1, 3], [2, 4], [3, 5]]


def test_lag_plot_dataframe_colored_by_column():
    df = pd.DataFrame({'a': [1, 2, 3], 'b': [10, 20, 30]})
    plot = lag_plot(df)
    assert plot.vdims == ['y(t + 1)', 'variable']
    assert plot.array().tolist() == [[1, 2, 'a'], [2, 3, 'a'], [10, 20, 'b'], [20, 30, 'b']]
    color = Store.lookup_options('bokeh', plot, 'style').kwargs['color']
    assert repr(color) == repr(hv.dim('variable'))


def test_lag_plot_kwds():
    plot = lag_plot(pd.Series([1, 2, 3]), width=300)
    assert Store.lookup_options('bokeh', plot, 'plot').kwargs['width'] == 300


@pytest.mark.parametrize('lag', [0, -1, 1.5])
def test_lag_plot_invalid_lag(lag):
    with pytest.raises(ValueError, match='lag must be a positive integer'):
        lag_plot(pd.Series([1, 2, 3]), lag=lag)
