"""
Tests  utilities to convert data and projections
"""

import sys

import numpy as np
import pandas as pd
import panel as pn
import pytest
import xarray as xr

from hvplot.tests._data import air_temperature
from hvplot.tests._deps import requires
from hvplot.util import (
    _bounds_in_range,
    _convert_col_names_to_str,
    _convert_latlon_to_mercator,
    _convert_limit_to_mercator,
    _generate_unique_name,
    _get_doc_and_signature,
    _is_within_latlon_bounds,
    check_crs,
    import_datashader,
    import_geoviews,
    instantiate_crs_str,
    is_geodataframe,
    is_list_like,
    is_mpl_cmap,
    process_crs,
    process_dynamic_args,
    process_xarray,
    proj_to_cartopy,
)

PROCESS_XARRAY_KWARGS = {
    'value_label': 'value',
    'label': None,
    'gridded': False,
    'persist': False,
    'use_dask': False,
    'groupby': None,
    'y': None,
    'x': None,
    'by': None,
    'other_dims': [],
}


def test_process_1d_xarray_dataarray_with_no_coords():
    da = xr.DataArray(data=[1, 2, 3])

    data, x, y, by, groupby = process_xarray(data=da, **PROCESS_XARRAY_KWARGS)
    assert isinstance(data, pd.DataFrame)
    assert x == 'index'
    assert y == ['value']
    assert not by
    assert not groupby


def test_process_1d_xarray_dataarray_with_coords():
    da = xr.DataArray(data=[1, 2, 3], coords={'day': [5, 6, 7]}, dims=['day'])

    data, x, y, by, groupby = process_xarray(data=da, **PROCESS_XARRAY_KWARGS)
    assert isinstance(data, pd.DataFrame)
    assert x == 'day'
    assert y == ['value']
    assert not by
    assert not groupby


def test_process_1d_xarray_dataarray_with_coords_and_name():
    da = xr.DataArray(data=[1, 2, 3], coords={'day': [5, 6, 7]}, dims=['day'], name='temp')

    data, x, y, by, groupby = process_xarray(data=da, **PROCESS_XARRAY_KWARGS)
    assert isinstance(data, pd.DataFrame)
    assert x == 'day'
    assert y == ['temp']
    assert not by
    assert not groupby


def test_process_2d_xarray_dataarray_with_no_coords(rng):
    da = xr.DataArray(rng.standard_normal((4, 5)))

    data, x, y, by, groupby = process_xarray(data=da, **PROCESS_XARRAY_KWARGS)
    assert isinstance(data, pd.DataFrame)
    assert x == 'index'
    assert y == ['value']
    assert not by
    assert not groupby


def test_process_2d_xarray_dataarray_with_no_coords_as_gridded(rng):
    da = xr.DataArray(rng.standard_normal((4, 5)))

    kwargs = dict(PROCESS_XARRAY_KWARGS, gridded=True)

    data, x, y, by, groupby = process_xarray(data=da, **kwargs)
    assert isinstance(data, xr.Dataset)
    assert list(data.data_vars.keys()) == ['value']
    assert x == 'dim_1'
    assert y == 'dim_0'
    assert not by
    assert not groupby


def test_process_2d_xarray_dataarray_with_coords_as_gridded(rng):
    da = xr.DataArray(
        data=rng.standard_normal((4, 5)), coords={'y': [3, 4, 5, 6, 7]}, dims=['x', 'y']
    )

    kwargs = dict(PROCESS_XARRAY_KWARGS, gridded=True)

    data, x, y, by, groupby = process_xarray(data=da, **kwargs)
    assert isinstance(data, xr.Dataset)
    assert list(data.data_vars.keys()) == ['value']
    assert x == 'y'
    assert y == 'x'
    assert not by
    assert not groupby


def test_process_3d_xarray_dataset_with_coords():
    data, x, y, by, groupby = process_xarray(data=air_temperature(), **PROCESS_XARRAY_KWARGS)
    assert isinstance(data, pd.DataFrame)
    assert x == 'time'
    assert y == ['air']
    assert not by
    assert groupby == ['lon', 'lat']


