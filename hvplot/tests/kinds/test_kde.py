import pandas as pd
import pytest
from holoviews import NdLayout, NdOverlay, Store
from holoviews.element import Distribution

pytestmark = pytest.mark.usefixtures('hvplot_pandas')


@pytest.fixture(scope='module')
def df():
    return pd.DataFrame(
        [[1, 2, 'A', 0.1], [3, 4, 'B', 0.2], [5, 6, 'C', 0.3]],
        columns=['x', 'y', 'category', 'number'],
    )


@pytest.mark.parametrize(
    'tabular_lib',
    [
        'pandas',
        'dask',
        'polars',
        'duckdb',
        pytest.param(
            'ibis',
            marks=pytest.mark.xfail(strict=True, reason='BUG: kde on ibis requires x'),
        ),
    ],
    indirect=True,
)
def test_y(df, tabular_lib):
    plot = tabular_lib(df).hvplot.kde(y='y')
    assert isinstance(plot, Distribution)
    assert plot.kdims == ['y']
    assert list(plot.dimension_values('y')) == [2, 4, 6]


def test_y_list(df):
    plot = df.hvplot.kde(y=['x', 'y'])
    assert isinstance(plot, NdOverlay)
    assert list(plot.keys()) == ['x', 'y']
    assert list(plot['y'].dimension_values(0)) == [2, 4, 6]


@pytest.fixture
def grouped():
    return pd.DataFrame({'v': [1.0, 2.0, 3.0, 10.0, 11.0, 12.0], 'g': list('aaabbb')})


def test_by(grouped):
    plot = grouped.hvplot.kde(y='v', by='g')
    assert isinstance(plot, NdOverlay)
    assert list(plot.keys()) == ['a', 'b']
    assert list(plot['a'].dimension_values('v')) == [1, 2, 3]
    assert list(plot['b'].dimension_values('v')) == [10, 11, 12]


def test_by_subplots(grouped):
    plot = grouped.hvplot.kde(y='v', by='g', subplots=True)
    assert isinstance(plot, NdLayout)
    assert list(plot.keys()) == ['a', 'b']


def test_by_list(df):
    plot = df.hvplot.kde(y='x', by=['category', 'y'])
    assert plot.kdims == ['category', 'y']
    assert list(plot.keys()) == [('A', 2), ('B', 4), ('C', 6)]


def test_y_empty(df):
    plot = df.iloc[:0].hvplot.kde(y='y')
    assert isinstance(plot, Distribution)
    assert len(plot) == 0


def test_bw_method_not_supported(df):
    with pytest.raises(ValueError, match='hvplot does not support bw_method and ind'):
        df.hvplot.kde(y='y', bw_method=1)


def test_ind_not_supported(df):
    with pytest.raises(ValueError, match='hvplot does not support bw_method and ind'):
        df.hvplot.kde(y='y', ind=1)


def test_bandwidth(df, backend):
    plot = df.hvplot.kde('x', bandwidth=0.2)
    assert Store.lookup_options(backend, plot, 'plot').kwargs['bandwidth'] == 0.2


def test_cut(df, backend):
    plot = df.hvplot.kde('x', cut=1)
    assert Store.lookup_options(backend, plot, 'plot').kwargs['cut'] == 1


def test_filled(df, backend):
    plot = df.hvplot.kde('x', filled=False)
    assert Store.lookup_options(backend, plot, 'plot').kwargs['filled'] is False
