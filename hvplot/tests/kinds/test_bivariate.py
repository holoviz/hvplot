import pandas as pd
import pytest
from holoviews import Store
from holoviews.element import Bivariate


@pytest.fixture(scope='module')
def df():
    return pd.DataFrame({'x': [1, 3, 5], 'y': [2, 4, 6], 'category': ['A', 'B', 'C']})


backends = pytest.mark.parametrize(
    'backend',
    [
        'bokeh',
        'matplotlib',
        pytest.param(
            'plotly',
            marks=pytest.mark.xfail(reason='bandwidth, cut, levels not supported with plotly'),
        ),
    ],
    indirect=True,
)


def test_x(df, hvplot_pandas):
    plot = df.hvplot.bivariate(x='y', y='x')
    assert isinstance(plot, Bivariate)
    assert plot.kdims == ['y', 'x']


def test_y(df, tabular_lib):
    plot = tabular_lib(df).hvplot.bivariate(x='x', y='y')
    assert isinstance(plot, Bivariate)
    assert plot.kdims == ['x', 'y']
    assert plot.vdims == ['Density']


@backends
def test_bandwidth(df, hvplot_pandas, backend):
    plot = df.hvplot.bivariate('x', 'y', bandwidth=0.2)
    assert Store.lookup_options(backend, plot, 'plot').kwargs['bandwidth'] == 0.2


@backends
def test_cut(df, hvplot_pandas, backend):
    plot = df.hvplot.bivariate('x', 'y', cut=1)
    assert Store.lookup_options(backend, plot, 'plot').kwargs['cut'] == 1


def test_filled(df, hvplot_pandas, backend):
    plot = df.hvplot.bivariate('x', 'y', filled=True)
    assert Store.lookup_options(backend, plot, 'plot').kwargs['filled'] is True


@backends
def test_levels(df, hvplot_pandas, backend):
    plot = df.hvplot.bivariate('x', 'y', levels=5)
    assert Store.lookup_options(backend, plot, 'plot').kwargs['levels'] == 5
