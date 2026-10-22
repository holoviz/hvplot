import pandas as pd
import pytest
from holoviews import Store
from holoviews.element import ErrorBars


@pytest.fixture(scope='module')
def df():
    return pd.DataFrame(
        {'x': [1, 2, 3], 'y': [1.0, 4.0, 2.0], 'neg': [0.1, 0.2, 0.3], 'pos': [0.3, 0.2, 0.1]}
    )


def test_x(df, hvplot_pandas):
    plot = df.hvplot.errorbars(x='x', y='y', yerr1='neg')
    assert isinstance(plot, ErrorBars)
    assert plot.kdims == ['x']


def test_x_default_index(df, hvplot_pandas):
    plot = df.hvplot.errorbars(y='y', yerr1='neg')
    assert plot.kdims == ['index']


def test_y(df, tabular_lib):
    plot = tabular_lib(df).hvplot.errorbars(x='x', y='y', yerr1='neg')
    assert isinstance(plot, ErrorBars)
    assert plot.vdims[0] == 'y'


def test_yerr1(df, hvplot_pandas):
    # Symmetric errors when yerr2 is not set.
    plot = df.hvplot.errorbars(x='x', y='y', yerr1='neg')
    assert plot.vdims == ['y', 'neg']
    assert list(plot.dimension_values('neg')) == [0.1, 0.2, 0.3]


def test_yerr2(df, hvplot_pandas):
    # yerr1 is then the negative error and yerr2 the positive one.
    plot = df.hvplot.errorbars(x='x', y='y', yerr1='neg', yerr2='pos')
    assert plot.vdims == ['y', 'neg', 'pos']
    assert list(plot.dimension_values('neg')) == [0.1, 0.2, 0.3]
    assert list(plot.dimension_values('pos')) == [0.3, 0.2, 0.1]


@pytest.mark.parametrize('tabular_lib', ['pandas', 'dask'], indirect=True)
def test_errorbars_no_hover(tabular_lib):
    df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
    df_desc = tabular_lib(df.describe().transpose().sort_values('mean'))
    plot = df_desc.hvplot.errorbars(y='mean', yerr1='std')
    assert list(plot.dimensions()) == ['index', 'mean', 'std']
    bkplot = Store.renderers['bokeh'].get_plot(plot)
    assert not bkplot.tools
