"""
These tests depends on GeoViews.
"""

import pathlib
import sys

from unittest import TestCase, SkipTest

import holoviews as hv
import numpy as np
import pandas as pd
import pytest

from hvplot.util import proj_to_cartopy
from packaging.version import Version

pytestmark = pytest.mark.geo

bk_renderer = hv.Store.renderers['bokeh']


@pytest.fixture
def simple_df():
    return pd.DataFrame(np.random.rand(10, 2), columns=['x', 'y'])


class TestGeo(TestCase):
    def setUp(self):
        if sys.platform == 'win32':
            raise SkipTest('Skip geo tests on windows for now')
        try:
            import xarray as xr  # noqa
            import rasterio  # noqa
            import geoviews  # noqa
            import cartopy.crs as ccrs  # noqa
            import pyproj  # noqa
            import rioxarray as rxr
        except ImportError:
            raise SkipTest(
                'xarray, rasterio, geoviews, cartopy, pyproj or rioxarray not available'
            )
        import hvplot.xarray  # noqa
        import hvplot.pandas  # noqa

        self.da = rxr.open_rasterio(
            pathlib.Path(__file__).parent / 'data' / 'RGB-red.byte.tif'
        ).isel(band=0)
        self.crs = proj_to_cartopy(self.da.spatial_ref.attrs['crs_wkt'])

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
        if sys.platform == 'win32':
            raise SkipTest('Skip CRS inference on Windows')
        super().setUp()

    def test_plot_with_crs_as_proj_string(self):
        da = self.da.copy()
        da.rio._crs = False  # To not treat it as a rioxarray

        plot = self.da.hvplot.image('x', 'y', crs='epsg:32618')
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
        da.rio._crs = False  # To not treat it as a rioxarray
        da.attrs = {'bar': self.crs}
        plot = da.hvplot.image('x', 'y', crs='bar')
        self.assertCRS(plot)

    def test_plot_with_crs_as_pyproj_Proj(self):
        import pyproj

        da = self.da.copy()
        da.rio._crs = False  # To not treat it as a rioxarray
        plot = da.hvplot.image('x', 'y', crs=pyproj.Proj(self.crs))
        self.assertCRS(plot)

    def test_plot_with_crs_as_nonexistent_attr_str(self):
        da = self.da.copy()
        da.rio._crs = False  # To not treat it as a rioxarray

        # Used to test crs='foo' but this is parsed under-the-hood
        # by PROJ (projinfo) which matches a geographic projection named
        # 'Amersfoort'
        with self.assertRaisesRegex(ValueError, "'name_of_some_invalid_projection' must be"):
            da.hvplot.image('x', 'y', crs='name_of_some_invalid_projection')

    def test_plot_with_geo_as_true_crs_no_crs_on_data_returns_default(self):
        da = self.da.copy()
        da.rio._crs = False  # To not treat it as a rioxarray
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
        with self.assertRaisesRegex(ValueError, 'Projection must be defined'):
            self.da.hvplot.image('x', 'y', projection='foo')

    def test_plot_with_projection_raises_an_error_when_tiles_set(self):
        da = self.da.copy()
        with self.assertRaisesRegex(ValueError, 'Tiles can only be used with output projection'):
            da.hvplot.image('x', 'y', crs=self.crs, projection='Robinson', tiles=True)

    def test_overlay_with_projection(self):
        # Regression test for https://github.com/holoviz/hvplot/issues/1090
        df = pd.DataFrame({'lon': [0, 10], 'lat': [40, 50], 'v': [0, 1]})

        plot1 = df.hvplot.points(x='lon', y='lat', s=200, c='y', geo=True, tiles='CartoLight')
        plot2 = df.hvplot.points(x='lon', y='lat', c='v', geo=True)

        # This should work without erroring
        plot = plot1 * plot2
        hv.renderer('bokeh').get_plot(plot)

    def test_geo_with_rasterize(self):
        import xarray as xr
        import cartopy.crs as ccrs
        import geoviews as gv

        try:
            from holoviews.operation.datashader import rasterize
        except ImportError:
            raise SkipTest('datashader not available')

        ds = xr.tutorial.open_dataset('air_temperature')
        hvplot_output = ds.isel(time=0).hvplot.points(
            'lon',
            'lat',
            crs=ccrs.PlateCarree(),
            projection=ccrs.LambertConformal(),
            rasterize=True,
            dynamic=False,
            aggregator='max',
            project=True,
        )

        p1 = gv.Points(ds.isel(time=0), kdims=['lon', 'lat'], crs=ccrs.PlateCarree())
        p2 = gv.project(p1, projection=ccrs.LambertConformal())
        expected = rasterize(p2, dynamic=False, aggregator='max')

        xr.testing.assert_allclose(hvplot_output.data, expected.data)


