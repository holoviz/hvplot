from unittest import SkipTest
from parameterized import parameterized

from holoviews.element import Image, QuadMesh
from holoviews.element.comparison import ComparisonTestCase


class TestChart2D(ComparisonTestCase):
    def setUp(self):
        try:
            import xarray as xr
            import numpy as np
        except:
            raise SkipTest('XArray not available')
        import hvplot.xarray  # noqa
        data = np.arange(0, 60).reshape(6, 10)
        x = np.arange(10)
        y = np.arange(6)
        self.da = xr.DataArray(data,
                               coords={'y': y, 'x': x},
                               dims=('y', 'x'))

    @parameterized.expand([('image', Image), ('quadmesh', QuadMesh)])
    def test_plot_resolution(self, kind, element):
        plot = self.da.hvplot(kind=kind)
        assert all(plot.data.x.diff('x').round(0) == 1)
        assert all(plot.data.y.diff('y').round(0) == 1)

    @parameterized.expand([('image', Image), ('quadmesh', QuadMesh)])
    def test_plot_resolution_with_rasterize(self, kind, element):
        plot = self.da.hvplot(kind=kind, dynamic=False, rasterize=True,
                              x_sampling=5, y_sampling=2)
        assert all(plot.data.x.diff('x').round(0) == 5)
        assert all(plot.data.y.diff('y').round(0) == 2)