def test_process_3d_xarray_dataset_with_coords_as_gridded():
    kwargs = dict(PROCESS_XARRAY_KWARGS, gridded=True, x='lon', y='lat')

    data, x, y, by, groupby = process_xarray(data=air_temperature(), **kwargs)
    assert isinstance(data, xr.Dataset)
    assert list(data.data_vars.keys()) == ['air']
    assert x == 'lon'
    assert y == 'lat'
    assert by is None
    assert groupby == ['time']


def test_process_3d_xarray_dataset_with_coords_as_gridded_uses_axis_to_get_defaults():
    kwargs = dict(PROCESS_XARRAY_KWARGS, gridded=True)

    data, x, y, by, groupby = process_xarray(data=air_temperature(), **kwargs)
    assert isinstance(data, xr.Dataset)
    assert list(data.data_vars.keys()) == ['air']
    assert x == 'lon'
    assert y == 'lat'
    assert not by
    assert groupby == ['time']


def test_process_xarray_dataset_with_by_as_derived_datetime():
    data = air_temperature().mean(dim=['lat', 'lon'])
    kwargs = dict(PROCESS_XARRAY_KWARGS, gridded=False, y='air', by=['time.hour'])

    data, x, y, by, groupby = process_xarray(data=data, **kwargs)
    assert isinstance(data, pd.DataFrame)
    assert x == 'time'
    assert y == 'air'
    assert by == ['time.hour']
    assert not groupby


def test_process_xarray_dataset_with_x_as_derived_datetime():
    data = air_temperature().mean(dim=['lat', 'lon'])
    kwargs = dict(PROCESS_XARRAY_KWARGS, gridded=False, y='air', x='time.dayofyear')

    data, x, y, by, groupby = process_xarray(data=data, **kwargs)
    assert isinstance(data, pd.DataFrame)
    assert x == 'time.dayofyear'
    assert y == 'air'
    assert not by
    assert not groupby


def test_process_dynamic_args_dynamic_and_static():
    x = 'sepal_width'
    y = pn.widgets.Select(
        label='y', value='sepal_length', options=['sepal_length', 'petal_length']
    )
    kind = pn.widgets.Select(label='kind', value='scatter', options=['bivariate', 'scatter'])

    dynamic, arg_deps, _arg_names = process_dynamic_args(x, y, kind)
    assert 'x' not in dynamic
    assert 'y' in dynamic
    assert arg_deps == []


def test_process_dynamic_args_dynamic_kwds():
    x = 'sepal_length'
    y = 'sepal_width'
    kind = 'scatter'
    color = pn.widgets.ColorPicker(value='#ff0000')

    dynamic, arg_deps, _arg_names = process_dynamic_args(x, y, kind, c=color)
    assert 'x' not in dynamic
    assert 'c' in dynamic
    assert arg_deps == []


def test_process_dynamic_args_fn_kwds():
    x = 'sepal_length'
    y = 'sepal_width'
    kind = 'scatter'
    by_species = pn.widgets.Checkbox(label='By species')
    color = pn.widgets.ColorPicker(value='#ff0000')

    @pn.depends(by_species.param.value, color.param.value)
    def by_species_fn(by_species, color):
        return 'species' if by_species else color

    dynamic, arg_deps, arg_names = process_dynamic_args(x, y, kind, c=by_species_fn)
    assert dynamic == {}
    assert arg_names == ['c', 'c']
    assert len(arg_deps) == 2


@requires('pyproj')
def test_check_crs():
    p = check_crs('epsg:26915')
    assert p.srs == '+proj=utm +zone=15 +datum=NAD83 +units=m +no_defs'
    p = check_crs('wrong')
    assert p is None


@pytest.mark.parametrize(
    'input',
    [
        'epsg:26911',
        'PlateCarree',
        'epsg:6933',
        6933,
        'EPSG: 6933',
    ],
)
@pytest.mark.geo
def test_process_crs(input):
    import cartopy.crs as ccrs

    crs = process_crs(input)
    assert isinstance(crs, ccrs.CRS)


@pytest.mark.geo
def test_process_crs_pyproj_crs():
    import cartopy.crs as ccrs
    import pyproj

    crs = process_crs(pyproj.CRS.from_epsg(4326))
    assert isinstance(crs, ccrs.PlateCarree)


@pytest.mark.geo
def test_process_crs_pyproj_proj():
    import cartopy.crs as ccrs
    import pyproj

    crs = process_crs(pyproj.Proj(init='epsg:4326'))
    assert isinstance(crs, ccrs.PlateCarree)


