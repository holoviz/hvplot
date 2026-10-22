import holoviews as hv
import numpy as np
import pandas as pd
import pytest
from holoviews import Store
from holoviews.element import Scatter

pytestmark = pytest.mark.usefixtures('hvplot_pandas')

alpha_backends = pytest.mark.parametrize(
    'backend',
    [
        'bokeh',
        pytest.param(
            'matplotlib',
            marks=pytest.mark.xfail(
                reason='BUG: a dim mapped to alpha is not supported by matplotlib, fails on render'
            ),
        ),
        pytest.param(
            'plotly', marks=pytest.mark.xfail(reason='cannot map a dim to alpha with plotly')
        ),
    ],
    indirect=True,
)


@pytest.fixture(scope='module')
def df():
    return pd.DataFrame(
        [[1, 2, 'A', 0.1], [3, 4, 'B', 0.2], [5, 6, 'C', 0.3]],
        columns=['x', 'y', 'category', 'number'],
    )


def size_opt(backend):
    return 's' if backend == 'matplotlib' else 'size'


def test_x(df):
    plot = df.hvplot.scatter(x='number', y='y')
    assert isinstance(plot, Scatter)
    assert plot.kdims == ['number']
    assert plot.vdims == ['y']


def test_y(df, tabular_lib):
    plot = tabular_lib(df).hvplot.scatter(x='x', y='y')
    assert isinstance(plot, Scatter)
    assert plot.kdims == ['x']
    assert plot.vdims == ['y']
    assert list(plot.dimension_values('y')) == [2, 4, 6]


def test_c(df, backend):
    plot = df.hvplot.scatter('x', 'y', c='number')
    assert 'number' in plot.vdims
    color = Store.lookup_options(backend, plot, 'style').kwargs['color']
    assert repr(color) == repr(hv.dim('number'))
    assert Store.lookup_options(backend, plot, 'plot').kwargs['colorbar'] is True


def test_logz(df, backend):
    plot = df.hvplot.scatter('x', 'y', c='x', logz=True)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['logz'] is True


def test_s(df, backend):
    # The marker area is proportional to s.
    plot = df.hvplot.scatter('x', 'y', s=16)
    assert Store.lookup_options(backend, plot, 'style').kwargs[size_opt(backend)] == 4


def test_s_dim(df, backend):
    plot = df.hvplot.scatter('x', 'y', s='number')
    size = Store.lookup_options(backend, plot, 'style').kwargs[size_opt(backend)]
    np.testing.assert_allclose(size.apply(plot), np.sqrt(df['number']))
    assert 'number' in plot.vdims


def test_s_dim_overlay(df, backend):
    plot = df.hvplot.scatter('x', 'y', s='number', by='category')
    size = Store.lookup_options(backend, plot.last, 'style').kwargs[size_opt(backend)]
    np.testing.assert_allclose(size.apply(plot.last), np.sqrt([0.3]))
    assert 'number' in plot.last.vdims


def test_s_dim_expression():
    df = pd.DataFrame({'x': np.linspace(0, 4, 5), 'y': np.linspace(1, 5, 5)})
    dim_expr = hv.dim('y') * 10
    scatter = df.hvplot.scatter('x', 'y', s=dim_expr)
    opts = Store.lookup_options('bokeh', scatter, 'style')
    assert repr(opts.kwargs['size']) == repr(dim_expr)


@pytest.mark.parametrize('tabular_lib', ['pandas', 'dask'], indirect=True)
def test_s_series(tabular_lib):
    df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
    plot = tabular_lib(df).hvplot.scatter('x', 'y', s=df['y'])
    opts = Store.lookup_options('bokeh', plot, 'style')
    assert '_size' in plot.data.columns
    assert opts.kwargs['size'] == '_size'


def test_scale(df, backend):
    plot = df.hvplot.scatter('x', 'y', s=16, scale=2)
    assert Store.lookup_options(backend, plot, 'style').kwargs[size_opt(backend)] == 8


def test_marker(df, backend):
    plot = df.hvplot.scatter('x', 'y', marker='^')
    assert Store.lookup_options(backend, plot, 'style').kwargs['marker'] == '^'


# Matplotlib and Plotly cannot render a marker mapped to a column.
@pytest.mark.parametrize('backend', ['bokeh'], indirect=True)
def test_marker_dim(df, backend):
    plot = df.hvplot.scatter('x', 'y', marker='category')
    opts = Store.lookup_options(backend, plot, 'style')
    assert opts.kwargs['marker'] == 'category'
    assert 'category' in plot.vdims


@alpha_backends
def test_alpha_dim(df, backend):
    plot = df.hvplot.scatter('x', 'y', alpha='number')
    opts = Store.lookup_options(backend, plot, 'style')
    assert opts.kwargs['alpha'] == 'number'
    assert 'number' in plot.vdims
    hv.render(plot, backend=backend)


# Unlike without `by`, the alpha mapping renders with matplotlib.
@pytest.mark.parametrize(
    'backend',
    [
        'bokeh',
        'matplotlib',
        pytest.param(
            'plotly', marks=pytest.mark.xfail(reason='cannot map a dim to alpha with plotly')
        ),
    ],
    indirect=True,
)
def test_alpha_dim_overlay(df, backend):
    plot = df.hvplot.scatter('x', 'y', alpha='number', by='category')
    opts = Store.lookup_options(backend, plot.last, 'style')
    assert opts.kwargs['alpha'] == 'number'
    assert 'number' in plot.last.vdims
    hv.render(plot, backend=backend)
