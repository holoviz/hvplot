import pandas as pd
import pytest
from holoviews.element import BoxWhisker


@pytest.fixture(scope='module')
def df():
    return pd.DataFrame(
        {'y': [1.0, 4.0, 2.0, 3.0], 'y2': [0.5, 1.0, 1.5, 2.0], 'cat': ['A', 'A', 'B', 'B']}
    )


def test_x_not_accepted(df, hvplot_pandas):
    # The categorical axis is set with `by` or with several `y`.
    with pytest.raises(TypeError, match="multiple values for keyword argument 'x'"):
        df.hvplot.box(x='cat', y='y')


@pytest.mark.lib_render_xfail(
    'ibis', reason='HoloViews: BoxWhisker of an ibis table fails to render', strict=False
)
def test_y(df, tabular_lib):
    plot = tabular_lib(df).hvplot.box(y='y')
    assert isinstance(plot, BoxWhisker)
    assert plot.kdims == []
    assert plot.vdims == ['y']


def test_y_list(df, hvplot_pandas):
    plot = df.hvplot.box(y=['y', 'y2'])
    assert plot.kdims == ['Variable']
    assert plot.vdims == ['value']
    assert list(plot.data['Variable'].unique()) == ['y', 'y2']
    assert list(plot.dimension_values('value')) == [1, 4, 2, 3, 0.5, 1, 1.5, 2]


def test_y_with_by(df, hvplot_pandas):
    plot = df.hvplot.box(y='y', by='cat')
    assert plot.kdims == ['cat']
    assert plot.vdims == ['y']
    assert list(plot.dimension_values('cat')) == ['A', 'A', 'B', 'B']
    assert list(plot.dimension_values('y')) == [1, 4, 2, 3]


def test_y_with_by_list(hvplot_pandas):
    df = pd.DataFrame(
        {'y': [1.0, 4.0, 2.0, 3.0], 'a': ['A', 'A', 'B', 'B'], 'b': ['u', 'v', 'u', 'v']}
    )
    plot = df.hvplot.box(y='y', by=['a', 'b'])
    assert plot.kdims == ['a', 'b']
    assert plot.vdims == ['y']
    assert list(plot.dimension_values('y')) == [1, 4, 2, 3]
