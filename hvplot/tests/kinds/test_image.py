from collections import OrderedDict

import numpy as np
import pytest
import xarray as xr
from holoviews.element import Image
from holoviews.element.comparison import ComparisonTestCase


@pytest.mark.usefixtures('hvplot_xarray')
class TestGridPlots(ComparisonTestCase):
    def setUp(self):
        coords = OrderedDict([('time', [0, 1]), ('lat', [0, 1]), ('lon', [0, 1])])
        self.da_img_by_time = xr.DataArray(
            np.arange(8).reshape((2, 2, 2)), coords, ['time', 'lat', 'lon']
        ).assign_coords(lat1=xr.DataArray([2, 3], dims=['lat']))

    def test_img_dataarray_infers_correct_other_dims(self):
        img = self.da_img_by_time[0].hvplot()
        self.assertEqual(img, Image(self.da_img_by_time[0], ['lon', 'lat'], ['value']))

    def test_img_dataarray_groupby_infers_correct_other_dims(self):
        img = self.da_img_by_time.hvplot(groupby='time')
        self.assertEqual(img[0], Image(self.da_img_by_time[0], ['lon', 'lat'], ['value']))
        self.assertEqual(img[1], Image(self.da_img_by_time[1], ['lon', 'lat'], ['value']))
