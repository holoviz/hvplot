"""
Geographic options, with GeoViews (tests marked with `geo`) and without it.
"""

import pathlib
import sys

import holoviews as hv
import numpy as np
import pandas as pd
import pytest
import xarray as xr
from holoviews.element import Image
from holoviews.util.transform import lon_lat_to_easting_northing

from hvplot.tests._data import air_temperature
from hvplot.tests._deps import requires
from hvplot.util import is_geodataframe, proj_to_cartopy

bk_renderer = hv.Store.renderers['bokeh']

skip_windows = pytest.mark.skipif(
    sys.platform == 'win32', reason='Skip geo tests on windows for now'
)


@pytest.fixture
def simple_df():
    return pd.DataFrame(np.random.rand(10, 2), columns=['x', 'y'])


@pytest.fixture
def utm_da(hvplot_xarray):
    """A rioxarray raster in UTM zone 18N."""
    rxr = pytest.importorskip('rioxarray')
    path = pathlib.Path(__file__).parents[1] / 'data' / 'RGB-red.byte.tif'
    return rxr.open_rasterio(path).isel(band=0)


@pytest.fixture
def utm_crs(utm_da):
    return proj_to_cartopy(utm_da.spatial_ref.attrs['crs_wkt'])


@pytest.fixture
def plain_da(utm_da):
    """The UTM raster, not treated as a rioxarray object."""
    da = utm_da.copy()
    da.rio._crs = False
    return da


def _utm():
    import cartopy.crs as ccrs

    return ccrs.UTM(zone=18)


def _projection_name(plot):
    opts = hv.Store.lookup_options('bokeh', plot, 'plot')
    return opts.kwargs['projection'].proj4_params['proj']


@pytest.mark.geo
@skip_windows
def test_crs_proj_string(plain_da):
    plot = plain_da.hvplot.image('x', 'y', crs='epsg:32618')
    assert plot.crs == _utm()


@pytest.mark.geo
@skip_windows
def test_crs_object(plain_da, utm_crs):
    plot = plain_da.hvplot.image('x', 'y', crs=utm_crs)
    assert plot.crs == _utm()


@pytest.mark.geo
@skip_windows
def test_crs_attr_name(plain_da, utm_crs):
    plain_da.attrs = {'bar': utm_crs}
    plot = plain_da.hvplot.image('x', 'y', crs='bar')
    assert plot.crs == _utm()


@pytest.mark.geo
@skip_windows
def test_crs_pyproj_proj(plain_da, utm_crs):
    import pyproj

    plot = plain_da.hvplot.image('x', 'y', crs=pyproj.Proj(utm_crs))
    assert plot.crs == _utm()


@pytest.mark.geo
@skip_windows
def test_crs_invalid_attr_name_error(plain_da):
    # Used to test crs='foo' but this is parsed under-the-hood
    # by PROJ (projinfo) which matches a geographic projection named
    # 'Amersfoort'
    with pytest.raises(ValueError, match="'name_of_some_invalid_projection' must be"):
        plain_da.hvplot.image('x', 'y', crs='name_of_some_invalid_projection')


@pytest.mark.geo
@skip_windows
def test_geo_crs_inferred_from_data(utm_da):
    plot = utm_da.hvplot.image('x', 'y', geo=True)
    assert plot.crs == _utm()


@pytest.mark.geo
@skip_windows
def test_geo_no_crs_on_data_defaults_to_plate_carree(hvplot_xarray, utm_crs):
    import cartopy.crs as ccrs

    # Longitudes and latitudes, as the data is plotted with a PlateCarree CRS.
    da = xr.DataArray(
        np.random.rand(5, 5),
        coords={'y': np.linspace(40, 44, 5), 'x': np.linspace(-75, -71, 5)},
        dims=['y', 'x'],
        attrs={'bar': utm_crs},
    )
    plot = da.hvplot.image('x', 'y', geo=True)
    assert plot.crs == ccrs.PlateCarree()