class TestGeoAnnotation(TestCase):
    def setUp(self):
        try:
            import geoviews  # noqa
            import cartopy.crs as ccrs  # noqa
        except ImportError:
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
        assert opts.kwargs['scale'] == '10m'

    def test_plot_with_tiles(self):
        plot = self.df.hvplot.points('x', 'y', geo=False, tiles=True)
        self.assertEqual(len(plot), 2)
        self.assertIsInstance(plot.get(0), hv.Tiles)
        self.assertIn('openstreetmap', plot.get(0).data)

    def test_plot_with_tiles_with_tiles_opts(self):
        plot = self.df.hvplot.points('x', 'y', geo=False, tiles=True, tiles_opts=dict(alpha=0.5))
        assert len(plot) == 2
        tiles = plot.get(0)
        assert isinstance(tiles, hv.Tiles)
        assert 'openstreetmap' in tiles.data
        assert tiles.opts['alpha'] == 0.5

    def test_plot_with_tiles_with_geo(self):
        import geoviews as gv

        plot = self.df.hvplot.points('x', 'y', geo=True, tiles=True)
        self.assertEqual(len(plot), 2)
        self.assertIsInstance(plot.get(0), gv.element.WMTS)
        self.assertIn('openstreetmap', plot.get(0).data)

    def test_plot_with_tiles_with_tiles_opts_with_geo(self):
        import geoviews as gv

        plot = self.df.hvplot.points('x', 'y', geo=True, tiles=True, tiles_opts=dict(alpha=0.5))
        assert len(plot) == 2
        tiles = plot.get(0)
        assert isinstance(tiles, gv.element.WMTS)
        assert 'openstreetmap' in tiles.data
        assert tiles.opts['alpha'] == 0.5

    def test_plot_with_specific_tiles(self):
        plot = self.df.hvplot.points('x', 'y', geo=False, tiles='ESRI')
        self.assertEqual(len(plot), 2)
        self.assertIsInstance(plot.get(0), hv.Tiles)
        self.assertIn('ArcGIS', plot.get(0).data)

    def test_plot_with_specific_tiles_geo(self):
        import geoviews as gv

        plot = self.df.hvplot.points('x', 'y', geo=True, tiles='ESRI')
        self.assertEqual(len(plot), 2)
        self.assertIsInstance(plot.get(0), gv.element.WMTS)
        self.assertIn('ArcGIS', plot.get(0).data)

    def test_plot_with_specific_tile_class(self):
        plot = self.df.hvplot.points('x', 'y', geo=False, tiles=hv.element.tiles.EsriImagery)
        self.assertEqual(len(plot), 2)
        self.assertIsInstance(plot.get(0), hv.Tiles)
        self.assertIn('ArcGIS', plot.get(0).data)

    def test_plot_with_specific_tile_class_with_geo(self):
        import geoviews as gv

        plot = self.df.hvplot.points('x', 'y', geo=True, tiles=gv.tile_sources.EsriImagery)
        self.assertEqual(len(plot), 2)
        self.assertIsInstance(plot.get(0), gv.element.WMTS)
        self.assertIn('ArcGIS', plot.get(0).data)

    def test_plot_with_specific_tile_obj(self):
        plot = self.df.hvplot.points('x', 'y', geo=False, tiles=hv.element.tiles.EsriImagery())
        self.assertEqual(len(plot), 2)
        self.assertIsInstance(plot.get(0), hv.Tiles)
        self.assertIn('ArcGIS', plot.get(0).data)

    def test_plot_with_specific_tile_obj_with_geo(self):
        plot = self.df.hvplot.points('x', 'y', geo=True, tiles=hv.element.tiles.EsriImagery())
        self.assertEqual(len(plot), 2)
        self.assertIsInstance(plot.get(0), hv.Tiles)
        self.assertIn('ArcGIS', plot.get(0).data)

    def test_plot_with_specific_gv_tile_obj(self):
        import geoviews as gv

        plot = self.df.hvplot.points('x', 'y', geo=True, tiles=gv.tile_sources.CartoDark)
        self.assertEqual(len(plot), 2)
        self.assertIsInstance(plot.get(0), gv.element.WMTS)

    def test_plot_with_xyzservices_tiles(self):
        xyzservices = pytest.importorskip('xyzservices')
        import geoviews as gv

        plot = self.df.hvplot.points(
            'x', 'y', geo=True, tiles=xyzservices.providers.Esri.WorldImagery
        )
        assert len(plot) == 2
        assert isinstance(plot.get(0), gv.element.WMTS)
        assert isinstance(plot.get(0).data, xyzservices.TileProvider)

    def test_plot_with_features_properly_overlaid_underlaid(self):
        # land should be under, borders should be over
        plot = self.df.hvplot.points('x', 'y', features=['land', 'borders'])
        assert plot.get(0).group == 'Land'
        assert plot.get(2).group == 'Borders'