@pytest.mark.parametrize(
    'input',
    [
        '4326',
        4326,
        'epsg:4326',
        'EPSG: 4326',
        'epsg:4326',
        # Created with pyproj.CRS("EPSG:4326").to_wkt()
        'GEOGCRS["WGS 84",ENSEMBLE["World Geodetic System 1984 ensemble",MEMBER["World Geodetic System 1984 (Transit)"],MEMBER["World Geodetic System 1984 (G730)"],MEMBER["World Geodetic System 1984 (G873)"],MEMBER["World Geodetic System 1984 (G1150)"],MEMBER["World Geodetic System 1984 (G1674)"],MEMBER["World Geodetic System 1984 (G1762)"],MEMBER["World Geodetic System 1984 (G2139)"],ELLIPSOID["WGS 84",6378137,298.257223563,LENGTHUNIT["metre",1]],ENSEMBLEACCURACY[2.0]],PRIMEM["Greenwich",0,ANGLEUNIT["degree",0.0174532925199433]],CS[ellipsoidal,2],AXIS["geodetic latitude (Lat)",north,ORDER[1],ANGLEUNIT["degree",0.0174532925199433]],AXIS["geodetic longitude (Lon)",east,ORDER[2],ANGLEUNIT["degree",0.0174532925199433]],USAGE[SCOPE["Horizontal component of 3D system."],AREA["World."],BBOX[-90,-180,90,180]],ID["EPSG",4326]]',  # noqa: E501
    ],
    ids=lambda x: str(x)[:20],
)
@pytest.mark.geo
def test_process_crs_platecarree(input):
    import cartopy.crs as ccrs

    crs = process_crs(input)
    assert isinstance(crs, ccrs.PlateCarree)


@pytest.mark.parametrize(
    'input',
    [
        '3857',
        3857,
        'epsg:3857',
        'EPSG: 3857',
        'epsg:3857',
        'PROJCS["WGS 84 / Pseudo-Mercator",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Mercator_1SP"],PARAMETER["central_meridian",0],PARAMETER["scale_factor",1],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],EXTENSION["PROJ4","+proj=merc +a=6378137 +b=6378137 +lat_ts=0 +lon_0=0 +x_0=0 +y_0=0 +k=1 +units=m +nadgrids=@null +wktext +no_defs"],AUTHORITY["EPSG","3857"]]',  # noqa: E501
        # Created with pyproj.CRS("EPSG:3857").to_wkt()
        'PROJCRS["WGS 84 / Pseudo-Mercator",BASEGEOGCRS["WGS 84",ENSEMBLE["World Geodetic System 1984 ensemble",MEMBER["World Geodetic System 1984 (Transit)"],MEMBER["World Geodetic System 1984 (G730)"],MEMBER["World Geodetic System 1984 (G873)"],MEMBER["World Geodetic System 1984 (G1150)"],MEMBER["World Geodetic System 1984 (G1674)"],MEMBER["World Geodetic System 1984 (G1762)"],MEMBER["World Geodetic System 1984 (G2139)"],ELLIPSOID["WGS 84",6378137,298.257223563,LENGTHUNIT["metre",1]],ENSEMBLEACCURACY[2.0]],PRIMEM["Greenwich",0,ANGLEUNIT["degree",0.0174532925199433]],ID["EPSG",4326]],CONVERSION["Popular Visualisation Pseudo-Mercator",METHOD["Popular Visualisation Pseudo Mercator",ID["EPSG",1024]],PARAMETER["Latitude of natural origin",0,ANGLEUNIT["degree",0.0174532925199433],ID["EPSG",8801]],PARAMETER["Longitude of natural origin",0,ANGLEUNIT["degree",0.0174532925199433],ID["EPSG",8802]],PARAMETER["False easting",0,LENGTHUNIT["metre",1],ID["EPSG",8806]],PARAMETER["False northing",0,LENGTHUNIT["metre",1],ID["EPSG",8807]]],CS[Cartesian,2],AXIS["easting (X)",east,ORDER[1],LENGTHUNIT["metre",1]],AXIS["northing (Y)",north,ORDER[2],LENGTHUNIT["metre",1]],USAGE[SCOPE["Web mapping and visualisation."],AREA["World between 85.06°S and 85.06°N."],BBOX[-85.06,-180,85.06,180]],ID["EPSG",3857]]',  # noqa: E501
    ],
    ids=lambda x: str(x)[:20],
)
@pytest.mark.geo
def test_process_crs_mercator(input):
    import cartopy.crs as ccrs

    crs = process_crs(input)
    assert isinstance(crs, ccrs.Mercator)


