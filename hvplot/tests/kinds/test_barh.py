import pandas as pd
import pytest
from holoviews import Store
from holoviews.element import Bars


@pytest.fixture(scope='module')
def df():
    return pd.DataFrame({'cat': ['A', 'B', 'C'], 'y': [1.0, 4.0, 2.0], 'y2': [0.5, 1.0, 1.5]})


def test_barh_inverts_axes(df, hvplot_pandas, backend):
    plot = df.hvplot.barh(x='cat', y='y')
    assert Store.lookup_options(backend, plot, 'plot').kwargs['invert_axes'] is True


def test_x(df, hvplot_pandas):
    # x is the categorical dimension, drawn along the vertical axis.
    plot = df.hvplot.barh(x='cat', y='y')
    assert isinstance(plot, Bars)
    assert plot.kdims == ['cat']


def test_x_default_index(df, hvplot_pandas):
    plot = df.hvplot.barh(y='y')
    assert plot.kdims == ['index']


def test_y(df, tabular_lib):
    # y is the value dimension, drawn along the horizontal axis.
    plot = tabular_lib(df).hvplot.barh(x='cat', y='y')
    assert isinstance(plot, Bars)
    assert plot.kdims == ['cat']
    assert plot.vdims == ['y']


@pytest.mark.parametrize('stacked', [True, False])
def test_stacked(df, hvplot_pandas, backend, stacked):
    plot = df.hvplot.barh(x='cat', y=['y', 'y2'], stacked=stacked)
    assert Store.lookup_options(backend, plot, 'plot').kwargs['stacked'] is stacked
