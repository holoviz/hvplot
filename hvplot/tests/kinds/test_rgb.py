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