@pytest.mark.geo
@skip_windows
def test_projection_string(utm_da, utm_crs):
    plot = utm_da.hvplot.image('x', 'y', crs=utm_crs, projection='Robinson')
    assert _projection_name(plot) == 'robin'


@pytest.mark.geo
@skip_windows
def test_projection_string_google_mercator(utm_da, utm_crs):
    plot = utm_da.hvplot.image('x', 'y', crs=utm_crs, projection='GOOGLE_MERCATOR')
    assert _projection_name(plot) == 'merc'


@pytest.mark.geo
@skip_windows
def test_projection_invalid_string_error(utm_da):
    with pytest.raises(ValueError, match='Projection must be defined'):
        utm_da.hvplot.image('x', 'y', projection='foo')


@pytest.mark.geo
@skip_windows
def test_projection_with_tiles_error(utm_da, utm_crs):
    with pytest.raises(ValueError, match='Tiles can only be used with output projection'):
        utm_da.hvplot.image('x', 'y', crs=utm_crs, projection='Robinson', tiles=True)


@pytest.mark.geo
@skip_windows
def test_geo_overlay_tiles_renders(hvplot_pandas):
    # Regression test for https://github.com/holoviz/hvplot/issues/1090
    df = pd.DataFrame({'lon': [0, 10], 'lat': [40, 50], 'v': [0, 1]})

    plot1 = df.hvplot.points(x='lon', y='lat', s=200, c='y', geo=True, tiles='CartoLight')
    plot2 = df.hvplot.points(x='lon', y='lat', c='v', geo=True)

    # This should work without erroring
    hv.renderer('bokeh').get_plot(plot1 * plot2)


@pytest.mark.geo
@skip_windows
@requires('datashader')
@pytest.mark.slow
def test_project_with_rasterize(hvplot_xarray):
    import cartopy.crs as ccrs
    import geoviews as gv
    from holoviews.operation.datashader import rasterize

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
def test_coastline(hvplot_pandas, simple_df):
    import geoviews as gv

    plot = simple_df.hvplot.points('x', 'y', geo=True, coastline=True)
    assert len(plot) == 2
    assert isinstance(plot.get(1), gv.Feature)


@pytest.mark.geo
def test_coastline_sets_geo_by_default(hvplot_pandas, simple_df):
    import cartopy.crs as ccrs
    import geoviews as gv

    plot = simple_df.hvplot.points('x', 'y', coastline=True)
    assert len(plot) == 2
    assert isinstance(plot.get(0), gv.Points)
    assert plot.get(0).crs == ccrs.PlateCarree()
    assert isinstance(plot.get(1), gv.Feature)


@pytest.mark.geo
def test_coastline_scale(hvplot_pandas, simple_df):
    plot = simple_df.hvplot.points('x', 'y', geo=True, coastline='50m')
    opts = plot.get(1).opts.get('plot')
    assert opts.kwargs['scale'] == '50m'


@pytest.mark.geo
def test_features_overlaid_and_underlaid(hvplot_pandas, simple_df):
    # land should be under, borders should be over
    plot = simple_df.hvplot.points('x', 'y', features=['land', 'borders'])
    assert plot.get(0).group == 'Land'
    assert plot.get(2).group == 'Borders'


@pytest.mark.geo
def test_global_extent(hvplot_pandas, simple_df):
    import geoviews as gv

    # Also makes the plot geographic.
    plot = simple_df.hvplot.points('x', 'y', global_extent=True)
    assert isinstance(plot, gv.Points)
    opts = hv.Store.lookup_options('bokeh', plot, 'plot')
    assert opts.kwargs['global_extent'] is True


@pytest.mark.geo
def test_global_extent_default(hvplot_pandas, simple_df):
    plot = simple_df.hvplot.points('x', 'y', geo=True)
    opts = hv.Store.lookup_options('bokeh', plot, 'plot')
    assert not opts.kwargs.get('global_extent')


