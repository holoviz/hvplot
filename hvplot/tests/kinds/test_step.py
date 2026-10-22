import pandas as pd
import pytest
from holoviews import Store
from holoviews.element import Curve


@pytest.fixture
def df():
    return pd.DataFrame({'x': [1, 2, 3], 'y': [2, 4, 3], 'z': [0.1, 0.2, 0.3]})


def test_x(df, hvplot_pandas):
    plot = df.hvplot.step(x='z', y='y')
    assert isinstance(plot, Curve)
    assert plot.kdims == ['z']
    assert plot.vdims == ['y']


@pytest.mark.lib_render_xfail(
    'ibis', reason='HoloViews: Curve with steps of an ibis table fails to render'
)
def test_y(df, tabular_lib):
    plot = tabular_lib(df).hvplot.step(x='x', y='y')
    assert isinstance(plot, Curve)
    assert plot.kdims == ['x']
    assert plot.vdims == ['y']
    assert list(plot.dimension_values('y')) == [2, 4, 3]


def test_where_default(df, hvplot_pandas, backend):
    plot = df.hvplot.step(x='x', y='y')
    assert Store.lookup_options(backend, plot, 'plot').kwargs['interpolation'] == 'steps-mid'


@pytest.mark.parametrize('where', ['pre', 'mid', 'post'])
def test_where(df, where, hvplot_pandas, backend):
    plot = df.hvplot.step(x='x', y='y', where=where)
    assert Store.lookup_options(backend, plot, 'plot').kwargs['interpolation'] == f'steps-{where}'