@pytest.mark.geo
@requires('rasterio')
def test_process_crs_rasterio():
    import cartopy.crs as ccrs
    import rasterio.crs as rcrs

    input = rcrs.CRS.from_epsg(4326).to_wkt()
    crs = process_crs(input)
    assert isinstance(crs, ccrs.CRS)


@pytest.mark.geo
def test_process_crs_raises_error():
    with pytest.raises(ValueError, match='must be defined as a EPSG code, proj4 string'):
        process_crs(43823)


def test_is_list_like():
    assert not is_list_like(0)
    assert not is_list_like('string')
    assert not is_list_like(np.array('a'))
    assert is_list_like(['a', 'b'])
    assert is_list_like(('a', 'b'))
    assert is_list_like({'a', 'b'})
    assert is_list_like(pd.Series(['a', 'b']))
    assert is_list_like(pd.Index(['a', 'b']))
    assert is_list_like(np.array(['a', 'b']))


@pytest.mark.parametrize('name,uname', [('a', 'a'), ('b', 'b_'), ('c_', 'c__')])
def test_generate_unique_name(name, uname):
    assert _generate_unique_name(name, ['b', 'c_']) == uname


def test_convert_col_names_to_str():
    df = pd.DataFrame(np.random.random((10, 2)))
    assert all(not isinstance(col, str) for col in df.columns)
    df = _convert_col_names_to_str(df)
    assert all(isinstance(col, str) for col in df.columns)


@requires('cartopy')
def test_instantiate_crs_str():
    import cartopy.crs as ccrs

    assert isinstance(instantiate_crs_str('PlateCarree'), ccrs.PlateCarree)


@requires('cartopy')
def test_instantiate_crs_google_mercator():
    import cartopy.crs as ccrs

    assert instantiate_crs_str('GOOGLE_MERCATOR') == ccrs.GOOGLE_MERCATOR
    assert instantiate_crs_str('google_mercator') == ccrs.GOOGLE_MERCATOR


@requires('cartopy')
def test_instantiate_crs_str_kwargs():
    import cartopy.crs as ccrs

    crs = instantiate_crs_str('PlateCarree', globe=ccrs.Globe(datum='WGS84'))
    assert isinstance(crs, ccrs.PlateCarree)
    assert isinstance(crs.globe, ccrs.Globe)
    assert crs.globe.datum == 'WGS84'


@requires('spatialpandas', 'dask')
def test_is_geodataframe_spatialpandas_dask():
    import dask.dataframe as dd
    import spatialpandas as spd

    square = spd.geometry.Polygon([(0.0, 0), (0, 1), (1, 1), (1, 0)])
    sdf = spd.GeoDataFrame({'geometry': spd.GeoSeries([square, square]), 'name': ['A', 'B']})
    sddf = dd.from_pandas(sdf, npartitions=2)
    assert isinstance(sddf, spd.dask.DaskGeoDataFrame)
    assert is_geodataframe(sddf)


def test_is_geodataframe_classic_dataframe():
    df = pd.DataFrame({'geometry': [None, None], 'name': ['A', 'B']})
    assert not is_geodataframe(df)


@pytest.mark.geo
def test_geoviews_is_available():
    assert import_geoviews()