@pytest.mark.geo
def test_tiles(hvplot_pandas, simple_df):
    plot = simple_df.hvplot.points('x', 'y', geo=False, tiles=True)
    assert len(plot) == 2
    assert isinstance(plot.get(0), hv.Tiles)
    assert 'openstreetmap' in plot.get(0).data


@pytest.mark.geo
def test_tiles_geo(hvplot_pandas, simple_df):
    import geoviews as gv

    plot = simple_df.hvplot.points('x', 'y', geo=True, tiles=True)
    assert len(plot) == 2
    assert isinstance(plot.get(0), gv.element.WMTS)
    assert 'openstreetmap' in plot.get(0).data


@pytest.mark.geo
def test_tiles_opts(hvplot_pandas, simple_df):
    plot = simple_df.hvplot.points('x', 'y', geo=False, tiles=True, tiles_opts={'alpha': 0.5})
    assert len(plot) == 2
    tiles = plot.get(0)
    assert isinstance(tiles, hv.Tiles)
    assert 'openstreetmap' in tiles.data
    assert tiles.opts['alpha'] == 0.5


@pytest.mark.geo
def test_tiles_opts_geo(hvplot_pandas, simple_df):
    import geoviews as gv

    plot = simple_df.hvplot.points('x', 'y', geo=True, tiles=True, tiles_opts={'alpha': 0.5})
    assert len(plot) == 2
    tiles = plot.get(0)
    assert isinstance(tiles, gv.element.WMTS)
    assert 'openstreetmap' in tiles.data
    assert tiles.opts['alpha'] == 0.5


@pytest.mark.geo
def test_tiles_name(hvplot_pandas, simple_df):
    plot = simple_df.hvplot.points('x', 'y', geo=False, tiles='ESRI')
    assert len(plot) == 2
    assert isinstance(plot.get(0), hv.Tiles)
    assert 'ArcGIS' in plot.get(0).data


@pytest.mark.geo
def test_tiles_name_geo(hvplot_pandas, simple_df):
    import geoviews as gv

    plot = simple_df.hvplot.points('x', 'y', geo=True, tiles='ESRI')
    assert len(plot) == 2
    assert isinstance(plot.get(0), gv.element.WMTS)
    assert 'ArcGIS' in plot.get(0).data


@pytest.mark.geo
def test_tiles_holoviews_class(hvplot_pandas, simple_df):
    plot = simple_df.hvplot.points('x', 'y', geo=False, tiles=hv.element.tiles.EsriImagery)
    assert len(plot) == 2
    assert isinstance(plot.get(0), hv.Tiles)
    assert 'ArcGIS' in plot.get(0).data


@pytest.mark.geo
def test_tiles_holoviews_object(hvplot_pandas, simple_df):
    plot = simple_df.hvplot.points('x', 'y', geo=False, tiles=hv.element.tiles.EsriImagery())
    assert len(plot) == 2
    assert isinstance(plot.get(0), hv.Tiles)
    assert 'ArcGIS' in plot.get(0).data


@pytest.mark.geo
def test_tiles_holoviews_object_geo(hvplot_pandas, simple_df):
    plot = simple_df.hvplot.points('x', 'y', geo=True, tiles=hv.element.tiles.EsriImagery())
    assert len(plot) == 2
    assert isinstance(plot.get(0), hv.Tiles)
    assert 'ArcGIS' in plot.get(0).data


@pytest.mark.geo
def test_tiles_geoviews_object_geo(hvplot_pandas, simple_df):
    import geoviews as gv

    plot = simple_df.hvplot.points('x', 'y', geo=True, tiles=gv.tile_sources.EsriImagery)
    assert len(plot) == 2
    assert isinstance(plot.get(0), gv.element.WMTS)
    assert 'ArcGIS' in plot.get(0).data


@pytest.mark.geo
def test_tiles_xyzservices_geo(hvplot_pandas, simple_df):
    xyzservices = pytest.importorskip('xyzservices')
    import geoviews as gv

    plot = simple_df.hvplot.points(
        'x', 'y', geo=True, tiles=xyzservices.providers.Esri.WorldImagery
    )
    assert len(plot) == 2
    assert isinstance(plot.get(0), gv.element.WMTS)
    assert isinstance(plot.get(0).data, xyzservices.TileProvider)


