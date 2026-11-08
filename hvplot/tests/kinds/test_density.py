import pandas as pd
import pytest
from holoviews import NdOverlay, Store
from holoviews.element import Distribution


@pytest.fixture(scope='module')
def df():
    return pd.DataFrame({'y': [1.0, 4.0, 2.0, 3.0], 'y2': [0.5, 1.0, 1.5, 2.0]})


@pytest.mark.lib_xfail(
    'ibis', reason='BUG: density fails with ibis, cannot determine what to plot'
)
def test_y(df, tabular_lib):
    plot = tabular_lib(df).hvplot.density(y='y')
    assert isinstance(plot, Distribution)
    assert plot.kdims == ['y']
    assert plot.vdims == ['Density']


def test_y_list(df, hvplot_pandas):
    plot = df.hvplot.density(y=['y', 'y2'])
    assert list(plot.keys()) == ['y', 'y2']
    assert all(isinstance(dist, Distribution) for dist in plot)


def test_by(hvplot_pandas):
    df = pd.DataFrame({'v': [1.0, 2.0, 3.0, 10.0, 11.0, 12.0], 'g': list('aaabbb')})
    plot = df.hvplot.density(y='v', by='g')
    assert isinstance(plot, NdOverlay)
    assert list(plot.keys()) == ['a', 'b']
    assert list(plot['a'].dimension_values('v')) == [1, 2, 3]
    assert list(plot['b'].dimension_values('v')) == [10, 11, 12]


def test_bw_method_not_supported(df, hvplot_pandas):
    with pytest.raises(ValueError, match='hvplot does not support bw_method and ind'):
        df.hvplot.density(y='y', bw_method=0.5)


def test_ind_not_supported(df, hvplot_pandas):
    with pytest.raises(ValueError, match='hvplot does not support bw_method and ind'):
        df.hvplot.density(y='y', ind=10)


def test_bandwidth(df, hvplot_pandas, backend):
    plot = df.hvplot.density(y='y', bandwidth=0.2)
    assert Store.lookup_options(backend, plot, 'plot').kwargs['bandwidth'] == 0.2


def test_cut(df, hvplot_pandas, backend):
    plot = df.hvplot.density(y='y', cut=1)
    assert Store.lookup_options(backend, plot, 'plot').kwargs['cut'] == 1


def test_filled(df, hvplot_pandas, backend):
    plot = df.hvplot.density(y='y', filled=False)
    assert Store.lookup_options(backend, plot, 'plot').kwargs['filled'] is False
