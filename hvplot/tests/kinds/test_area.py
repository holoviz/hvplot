import pandas as pd
import pytest
from holoviews import NdOverlay, Store
from holoviews.core.dimension import Dimension
from holoviews.element import Area
from holoviews.testing import assert_element_equal


@pytest.fixture(scope='module')
def df():
    return pd.DataFrame({'x': [1, 2, 3], 'y': [1.0, 4.0, 2.0], 'y2': [0.5, 1.0, 1.5]})


def test_x(df, hvplot_pandas):
    plot = df.hvplot.area(x='x', y='y')
    assert isinstance(plot, Area)
    assert plot.kdims == ['x']


def test_x_default_index(df, hvplot_pandas):
    plot = df.hvplot.area(y='y')
    assert plot.kdims == ['index']


def test_y(df, tabular_lib):
    plot = tabular_lib(df).hvplot.area(x='x', y='y')
    assert isinstance(plot, Area)
    assert plot.kdims == ['x']
    assert plot.vdims == ['y']


def test_y2(df, hvplot_pandas):
    plot = df.hvplot.area(x='x', y='y', y2='y2')
    assert isinstance(plot, Area)
    assert plot.vdims == ['y', 'y2']


@pytest.mark.parametrize('tabular_lib', ['pandas', 'dask'], indirect=True)
def test_stacked(tabular_lib):
    df = tabular_lib(pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y']))
    plot = df.hvplot.area(stacked=True)
    obj = NdOverlay(
        {
            'x': Area(df, 'index', Dimension('x', label='value')),
            'y': Area(df, 'index', Dimension('y', label='value')),
        },
        'Variable',
    )
    assert_element_equal(plot, Area.stack(obj))


def test_stacked_false(df, hvplot_pandas):
    plot = df.hvplot.area(x='x', y=['y', 'y2'], stacked=False)
    # Not stacked: the second area keeps its own values.
    assert list(plot['y2'].dimension_values('value')) == [0.5, 1.0, 1.5]
    # Overlaid areas are made transparent.
    assert Store.lookup_options('bokeh', plot['y'], 'style').kwargs['alpha'] == 0.5
