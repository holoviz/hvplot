import numpy as np
import pandas as pd
import pytest
from holoviews import Store
from holoviews.element import HexTiles

# HexTiles is not supported by the plotly backend.
backends = pytest.mark.parametrize('backend', ['bokeh', 'matplotlib'], indirect=True)


@pytest.fixture(scope='module')
def df():
    return pd.DataFrame({'x': [1, 2, 3], 'y': [1.0, 4.0, 2.0], 'value': [0.5, 1.0, 1.5]})


def test_x(df, hvplot_pandas):
    plot = df.hvplot.hexbin(x='y', y='x')
    assert isinstance(plot, HexTiles)
    assert plot.kdims == ['y', 'x']


def test_y(df, tabular_lib):
    plot = tabular_lib(df).hvplot.hexbin(x='x', y='y')
    assert isinstance(plot, HexTiles)
    assert plot.kdims == ['x', 'y']
    # Counts are computed when plotting, without a value dimension.
    assert plot.vdims == []


def test_C(df, hvplot_pandas):
    plot = df.hvplot.hexbin(x='x', y='y', C='value')
    assert plot.vdims == ['value']


@backends
def test_reduce_function(df, hvplot_pandas, backend):
    plot = df.hvplot.hexbin(x='x', y='y', C='value', reduce_function=np.mean)
    assert Store.lookup_options(backend, plot, 'plot').kwargs['aggregator'] is np.mean


@backends
@pytest.mark.parametrize('gridsize', [10, (10, 20)])
def test_gridsize(df, hvplot_pandas, backend, gridsize):
    plot = df.hvplot.hexbin(x='x', y='y', gridsize=gridsize)
    assert Store.lookup_options(backend, plot, 'plot').kwargs['gridsize'] == gridsize


@backends
def test_logz(df, hvplot_pandas, backend):
    plot = df.hvplot.hexbin(x='x', y='y', logz=True)
    assert Store.lookup_options(backend, plot, 'plot').kwargs['logz'] is True


@backends
def test_min_count(df, hvplot_pandas, backend):
    plot = df.hvplot.hexbin(x='x', y='y', min_count=2)
    assert Store.lookup_options(backend, plot, 'plot').kwargs['min_count'] == 2
