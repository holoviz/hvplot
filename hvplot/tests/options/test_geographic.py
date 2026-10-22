"""
Geographic options, with GeoViews (tests marked with `geo`) and without it.
"""

import pathlib
import sys
from unittest import SkipTest, TestCase

import holoviews as hv
import numpy as np
import pandas as pd
import pytest
import xarray as xr
from holoviews.element import Image
from holoviews.element.comparison import ComparisonTestCase
from holoviews.util.transform import lon_lat_to_easting_northing

from hvplot.tests._data import air_temperature
from hvplot.tests._deps import requires
from hvplot.util import is_geodataframe, proj_to_cartopy

try:
    import dask.dataframe as dd
except ImportError:
    dd = None

try:
    import spatialpandas as spd
except ModuleNotFoundError:
    spd = None

bk_renderer = hv.Store.renderers['bokeh']


@pytest.fixture
def simple_df():
    return pd.DataFrame(np.random.rand(10, 2), columns=['x', 'y'])


@pytest.mark.geo
@requires('pyproj', 'rasterio', 'rioxarray')
class TestGeo(TestCase):
    def setUp(self):
        if sys.platform == 'win32':
            raise SkipTest('Skip geo tests on windows for now')
        import rioxarray as rxr

        import hvplot.pandas
        import hvplot.xarray  # noqa: F401

        self.da = rxr.open_rasterio(
            pathlib.Path(__file__).parents[1] / 'data' / 'RGB-red.byte.tif'
        ).isel(band=0)
        # UTM zone 18N
        self.crs = proj_to_cartopy(self.da.spatial_ref.attrs['crs_wkt'])

    def assertCRS(self, plot, proj=None):
        import cartopy

        if proj is None:
            proj = cartopy.crs.UTM(zone=18)

        assert plot.crs == proj

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
        import cartopy.crs as ccrs

        da = self.da.copy()
        da.rio._crs = False  # To not treat it as a rioxarray
        da.attrs = {'bar': self.crs}
        plot = da.hvplot.image('x', 'y', geo=True)
        self.assertCRS(plot, ccrs.PlateCarree())

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
        import cartopy.crs as ccrs
        import geoviews as gv
        import xarray as xr

        try:
            from holoviews.operation.datashader import rasterize
        except ImportError:
            raise SkipTest('datashader not available')

        ds = air_temperature()
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


@pytest.mark.geo
class TestGeoAnnotation(TestCase):
    def setUp(self):
        import cartopy.crs as ccrs

        import hvplot.pandas  # noqa: F401

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
        plot = self.df.hvplot.points('x', 'y', geo=False, tiles=True, tiles_opts={'alpha': 0.5})
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

        plot = self.df.hvplot.points('x', 'y', geo=True, tiles=True, tiles_opts={'alpha': 0.5})
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


@pytest.mark.geo
class TestGeoElements(TestCase):
    def setUp(self):
        import cartopy.crs as ccrs

        import hvplot.pandas  # noqa: F401

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


# Without GeoViews


# Not autouse, so that the tests marked with `geo` above still get GeoViews.
@pytest.fixture
def _without_geoviews(block_import, hvplot_pandas):
    block_import('geoviews')


@pytest.fixture
def lat_lon_df():
    return pd.DataFrame(
        {
            'lon': [-120.0, -100.0, -80.0],
            'lat': [30.0, 35.0, 40.0],
        }
    )


@pytest.fixture
def mercator_df():
    x_merc, y_merc = lon_lat_to_easting_northing(
        np.array([-120.0, -100.0, -80.0]), np.array([30.0, 35.0, 40.0])
    )
    return pd.DataFrame(
        {
            'x': x_merc,
            'y': y_merc,
        }
    )


