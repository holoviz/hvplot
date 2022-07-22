import pathlib
import sys

from unittest import TestCase, SkipTest, expectedFailure

from packaging.version import Version
import numpy as np
import pandas as pd
import holoviews as hv


class TestGeo(TestCase):

    def setUp(self):
        if sys.platform == "win32":
            raise SkipTest("Skip geo tests on windows for now")
        try:
            import xarray as xr
            import rasterio  # noqa
            import geoviews  # noqa
            import cartopy.crs as ccrs
        except:
            raise SkipTest('xarray, rasterio, geoviews, or cartopy not available')
        import hvplot.xarray  # noqa
        import hvplot.pandas  # noqa
        self.da = xr.open_rasterio(
           pathlib.Path(__file__).parent / 'data' / 'RGB-red.byte.tif'
        ).sel(band=1)
        self.crs = ccrs.epsg(self.da.crs.split('epsg:')[1])

    def assertCRS(self, plot, proj='utm'):
        import cartopy
        if Version(cartopy.__version__) < Version('0.20'):
            assert plot.crs.proj4_params['proj'] == proj
        else:
            assert plot.crs.to_dict()['proj'] == proj

    def assert_projection(self, plot, proj):
        opts = hv.Store.lookup_options('bokeh', plot, 'plot')
        assert opts.kwargs['projection'].proj4_params['proj'] == proj


class TestCRSInference(TestGeo):

    def setUp(self):
        if sys.platform == "win32":
            raise SkipTest("Skip CRS inference on Windows")
        super().setUp()
        
    def test_plot_with_crs_as_proj_string(self):
        plot = self.da.hvplot.image('x', 'y', crs=self.da.crs)
        self.assertCRS(plot)

    def test_plot_with_geo_as_true_crs_undefined(self):
        plot = self.da.hvplot.image('x', 'y', geo=True)
        self.assertCRS(plot)


class TestProjections(TestGeo):

    def test_plot_with_crs_as_object(self):
        plot = self.da.hvplot.image('x', 'y', crs=self.crs)
        self.assertCRS(plot)

    def test_plot_with_crs_as_attr_str(self):
        da = self.da.copy()
        da.attrs = {'bar': self.crs}
        plot = da.hvplot.image('x', 'y', crs='bar')
        self.assertCRS(plot)

    def test_plot_with_crs_as_nonexistent_attr_str(self):
        # Used to test crs='foo' but this is parsed under-the-hood
        # by PROJ (projinfo) which matches a geographic projection named
        # 'Amersfoort'
        with self.assertRaisesRegex(ValueError, "'name_of_some_invalid_projection' must be"):
            self.da.hvplot.image('x', 'y', crs='name_of_some_invalid_projection')

    def test_plot_with_geo_as_true_crs_no_crs_on_data_returns_default(self):
        da = self.da.copy()
        da.attrs = {'bar': self.crs}
        plot = da.hvplot.image('x', 'y', geo=True)
        self.assertCRS(plot, 'eqc')

    def test_plot_with_projection_as_string(self):
        da = self.da.copy()
        plot = da.hvplot.image('x', 'y', crs=self.crs, projection='Robinson')
        self.assert_projection(plot, 'robin')

    def test_plot_with_projection_as_string_google_mercator(self):
        da = self.da.copy()
        plot = da.hvplot.image('x', 'y', crs=self.crs, projection='GOOGLE_MERCATOR')
        self.assert_projection(plot, 'merc')

    def test_plot_with_projection_as_invalid_string(self):
        with self.assertRaisesRegex(ValueError, "Projection must be defined"):
            self.da.hvplot.image('x', 'y', projection='foo')


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

    def test_plot_with_coastline_sets_geo_by_default(self):
        import geoviews as gv
        plot = self.df.hvplot.points('x', 'y', coastline=True)
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
        self.assertIn('openstreetmap', plot.get(0).data)

    def test_plot_with_specific_tiles(self):
        plot = self.df.hvplot.points('x', 'y', geo=True, tiles='ESRI')
        self.assertEqual(len(plot), 2)
        self.assertIsInstance(plot.get(0), hv.Tiles)
        self.assertIn('ArcGIS', plot.get(0).data)

    def test_plot_with_specific_tile_class(self):
        plot = self.df.hvplot.points('x', 'y', geo=True, tiles=hv.element.tiles.EsriImagery)
        self.assertEqual(len(plot), 2)
        self.assertIsInstance(plot.get(0), hv.Tiles)
        self.assertIn('ArcGIS', plot.get(0).data)

    def test_plot_with_specific_tile_obj(self):
        plot = self.df.hvplot.points('x', 'y', geo=True, tiles=hv.element.tiles.EsriImagery())
        self.assertEqual(len(plot), 2)
        self.assertIsInstance(plot.get(0), hv.Tiles)
        self.assertIn('ArcGIS', plot.get(0).data)

    def test_plot_with_specific_gv_tile_obj(self):
        import geoviews as gv
        plot = self.df.hvplot.points('x', 'y', geo=True, tiles=gv.tile_sources.CartoDark)
        self.assertEqual(len(plot), 2)
        self.assertIsInstance(plot.get(0), gv.element.WMTS)


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

    def test_geo_points_color_internally_set_to_dim(self):
        altered_df = self.df.copy().assign(red=np.random.choice(['a', 'b'], len(self.df)))
        plot = altered_df.hvplot.points('x', 'y', c='red', geo=True)
        opts = hv.Store.lookup_options('bokeh', plot, 'style')
        self.assertIsInstance(opts.kwargs['color'], hv.dim)
        self.assertEqual(opts.kwargs['color'].dimension.name, 'red')

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


