import holoviews as hv
import numpy as np
import pandas as pd
import pytest
from holoviews import Store

pytestmark = pytest.mark.usefixtures('hvplot_pandas')

kinds = pytest.mark.parametrize('kind', ['scatter', 'points'])

alpha_backends = pytest.mark.parametrize(
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


@pytest.fixture(scope='module')
def df():
    return pd.DataFrame(
        [[1, 2, 'A', 0.1], [3, 4, 'B', 0.2], [5, 6, 'C', 0.3]],
        columns=['x', 'y', 'category', 'number'],
    )


@kinds
def test_logz(df, kind, backend):
    plot = df.hvplot('x', 'y', c='x', logz=True, kind=kind)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['logz'] is True


@kinds
def test_size_dim(df, kind, backend):
    plot = df.hvplot('x', 'y', s='number', kind=kind)
    opts = Store.lookup_options(backend, plot, 'style')
    param = 's' if backend == 'matplotlib' else 'size'
    assert opts.kwargs[param] == 'number'
    assert 'number' in plot.vdims


@alpha_backends
@kinds
def test_alpha_dim(df, kind, backend):
    plot = df.hvplot('x', 'y', alpha='number', kind=kind)
    opts = Store.lookup_options(backend, plot, 'style')
    assert opts.kwargs['alpha'] == 'number'
    assert 'number' in plot.vdims


@kinds
def test_marker_dim(df, kind, backend):
    plot = df.hvplot('x', 'y', marker='category', kind=kind)
    opts = Store.lookup_options(backend, plot, 'style')
    assert opts.kwargs['marker'] == 'category'
    assert 'category' in plot.vdims


@kinds
def test_size_dim_overlay(df, kind, backend):
    plot = df.hvplot('x', 'y', s='number', by='category', kind=kind)
    opts = Store.lookup_options(backend, plot.last, 'style')
    param = 's' if backend == 'matplotlib' else 'size'
    assert opts.kwargs[param] == 'number'
    assert 'number' in plot.last.vdims


@alpha_backends
@kinds
def test_alpha_dim_overlay(df, kind, backend):
    plot = df.hvplot('x', 'y', alpha='number', by='category', kind=kind)
    opts = Store.lookup_options(backend, plot.last, 'style')
    assert opts.kwargs['alpha'] == 'number'
    assert 'number' in plot.last.vdims


def test_pandas_dim_size_alias():
    df = pd.DataFrame({'x': np.linspace(0, 4, 5), 'y': np.linspace(1, 5, 5)})
    dim_expr = hv.dim('y') * 10
    scatter = df.hvplot.scatter('x', 'y', s=dim_expr)
    opts = Store.lookup_options('bokeh', scatter, 'style')
    assert repr(opts.kwargs['size']) == repr(dim_expr)


@pytest.mark.parametrize('tabular_lib', ['pandas', 'dask'], indirect=True)
def test_scatter_size_set_to_series(tabular_lib):
    df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
    plot = tabular_lib(df).hvplot.scatter('x', 'y', s=df['y'])
    opts = Store.lookup_options('bokeh', plot, 'style')
    assert '_size' in plot.data.columns
    assert opts.kwargs['size'] == '_size'