@pytest.mark.geo
def test_geo_hexbin(hvplot_pandas, simple_df):
    import cartopy.crs as ccrs

    hextiles = simple_df.hvplot.hexbin('x', 'y', geo=True)
    assert hextiles.crs == ccrs.PlateCarree()


@pytest.mark.geo
def test_geo_points(hvplot_pandas, simple_df):
    import cartopy.crs as ccrs

    points = simple_df.hvplot.points('x', 'y', geo=True)
    assert points.crs == ccrs.PlateCarree()


@pytest.mark.geo
def test_geo_points_c_column_named_like_a_color(hvplot_pandas, simple_df):
    df = simple_df.assign(red=np.random.choice(['a', 'b'], len(simple_df)))
    plot = df.hvplot.points('x', 'y', c='red', geo=True)
    opts = hv.Store.lookup_options('bokeh', plot, 'style')
    assert isinstance(opts.kwargs['color'], hv.dim)
    assert opts.kwargs['color'].dimension.name == 'red'


@pytest.mark.geo
def test_geo_default_data_aspect(hvplot_pandas, simple_df):
    points = simple_df.hvplot.points('x', 'y', geo=True)
    opts = hv.Store.lookup_options('bokeh', points, 'plot').kwargs
    assert opts.get('data_aspect') == 1
    assert opts.get('width') is None


@pytest.mark.geo
# bokeh warns (expected) when data_aspect and width are both set.
@pytest.mark.usefixtures('disable_param_warnings_as_exceptions')
def test_geo_data_aspect_and_width(hvplot_pandas, simple_df):
    points = simple_df.hvplot.points('x', 'y', geo=True, width=200)
    opts = hv.Store.lookup_options('bokeh', points, 'plot').kwargs
    assert opts.get('data_aspect') == 1
    assert opts.get('width') == 200
    assert opts.get('height') is None


@pytest.mark.geo
@pytest.mark.usefixtures('disable_param_warnings_as_exceptions')
def test_geo_unsupported_kind_warning(hvplot_pandas, simple_df, caplog):
    plot = simple_df.hvplot.line('x', 'y', geo=True)
    assert isinstance(plot, hv.Curve)
    assert "geo option cannot be used with kind='line'" in caplog.text


@pytest.mark.geo
def test_features_dict_scale(hvplot_pandas, simple_df):
    plot = simple_df.hvplot.points('x', 'y', features={'land': '110m', 'coastline': '50m'})
    scales = [hv.Store.lookup_options('bokeh', el, 'plot').kwargs.get('scale') for el in plot]
    # land is underlaid, coastline overlaid
    assert scales == ['110m', None, '50m']


@pytest.mark.geo
@pytest.mark.usefixtures('disable_param_warnings_as_exceptions')
def test_features_invalid_scale_warning(hvplot_pandas, simple_df, caplog):
    plot = simple_df.hvplot.points('x', 'y', features={'land': '5m'})
    assert len(plot) == 2
    assert 'Feature scale of 5m not recognized' in caplog.text


@pytest.mark.geo
@pytest.mark.xfail(
    strict=True, reason='BUG: invalid feature name raises AttributeError, not the ValueError'
)
def test_features_invalid_name_error(hvplot_pandas, simple_df):
    with pytest.raises(ValueError, match='not recognized'):
        simple_df.hvplot.points('x', 'y', features=['foo'])


@pytest.mark.geo
@pytest.mark.usefixtures('disable_param_warnings_as_exceptions')
@pytest.mark.xfail(strict=True, reason='BUG: the coastline scale warning is missing its f prefix')
def test_coastline_invalid_scale_warning(hvplot_pandas, simple_df, caplog):
    simple_df.hvplot.points('x', 'y', coastline='5m')
    assert 'coastline scale of 5m not recognized' in caplog.text