class TestIsWithinLatlonBounds:
    """Test is_within_latlon_bounds function."""

    def test_valid_bounds_dataframe(self):
        """Return True for valid lat/lon bounds in DataFrame."""
        df = pd.DataFrame({'lon': [-180, 0, 180], 'lat': [-90, 0, 90]})
        assert _is_within_latlon_bounds(df, 'lon', 'lat')

    def test_valid_bounds_dict(self):
        """Return True for valid lat/lon bounds in dict."""
        data = {'lon': np.array([0, 90]), 'lat': np.array([45, 60])}
        assert _is_within_latlon_bounds(data, 'lon', 'lat')

    def test_lon_extended_range(self):
        """Return True when lon within -180 to 360 range."""
        df = pd.DataFrame({'lon': [0, 180, 360], 'lat': [0, 45, 90]})
        assert _is_within_latlon_bounds(df, 'lon', 'lat')

    def test_lon_boundary_values(self):
        """Return True at exact boundary values."""
        df = pd.DataFrame({'lon': [-180, 360], 'lat': [-90, 90]})
        assert _is_within_latlon_bounds(df, 'lon', 'lat')

    def test_lon_below_min_bound(self):
        """Return False when lon min is below -180."""
        df = pd.DataFrame({'lon': [-181, 0, 90], 'lat': [0, 45, 90]})
        assert not _is_within_latlon_bounds(df, 'lon', 'lat')

    def test_lon_above_max_bound(self):
        """Return False when lon max exceeds 360."""
        df = pd.DataFrame({'lon': [-180, 0, 361], 'lat': [0, 45, 90]})
        assert not _is_within_latlon_bounds(df, 'lon', 'lat')

    def test_lat_below_min_bound(self):
        """Return False when lat min is below -90."""
        df = pd.DataFrame({'lon': [-180, 0, 90], 'lat': [-91, 0, 45]})
        assert not _is_within_latlon_bounds(df, 'lon', 'lat')

    def test_lat_above_max_bound(self):
        """Return False when lat max exceeds 90."""
        df = pd.DataFrame({'lon': [-180, 0, 90], 'lat': [-45, 0, 91]})
        assert not _is_within_latlon_bounds(df, 'lon', 'lat')

    def test_missing_column(self):
        """Return False and warn when column doesn't exist."""
        df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
        with pytest.warns(
            UserWarning, match="Could not determine longitude bounds from variable 'lon'"
        ):
            result = _is_within_latlon_bounds(df, 'lon', 'lat')
        assert not result

    def test_non_numeric_values(self):
        """Return False and warn for non-numeric data."""
        df = pd.DataFrame({'lon': ['a', 'b', 'c'], 'lat': [45, 60, 75]})
        with pytest.warns(
            UserWarning, match="Could not determine longitude bounds from variable 'lon'"
        ):
            result = _is_within_latlon_bounds(df, 'lon', 'lat')
        assert not result


class TestBoundsInRange:
    """Test _bounds_in_range helper function."""

    def test_valid_bounds_in_range(self):
        """Return True when both bounds are valid and in range."""
        assert _bounds_in_range(-90, 90, -90, 90)
        assert _bounds_in_range(-180, 360, -180, 360)
        assert _bounds_in_range(0, 45, -180, 360)

    def test_first_bound_out_of_range(self):
        """Return False when first bound exceeds range."""
        assert not _bounds_in_range(-181, 0, -180, 360)

    def test_second_bound_out_of_range(self):
        """Return False when second bound exceeds range."""
        assert not _bounds_in_range(0, 361, -180, 360)

    def test_both_bounds_out_of_range(self):
        """Return False when both bounds exceed range."""
        assert not _bounds_in_range(-200, 400, -180, 360)

    def test_first_bound_nan(self):
        """Return True when first bound is NaN."""
        assert _bounds_in_range(np.nan, 0, -180, 360)

    def test_second_bound_nan(self):
        """Return True when second bound is NaN."""
        assert _bounds_in_range(0, np.nan, -180, 360)


class TestConvertLatlonToMercator:
    """Test convert_latlon_to_mercator function."""

    def test_prime_meridian(self):
        """Convert coordinates at prime meridian and equator."""
        lon = np.array([0])
        lat = np.array([0])
        easting, northing = _convert_latlon_to_mercator(lon, lat)
        np.testing.assert_almost_equal(easting[0], 0, decimal=5)
        np.testing.assert_almost_equal(northing[0], 0, decimal=5)

    def test_multiple_points(self):
        """Convert multiple lat/lon points."""
        lon = np.array([-180, 0, 180])
        lat = np.array([-45, 0, 45])
        easting, northing = _convert_latlon_to_mercator(lon, lat)
        assert len(easting) == 3 and len(northing) == 3

    def test_lon_normalization_180(self):
        """Normalize 180 and -180 to same value."""
        lon1 = np.array([180])
        lon2 = np.array([-180])
        e1, _ = _convert_latlon_to_mercator(lon1, np.array([0]))
        e2, _ = _convert_latlon_to_mercator(lon2, np.array([0]))
        np.testing.assert_almost_equal(e1[0], e2[0], decimal=5)

    def test_lon_normalization_270(self):
        """Normalize 270 to -90."""
        lon1 = np.array([270])
        lon2 = np.array([-90])
        e1, _ = _convert_latlon_to_mercator(lon1, np.array([0]))
        e2, _ = _convert_latlon_to_mercator(lon2, np.array([0]))
        np.testing.assert_almost_equal(e1[0], e2[0], decimal=5)

    def test_returns_tuple(self):
        """Return tuple of easting and northing arrays."""
        result = _convert_latlon_to_mercator(np.array([0, 45, 90]), np.array([0, 30, 60]))
        assert isinstance(result, tuple) and len(result) == 2


