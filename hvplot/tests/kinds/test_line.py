import pandas as pd
import pytest
from holoviews import NdOverlay
from holoviews.element import Curve


@pytest.fixture
def df():
    return pd.DataFrame({'x': [1, 2, 3], 'y': [2, 4, 3], 'z': [0.1, 0.2, 0.3]})


def test_x(df, hvplot_pandas):
    plot = df.hvplot.line(x='z', y='y')
    assert isinstance(plot, Curve)
    assert plot.kdims == ['z']
    assert plot.vdims == ['y']


def test_x_default_index(df, hvplot_pandas):
    plot = df.hvplot.line(y='y')
    assert plot.kdims == ['index']


def test_y(df, tabular_lib):
    plot = tabular_lib(df).hvplot.line(x='x', y='y')
    assert isinstance(plot, Curve)
    assert plot.kdims == ['x']
    assert plot.vdims == ['y']
    assert list(plot.dimension_values('y')) == [2, 4, 3]


def test_y_list(df, hvplot_pandas):
    plot = df.hvplot.line(x='x', y=['y', 'z'])
    assert isinstance(plot, NdOverlay)
    assert list(plot.keys()) == ['y', 'z']
    assert plot['z'].kdims == ['x']
    assert plot['z'].vdims[0].name == 'z'


def test_y_list_single(df, hvplot_pandas):
    # A list of one column is plotted as a single curve, not as an overlay.
    plot = df.hvplot.line(x='x', y=['y'])
    assert isinstance(plot, Curve)
    assert plot.vdims == ['y']
