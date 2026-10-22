import numpy as np
import pytest
import xarray as xr
from holoviews import Store
from holoviews.element import Image
from holoviews.testing import assert_element_equal

pytestmark = pytest.mark.usefixtures('hvplot_xarray')

DA_IMG_BY_TIME = xr.DataArray(
    np.arange(8).reshape((2, 2, 2)),
    {'time': [0, 1], 'lat': [0, 1], 'lon': [0, 1]},
    ['time', 'lat', 'lon'],
).assign_coords(lat1=xr.DataArray([2, 3], dims=['lat']))


@pytest.fixture(scope='module')
def ds():
    v1 = xr.DataArray(
        np.arange(1.0, 13.0).reshape(3, 4), coords={'y': [0, 1, 2], 'x': [0, 1, 2, 3]}
    )
    return xr.Dataset({'v1': v1, 'v2': v1 * 2})


def test_x(ds):
    plot = ds.hvplot.image(x='y', y='x', z='v1')
    assert isinstance(plot, Image)
    assert plot.kdims == ['y', 'x']


def test_y(ds):
    plot = ds.hvplot.image(x='x', y='y', z='v1')
    assert plot.kdims == ['x', 'y']


def test_z(ds, gridded_lib):
    plot = gridded_lib(ds).hvplot.image(z='v2')
    assert isinstance(plot, Image)
    assert plot.kdims == ['x', 'y']
    assert plot.vdims == ['v2']


def test_logz(ds, backend):
    plot = ds.hvplot.image(z='v1', logz=True)
    assert Store.lookup_options(backend, plot, 'plot').kwargs['logz'] is True


def test_img_dataarray_infers_correct_other_dims():
    img = DA_IMG_BY_TIME[0].hvplot()
    assert_element_equal(img, Image(DA_IMG_BY_TIME[0], ['lon', 'lat'], ['value']))


def test_img_dataarray_groupby_infers_correct_other_dims():
    img = DA_IMG_BY_TIME.hvplot(groupby='time')
    assert_element_equal(img[0], Image(DA_IMG_BY_TIME[0], ['lon', 'lat'], ['value']))
    assert_element_equal(img[1], Image(DA_IMG_BY_TIME[1], ['lon', 'lat'], ['value']))