class TestConvertLimitToMercator:
    """Test convert_limit_to_mercator function."""

    def test_none_and_empty_limits(self):
        """Return None for None or empty limits."""
        assert _convert_limit_to_mercator(None, is_x_axis=True) is None
        assert _convert_limit_to_mercator((), is_x_axis=True) is None

    def test_valid_x_limits(self):
        """Convert valid x-axis (longitude) limits."""
        result = _convert_limit_to_mercator((-90, 90), is_x_axis=True)
        assert result is not None and isinstance(result, tuple) and len(result) == 2

    def test_valid_y_limits(self):
        """Convert valid y-axis (latitude) limits."""
        result = _convert_limit_to_mercator((-45, 45), is_x_axis=False)
        assert result is not None and isinstance(result, tuple) and len(result) == 2

    def test_out_of_range_x_limits(self):
        """Return original limits when x bounds out of range."""
        limits = (-200, 0)
        result = _convert_limit_to_mercator(limits, is_x_axis=True)
        assert result == limits

    def test_out_of_range_y_limits(self):
        """Return original limits when y bounds out of range."""
        limits = (0, 100)
        result = _convert_limit_to_mercator(limits, is_x_axis=False)
        assert result == limits

    def test_x_limits_with_none(self):
        """Return np.nan limit when x bound is None."""
        limits = (0, None)
        result = _convert_limit_to_mercator(limits, is_x_axis=True)
        assert result[0] == limits[0]
        assert np.isnan(result[1])

    def test_y_limits_with_none(self):
        """Return np.nan limit when y bound is None."""
        limits = (None, 0)
        result = _convert_limit_to_mercator(limits, is_x_axis=False)
        np.testing.assert_almost_equal(result[1], limits[1])
        assert np.isnan(result[0])

    def test_x_limits_with_nan(self):
        """Return original limits when x bound is NaN."""
        limits = (0, np.nan)
        result = _convert_limit_to_mercator(limits, is_x_axis=True)
        assert result[0] == limits[0]
        assert np.isnan(result[1])

    def test_y_limits_with_nan(self):
        """Return original limits when y bound is NaN."""
        limits = (np.nan, 0)
        result = _convert_limit_to_mercator(limits, is_x_axis=False)
        np.testing.assert_almost_equal(result[1], limits[1])
        assert np.isnan(result[0])

    def test_unpacking_error_too_many_values(self):
        """Return original and warn when unpacking too many values."""
        limits = (1, 2, 3)
        with pytest.warns(UserWarning, match='Could not convert limits'):
            result = _convert_limit_to_mercator(limits, is_x_axis=True)
        assert result == limits

    def test_unpacking_error_single_value(self):
        """Return original and warn when unpacking single value."""
        limits = (45,)
        with pytest.warns(UserWarning, match='Could not convert limits'):
            result = _convert_limit_to_mercator(limits, is_x_axis=False)
        assert result == limits

    def test_mercator_y_conversion_changes_values(self):
        """Ensure Mercator conversion changes y-axis limit values."""
        original = (-45, 45)
        result = _convert_limit_to_mercator(original, is_x_axis=False)
        assert result != original and result[0] != original[0]

    def test_mercator_x_conversion_changes_values(self):
        """Ensure Mercator conversion changes x-axis limit values."""
        original = (-90, 90)
        result = _convert_limit_to_mercator(original, is_x_axis=True)
        assert result != original and result[0] != original[0]

    @pytest.mark.parametrize('bounds', [(0, 90), (190, 250), (170, -170), (350, 10)])
    def test_converted_x_limits_ordered(self, bounds):
        """Ensure converted x-axis limits maintain order."""
        result = _convert_limit_to_mercator(bounds, is_x_axis=True)
        assert result[0] < result[1]

    def test_converted_y_limits_ordered(self):
        """Ensure converted y-axis limits maintain order."""
        result = _convert_limit_to_mercator((-45, -10), is_x_axis=False)
        assert result[0] < result[1]