@pytest.mark.geo
def test_project_without_resampling(hvplot_pandas, lat_lon_df):
    import cartopy.crs as ccrs

    plot = lat_lon_df.hvplot.points('lon', 'lat', project=True, projection=ccrs.GOOGLE_MERCATOR)
    lon, lat = lon_lat_to_easting_northing(lat_lon_df['lon'], lat_lon_df['lat'])
    np.testing.assert_allclose(plot.data['lon'], lon, rtol=1e-6)
    np.testing.assert_allclose(plot.data['lat'], lat, rtol=1e-6)


@pytest.mark.geo
def test_projection_without_project_keeps_data(hvplot_pandas, lat_lon_df):
    import cartopy.crs as ccrs

    plot = lat_lon_df.hvplot.points('lon', 'lat', geo=True, projection=ccrs.GOOGLE_MERCATOR)
    pd.testing.assert_frame_equal(plot.data, lat_lon_df)


@pytest.mark.geo
@skip_windows
def test_geo_xlim_reprojected_with_tiles(hvplot_pandas, lat_lon_df):
    plot = lat_lon_df.hvplot.points('lon', 'lat', geo=True, tiles=True, xlim=(-130, -70))
    xlim = hv.Store.lookup_options('bokeh', plot.get(1), 'plot').kwargs['xlim']
    np.testing.assert_allclose(xlim, (-14471533.8, -7792364.4))


@pytest.mark.geo
@skip_windows
@pytest.mark.parametrize('backend', ['bokeh', 'matplotlib'], indirect=True)
def test_projection_backends(hvplot_pandas, backend, simple_df):
    plot = simple_df.hvplot.points('x', 'y', projection='Robinson')
    proj = hv.Store.lookup_options(backend, plot, 'plot').kwargs['projection']
    assert proj.proj4_params['proj'] == 'robin'


@pytest.mark.geo
@pytest.mark.parametrize('backend', ['bokeh', 'matplotlib'], indirect=True)
def test_global_extent_backends(hvplot_pandas, backend, simple_df):
    plot = simple_df.hvplot.points('x', 'y', global_extent=True)
    assert hv.Store.lookup_options(backend, plot, 'plot').kwargs['global_extent'] is True


@pytest.mark.geo
@pytest.mark.parametrize('backend', ['bokeh', 'matplotlib'], indirect=True)
def test_coastline_scale_backends(hvplot_pandas, backend, simple_df):
    plot = simple_df.hvplot.points('x', 'y', coastline='50m')
    assert hv.Store.lookup_options(backend, plot.get(1), 'plot').kwargs['scale'] == '50m'


@pytest.mark.geo
@pytest.mark.parametrize('backend', ['bokeh', 'matplotlib'], indirect=True)
def test_tiles_backends(hvplot_pandas, backend, simple_df):
    import geoviews as gv

    plot = simple_df.hvplot.points('x', 'y', geo=True, tiles=True)
    assert isinstance(plot.get(0), gv.element.WMTS)


# Without GeoViews


@pytest.fixture
def without_geoviews(block_import, hvplot_pandas):
    block_import('geoviews')


@pytest.fixture
def lat_lon_df():
    return pd.DataFrame({'lon': [-120.0, -100.0, -80.0], 'lat': [30.0, 35.0, 40.0]})


@pytest.fixture
def mercator_df():
    x_merc, y_merc = lon_lat_to_easting_northing(
        np.array([-120.0, -100.0, -80.0]), np.array([30.0, 35.0, 40.0])
    )
    return pd.DataFrame({'x': x_merc, 'y': y_merc})


def test_tiles_without_geoviews(without_geoviews, simple_df):
    plot = simple_df.hvplot.points('x', 'y', tiles=True)
    assert len(plot) == 2
    assert isinstance(plot.get(0), hv.Tiles)
    assert 'openstreetmap' in plot.get(0).data
    assert 'x_' in plot.get(1).data
    assert 'y_' in plot.get(1).data
    bk_plot = bk_renderer.get_plot(plot)
    assert bk_plot.projection == 'mercator'


