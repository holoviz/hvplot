"""
Provides utilities to convert data and projections
"""
from __future__ import absolute_import

from distutils.version import LooseVersion

import pandas as pd
import holoviews as hv

from holoviews.core.util import basestring

hv_version = LooseVersion(hv.__version__)


def check_crs(crs):
    """
    Checks if the crs represents a valid grid, projection or ESPG string.

    (Code copied from https://github.com/fmaussion/salem)

    Examples
    --------
    >>> p = check_crs('+units=m +init=epsg:26915')
    >>> p.srs
    '+units=m +init=epsg:26915 '
    >>> p = check_crs('wrong')
    >>> p is None
    True
    Returns
    -------
    A valid crs if possible, otherwise None
    """
    import pyproj
    if isinstance(crs, pyproj.Proj):
        out = crs
    elif isinstance(crs, dict) or isinstance(crs, basestring):
        try:
            out = pyproj.Proj(crs)
        except RuntimeError:
            try:
                out = pyproj.Proj(init=crs)
            except RuntimeError:
                out = None
    else:
        out = None
    return out


def proj_to_cartopy(proj):
    """
    Converts a pyproj.Proj to a cartopy.crs.Projection

    (Code copied from https://github.com/fmaussion/salem)

    Parameters
    ----------
    proj: pyproj.Proj
        the projection to convert
    Returns
    -------
    a cartopy.crs.Projection object
    """

    import cartopy.crs as ccrs
    try:
        from osgeo import osr
        has_gdal = True
    except ImportError:
        has_gdal = False

    proj = check_crs(proj)

    if proj.is_latlong():
        return ccrs.PlateCarree()

    srs = proj.srs
    if has_gdal:
        # this is more robust, as srs could be anything (espg, etc.)
        s1 = osr.SpatialReference()
        s1.ImportFromProj4(proj.srs)
        srs = s1.ExportToProj4()

    km_proj = {'lon_0': 'central_longitude',
               'lat_0': 'central_latitude',
               'x_0': 'false_easting',
               'y_0': 'false_northing',
               'k': 'scale_factor',
               'zone': 'zone',
               }
    km_globe = {'a': 'semimajor_axis',
                'b': 'semiminor_axis',
                }
    km_std = {'lat_1': 'lat_1',
              'lat_2': 'lat_2',
              }
    kw_proj = dict()
    kw_globe = dict()
    kw_std = dict()
    for s in srs.split('+'):
        s = s.split('=')
        if len(s) != 2:
            continue
        k = s[0].strip()
        v = s[1].strip()
        try:
            v = float(v)
        except:
            pass
        if k == 'proj':
            if v == 'tmerc':
                cl = ccrs.TransverseMercator
            if v == 'lcc':
                cl = ccrs.LambertConformal
            if v == 'merc':
                cl = ccrs.Mercator
            if v == 'utm':
                cl = ccrs.UTM
        if k in km_proj:
            kw_proj[km_proj[k]] = v
        if k in km_globe:
            kw_globe[km_globe[k]] = v
        if k in km_std:
            kw_std[km_std[k]] = v

    globe = None
    if kw_globe:
        globe = ccrs.Globe(**kw_globe)
    if kw_std:
        kw_proj['standard_parallels'] = (kw_std['lat_1'], kw_std['lat_2'])

    # mercatoooor
    if cl.__name__ == 'Mercator':
        kw_proj.pop('false_easting', None)
        kw_proj.pop('false_northing', None)

    return cl(globe=globe, **kw_proj)


def process_crs(crs):
    """
    Parses cartopy CRS definitions defined in one of a few formats:

      1. EPSG codes:   Defined as string of the form "EPSG: {code}" or an integer
      2. proj.4 string: Defined as string of the form "{proj.4 string}"
      3. cartopy.crs.CRS instance
      4. None defaults to crs.PlateCaree
    """
    try:
        import cartopy.crs as ccrs
        import geoviews as gv # noqa
        import pyproj
    except:
        raise ImportError('Geographic projection support requires GeoViews and cartopy.')

    if crs is None:
        return ccrs.PlateCarree()

    if isinstance(crs, basestring) and crs.lower().startswith('epsg'):
        try:
            crs = ccrs.epsg(crs[5:].lstrip().rstrip())
        except:
            raise ValueError("Could not parse EPSG code as CRS, must be of the format 'EPSG: {code}.'")
    elif isinstance(crs, int):
        crs = ccrs.epsg(crs)
    elif isinstance(crs, (basestring, pyproj.Proj)):
        try:
            crs = proj_to_cartopy(crs)
        except:
            raise ValueError("Could not parse EPSG code as CRS, must be of the format 'proj4: {proj4 string}.'")
    elif not isinstance(crs, ccrs.CRS):
        raise ValueError("Projection must be defined as a EPSG code, proj4 string, cartopy CRS or pyproj.Proj.")
    return crs



