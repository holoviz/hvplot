import numpy as np
import pandas as pd
import pytest
import xarray as xr
from holoviews import Store
from holoviews.element import Violin


@pytest.fixture
def df():
    return pd.DataFrame({'x': [1.0, 2.0, 3.0], 'y': [2.0, 4.0, 3.0]})


def test_y(df, tabular_lib):
    plot = tabular_lib(df).hvplot.violin(y='y')
    assert isinstance(plot, Violin)
    assert plot.kdims == []
    assert plot.vdims == ['y']
    assert list(plot.dimension_values('y')) == [2, 4, 3]


def test_y_list(df, hvplot_pandas):
    plot = df.hvplot.violin(y=['x', 'y'])
    assert isinstance(plot, Violin)
    assert plot.kdims == ['Variable']
    assert plot.vdims == ['value']
    assert list(plot.dimension_values('Variable')) == ['x', 'x', 'x', 'y', 'y', 'y']


def test_violin_from_xarray_with_by_and_color(hvplot_xarray):
    latitudes = np.linspace(-90, 90, 3)
    longitudes = np.linspace(-180, 180, 4)
    times = pd.date_range('2023-01-01', periods=5, freq='D')
    data = np.random.random((5, 3, 4))
    da = xr.DataArray(
        data,
        coords={'time': times, 'lat': latitudes, 'lon': longitudes},
        dims=['time', 'lat', 'lon'],
        name='temperature',
    )
    plot = da.hvplot.violin(y='temperature', by='lat', color='lat')
    assert plot.kdims == ['lat']
    opts = Store.lookup_options('bokeh', plot, 'style')
    assert opts.kwargs['violin_fill_color'] == 'lat'