def test_projection_false_disables_tile_projection(without_geoviews, lat_lon_df):
    plot = lat_lon_df.hvplot.points('lon', 'lat', tiles=True, projection=False)
    assert list(plot.get(1).data.columns) == ['lon', 'lat']


def test_tiles_name_without_geoviews(without_geoviews, simple_df):
    plot = simple_df.hvplot.points('x', 'y', tiles='ESRI')
    assert len(plot) == 2
    assert isinstance(plot.get(0), hv.Tiles)
    assert 'ArcGIS' in plot.get(0).data
    assert 'x_' in plot.get(1).data
    assert 'y_' in plot.get(1).data
    bk_plot = bk_renderer.get_plot(plot)
    assert bk_plot.projection == 'mercator'


def test_tiles_holoviews_class_without_geoviews(without_geoviews, simple_df):
    plot = simple_df.hvplot.points('x', 'y', tiles=hv.element.tiles.EsriImagery)
    assert len(plot) == 2
    assert isinstance(plot.get(0), hv.Tiles)
    assert 'ArcGIS' in plot.get(0).data
    bk_plot = bk_renderer.get_plot(plot)
    assert bk_plot.projection == 'mercator'


def test_tiles_holoviews_object_without_geoviews(without_geoviews, simple_df):
    plot = simple_df.hvplot.points('x', 'y', tiles=hv.element.tiles.EsriImagery())
    assert len(plot) == 2
    assert isinstance(plot.get(0), hv.Tiles)
    assert 'ArcGIS' in plot.get(0).data
    assert 'x_' in plot.get(1).data
    assert 'y_' in plot.get(1).data
    bk_plot = bk_renderer.get_plot(plot)
    assert bk_plot.projection == 'mercator'


def test_tiles_xyzservices_without_geoviews(without_geoviews, simple_df):
    xyzservices = pytest.importorskip('xyzservices')
    plot = simple_df.hvplot.points('x', 'y', tiles=xyzservices.providers.Esri.WorldImagery)
    assert 'x_' in plot.get(1).data
    assert 'y_' in plot.get(1).data
    assert len(plot) == 2
    assert isinstance(plot.get(0), hv.Tiles)
    assert isinstance(plot.get(0).data, xyzservices.TileProvider)
    bk_plot = bk_renderer.get_plot(plot)
    assert bk_plot.projection == 'mercator'


def test_tiles_dask_without_geoviews(without_geoviews, simple_df):
    dd = pytest.importorskip('dask.dataframe')
    import hvplot.dask  # noqa: F401

    plot = dd.from_pandas(simple_df, npartitions=2).hvplot.points('x', 'y', tiles=True)
    assert 'x_' not in plot.get(1).data
    assert 'y_' not in plot.get(1).data
    assert len(plot) == 2
    assert isinstance(plot.get(0), hv.Tiles)
    bk_plot = bk_renderer.get_plot(plot)
    assert bk_plot.projection == 'mercator'


def test_tiles_spatialpandas_without_crs(without_geoviews):
    spd = pytest.importorskip('spatialpandas')
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


def test_tiles_xarray_without_geoviews(without_geoviews, hvplot_xarray):
    ds = xr.Dataset(
        {
            'temp': (('lon', 'lat'), 15 + 8 * np.random.randn(2, 2)),
            'precip': (('lon', 'lat'), 10 * np.random.rand(2, 2)),
        },
        coords={'lon': [-99.83, -99.32], 'lat': [42.25, 42.21]},
    )
    plot = ds.hvplot('lon', 'lat', tiles=True)
    assert len(plot) == 2
    assert isinstance(plot.get(1), Image)
    assert 'x' in plot.get(1).data
    assert 'y' in plot.get(1).data


