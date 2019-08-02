from unittest import SkipTest
from parameterized import parameterized

import numpy as np
import pandas as pd

from holoviews import Store
from holoviews.element import Image, QuadMesh
from holoviews.element.comparison import ComparisonTestCase


class TestDatashader(ComparisonTestCase):

    def setUp(self):
        try:
            import datashader # noqa
        except:
            raise SkipTest('Datashader not available')
        import hvplot.pandas # noqa
        self.df = pd.DataFrame([[1, 2, 'A', 0.1], [3, 4, 'B', 0.2], [5, 6, 'C', 0.3]],
                               columns=['x', 'y', 'category', 'number'])

    def test_rasterize_by_cat(self):
        from datashader.reductions import count_cat
        dmap = self.df.hvplot.scatter('x', 'y', by='category', rasterize=True)
        agg = dmap.callback.inputs[0].callback.operation.p.aggregator
        self.assertIsInstance(agg, count_cat)
        self.assertEqual(agg.column, 'category')

    def test_rasterize_color_dim(self):
        from datashader.reductions import mean
        dmap = self.df.hvplot.scatter('x', 'y', c='number', rasterize=True)
        agg = dmap.callback.inputs[0].callback.operation.p.aggregator
        self.assertIsInstance(agg, mean)
        self.assertEqual(agg.column, 'number')

    def test_rasterize_color_dim_with_string_agg(self):
        from datashader.reductions import sum
        dmap = self.df.hvplot.scatter('x', 'y', c='number', rasterize=True, aggregator='sum')
        agg = dmap.callback.inputs[0].callback.operation.p.aggregator
        self.assertIsInstance(agg, sum)
        self.assertEqual(agg.column, 'number')

    @parameterized.expand([('aspect',), ('data_aspect',)])
    def test_aspect_with_datashade(self, opt):
        plot = self.df.hvplot(x='x', y='y', datashade=True, **{opt: 2})
        opts = Store.lookup_options('bokeh', plot[0], 'plot').kwargs
        self.assertEqual(opts[opt], 2)
        self.assertEqual(opts.get('height'), None)
        self.assertEqual(opts.get('frame_height'), None)

    @parameterized.expand([('aspect',), ('data_aspect',)])
    def test_aspect_with_datashade_and_dynamic_is_false(self, opt):
        plot = self.df.hvplot(x='x', y='y', datashade=True, dynamic=False, **{opt: 2})
        opts = Store.lookup_options('bokeh', plot[0], 'plot').kwargs
        self.assertEqual(opts[opt], 2)
        self.assertEqual(opts.get('height'), None)
        self.assertEqual(opts.get('frame_height'), None)

    @parameterized.expand([('aspect',), ('data_aspect',)])
    def test_aspect_and_frame_height_with_datashade(self, opt):
        plot = self.df.hvplot(x='x', y='y', frame_height=150, datashade=True, **{opt: 2})
        opts = Store.lookup_options('bokeh', plot[0], 'plot').kwargs
        self.assertEqual(opts[opt], 2)
        self.assertEqual(opts.get('frame_height'), 150)
        self.assertEqual(opts.get('height'), None)
        self.assertEqual(opts.get('frame_width'), None)

    @parameterized.expand([('aspect',), ('data_aspect',)])
    def test_aspect_and_frame_height_with_datashade_and_dynamic_is_false(self, opt):
        plot = self.df.hvplot(x='x', y='y', frame_height=150, datashade=True, dynamic=False, **{opt: 2})
        opts = Store.lookup_options('bokeh', plot[0], 'plot').kwargs
        self.assertEqual(opts[opt], 2)
        self.assertEqual(opts.get('frame_height'), 150)
        self.assertEqual(opts.get('height'), None)
        self.assertEqual(opts.get('frame_width'), None)


class TestChart2D(ComparisonTestCase):

    def setUp(self):
        try:
            import xarray as xr
            import datashader as ds # noqa
        except:
            raise SkipTest('xarray or datashader not available')
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
