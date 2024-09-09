import numpy as np
import pandas as pd
import xarray as xr

from holoviews import Store

import hvplot.xarray  # noqa: F401


def test_violin_from_xarray_with_by_and_color():
    latitudes = np.linspace(-90, 90, 180)
    longitudes = np.linspace(-180, 180, 360)
    times = pd.date_range('2023-01-01', periods=365, freq='D')
    data = np.random.random((365, 180, 360))
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
