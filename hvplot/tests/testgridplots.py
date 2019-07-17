from unittest import SkipTest
from collections import OrderedDict

import numpy as np
from holoviews.element import RGB, Image
from holoviews.element.comparison import ComparisonTestCase
from hvplot import patch

try:
    import xarray as xr
except:
    raise SkipTest('XArray not available')
else:
    patch('xarray')

class TestGridPlots(ComparisonTestCase):

    def setUp(self):
        coords = OrderedDict([('band', [1, 2, 3]), ('y', [0, 1]), ('x', [0, 1])])
        self.da_rgb = xr.DataArray(np.arange(12).reshape((3, 2, 2)),
                                   coords, ['band', 'y', 'x'])
        coords = OrderedDict([('time', [0, 1]), ('band', [1, 2, 3]), ('y', [0, 1]), ('x', [0, 1])])
        self.da_rgb_by_time = xr.DataArray(np.arange(24).reshape((2, 3, 2, 2)),
                                           coords, ['time', 'band', 'y', 'x'])

        coords = OrderedDict([('time', [0, 1]), ('lat', [0, 1]), ('lon', [0, 1])])
        self.da_img_by_time = xr.DataArray(np.arange(8).reshape((2, 2, 2)),
                                           coords, ['time', 'lat', 'lon']).assign_coords(
                                               lat1=xr.DataArray([2,3], dims=['lat']))
        self.da_img_by_time

    def test_rgb_dataarray_no_args(self):
        rgb = self.da_rgb.hvplot()
        self.assertEqual(rgb, RGB(([0, 1], [0, 1])+tuple(self.da_rgb.values)))

    def test_rgb_dataarray_explicit_args(self):
        rgb = self.da_rgb.hvplot('x', 'y')
        self.assertEqual(rgb, RGB(([0, 1], [0, 1])+tuple(self.da_rgb.values)))

    def test_rgb_dataarray_explicit_args_and_kind(self):
        rgb = self.da_rgb.hvplot.rgb('x', 'y')
        self.assertEqual(rgb, RGB(([0, 1], [0, 1])+tuple(self.da_rgb.values)))

    def test_rgb_dataset(self):
        rgb = self.da_rgb.to_dataset(name='z').hvplot.rgb()
        self.assertEqual(rgb, RGB(([0, 1], [0, 1])+tuple(self.da_rgb.values)))

    def test_rgb_dataset_explicit_z(self):
        rgb = self.da_rgb.to_dataset(name='z').hvplot.rgb(z='z')
        self.assertEqual(rgb, RGB(([0, 1], [0, 1])+tuple(self.da_rgb.values)))

    def test_rgb_dataarray_groupby_explicit(self):
        rgb = self.da_rgb_by_time.hvplot.rgb('x', 'y', groupby='time')
        self.assertEqual(rgb[0], RGB(([0, 1], [0, 1])+tuple(self.da_rgb_by_time.values[0])))
        self.assertEqual(rgb[1], RGB(([0, 1], [0, 1])+tuple(self.da_rgb_by_time.values[1])))

    def test_rgb_dataarray_groupby_infer(self):
        rgb = self.da_rgb_by_time.hvplot.rgb('x', 'y', bands='band')
        self.assertEqual(rgb[0], RGB(([0, 1], [0, 1])+tuple(self.da_rgb_by_time.values[0])))
        self.assertEqual(rgb[1], RGB(([0, 1], [0, 1])+tuple(self.da_rgb_by_time.values[1])))

    def test_img_dataarray_groupby_infers_correct_other_dims(self):
        img = self.da_img_by_time.hvplot(groupby='time')
        self.assertEqual(img[0], Image(([0, 1], [0, 1])+tuple(self.da_img_by_time.values[0])))
        self.assertEqual(img[1], Image(([0, 1], [0, 1])+tuple(self.da_img_by_time.values[1])))