class TestGeoElements(TestCase):
    def setUp(self):
        try:
            import geoviews  # noqa
            import cartopy.crs as ccrs  # noqa
        except ImportError:
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
            import cartopy.crs as ccrs  # noqa
            import shapely  # noqa
        except ImportError:
            raise SkipTest('geopandas, geoviews, shapely or cartopy not available')
        import hvplot.pandas  # noqa

        from shapely.geometry import Polygon

        p_geometry = gpd.points_from_xy(
            x=[12.45339, 12.44177, 9.51667, 6.13000, 158.14997],
            y=[41.90328, 43.93610, 47.13372, 49.61166, 6.91664],
            crs='EPSG:4326',
        )
        p_names = ['Vatican City', 'San Marino', 'Vaduz', 'Luxembourg', 'Palikir']
        self.cities = gpd.GeoDataFrame(dict(name=p_names), geometry=p_geometry)

        pg_geometry = [
            Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0))),
            Polygon(((2, 2), (2, 3), (3, 3), (3, 2), (2, 2))),
        ]
        pg_names = ['A', 'B']
        self.polygons = gpd.GeoDataFrame(dict(name=pg_names), geometry=pg_geometry)

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

    def test_points_hover_cols_positional_arg_sets_color(self):
        points = self.cities.hvplot('name')
        assert points.kdims == ['x', 'y']
        assert points.vdims == ['name']
        opts = hv.Store.lookup_options('bokeh', points, 'style').kwargs
        assert opts['color'] == 'name'

    def test_points_hover_cols_with_c_set_to_name(self):
        points = self.cities.hvplot(c='name')
        assert points.kdims == ['x', 'y']
        assert points.vdims == ['name']
        opts = hv.Store.lookup_options('bokeh', points, 'style').kwargs
        assert opts['color'] == 'name'

    def test_points_hover_cols_with_by_set_to_name(self):
        points = self.cities.hvplot(by='name')
        assert isinstance(points, hv.core.overlay.NdOverlay)
        assert points.kdims == ['name']
        assert points.vdims == []
        for element in points.values():
            assert element.kdims == ['x', 'y']
            assert element.vdims == []

    def test_points_project_xlim_and_ylim(self):
        points = self.cities.hvplot(geo=False, xlim=(-10, 10), ylim=(-20, -10))
        opts = hv.Store.lookup_options('bokeh', points, 'plot').options
        np.testing.assert_equal(opts['xlim'], (-10, 10))
        np.testing.assert_equal(opts['ylim'], (-20, -10))

    def test_points_project_xlim_and_ylim_with_geo(self):
        points = self.cities.hvplot(geo=True, xlim=(-10, 10), ylim=(-20, -10))
        opts = hv.Store.lookup_options('bokeh', points, 'plot').options
        np.testing.assert_allclose(opts['xlim'], (-10, 10))
        np.testing.assert_allclose(opts['ylim'], (-20, -10))

    def test_polygons_by_subplots(self):
        polygons = self.polygons.hvplot(geo=True, by='name', subplots=True)
        assert isinstance(polygons, hv.core.layout.NdLayout)

    def test_polygons_turns_off_hover_when_there_are_no_fields_to_include(self):
        polygons = self.polygons.hvplot(geo=True)
        opts = hv.Store.lookup_options('bokeh', polygons, 'plot').kwargs
        assert 'hover' not in opts.get('tools')

    def test_geometry_none(self):
        polygons = self.polygons.copy()
        polygons.geometry[1] = None
        assert polygons.hvplot(geo=True)

    def test_tiles_without_gv(self):
        polygons = self.polygons.copy()
        polygons_plot = polygons.hvplot(tiles=True)
        polygons_plot.get(1).data.crs is None

        polygons.crs = 'EPSG:4326'
        polygons_plot = self.polygons.hvplot(tiles=True)
        polygons_plot.get(1).data.crs == 'EPSG:3857'


