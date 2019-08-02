from unittest import TestCase, SkipTest

import numpy as np
import pandas as pd
import holoviews as hv


class TestGeo(TestCase):

    def setUp(self):
        try:
            import xarray as xr
            import rasterio  # noqa
            import geoviews  # noqa
            import cartopy.crs as ccrs
        except:
            raise SkipTest('xarray, rasterio, geoviews, or cartopy not available')
        import hvplot.xarray  # noqa
        import hvplot.pandas  # noqa
        self.da = (xr.open_rasterio(
            'https://github.com/mapbox/rasterio/raw/master/tests/data/RGB.byte.tif')
            .sel(band=1))
        self.crs = ccrs.epsg(self.da.crs.split('epsg:')[1])

    def assertCRS(self, plot, proj='utm'):
        assert plot.crs.proj4_params['proj'] == proj

    def test_plot_with_crs_as_object(self):
        plot = self.da.hvplot.image('x', 'y', crs=self.crs)
        self.assertCRS(plot)

    def test_plot_with_crs_as_proj_string(self):
        plot = self.da.hvplot.image('x', 'y', crs=self.da.crs)
        self.assertCRS(plot)

    def test_plot_with_geo_as_true_crs_undefined(self):
        plot = self.da.hvplot.image('x', 'y', geo=True)
        self.assertCRS(plot)

    def test_plot_with_crs_as_attr_str(self):
        da = self.da.copy()
        da.attrs = {'bar': self.crs}
        plot = da.hvplot.image('x', 'y', crs='bar')
        self.assertCRS(plot)

    def test_plot_with_crs_as_nonexistent_attr_str(self):
        with self.assertRaisesRegex(ValueError, "'foo' must be"):
            self.da.hvplot.image('x', 'y', crs='foo')

    def test_plot_with_geo_as_true_crs_no_crs_on_data_returns_default(self):
        da = self.da.copy()
        da.attrs = {'bar': self.crs}
        plot = da.hvplot.image('x', 'y', geo=True)
        self.assertCRS(plot, 'eqc')


class TestGeoAnnotation(TestCase):

    def setUp(self):
        try:
            import geoviews  # noqa
            import cartopy.crs as ccrs # noqa
        except:
            raise SkipTest('geoviews or cartopy not available')
        import hvplot.pandas  # noqa
        self.crs = ccrs.PlateCarree()
        self.df = pd.DataFrame(np.random.rand(10, 2), columns=['x', 'y'])

    def test_plot_with_coastline(self):
        import geoviews as gv
        plot = self.df.hvplot.points('x', 'y', geo=True, coastline=True)
        self.assertEqual(len(plot), 2)
        coastline = plot.get(1)
        self.assertIsInstance(coastline, gv.Feature)

    def test_plot_with_coastline_scale(self):
        plot = self.df.hvplot.points('x', 'y', geo=True, coastline='10m')
        opts = plot.get(1).opts.get('plot')
        self.assertEqual(opts.kwargs, {'scale': '10m'})

    def test_plot_with_tiles(self):
        plot = self.df.hvplot.points('x', 'y', geo=True, tiles=True)
        self.assertEqual(len(plot), 2)
        self.assertIsInstance(plot.get(0), hv.Tiles)
        self.assertIn('wikimedia', plot.get(0).data)

    def test_plot_with_specific_tiles(self):
        plot = self.df.hvplot.points('x', 'y', geo=True, tiles='ESRI')
        self.assertEqual(len(plot), 2)
        self.assertIsInstance(plot.get(0), hv.Tiles)
        self.assertIn('ArcGIS', plot.get(0).data)


class TestGeoElements(TestCase):

    def setUp(self):
        try:
            import geoviews  # noqa
            import cartopy.crs as ccrs # noqa
        except:
            raise SkipTest('geoviews or cartopy not available')
        import hvplot.pandas  # noqa
        self.crs = ccrs.PlateCarree()
        self.df = pd.DataFrame(np.random.rand(10, 2), columns=['x', 'y'])

    def test_geo_hexbin(self):
        hextiles = self.df.hvplot.hexbin('x', 'y', geo=True)
        self.assertEqual(hextiles.crs, self.crs)

    def test_geo_points(self):
        points = self.df.hvplot.points('x', 'y', geo=True)
        self.assertEqual(points.crs, self.crs)

    def test_geo_opts(self):
        points = self.df.hvplot.points('x', 'y', geo=True)
        opts = hv.Store.lookup_options('bokeh', points, 'plot').kwargs
        self.assertEqual(opts.get('data_aspect'), 1)
        self.assertEqual(opts.get('width'), None)

    def test_geo_opts_with_width(self):
        points = self.df.hvplot.points('x', 'y', geo=True, width=200)
        opts = hv.Store.lookup_options('bokeh', points, 'plot').kwargs
        self.assertEqual(opts.get('data_aspect'), 1)
        self.assertEqual(opts.get('width'), 200)
        self.assertEqual(opts.get('height'), None)
