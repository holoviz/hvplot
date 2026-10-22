import numpy as np
import pandas as pd
import pytest
from holoviews import Store
from holoviews.element import HeatMap
from holoviews.testing import assert_element_equal


@pytest.fixture(scope='module')
def df():
    return pd.DataFrame({'x': [1, 1, 2], 'y': ['A', 'A', 'B'], 'value': [1.0, 3.0, 5.0]})


def test_x(df, hvplot_pandas):
    plot = df.hvplot.heatmap(x='y', y='x', C='value')
    assert isinstance(plot, HeatMap)
    assert plot.kdims == ['y', 'x']


def test_y(df, tabular_lib):
    plot = tabular_lib(df).hvplot.heatmap(x='x', y='y', C='value')
    assert isinstance(plot, HeatMap)
    assert plot.kdims == ['x', 'y']
    assert plot.vdims == ['value']


@pytest.mark.parametrize(
    'tabular_lib',
    [
        'pandas',
        pytest.param(
            'dask',
            marks=pytest.mark.xfail(
                strict=True, reason='BUG: heatmap of the index and columns fails with dask'
            ),
        ),
    ],
    indirect=True,
)
def test_x_y_default_columns_and_index(tabular_lib):
    df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
    plot = tabular_lib(df).hvplot.heatmap()
    assert_element_equal(
        plot, HeatMap((['x', 'y'], [0, 1, 2], df.values), ['columns', 'index'], 'value')
    )


@pytest.mark.parametrize('tabular_lib', ['pandas', 'dask'], indirect=True)
def test_x_y_derived_datetime(tabular_lib):
    time_df = pd.DataFrame(
        {
            'time': pd.date_range('1/1/2000', periods=5 * 24, freq='1h', tz='UTC'),
            'temp': np.sin(np.linspace(0, 5 * 2 * np.pi, 5 * 24)).cumsum(),
        }
    )
    plot = tabular_lib(time_df).hvplot.heatmap(x='time.hour', y='time.day', C='temp')
    assert plot.kdims == ['time.hour', 'time.day']
    assert plot.vdims == ['temp']


def test_C(hvplot_pandas):
    df = pd.DataFrame({'x': [1, 2], 'y': ['A', 'B'], 'v1': [1.0, 2.0], 'v2': [3.0, 4.0]})
    plot = df.hvplot.heatmap(x='x', y='y', C='v2')
    assert plot.vdims == ['v2']
    assert list(plot.dimension_values('v2')) == [3.0, 4.0]


def test_reduce_function(df, hvplot_pandas):
    plot = df.hvplot.heatmap(x='x', y='y', C='value', reduce_function=np.mean)
    assert list(plot.dimension_values('value')) == [2.0, 5.0]


def test_logz(df, hvplot_pandas, backend):
    plot = df.hvplot.heatmap(x='x', y='y', C='value', logz=True)
    assert Store.lookup_options(backend, plot, 'plot').kwargs['logz'] is True