def test_xlim_ylim_converted_with_tiles(without_geoviews, lat_lon_df):
    """Test that xlim and ylim are automatically converted to Web Mercator when tiles=True"""
    plot = lat_lon_df.hvplot.points('lon', 'lat', tiles=True, xlim=(-130, -70), ylim=(25, 45))
    points = plot.get(1)

    assert 'x' in points.data.columns
    assert 'y' in points.data.columns

    xlim_expected_0, _ = lon_lat_to_easting_northing(-130, 0)
    xlim_expected_1, _ = lon_lat_to_easting_northing(-70, 0)
    _, ylim_expected_0 = lon_lat_to_easting_northing(0, 25)
    _, ylim_expected_1 = lon_lat_to_easting_northing(0, 45)

    bk_plot = bk_renderer.get_plot(plot)
    assert bk_plot.handles['plot'].x_range.start == xlim_expected_0
    assert bk_plot.handles['plot'].x_range.end == xlim_expected_1
    assert bk_plot.handles['plot'].y_range.start == ylim_expected_0
    assert bk_plot.handles['plot'].y_range.end == ylim_expected_1


def test_xlim_converted_with_tiles(without_geoviews, lat_lon_df):
    """Opt xlim should convert even when ylim is not provided."""
    plot = lat_lon_df.hvplot.points('lon', 'lat', tiles=True, xlim=(-130, -70))
    bk_plot = bk_renderer.get_plot(plot)

    x_start = bk_plot.state.x_range.start
    x_end = bk_plot.state.x_range.end

    np.testing.assert_almost_equal(x_start, -14471533.803125564)
    np.testing.assert_almost_equal(x_end, -7792364.355529151)
    assert x_start < x_end


def test_ylim_converted_with_tiles(without_geoviews, lat_lon_df):
    """Opt ylim should convert even when xlim is not provided."""
    plot = lat_lon_df.hvplot.points('lon', 'lat', tiles=True, ylim=(25, 45))
    bk_plot = bk_renderer.get_plot(plot)

    y_start = bk_plot.state.y_range.start
    y_end = bk_plot.state.y_range.end

    assert y_start > 2_000_000
    assert y_end > 5_000_000
    assert y_start < y_end


def test_xlim_ylim_not_converted_without_tiles(without_geoviews, lat_lon_df):
    """Test that xlim and ylim are NOT converted when tiles=False"""
    plot = lat_lon_df.hvplot.points('lon', 'lat', xlim=(-130, -70), ylim=(25, 45))
    bk_plot = bk_renderer.get_plot(plot)

    assert bk_plot.handles['plot'].x_range.start == -130
    assert bk_plot.handles['plot'].x_range.end == -70
    assert bk_plot.handles['plot'].y_range.start == 25
    assert bk_plot.handles['plot'].y_range.end == 45


def test_xlim_ylim_out_of_bounds_not_converted_with_tiles(without_geoviews, mercator_df):
    """Test that xlim and ylim are NOT converted when values are outside lat/lon bounds"""
    plot = mercator_df.hvplot.points('x', 'y', tiles=True, xlim=(1000, 3000), ylim=(400, 800))
    bk_plot = bk_renderer.get_plot(plot.get(1))

    assert bk_plot.handles['plot'].x_range.start == 1000
    assert bk_plot.handles['plot'].x_range.end == 3000
    assert bk_plot.handles['plot'].y_range.start == 400
    assert bk_plot.handles['plot'].y_range.end == 800


def test_geo_without_geoviews(without_geoviews, simple_df):
    with pytest.raises(ModuleNotFoundError, match='`geoviews` package must be installed'):
        simple_df.hvplot.points('x', 'y', geo=True)


def test_tiles_unknown_without_xyzservices(without_geoviews, simple_df, monkeypatch):
    # hvPlot only uses xyzservices when it is already imported, so it is removed
    # from sys.modules rather than blocked.
    monkeypatch.delitem(sys.modules, 'xyzservices', raising=False)
    with pytest.raises(ValueError, match='not_a_source tiles not recognized'):
        simple_df.hvplot.points('x', 'y', tiles='not_a_source')
    assert 'xyzservices' not in sys.modules
