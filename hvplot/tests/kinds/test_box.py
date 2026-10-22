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


def test_y_with_by(df, hvplot_pandas):
    plot = df.hvplot.box(y='y', by='cat')
    assert plot.kdims == ['cat']
    assert plot.vdims == ['y']
