import os
import tempfile
from unittest import TestCase

import numpy as np
import pytest
import xarray as xr
from holoviews import Store
from holoviews.element.comparison import ComparisonTestCase

import hvplot
from hvplot.plotting import hvPlot


@pytest.fixture(scope='module')
def da():
    return xr.DataArray(
        data=np.arange(16).reshape((2, 2, 2, 2)),
        coords={'time': [0, 1], 'y': [0, 1], 'x': [0, 1], 'band': [0, 1]},
        dims=['time', 'y', 'x', 'band'],
        name='test',
    )


@pytest.fixture(scope='module')
def ds1(da):
    return xr.Dataset({'foo': da})


@pytest.mark.usefixtures('hvplot_xarray')
class TestXarray:
    def test_dataset_empty_raises(self, ds1, backend):
        with pytest.raises(ValueError, match=r'empty xarray.Dataset'):
            ds1.drop_vars('foo').hvplot()


@pytest.mark.usefixtures('hvplot_xarray')
class TestGridPlots(ComparisonTestCase):
    def setUp(self):
        self.ds = xr.Dataset(
            {
                'temp': (('lon', 'lat'), 15 + 8 * np.random.randn(2, 2)),
                'precip': (('lon', 'lat'), 10 * np.random.rand(2, 2)),
            },
            coords={'lon': [-99.83, -99.32], 'lat': [42.25, 42.21]},
        )

    def test_multiple_zs(self):
        plot = self.ds.hvplot(x='lat', y='lon', z=['temp', 'precip'], dynamic=False)
        assert 'temp' in plot.keys()
        assert 'precip' in plot.keys()
        assert plot['temp'].kdims == ['lat', 'lon']
        assert plot['precip'].kdims == ['lat', 'lon']

    def test_symmetric_dataset_not_in_memory(self):
        # Creating a netcdf file and loading it as to get an non in memory
        # DataArray.
        da = xr.DataArray(
            data=np.arange(-100, 100).reshape(10, 10, 2),
            dims=['x', 'y', 'z'],
            coords={'x': np.arange(10), 'y': np.arange(10), 'z': np.arange(2)},
        )
        ds = xr.Dataset(data_vars={'value': da})
        with tempfile.TemporaryDirectory() as tempdir:
            fpath = os.path.join(tempdir, 'data.nc')
            ds.to_netcdf(fpath)
            ds = xr.open_dataset(fpath)
            plot = ds.value.hvplot(x='x', y='y', check_symmetric_max=ds.value.size + 1)
            plot[(0)]
            plot_opts = Store.lookup_options('bokeh', plot.last, 'plot')
            # If a DataArray is not in memory, computing whether it's symmetric should
            # not be done and return False.
            assert not plot_opts.kwargs['symmetric']
            ds.close()

    def test_symmetric_dataset_in_memory(self):
        da = xr.DataArray(
            data=np.arange(-100, 100).reshape(10, 10, 2),
            dims=['x', 'y', 'z'],
            coords={'x': np.arange(10), 'y': np.arange(10), 'z': np.arange(2)},
        )
        ds = xr.Dataset(data_vars={'value': da})
        plot = ds.value.hvplot(x='x', y='y', check_symmetric_max=ds.value.size + 1)
        plot[(0)]
        plot_opts = Store.lookup_options('bokeh', plot.last, 'plot')
        # This DataArray happens to be symmetric.
        assert plot_opts.kwargs['symmetric']


class TestPatchXArray(TestCase):
    def setUp(self):
        import hvplot.xarray  # noqa: F401

    def test_xarray_dataarray_patched(self):
        array = np.random.rand(100, 100)
        xr_array = xr.DataArray(array, coords={'x': range(100), 'y': range(100)}, dims=('y', 'x'))
        self.assertIsInstance(xr_array.hvplot, hvPlot)

    def test_xarray_dataset_patched(self):
        array = np.random.rand(100, 100)
        xr_array = xr.DataArray(array, coords={'x': range(100), 'y': range(100)}, dims=('y', 'x'))
        xr_ds = xr.Dataset({'z': xr_array})
        self.assertIsInstance(xr_ds.hvplot, hvPlot)


def _patched(classes, attrs):
    return all(attr in vars(cls) for cls in classes for attr in attrs)


def _unpatched(classes, attrs):
    return not any(attr in vars(cls) for cls in classes for attr in attrs)


def _round_trip(ext, classes, attrs=('hvplot',)):
    # Ends patched, so the _isolate_hvplot fixture unpatches the extension
    # and removes its module from sys.modules after the test.
    ext.patch()
    assert _patched(classes, attrs)
    assert ext.__name__ in hvplot._module_extensions

    ext._unpatch()
    assert _unpatched(classes, attrs)
    assert ext.__name__ not in hvplot._module_extensions

    ext.patch()
    assert _patched(classes, attrs)
    assert ext.__name__ in hvplot._module_extensions


def test_unpatch_xarray():
    import hvplot.xarray

    _round_trip(hvplot.xarray, [xr.Dataset, xr.DataArray], ['hvplot', 'interactive'])