@requires('cartopy', 'pyproj')
@pytest.mark.skipif(sys.platform == 'win32', reason='Skip geo tests on windows for now')
class TestProjToCartopy:
    def test_proj_to_cartopy(self):
        import cartopy.crs as ccrs

        crs = proj_to_cartopy('epsg:26911')

        assert isinstance(crs, ccrs.CRS)

    def test_proj_to_cartopy_wkt_string(self):
        import cartopy.crs as ccrs

        crs = proj_to_cartopy(
            'GEOGCRS["unnamed",BASEGEOGCRS["unknown",DATUM["unknown",ELLIPSOID["WGS 84",6378137,298.257223563,LENGTHUNIT["metre",1,ID["EPSG",9001]]]],PRIMEM["Greenwich",0,ANGLEUNIT["degree",0.0174532925199433],ID["EPSG",8901]]],DERIVINGCONVERSION["unknown",METHOD["PROJ ob_tran o_proj=latlon"],PARAMETER["o_lon_p",0,ANGLEUNIT["degree",0.0174532925199433,ID["EPSG",9122]]],PARAMETER["o_lat_p",37.5,ANGLEUNIT["degree",0.0174532925199433,ID["EPSG",9122]]],PARAMETER["lon_0",357.5,ANGLEUNIT["degree",0.0174532925199433,ID["EPSG",9122]]]],CS[ellipsoidal,2],AXIS["longitude",east,ORDER[1],ANGLEUNIT["degree",0.0174532925199433,ID["EPSG",9122]]],AXIS["latitude",north,ORDER[2],ANGLEUNIT["degree",0.0174532925199433,ID["EPSG",9122]]]]'  # noqa: E501
        )

        assert isinstance(crs, ccrs.RotatedPole)
        assert crs.proj4_params['lon_0'] == 357.5
        assert crs.proj4_params['o_lat_p'] == 37.5

    def test_proj_to_cartopy_albers_equal_area_wkt(self):
        """Test Albers Equal Area projection from WKT string"""
        import cartopy.crs as ccrs

        albers_wkt = 'PROJCS["Projection = Albers Conical Equal Area",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Albers_Conic_Equal_Area"],PARAMETER["latitude_of_center",23],PARAMETER["longitude_of_center",-96],PARAMETER["standard_parallel_1",29.5],PARAMETER["standard_parallel_2",45.5],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH]]'  # noqa: E501

        crs = proj_to_cartopy(albers_wkt)

        assert isinstance(crs, ccrs.AlbersEqualArea)
        assert crs.proj4_params['proj'] == 'aea'
        assert crs.proj4_params['lat_0'] == 23.0
        assert crs.proj4_params['lon_0'] == -96.0
        assert crs.proj4_params['lat_1'] == 29.5
        assert crs.proj4_params['lat_2'] == 45.5

    def test_proj_to_cartopy_albers_equal_area_proj4(self):
        """Test Albers Equal Area projection from PROJ4 string"""
        import cartopy.crs as ccrs

        proj4_string = '+proj=aea +lat_0=23 +lon_0=-96 +lat_1=29.5 +lat_2=45.5 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs'  # noqa: E501

        crs = proj_to_cartopy(proj4_string)

        assert isinstance(crs, ccrs.AlbersEqualArea)

    @pytest.mark.parametrize(
        ('proj4_string', 'expected_class'),
        [
            ('+proj=eqdc +lat_0=40 +lon_0=-96 +lat_1=33 +lat_2=45', 'EquidistantConic'),
            ('+proj=aeqd +lat_0=40 +lon_0=-96', 'AzimuthalEquidistant'),
            ('+proj=gnom +lat_0=40 +lon_0=-96', 'Gnomonic'),
            ('+proj=ortho +lat_0=40 +lon_0=-96', 'Orthographic'),
            ('+proj=robin +lon_0=0', 'Robinson'),
            ('+proj=moll +lon_0=0', 'Mollweide'),
            ('+proj=sinu +lon_0=0', 'Sinusoidal'),
            ('+proj=eck4 +lon_0=0', 'EckertIV'),
            ('+proj=laea +lat_0=40 +lon_0=-96', 'LambertAzimuthalEqualArea'),
            ('+proj=cea +lon_0=0', 'LambertCylindrical'),
            ('+proj=mill +lon_0=0', 'Miller'),
        ],
    )
    def test_proj_to_cartopy_additional_projections(self, proj4_string, expected_class):
        """
        Test that various PROJ.4 projection strings are correctly mapped to their
        expected Cartopy CRS classes by `proj_to_cartopy`.
        """
        import cartopy.crs as ccrs

        crs = proj_to_cartopy(proj4_string)
        assert isinstance(crs, getattr(ccrs, expected_class))

    def test_proj_to_cartopy_geostationary_special_case(self):
        """Test Geostationary projection which requires special parameters"""
        import cartopy.crs as ccrs

        # Geostationary typically requires satellite height
        proj4_string = '+proj=geos +lon_0=0 +h=35786023 +x_0=0 +y_0=0'

        crs = proj_to_cartopy(proj4_string)
        assert isinstance(crs, ccrs.Geostationary)

    def test_proj_to_cartopy_nearsided_perspective(self):
        """Test Near-sided Perspective projection"""
        import cartopy.crs as ccrs

        proj4_string = '+proj=nsper +lat_0=40 +lon_0=-96 +h=10000000'

        crs = proj_to_cartopy(proj4_string)
        assert isinstance(crs, ccrs.NearsidePerspective)


