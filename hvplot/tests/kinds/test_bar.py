import pandas as pd
import pytest
from holoviews import Store
from holoviews.element import Bars


@pytest.fixture(scope='module')
def df():
    return pd.DataFrame({'cat': ['A', 'B', 'C'], 'y': [1.0, 4.0, 2.0], 'y2': [0.5, 1.0, 1.5]})


def test_x(df, hvplot_pandas):
    plot = df.hvplot.bar(x='cat', y='y')
    assert isinstance(plot, Bars)
    assert plot.kdims == ['cat']


def test_x_default_index(df, hvplot_pandas):
    plot = df.hvplot.bar(y='y')
    assert plot.kdims == ['index']


def test_y(df, tabular_lib):
    plot = tabular_lib(df).hvplot.bar(x='cat', y='y')
    assert isinstance(plot, Bars)
    assert plot.kdims == ['cat']
    assert plot.vdims == ['y']


def test_y_list(df, hvplot_pandas):
    plot = df.hvplot.bar(x='cat', y=['y', 'y2'])
    assert plot.kdims == ['cat', 'Variable']
    assert plot.vdims == ['value']


@pytest.mark.parametrize('tabular_lib', ['pandas', 'dask'], indirect=True)
def test_y_from_index_with_by(tabular_lib):
    cat_df = pd.DataFrame([[1, 2, 'A'], [3, 4, 'B'], [5, 6, 'C']], columns=['x', 'y', 'category'])
    df = tabular_lib(cat_df.set_index('y'))
    # Testing a somewhat silly plot but that seemed to be supported
    # https://github.com/holoviz/hvplot/blob/6c96c7e9abcd44380d2122e3d86827dedab32dea/hvplot/converter.py#L1996-L1999
    plot = df.hvplot.bar(x='x', y='y', by='category')
    assert plot.kdims == ['x', 'category']
    assert plot.vdims == ['y']


def test_stacked(df, hvplot_pandas, backend):
    plot = df.hvplot.bar(x='cat', y=['y', 'y2'], stacked=True)
    assert Store.lookup_options(backend, plot, 'plot').kwargs['stacked'] is True