@pytest.mark.usefixtures('_without_geoviews')
class TestAnnotationNotGeo:
    def test_plot_tiles_doesnt_set_geo(self, simple_df):
        plot = simple_df.hvplot.points('x', 'y', tiles=True)
        assert len(plot) == 2
        assert isinstance(plot.get(0), hv.Tiles)
        assert 'openstreetmap' in plot.get(0).data
        assert 'x_' in plot.get(1).data
        assert 'y_' in plot.get(1).data
        bk_plot = bk_renderer.get_plot(plot)
        assert bk_plot.projection == 'mercator'

    def test_plot_specific_tiles_doesnt_set_geo(self, simple_df):
        plot = simple_df.hvplot.points('x', 'y', tiles='ESRI')
        assert len(plot) == 2
        assert isinstance(plot.get(0), hv.Tiles)
        assert 'ArcGIS' in plot.get(0).data
        assert 'x_' in plot.get(1).data
        assert 'y_' in plot.get(1).data
        bk_plot = bk_renderer.get_plot(plot)
        assert bk_plot.projection == 'mercator'

    def test_plot_with_specific_tile_class(self, simple_df):
        plot = simple_df.hvplot.points('x', 'y', tiles=hv.element.tiles.EsriImagery)
        assert len(plot) == 2
        assert isinstance(plot.get(0), hv.Tiles)
        assert 'ArcGIS' in plot.get(0).data
        bk_plot = bk_renderer.get_plot(plot)
        assert bk_plot.projection == 'mercator'

    def test_plot_with_specific_tile_obj(self, simple_df):
        plot = simple_df.hvplot.points('x', 'y', tiles=hv.element.tiles.EsriImagery())
        assert len(plot) == 2
        assert isinstance(plot.get(0), hv.Tiles)
        assert 'ArcGIS' in plot.get(0).data
        assert 'x_' in plot.get(1).data
        assert 'y_' in plot.get(1).data
        bk_plot = bk_renderer.get_plot(plot)
        assert bk_plot.projection == 'mercator'

    def test_plot_with_xyzservices_tileprovider(self, simple_df):
        xyzservices = pytest.importorskip('xyzservices')
        plot = simple_df.hvplot.points('x', 'y', tiles=xyzservices.providers.Esri.WorldImagery)
        assert 'x_' in plot.get(1).data
        assert 'y_' in plot.get(1).data
        assert len(plot) == 2
        assert isinstance(plot.get(0), hv.Tiles)
        assert isinstance(plot.get(0).data, xyzservices.TileProvider)
        bk_plot = bk_renderer.get_plot(plot)
        assert bk_plot.projection == 'mercator'

    @pytest.mark.skipif(dd is None, reason='dask not installed')
    def test_plot_with_dask(self, simple_df):
        import hvplot.dask  # noqa: F401

        ddf = dd.from_pandas(simple_df, npartitions=2)
        plot = ddf.hvplot.points('x', 'y', tiles=True)
        assert 'x_' not in plot.get(1).data
        assert 'y_' not in plot.get(1).data
        assert len(plot) == 2
        assert isinstance(plot.get(0), hv.Tiles)
        bk_plot = bk_renderer.get_plot(plot)
        assert bk_plot.projection == 'mercator'

    @pytest.mark.skipif(spd is None, reason='spatialpandas not installed')
    def test_plot_without_crs(self):
        square = spd.geometry.Polygon([(0.0, 0), (0, 1), (1, 1), (1, 0)])
        sdf = spd.GeoDataFrame({'geometry': spd.GeoSeries([square, square]), 'name': ['A', 'B']})
        plot = sdf.hvplot.polygons(tiles=True)

        assert len(plot) == 2
        assert is_geodataframe(sdf)
        assert not hasattr(sdf, 'crs')
        assert isinstance(plot.get(0), hv.Tiles)
        assert isinstance(plot.get(1), hv.Polygons)
        bk_plot = bk_renderer.get_plot(plot)
        assert bk_plot.projection == 'mercator'  # projection enabled due to `tiles=True`

    def test_xlim_ylim_conversion_with_tiles(self, simple_df):
        """Test that xlim and ylim are automatically converted to Web Mercator when tiles=True"""
        df = pd.DataFrame(
            {'lon': [-120.0, -100.0, -80.0], 'lat': [30.0, 35.0, 40.0], 'value': [1, 2, 3]}
        )
        plot = df.hvplot.points('lon', 'lat', tiles=True, xlim=(-130, -70), ylim=(25, 45))
        points = plot.get(1)

        assert 'x' in points.data.columns
        assert 'y' in points.data.columns

        xlim_expected_0, _ = lon_lat_to_easting_northing(-130, 0)
        xlim_expected_1, _ = lon_lat_to_easting_northing(-70, 0)
        _, ylim_expected_0 = lon_lat_to_easting_northing(0, 25)
        _, ylim_expected_1 = lon_lat_to_easting_northing(0, 45)

        bk_plot = bk_renderer.get_plot(plot)
        x_range_start = bk_plot.handles['plot'].x_range.start
        x_range_end = bk_plot.handles['plot'].x_range.end
        y_range_start = bk_plot.handles['plot'].y_range.start
        y_range_end = bk_plot.handles['plot'].y_range.end
        assert x_range_start == xlim_expected_0
        assert x_range_end == xlim_expected_1
        assert y_range_start == ylim_expected_0
        assert y_range_end == ylim_expected_1

    def test_xlim_only_conversion_with_tiles(self, lat_lon_df):
        """Opt xlim should convert even when ylim is not provided."""
        plot = lat_lon_df.hvplot.points('lon', 'lat', tiles=True, xlim=(-130, -70))
        bk_plot = bk_renderer.get_plot(plot)

        x_start = bk_plot.state.x_range.start
        x_end = bk_plot.state.x_range.end

        np.testing.assert_almost_equal(x_start, -14471533.803125564)
        np.testing.assert_almost_equal(x_end, -7792364.355529151)
        assert x_start < x_end

    def test_ylim_only_conversion_with_tiles(self, lat_lon_df):
        """Opt ylim should convert even when xlim is not provided."""
        plot = lat_lon_df.hvplot.points('lon', 'lat', tiles=True, ylim=(25, 45))
        bk_plot = bk_renderer.get_plot(plot)

        y_start = bk_plot.state.y_range.start
        y_end = bk_plot.state.y_range.end

        assert y_start > 2_000_000
        assert y_end > 5_000_000
        assert y_start < y_end

    def test_xlim_ylim_not_converted_without_tiles(self, lat_lon_df):
        """Test that xlim and ylim are NOT converted when tiles=False"""
        plot = lat_lon_df.hvplot.points('lon', 'lat', xlim=(-130, -70), ylim=(25, 45))
        bk_plot = bk_renderer.get_plot(plot)

        x_range_start = bk_plot.handles['plot'].x_range.start
        x_range_end = bk_plot.handles['plot'].x_range.end
        y_range_start = bk_plot.handles['plot'].y_range.start
        y_range_end = bk_plot.handles['plot'].y_range.end

        assert x_range_start == -130
        assert x_range_end == -70
        assert y_range_start == 25
        assert y_range_end == 45

    def test_xlim_ylim_out_of_bounds_not_converted(self, mercator_df):
        """Test that xlim and ylim are NOT converted when values are outside lat/lon bounds"""
        plot = mercator_df.hvplot.points('x', 'y', tiles=True, xlim=(1000, 3000), ylim=(400, 800))
        bk_plot = bk_renderer.get_plot(plot.get(1))

        x_range_start = bk_plot.handles['plot'].x_range.start
        x_range_end = bk_plot.handles['plot'].x_range.end
        y_range_start = bk_plot.handles['plot'].y_range.start
        y_range_end = bk_plot.handles['plot'].y_range.end

        assert x_range_start == 1000
        assert x_range_end == 3000
        assert y_range_start == 400
        assert y_range_end == 800


@pytest.mark.usefixtures('hvplot_xarray')
class TestGridPlots(ComparisonTestCase):
    def setUp(self):
        self.ds = xr.Dataset(
            {
                'temp': (('lon', 'lat'), 15 + 8 * np.random.randn(2, 2)),
                'precip': (('lon', 'lat'), 10 * np.random.rand(2, 2)),
            },
            coords={'lon': [-99.83, -99.32], 'lat': [42.25, 42.21]},
        )

    def test_tiles_without_gv(self):
        plot = self.ds.hvplot('lon', 'lat', tiles=True)
        assert len(plot) == 2
        assert isinstance(plot.get(1), Image)
        assert 'x' in plot.get(1).data
        assert 'y' in plot.get(1).data
