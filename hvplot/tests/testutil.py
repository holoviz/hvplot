"""
Tests  utilities to convert data and projections
"""

import numpy as np
import pandas as pd
import panel as pn
import pytest

try:
    import dask.dataframe as dd
    import spatialpandas as spd
except ImportError:
    spd = None
    dd = None

from unittest import TestCase, SkipTest

from hvplot.util import (
    check_crs,
    import_geoviews,
    is_list_like,
    process_crs,
    process_xarray,
    _convert_col_names_to_str,
    instantiate_crs_str,
    is_geodataframe,
)


class TestProcessXarray(TestCase):
    def setUp(self):
        try:
            import xarray as xr
        except ImportError:
            raise SkipTest('xarray not available')
        self.default_kwargs = {
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
        self.ds = xr.tutorial.open_dataset('air_temperature')

    def test_process_1d_xarray_dataarray_with_no_coords(self):
        import xarray as xr

        da = xr.DataArray(data=[1, 2, 3])

        data, x, y, by, groupby = process_xarray(data=da, **self.default_kwargs)
        assert isinstance(data, pd.DataFrame)
        assert x == 'index'
        assert y == ['value']
        assert not by
        assert not groupby

    def test_process_1d_xarray_dataarray_with_coords(self):
        import xarray as xr

        da = xr.DataArray(data=[1, 2, 3], coords={'day': [5, 6, 7]}, dims=['day'])

        data, x, y, by, groupby = process_xarray(data=da, **self.default_kwargs)
        assert isinstance(data, pd.DataFrame)
        assert x == 'day'
        assert y == ['value']
        assert not by
        assert not groupby

    def test_process_1d_xarray_dataarray_with_coords_and_name(self):
        import xarray as xr

        da = xr.DataArray(data=[1, 2, 3], coords={'day': [5, 6, 7]}, dims=['day'], name='temp')

        data, x, y, by, groupby = process_xarray(data=da, **self.default_kwargs)
        assert isinstance(data, pd.DataFrame)
        assert x == 'day'
        assert y == ['temp']
        assert not by
        assert not groupby

    def test_process_2d_xarray_dataarray_with_no_coords(self):
        import xarray as xr

        da = xr.DataArray(np.random.randn(4, 5))

        data, x, y, by, groupby = process_xarray(data=da, **self.default_kwargs)
        assert isinstance(data, pd.DataFrame)
        assert x == 'index'
        assert y == ['value']
        assert not by
        assert not groupby

    def test_process_2d_xarray_dataarray_with_no_coords_as_gridded(self):
        import xarray as xr

        da = xr.DataArray(np.random.randn(4, 5))

        kwargs = self.default_kwargs
        kwargs.update(gridded=True)

        data, x, y, by, groupby = process_xarray(data=da, **kwargs)
        assert isinstance(data, xr.Dataset)
        assert list(data.data_vars.keys()) == ['value']
        assert x == 'dim_1'
        assert y == 'dim_0'
        assert not by
        assert not groupby

    def test_process_2d_xarray_dataarray_with_coords_as_gridded(self):
        import xarray as xr

        da = xr.DataArray(
            data=np.random.randn(4, 5), coords={'y': [3, 4, 5, 6, 7]}, dims=['x', 'y']
        )

        kwargs = self.default_kwargs
        kwargs.update(gridded=True)

        data, x, y, by, groupby = process_xarray(data=da, **kwargs)
        assert isinstance(data, xr.Dataset)
        assert list(data.data_vars.keys()) == ['value']
        assert x == 'y'
        assert y == 'x'
        assert not by
        assert not groupby

    def test_process_3d_xarray_dataset_with_coords(self):
        data, x, y, by, groupby = process_xarray(data=self.ds, **self.default_kwargs)
        assert isinstance(data, pd.DataFrame)
        assert x == 'time'
        assert y == ['air']
        assert not by
        assert groupby == ['lon', 'lat']

    def test_process_3d_xarray_dataset_with_coords_as_gridded(self):
        import xarray as xr

        kwargs = self.default_kwargs
        kwargs.update(gridded=True, x='lon', y='lat')

        data, x, y, by, groupby = process_xarray(data=self.ds, **kwargs)
        assert isinstance(data, xr.Dataset)
        assert list(data.data_vars.keys()) == ['air']
        assert x == 'lon'
        assert y == 'lat'
        assert by is None
        assert groupby == ['time']

    def test_process_3d_xarray_dataset_with_coords_as_gridded_uses_axis_to_get_defaults(self):
        import xarray as xr

        kwargs = self.default_kwargs
        kwargs.update(gridded=True)

        data, x, y, by, groupby = process_xarray(data=self.ds, **kwargs)
        assert isinstance(data, xr.Dataset)
        assert list(data.data_vars.keys()) == ['air']
        assert x == 'lon'
        assert y == 'lat'
        assert not by
        assert groupby == ['time']

    def test_process_xarray_dataset_with_by_as_derived_datetime(self):
        data = self.ds.mean(dim=['lat', 'lon'])
        kwargs = self.default_kwargs
        kwargs.update(gridded=False, y='air', by=['time.hour'])

        data, x, y, by, groupby = process_xarray(data=data, **kwargs)
        assert isinstance(data, pd.DataFrame)
        assert x == 'time'
        assert y == 'air'
        assert by == ['time.hour']
        assert not groupby

    def test_process_xarray_dataset_with_x_as_derived_datetime(self):
        data = self.ds.mean(dim=['lat', 'lon'])
        kwargs = self.default_kwargs
        kwargs.update(gridded=False, y='air', x='time.dayofyear')

        data, x, y, by, groupby = process_xarray(data=data, **kwargs)
        assert isinstance(data, pd.DataFrame)
        assert x == 'time.dayofyear'
        assert y == 'air'
        assert not by
        assert not groupby


class TestDynamicArgs(TestCase):
    def test_dynamic_and_static(self):
        from hvplot.util import process_dynamic_args

        x = 'sepal_width'
        y = pn.widgets.Select(
            name='y', value='sepal_length', options=['sepal_length', 'petal_length']
        )
        kind = pn.widgets.Select(name='kind', value='scatter', options=['bivariate', 'scatter'])

        dynamic, arg_deps, arg_names = process_dynamic_args(x, y, kind)
        assert 'x' not in dynamic
        assert 'y' in dynamic
        assert arg_deps == []

    def test_dynamic_kwds(self):
        from hvplot.util import process_dynamic_args

        x = 'sepal_length'
        y = 'sepal_width'
        kind = 'scatter'
        color = pn.widgets.ColorPicker(value='#ff0000')

        dynamic, arg_deps, arg_names = process_dynamic_args(x, y, kind, c=color)
        assert 'x' not in dynamic
        assert 'c' in dynamic
        assert arg_deps == []

    def test_fn_kwds(self):
        from hvplot.util import process_dynamic_args

        x = 'sepal_length'
        y = 'sepal_width'
        kind = 'scatter'
        by_species = pn.widgets.Checkbox(name='By species')
        color = pn.widgets.ColorPicker(value='#ff0000')

        @pn.depends(by_species.param.value, color.param.value)
        def by_species_fn(by_species, color):
            return 'species' if by_species else color

        dynamic, arg_deps, arg_names = process_dynamic_args(x, y, kind, c=by_species_fn)
        assert dynamic == {}
        assert arg_names == ['c', 'c']
        assert len(arg_deps) == 2


def test_check_crs():
    pytest.importorskip('pyproj')
    p = check_crs('epsg:26915 +units=m')
    assert p.srs == '+proj=utm +zone=15 +datum=NAD83 +units=m +no_defs'
    p = check_crs('wrong')
    assert p is None


@pytest.mark.parametrize(
    'input',
    [
        '+init=epsg:26911',
        'PlateCarree',
        'epsg:6933',
        6933,
        'EPSG: 6933',
    ],
)
def test_process_crs(input):
    pytest.importorskip('pyproj')
    ccrs = pytest.importorskip('cartopy.crs')
    crs = process_crs(input)
    assert isinstance(crs, ccrs.CRS)


def test_process_crs_pyproj_crs():
    pyproj = pytest.importorskip('pyproj')
    ccrs = pytest.importorskip('cartopy.crs')
    crs = process_crs(pyproj.CRS.from_epsg(4326))
    assert isinstance(crs, ccrs.PlateCarree)


def test_process_crs_pyproj_proj():
    pyproj = pytest.importorskip('pyproj')
    ccrs = pytest.importorskip('cartopy.crs')
    crs = process_crs(pyproj.Proj(init='epsg:4326'))
    assert isinstance(crs, ccrs.PlateCarree)


@pytest.mark.parametrize(
    'input',
    [
        '4326',
        4326,
        'epsg:4326',
        'EPSG: 4326',
        '+init=epsg:4326',
        # Created with pyproj.CRS("EPSG:4326").to_wkt()
        'GEOGCRS["WGS 84",ENSEMBLE["World Geodetic System 1984 ensemble",MEMBER["World Geodetic System 1984 (Transit)"],MEMBER["World Geodetic System 1984 (G730)"],MEMBER["World Geodetic System 1984 (G873)"],MEMBER["World Geodetic System 1984 (G1150)"],MEMBER["World Geodetic System 1984 (G1674)"],MEMBER["World Geodetic System 1984 (G1762)"],MEMBER["World Geodetic System 1984 (G2139)"],ELLIPSOID["WGS 84",6378137,298.257223563,LENGTHUNIT["metre",1]],ENSEMBLEACCURACY[2.0]],PRIMEM["Greenwich",0,ANGLEUNIT["degree",0.0174532925199433]],CS[ellipsoidal,2],AXIS["geodetic latitude (Lat)",north,ORDER[1],ANGLEUNIT["degree",0.0174532925199433]],AXIS["geodetic longitude (Lon)",east,ORDER[2],ANGLEUNIT["degree",0.0174532925199433]],USAGE[SCOPE["Horizontal component of 3D system."],AREA["World."],BBOX[-90,-180,90,180]],ID["EPSG",4326]]',
    ],
    ids=lambda x: str(x)[:20],
)
def test_process_crs_platecarree(input):
    pytest.importorskip('pyproj')
    ccrs = pytest.importorskip('cartopy.crs')
    crs = process_crs(input)
    assert isinstance(crs, ccrs.PlateCarree)


@pytest.mark.parametrize(
    'input',
    [
        '3857',
        3857,
        'epsg:3857',
        'EPSG: 3857',
        '+init=epsg:3857',
        'PROJCS["WGS 84 / Pseudo-Mercator",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Mercator_1SP"],PARAMETER["central_meridian",0],PARAMETER["scale_factor",1],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],EXTENSION["PROJ4","+proj=merc +a=6378137 +b=6378137 +lat_ts=0 +lon_0=0 +x_0=0 +y_0=0 +k=1 +units=m +nadgrids=@null +wktext +no_defs"],AUTHORITY["EPSG","3857"]]',
        # Created with pyproj.CRS("EPSG:3857").to_wkt()
        'PROJCRS["WGS 84 / Pseudo-Mercator",BASEGEOGCRS["WGS 84",ENSEMBLE["World Geodetic System 1984 ensemble",MEMBER["World Geodetic System 1984 (Transit)"],MEMBER["World Geodetic System 1984 (G730)"],MEMBER["World Geodetic System 1984 (G873)"],MEMBER["World Geodetic System 1984 (G1150)"],MEMBER["World Geodetic System 1984 (G1674)"],MEMBER["World Geodetic System 1984 (G1762)"],MEMBER["World Geodetic System 1984 (G2139)"],ELLIPSOID["WGS 84",6378137,298.257223563,LENGTHUNIT["metre",1]],ENSEMBLEACCURACY[2.0]],PRIMEM["Greenwich",0,ANGLEUNIT["degree",0.0174532925199433]],ID["EPSG",4326]],CONVERSION["Popular Visualisation Pseudo-Mercator",METHOD["Popular Visualisation Pseudo Mercator",ID["EPSG",1024]],PARAMETER["Latitude of natural origin",0,ANGLEUNIT["degree",0.0174532925199433],ID["EPSG",8801]],PARAMETER["Longitude of natural origin",0,ANGLEUNIT["degree",0.0174532925199433],ID["EPSG",8802]],PARAMETER["False easting",0,LENGTHUNIT["metre",1],ID["EPSG",8806]],PARAMETER["False northing",0,LENGTHUNIT["metre",1],ID["EPSG",8807]]],CS[Cartesian,2],AXIS["easting (X)",east,ORDER[1],LENGTHUNIT["metre",1]],AXIS["northing (Y)",north,ORDER[2],LENGTHUNIT["metre",1]],USAGE[SCOPE["Web mapping and visualisation."],AREA["World between 85.06°S and 85.06°N."],BBOX[-85.06,-180,85.06,180]],ID["EPSG",3857]]',
    ],
    ids=lambda x: str(x)[:20],
)
def test_process_crs_mercator(input):
    pytest.importorskip('pyproj')
    ccrs = pytest.importorskip('cartopy.crs')
    crs = process_crs(input)
    assert isinstance(crs, ccrs.Mercator)


def test_process_crs_rasterio():
    pytest.importorskip('pyproj')
    rcrs = pytest.importorskip('rasterio.crs')
    ccrs = pytest.importorskip('cartopy.crs')
    input = rcrs.CRS.from_epsg(4326).to_wkt()
    crs = process_crs(input)
    assert isinstance(crs, ccrs.CRS)


def test_process_crs_raises_error():
    pytest.importorskip('pyproj')
    pytest.importorskip('cartopy.crs')
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


def test_convert_col_names_to_str():
    df = pd.DataFrame(np.random.random((10, 2)))
    assert all(not isinstance(col, str) for col in df.columns)
    df = _convert_col_names_to_str(df)
    assert all(isinstance(col, str) for col in df.columns)


def test_instantiate_crs_str():
    ccrs = pytest.importorskip('cartopy.crs')
    assert isinstance(instantiate_crs_str('PlateCarree'), ccrs.PlateCarree)


def test_instantiate_crs_google_mercator():
    ccrs = pytest.importorskip('cartopy.crs')
    assert instantiate_crs_str('GOOGLE_MERCATOR') == ccrs.GOOGLE_MERCATOR
    assert instantiate_crs_str('google_mercator') == ccrs.GOOGLE_MERCATOR


def test_instantiate_crs_str_kwargs():
    ccrs = pytest.importorskip('cartopy.crs')
    crs = instantiate_crs_str('PlateCarree', globe=ccrs.Globe(datum='WGS84'))
    assert isinstance(crs, ccrs.PlateCarree)
    assert isinstance(crs.globe, ccrs.Globe)
    assert crs.globe.datum == 'WGS84'


@pytest.mark.skipif(spd is None or dd is None, reason='spatialpandas or dask is not available')
def test_is_geodataframe_spatialpandas_dask():
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
