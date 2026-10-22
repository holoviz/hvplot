import numpy as np
import pytest
import xarray as xr
from holoviews import Store

import hvplot
from hvplot.plotting import hvPlot

pytestmark = pytest.mark.usefixtures('hvplot_xarray')


@pytest.fixture
def dataarray():
    return xr.DataArray([[1, 2], [3, 4]], coords={'x': [0, 1], 'y': [0, 1]}, dims=('y', 'x'))


@pytest.fixture
def symmetric_dataset():
    da = xr.DataArray(
        data=np.arange(-100, 100).reshape(10, 10, 2),
        dims=['x', 'y', 'z'],
        coords={'x': np.arange(10), 'y': np.arange(10), 'z': np.arange(2)},
    )
    return xr.Dataset(data_vars={'value': da})


def test_dataset_empty_raises(backend):
    ds = xr.Dataset({'foo': (('y', 'x'), [[0, 1], [2, 3]])}, coords={'x': [0, 1], 'y': [0, 1]})
    with pytest.raises(ValueError, match=r'empty xarray.Dataset'):
        ds.drop_vars('foo').hvplot()


def test_multiple_zs(rng):
    ds = xr.Dataset(
        {
            'temp': (('lon', 'lat'), 15 + 8 * rng.standard_normal((2, 2))),
            'precip': (('lon', 'lat'), 10 * rng.random((2, 2))),
        },
        coords={'lon': [-99.83, -99.32], 'lat': [42.25, 42.21]},
    )
    plot = ds.hvplot(x='lat', y='lon', z=['temp', 'precip'], dynamic=False)
    assert 'temp' in plot.keys()
    assert 'precip' in plot.keys()
    assert plot['temp'].kdims == ['lat', 'lon']
    assert plot['precip'].kdims == ['lat', 'lon']


def test_symmetric_dataset_not_in_memory(symmetric_dataset, tmp_path):
    # Saved to and loaded from a netCDF file to get a DataArray not in memory.
    fpath = tmp_path / 'data.nc'
    symmetric_dataset.to_netcdf(fpath)
    with xr.open_dataset(fpath) as ds:
        plot = ds.value.hvplot(x='x', y='y', check_symmetric_max=ds.value.size + 1)
        plot[0]
        plot_opts = Store.lookup_options('bokeh', plot.last, 'plot')
        # If a DataArray is not in memory, computing whether it's symmetric should
        # not be done and return False.
        assert not plot_opts.kwargs['symmetric']


def test_symmetric_dataset_in_memory(symmetric_dataset):
    ds = symmetric_dataset
    plot = ds.value.hvplot(x='x', y='y', check_symmetric_max=ds.value.size + 1)
    plot[0]
    plot_opts = Store.lookup_options('bokeh', plot.last, 'plot')
    # This DataArray happens to be symmetric.
    assert plot_opts.kwargs['symmetric']


def test_xarray_dataarray_patched(dataarray):
    assert isinstance(dataarray.hvplot, hvPlot)


def test_xarray_dataset_patched(dataarray):
    assert isinstance(xr.Dataset({'z': dataarray}).hvplot, hvPlot)


def test_unpatch_xarray():
    classes = [xr.Dataset, xr.DataArray]

    hvplot.xarray._unpatch()
    assert not any('hvplot' in vars(cls) or 'interactive' in vars(cls) for cls in classes)
    assert 'hvplot.xarray' not in hvplot._module_extensions

    # Ends patched, the _isolate_hvplot fixture unpatches it after the test.
    hvplot.xarray.patch()
    assert all('hvplot' in vars(cls) and 'interactive' in vars(cls) for cls in classes)
    assert 'hvplot.xarray' in hvplot._module_extensions