class TestGeoUtil(TestCase):
    def setUp(self):
        if sys.platform == 'win32':
            raise SkipTest('Skip geo tests on windows for now')
        try:
            import cartopy.crs as ccrs
        except ImportError:
            raise SkipTest('cartopy not available')
        self.ccrs = ccrs

    def test_proj_to_cartopy(self):
        from ..util import proj_to_cartopy

        crs = proj_to_cartopy('+init=epsg:26911')

        assert isinstance(crs, self.ccrs.CRS)

    def test_proj_to_cartopy_wkt_string(self):
        from ..util import proj_to_cartopy

        crs = proj_to_cartopy(
            'GEOGCRS["unnamed",BASEGEOGCRS["unknown",DATUM["unknown",ELLIPSOID["WGS 84",6378137,298.257223563,LENGTHUNIT["metre",1,ID["EPSG",9001]]]],PRIMEM["Greenwich",0,ANGLEUNIT["degree",0.0174532925199433],ID["EPSG",8901]]],DERIVINGCONVERSION["unknown",METHOD["PROJ ob_tran o_proj=latlon"],PARAMETER["o_lon_p",0,ANGLEUNIT["degree",0.0174532925199433,ID["EPSG",9122]]],PARAMETER["o_lat_p",37.5,ANGLEUNIT["degree",0.0174532925199433,ID["EPSG",9122]]],PARAMETER["lon_0",357.5,ANGLEUNIT["degree",0.0174532925199433,ID["EPSG",9122]]]],CS[ellipsoidal,2],AXIS["longitude",east,ORDER[1],ANGLEUNIT["degree",0.0174532925199433,ID["EPSG",9122]]],AXIS["latitude",north,ORDER[2],ANGLEUNIT["degree",0.0174532925199433,ID["EPSG",9122]]]]'
        )  # noqa: E501

        assert isinstance(crs, self.ccrs.RotatedPole)
        assert crs.proj4_params['lon_0'] == 357.5
        assert crs.proj4_params['o_lat_p'] == 37.5

    def test_proj_to_cartopy_albers_equal_area_wkt(self):
        """Test Albers Equal Area projection from WKT string"""
        from ..util import proj_to_cartopy

        albers_wkt = 'PROJCS["Projection = Albers Conical Equal Area",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Albers_Conic_Equal_Area"],PARAMETER["latitude_of_center",23],PARAMETER["longitude_of_center",-96],PARAMETER["standard_parallel_1",29.5],PARAMETER["standard_parallel_2",45.5],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH]]'

        crs = proj_to_cartopy(albers_wkt)

        assert isinstance(crs, self.ccrs.AlbersEqualArea)
        assert crs.proj4_params['proj'] == 'aea'
        assert crs.proj4_params['lat_0'] == 23.0
        assert crs.proj4_params['lon_0'] == -96.0
        assert crs.proj4_params['lat_1'] == 29.5
        assert crs.proj4_params['lat_2'] == 45.5

    def test_proj_to_cartopy_albers_equal_area_proj4(self):
        """Test Albers Equal Area projection from PROJ4 string"""
        from ..util import proj_to_cartopy

        proj4_string = '+proj=aea +lat_0=23 +lon_0=-96 +lat_1=29.5 +lat_2=45.5 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs'

        crs = proj_to_cartopy(proj4_string)

        assert isinstance(crs, self.ccrs.AlbersEqualArea)

    def test_proj_to_cartopy_additional_projections(self):
        """
        Test that various PROJ.4 projection strings are correctly mapped to their
        expected Cartopy CRS classes by `proj_to_cartopy`.
        """
        from ..util import proj_to_cartopy

        test_cases = [
            ('+proj=eqdc +lat_0=40 +lon_0=-96 +lat_1=33 +lat_2=45', self.ccrs.EquidistantConic),
            ('+proj=aeqd +lat_0=40 +lon_0=-96', self.ccrs.AzimuthalEquidistant),
            ('+proj=gnom +lat_0=40 +lon_0=-96', self.ccrs.Gnomonic),
            ('+proj=ortho +lat_0=40 +lon_0=-96', self.ccrs.Orthographic),
            ('+proj=robin +lon_0=0', self.ccrs.Robinson),
            ('+proj=moll +lon_0=0', self.ccrs.Mollweide),
            ('+proj=sinu +lon_0=0', self.ccrs.Sinusoidal),
            ('+proj=eck4 +lon_0=0', self.ccrs.EckertIV),
            ('+proj=laea +lat_0=40 +lon_0=-96', self.ccrs.LambertAzimuthalEqualArea),
            ('+proj=cea +lon_0=0', self.ccrs.LambertCylindrical),
            ('+proj=mill +lon_0=0', self.ccrs.Miller),
        ]

        for proj4_string, expected_class in test_cases:
            with self.subTest(proj4=proj4_string):
                crs = proj_to_cartopy(proj4_string)
                assert isinstance(crs, expected_class), (
                    f'Expected {expected_class} for {proj4_string}, got {type(crs)}'
                )

    def test_proj_to_cartopy_geostationary_special_case(self):
        """Test Geostationary projection which requires special parameters"""
        from ..util import proj_to_cartopy

        # Geostationary typically requires satellite height
        proj4_string = '+proj=geos +lon_0=0 +h=35786023 +x_0=0 +y_0=0'

        crs = proj_to_cartopy(proj4_string)
        assert isinstance(crs, self.ccrs.Geostationary)

    def test_proj_to_cartopy_nearsided_perspective(self):
        """Test Near-sided Perspective projection"""
        from ..util import proj_to_cartopy

        proj4_string = '+proj=nsper +lat_0=40 +lon_0=-96 +h=10000000'

        crs = proj_to_cartopy(proj4_string)
        assert isinstance(crs, self.ccrs.NearsidePerspective)
