import holoviews as hv
import numpy as np
import pandas as pd
import pytest
from holoviews import Store
from holoviews.element import Points
from holoviews.testing import assert_element_equal

pytestmark = pytest.mark.usefixtures('hvplot_pandas')


@pytest.fixture
def df():
    return pd.DataFrame(
        {'cat': ['a', 'b', 'c'], 'x': [1, 3, 5], 'y': [2, 4, 6], 'number': [0.1, 0.2, 0.3]}
    )


def size_opt(backend):
    return 's' if backend == 'matplotlib' else 'size'


def test_x(df):
    plot = df.hvplot.points(x='number', y='y')
    assert_element_equal(plot, Points(df, ['number', 'y'], []))


def test_x_default(df):
    plot = df.drop(columns='cat').hvplot.points()
    assert_element_equal(plot, Points(df, ['x', 'y'], []))


@pytest.mark.xfail(
    strict=True, reason='BUG: points defaults x/y to the first two columns, not numeric ones'
)
def test_x_default_first_numeric(df):
    plot = df.hvplot.points()
    assert plot.kdims == ['x', 'y']


def test_x_index(df):
    plot = df.hvplot.points(x='index', y='y', c='x')
    assert_element_equal(plot, Points(df.reset_index(), ['index', 'y'], ['x']))


def test_y(df, tabular_lib):
    plot = tabular_lib(df).hvplot.points(x='x', y='y')
    assert isinstance(plot, Points)
    assert plot.kdims == ['x', 'y']
    assert plot.vdims == []
    assert list(plot.dimension_values('y')) == [2, 4, 6]


def test_c(df, backend):
    plot = df.hvplot.points('x', 'y', c='number')
    assert plot.vdims == ['number']
    color = Store.lookup_options(backend, plot, 'style').kwargs['color']
    assert repr(color) == repr(hv.dim('number'))
    assert Store.lookup_options(backend, plot, 'plot').kwargs['colorbar'] is True


def test_logz(df, backend):
    plot = df.hvplot.points('x', 'y', c='number', logz=True)
    assert Store.lookup_options(backend, plot, 'plot').kwargs['logz'] is True


def test_s(df, backend):
    # The marker area is proportional to s.
    plot = df.hvplot.points('x', 'y', s=16)
    assert Store.lookup_options(backend, plot, 'style').kwargs[size_opt(backend)] == 4


def test_s_dim(df, backend):
    plot = df.hvplot.points('x', 'y', s='number')
    assert 'number' in plot.vdims
    size = Store.lookup_options(backend, plot, 'style').kwargs[size_opt(backend)]
    np.testing.assert_allclose(size.apply(plot), np.sqrt(df['number']))


def test_scale(df, backend):
    plot = df.hvplot.points('x', 'y', s=16, scale=2)
    assert Store.lookup_options(backend, plot, 'style').kwargs[size_opt(backend)] == 8


def test_marker(df, backend):
    plot = df.hvplot.points('x', 'y', marker='^')
    assert Store.lookup_options(backend, plot, 'style').kwargs['marker'] == '^'


def test_marker_dim(df, backend):
    plot = df.hvplot.points('x', 'y', marker='cat')
    assert 'cat' in plot.vdims
    assert Store.lookup_options(backend, plot, 'style').kwargs['marker'] == 'cat'
