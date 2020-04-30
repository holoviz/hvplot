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

    @parameterized.expand([('rasterize',), ('datashade',)])
    def test_color_dim_with_default_agg(self, operation):
        from datashader.reductions import mean
        dmap = self.df.hvplot.scatter('x', 'y', c='number', **{operation: True})
        agg = dmap.callback.inputs[0].callback.operation.p.aggregator
        self.assertIsInstance(agg, mean)
        self.assertEqual(agg.column, 'number')

    @parameterized.expand([('rasterize',), ('datashade',)])
    def test_color_dim_with_string_agg(self, operation):
        from datashader.reductions import sum
        dmap = self.df.hvplot.scatter('x', 'y', c='number', aggregator='sum', **{operation: True})
        agg = dmap.callback.inputs[0].callback.operation.p.aggregator
        self.assertIsInstance(agg, sum)
        self.assertEqual(agg.column, 'number')

    @parameterized.expand([('rasterize',), ('datashade',)])
    def test_color_dim_also_an_axis(self, operation):
        from datashader.reductions import mean
        original_data = self.df.copy(deep=True)
        dmap = self.df.hvplot.scatter('x', 'y', c='y', **{operation: True})
        agg = dmap.callback.inputs[0].callback.operation.p.aggregator
        self.assertIsInstance(agg, mean)
        self.assertEqual(agg.column, '_color')
        assert original_data.equals(self.df)

    def test_rasterize_color_dim_with_new_column_gets_default_cmap(self):
        plot = self.df.hvplot.scatter('x', 'y', c='y', dynamic=False, rasterize=True)
        opts = Store.lookup_options('bokeh', plot, 'style').kwargs
        self.assertEqual(opts.get('cmap'), 'kbc_r')

    def test_rasterize_default_cmap(self):
        plot = self.df.hvplot.scatter('x', 'y', dynamic=False, rasterize=True)
        opts = Store.lookup_options('bokeh', plot, 'style').kwargs
        self.assertEqual(opts.get('cmap'), 'kbc_r')

    def test_rasterize_set_clim(self):
        plot = self.df.hvplot.scatter('x', 'y', dynamic=False, rasterize=True, clim=(1, 4))
        opts = Store.lookup_options('bokeh', plot, 'plot').kwargs
        self.assertEqual(opts.get('clim'), (1, 4))

    @parameterized.expand([('aspect',), ('data_aspect',)])
    def test_aspect_with_datashade(self, opt):
        plot = self.df.hvplot(x='x', y='y', datashade=True, **{opt: 2})
        opts = Store.lookup_options('bokeh', plot[()], 'plot').kwargs
        self.assertEqual(opts[opt], 2)
        self.assertEqual(opts.get('height'), None)
        self.assertEqual(opts.get('frame_height'), None)

    @parameterized.expand([('aspect',), ('data_aspect',)])
    def test_aspect_with_datashade_and_dynamic_is_false(self, opt):
        plot = self.df.hvplot(x='x', y='y', datashade=True, dynamic=False, **{opt: 2})
        opts = Store.lookup_options('bokeh', plot[()], 'plot').kwargs
        self.assertEqual(opts[opt], 2)
        self.assertEqual(opts.get('height'), None)
        self.assertEqual(opts.get('frame_height'), None)

    @parameterized.expand([('aspect',), ('data_aspect',)])
    def test_aspect_and_frame_height_with_datashade(self, opt):
        plot = self.df.hvplot(x='x', y='y', frame_height=150, datashade=True, **{opt: 2})
        opts = Store.lookup_options('bokeh', plot[()], 'plot').kwargs
        self.assertEqual(opts[opt], 2)
        self.assertEqual(opts.get('frame_height'), 150)
        self.assertEqual(opts.get('height'), None)
        self.assertEqual(opts.get('frame_width'), None)

    @parameterized.expand([('aspect',), ('data_aspect',)])
    def test_aspect_and_frame_height_with_datashade_and_dynamic_is_false(self, opt):
        plot = self.df.hvplot(x='x', y='y', frame_height=150, datashade=True, dynamic=False, **{opt: 2})
        opts = Store.lookup_options('bokeh', plot[()], 'plot').kwargs
        self.assertEqual(opts[opt], 2)
        self.assertEqual(opts.get('frame_height'), 150)
        self.assertEqual(opts.get('height'), None)
        self.assertEqual(opts.get('frame_width'), None)

    def test_cmap_can_be_color_key(self):
        color_key = {'A': '#ff0000', 'B': '#00ff00', 'C': '#0000ff'}
        self.df.hvplot.points(x='x', y='y', by='category', cmap=color_key, datashade=True)
        with self.assertRaises(TypeError):
            self.df.hvplot.points(x='x', y='y', by='category', datashade=True,
                                  cmap='kbc_r', color_key=color_key)

    def test_when_datashade_is_true_set_hover_to_false_by_default(self):
        plot = self.df.hvplot(x='x', y='y', datashade=True)
        opts = Store.lookup_options('bokeh', plot[()], 'plot').kwargs
        assert 'hover' not in opts.get('tools')

    def test_when_datashade_is_true_hover_can_still_be_true(self):
        plot = self.df.hvplot(x='x', y='y', datashade=True, hover=True)
        opts = Store.lookup_options('bokeh', plot[()], 'plot').kwargs
        assert 'hover' in opts.get('tools')

    def test_xlim_affects_x_range(self):
        data = pd.DataFrame(np.random.randn(100).cumsum())
        img = data.hvplot(xlim=(0, 20000), datashade=True, dynamic=False)
        assert img.range(0) == (0, 20000)


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