def is_series(data):
    if not check_library(data, ['dask', 'streamz', 'pandas']):
        return False
    elif isinstance(data, pd.Series):
        return True
    elif check_library(data, 'streamz'):
        import streamz.dataframe as sdf
        return isinstance(data, (sdf.Series, sdf.Seriess))
    elif check_library(data, 'dask'):
        import dask.dataframe as dd
        return isinstance(data, dd.Series)
    else:
        return False


def check_library(obj, library):
    if not isinstance(library, list):
        library = [library]
    return any([obj.__module__.split('.')[0].startswith(l) for l in library])

def is_dask(data):
    if not check_library(data, 'dask'):
        return False
    import dask.dataframe as dd
    return isinstance(data, (dd.DataFrame, dd.Series))

def is_intake(data):
    if not check_library(data, 'intake'):
        return False
    from intake.source.base import DataSource
    return isinstance(data, DataSource)

def is_streamz(data):
    if not check_library(data, 'streamz'):
        return False
    import streamz.dataframe as sdf
    return sdf and isinstance(data, (sdf.DataFrame, sdf.Series, sdf.DataFrames, sdf.Seriess))

def is_xarray(data):
    if not check_library(data, 'xarray'):
        return False
    from xarray import DataArray, Dataset
    return isinstance(data, (DataArray, Dataset))


def process_intake(data, use_dask):
    if data.container not in ('dataframe', 'xarray'):
        raise NotImplementedError('Plotting interface currently only '
                                  'supports DataSource objects declaring '
                                  'a dataframe or xarray container.')
    if use_dask:
        data = data.to_dask()
    else:
        data = data.read()
    return data


def is_geopandas(data):
    return isinstance(data, pd.DataFrame) and hasattr(data, 'geom_type') and hasattr(data, 'geometry')


def process_xarray(data, x, y, by, groupby, use_dask, persist, gridded, label, value_label):
    import xarray as xr
    dataset = data
    data_vars = list(dataset.data_vars) if isinstance(data, xr.Dataset) else [data.name]
    ignore = (by or []) + (groupby or [])
    dims = [c for c in data.coords if data[c].shape != () and c not in ignore][::-1]

    if gridded:
        data = dataset
        if data_vars == [None]:
            label = label or value_label
            data = data.to_dataset(name=label)
            data_vars = [label]
        if not (x or y):
            x, y = dims[:2]
        elif x and not y:
            y = [d for d in dims if d != x][0]
        elif y and not x:
            x = [d for d in dims if d != y][0]
        if len(dims) > 2 and not groupby:
            groupby = [d for d in dims if d not in (x, y)]
    else:
        name = None
        if not isinstance(dataset, xr.Dataset):
            name = dataset.name or label or value_label
            data_vars = [name]
        if use_dask:
            if not isinstance(dataset, xr.Dataset):
                dataset = dataset.to_dataset(name=name)
            data = dataset.to_dask_dataframe()
            data = data.persist() if persist else data
        else:
            data = dataset.to_dataframe(name=name)
            if len(data.index.names) > 1:
                data = data.reset_index()
        if x and not y:
            y = dims[0] if x in data_vars else data_vars
        elif y and not x:
            x = data_vars[0] if y in dims else dims[0]
        elif not x and not y:
            x, y = dims[0], data_vars

        if by is None:
            by = [c for c in dims if c not in (x, y)]
            if len(by) > 1: by = []
        if groupby is None:
            groupby = [c for c in dims if c not in by+[x, y]]
    return data, x, y, by, groupby