def test_import_datashader_without_datashader(block_import):
    block_import('datashader')
    with pytest.raises(ModuleNotFoundError, match='`datashader` package must be installed'):
        import_datashader()


def test_import_geoviews_without_geoviews(block_import):
    block_import('geoviews')
    with pytest.raises(ModuleNotFoundError, match='`geoviews` package must be installed'):
        import_geoviews()


def test_process_crs_without_geo_dependencies(block_import):
    block_import('cartopy', 'geoviews', 'pyproj')
    with pytest.raises(
        ImportError, match='Geographic projection support requires: cartopy, geoviews, pyproj'
    ):
        process_crs('EPSG:4326')


# is_mpl_cmap, is_geodataframe and DaskInteractive.applies check `sys.modules` to avoid
# importing the library: without it installed it's never imported, so the tests remove
# it from `sys.modules` (block_import would make it look imported).


def test_is_mpl_cmap():
    from matplotlib.colors import LinearSegmentedColormap

    cmap = LinearSegmentedColormap.from_list('test', ['red', 'blue'])
    assert is_mpl_cmap(cmap)
    assert not is_mpl_cmap('viridis')


def test_is_mpl_cmap_without_matplotlib(monkeypatch):
    monkeypatch.delitem(sys.modules, 'matplotlib', raising=False)
    assert not is_mpl_cmap('viridis')
    assert 'matplotlib' not in sys.modules


@requires('geopandas')
def test_is_geodataframe_without_spatialpandas(monkeypatch):
    import geopandas as gpd
    from shapely.geometry import Point

    monkeypatch.delitem(sys.modules, 'spatialpandas', raising=False)
    assert is_geodataframe(gpd.GeoDataFrame({'geometry': [Point(0, 0)]}))
    assert not is_geodataframe(pd.DataFrame({'geometry': [None]}))
    assert 'spatialpandas' not in sys.modules


def test_get_doc_and_signature_without_datashader_and_geoviews(block_import):
    from hvplot.plotting.core import hvPlot

    block_import('datashader', 'geoviews')
    doc, signature = _get_doc_and_signature(hvPlot, 'points')
    assert 'rasterize' not in signature.parameters
    assert 'geo' not in signature.parameters
    assert 'Resampling Options' not in doc
    assert 'Geographic Options' not in doc


@requires('datashader', 'geoviews')
def test_get_doc_and_signature_with_datashader_and_geoviews():
    from hvplot.plotting.core import hvPlot

    doc, signature = _get_doc_and_signature(hvPlot, 'points')
    assert 'rasterize' in signature.parameters
    assert 'geo' in signature.parameters
    assert 'Resampling Options' in doc
    assert 'Geographic Options' in doc
