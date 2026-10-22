import numpy as np
import pytest
import xarray as xr
from holoviews.element import RGB
from holoviews.testing import assert_element_equal

pytestmark = pytest.mark.usefixtures('hvplot_xarray')

DA_RGB = xr.DataArray(
    np.arange(12).reshape((3, 2, 2)),
    {'band': [1, 2, 3], 'y': [0, 1], 'x': [0, 1]},
    ['band', 'y', 'x'],
)
DA_RGB_BY_TIME = xr.DataArray(
    np.arange(24).reshape((2, 3, 2, 2)),
    {'time': [0, 1], 'band': [1, 2, 3], 'y': [0, 1], 'x': [0, 1]},
    ['time', 'band', 'y', 'x'],
)
EXPECTED_RGB = RGB(([0, 1], [0, 1], *DA_RGB.values))


def test_rgb_dataarray_no_args():
    rgb = DA_RGB.hvplot()
    assert_element_equal(rgb, EXPECTED_RGB)


def test_rgb_dataarray_explicit_args():
    rgb = DA_RGB.hvplot('x', 'y')
    assert_element_equal(rgb, EXPECTED_RGB)


def test_rgb_dataarray_explicit_args_and_kind():
    rgb = DA_RGB.hvplot.rgb('x', 'y')
    assert_element_equal(rgb, EXPECTED_RGB)


def test_rgb_dataset():
    rgb = DA_RGB.to_dataset(name='z').hvplot.rgb()
    assert_element_equal(rgb, EXPECTED_RGB)


def test_rgb_dataset_explicit_z():
    rgb = DA_RGB.to_dataset(name='z').hvplot.rgb(z='z')
    assert_element_equal(rgb, EXPECTED_RGB)


def test_rgb_dataset_robust():
    rgb = DA_RGB.to_dataset(name='z').hvplot.rgb(robust=True)
    with pytest.raises(AssertionError):
        assert_element_equal(rgb, EXPECTED_RGB)


def test_rgb_dataarray_groupby_explicit():
    rgb = DA_RGB_BY_TIME.hvplot.rgb('x', 'y', groupby='time')
    assert_element_equal(rgb[0], RGB(([0, 1], [0, 1], *DA_RGB_BY_TIME.values[0])))
    assert_element_equal(rgb[1], RGB(([0, 1], [0, 1], *DA_RGB_BY_TIME.values[1])))


def test_rgb_dataarray_groupby_infer():
    rgb = DA_RGB_BY_TIME.hvplot.rgb('x', 'y', bands='band')
    assert_element_equal(rgb[0], RGB(([0, 1], [0, 1], *DA_RGB_BY_TIME.values[0])))
    assert_element_equal(rgb[1], RGB(([0, 1], [0, 1], *DA_RGB_BY_TIME.values[1])))


# Not square, to catch x and y being swapped.
DA_LATLON = xr.DataArray(
    np.arange(18).reshape((3, 2, 3)),
    {'band': [1, 2, 3], 'lat': [0, 1], 'lon': [10, 20, 30]},
    ['band', 'lat', 'lon'],
)
EXPECTED_LATLON = RGB(([10, 20, 30], [0, 1], *DA_LATLON.values), ['lon', 'lat'])


# The coords are ordered (band, lon, lat) but the data dims are (band, lat, lon), so that
# the x and y rgb picks by default from the coords are not the right ones.
DA_LATLON_COORDS_SWAPPED = xr.DataArray(
    DA_LATLON.values,
    coords={'band': [1, 2, 3], 'lon': [10, 20, 30], 'lat': [0, 1]},
    dims=['band', 'lat', 'lon'],
)


def test_x(gridded_lib):
    rgb = gridded_lib(DA_LATLON_COORDS_SWAPPED).hvplot.rgb(x='lon', y='lat')
    assert_element_equal(rgb, EXPECTED_LATLON)


@pytest.mark.xfail(strict=True, reason='BUG: rgb does not transpose the data when x/y are swapped')
def test_x_swapped():
    rgb = DA_LATLON.hvplot.rgb(x='lat', y='lon')
    assert rgb.kdims == ['lat', 'lon']


def test_y():
    rgb = DA_LATLON.transpose('band', 'lon', 'lat').hvplot.rgb(x='lat', y='lon')
    assert rgb.kdims == ['lat', 'lon']
    assert list(rgb.dimension_values('lon', expanded=False)) == [10, 20, 30]


def test_z():
    ds = xr.Dataset({'zeros': DA_LATLON * 0, 'z': DA_LATLON})
    rgb = ds.hvplot.rgb(z='z')
    assert_element_equal(rgb, EXPECTED_LATLON)


def test_bands():
    # The first coord is not the bands one.
    da = xr.DataArray(
        np.moveaxis(DA_LATLON.values, 0, -1),
        coords={'lat': [0, 1], 'lon': [10, 20, 30], 'channel': [1, 2, 3]},
        dims=['lat', 'lon', 'channel'],
    )
    rgb = da.hvplot.rgb(x='lon', y='lat', bands='channel')
    assert_element_equal(rgb, EXPECTED_LATLON)
