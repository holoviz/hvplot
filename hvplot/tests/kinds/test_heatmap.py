import numpy as np
import pandas as pd
import pytest
from holoviews.element import HeatMap
from holoviews.testing import assert_element_equal


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
def test_heatmap_2d_index_columns(tabular_lib):
    df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
    plot = tabular_lib(df).hvplot.heatmap()
    assert_element_equal(
        plot, HeatMap((['x', 'y'], [0, 1, 2], df.values), ['columns', 'index'], 'value')
    )


@pytest.mark.parametrize('tabular_lib', ['pandas', 'dask'], indirect=True)
def test_heatmap_2d_derived_x_and_y(tabular_lib):
    time_df = pd.DataFrame(
        {
            'time': pd.date_range('1/1/2000', periods=5 * 24, freq='1h', tz='UTC'),
            'temp': np.sin(np.linspace(0, 5 * 2 * np.pi, 5 * 24)).cumsum(),
        }
    )
    plot = tabular_lib(time_df).hvplot.heatmap(x='time.hour', y='time.day', C='temp')
    assert plot.kdims == ['time.hour', 'time.day']
    assert plot.vdims == ['temp']
