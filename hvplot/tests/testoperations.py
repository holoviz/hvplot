import sys

from unittest import SkipTest
from parameterized import parameterized

import hvplot.pandas  # noqa
import numpy as np
import pandas as pd

from holoviews import Store
from holoviews.element import Image, QuadMesh
from holoviews.element.comparison import ComparisonTestCase
from hvplot.converter import HoloViewsConverter


class TestDatashader(ComparisonTestCase):

    def setUp(self):
        try:
            import datashader # noqa
        except:
            raise SkipTest('Datashader not available')
        if sys.maxsize < 2**32:
            raise SkipTest('Datashader does not support 32-bit systems')
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

    def test_rasterize_default_colorbar(self):
        plot = self.df.hvplot.scatter('x', 'y', dynamic=False, rasterize=True)
        opts = Store.lookup_options('bokeh', plot, 'plot').kwargs
        self.assertTrue(opts.get('colorbar'))

    def test_rasterize_default_colorbar_with_cmap(self):
        cmap = 'Reds'
        plot = self.df.hvplot.scatter('x', 'y', dynamic=False, rasterize=True, cmap=cmap)
        opts = Store.lookup_options('bokeh', plot, 'style').kwargs
        self.assertEqual(opts.get('cmap'), cmap)
        opts = Store.lookup_options('bokeh', plot, 'plot').kwargs
        self.assertTrue(opts.get('colorbar'))

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

    @parameterized.expand([('scatter',), ('line',), ('area',)])
    def test_wide_charts_categorically_shaded_explicit_ys(self, kind):
        df = pd._testing.makeTimeDataFrame()
        plot = pd._testing.makeTimeDataFrame().hvplot(y=list(df.columns), datashade=True, kind=kind)
        expected_cmap = HoloViewsConverter._default_cmaps['categorical']
        assert plot.callback.inputs[0].callback.operation.p.cmap == expected_cmap
        assert  plot.callback.inputs[0].callback.operation.p.aggregator.column == 'Variable'

    @parameterized.expand([('scatter',), ('line',), ('area',)])
    def test_wide_charts_categorically_shaded_implicit_ys(self, kind):
        plot = pd._testing.makeTimeDataFrame().hvplot(datashade=True, kind=kind)
        expected_cmap = HoloViewsConverter._default_cmaps['categorical']
        assert plot.callback.inputs[0].callback.operation.p.cmap == expected_cmap
        assert  plot.callback.inputs[0].callback.operation.p.aggregator.column == 'Variable'

    def test_wide_charts_categorically_shaded_by(self):
        cat_col = 'category'
        plot = self.df.hvplot.scatter('x', 'y', by=cat_col, datashade=True)
        expected_cmap = HoloViewsConverter._default_cmaps['categorical']
        assert  plot.callback.inputs[0].callback.operation.p.cmap == expected_cmap
        assert  plot.callback.inputs[0].callback.operation.p.aggregator.column == cat_col
    def test_rasterize_cnorm(self):
        expected = 'eq_hist'
        plot = self.df.hvplot(x='x', y='y', rasterize=True, cnorm=expected)
        opts = Store.lookup_options('bokeh', plot[()], 'plot').kwargs
        assert opts.get('cnorm') == expected

    def test_datashade_cnorm(self):
        expected = 'eq_hist'
        plot = self.df.hvplot(x='x', y='y', datashade=True, cnorm=expected)
        actual = plot.callback.inputs[0].callback.operation.p['cnorm']
        assert actual == expected

    def test_rasterize_rescale_discrete_levels(self):
        expected = False
        plot = self.df.hvplot(x='x', y='y', rasterize=True, cnorm='eq_hist', rescale_discrete_levels=expected)
        opts = Store.lookup_options('bokeh', plot[()], 'plot').kwargs
        assert opts.get('rescale_discrete_levels') is expected

    def test_datashade_rescale_discrete_levels(self):
        expected = False
        plot = self.df.hvplot(x='x', y='y', datashade=True, cnorm='eq_hist', rescale_discrete_levels=expected)
        actual = plot.callback.inputs[0].callback.operation.p['rescale_discrete_levels']
        assert actual is expected

    def test_datashade_rescale_discrete_levels_default_True(self):
        expected = True
        plot = self.df.hvplot(x='x', y='y', datashade=True, cnorm='eq_hist')
        actual = plot.callback.inputs[0].callback.operation.p['rescale_discrete_levels']
        assert actual is expected


class TestChart2D(ComparisonTestCase):

    def setUp(self):
        try:
            import xarray as xr
            import datashader as ds # noqa
        except:
            raise SkipTest('xarray or datashader not available')
        if sys.maxsize < 2**32:
            raise SkipTest('Datashader does not support 32-bit systems')
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
