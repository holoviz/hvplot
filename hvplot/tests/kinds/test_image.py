import numpy as np
import pytest
import xarray as xr
from holoviews.element import Image
from holoviews.testing import assert_element_equal

pytestmark = pytest.mark.usefixtures('hvplot_xarray')

DA_IMG_BY_TIME = xr.DataArray(
    np.arange(8).reshape((2, 2, 2)),
    {'time': [0, 1], 'lat': [0, 1], 'lon': [0, 1]},
    ['time', 'lat', 'lon'],
).assign_coords(lat1=xr.DataArray([2, 3], dims=['lat']))


def test_img_dataarray_infers_correct_other_dims():
    img = DA_IMG_BY_TIME[0].hvplot()
    assert_element_equal(img, Image(DA_IMG_BY_TIME[0], ['lon', 'lat'], ['value']))


def test_img_dataarray_groupby_infers_correct_other_dims():
    img = DA_IMG_BY_TIME.hvplot(groupby='time')
    assert_element_equal(img[0], Image(DA_IMG_BY_TIME[0], ['lon', 'lat'], ['value']))
    assert_element_equal(img[1], Image(DA_IMG_BY_TIME[1], ['lon', 'lat'], ['value']))