class TestGeoPandas(TestCase):

    def setUp(self):
        try:
            import geopandas as gpd  # noqa
            import geoviews  # noqa
            import cartopy.crs as ccrs # noqa
        except:
            raise SkipTest('geopandas, geoviews, or cartopy not available')
        import hvplot.pandas  # noqa

        geometry = gpd.points_from_xy(
            x=[12.45339, 12.44177, 9.51667, 6.13000, 158.14997],
            y=[41.90328, 43.93610, 47.13372, 49.61166, 6.91664],
            crs='EPSG:4326'
        )
        names = ['Vatican City', 'San Marino', 'Vaduz', 'Luxembourg', 'Palikir']
        self.cities = gpd.GeoDataFrame(dict(name=names), geometry=geometry)

    def test_points_hover_cols_is_empty_by_default(self):
        points = self.cities.hvplot()
        assert points.kdims == ['x', 'y']
        assert points.vdims == []

    def test_points_hover_cols_does_not_include_geometry_when_all(self):
        points = self.cities.hvplot(x='x', y='y', hover_cols='all')
        assert points.kdims == ['x', 'y']
        assert points.vdims == ['index', 'name']

    def test_points_hover_cols_when_all_and_use_columns_is_false(self):
        points = self.cities.hvplot(x='x', hover_cols='all', use_index=False)
        assert points.kdims == ['x', 'y']
        assert points.vdims == ['name']

    def test_points_hover_cols_index_in_list(self):
        points = self.cities.hvplot(y='y', hover_cols=['index'])
        assert points.kdims == ['x', 'y']
        assert points.vdims == ['index']

    def test_points_hover_cols_with_c_set_to_name(self):
        points = self.cities.hvplot(c='name')
        assert points.kdims == ['x', 'y']
        assert points.vdims == ['name']
        opts = hv.Store.lookup_options('bokeh', points, 'style').kwargs
        assert opts['color'] == 'name'

    @expectedFailure
    def test_points_hover_cols_with_by_set_to_name(self):
        points = self.cities.hvplot(by='name')
        assert points.kdims == ['x', 'y']
        assert points.vdims == ['name']
