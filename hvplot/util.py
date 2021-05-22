"""
Provides utilities to convert data and projections
"""
from __future__ import absolute_import

import sys

from distutils.version import LooseVersion
from functools import wraps
from types import FunctionType

import pandas as pd
import holoviews as hv
import param
try:
    import panel as pn
    panel_available = True
except:
    panel_available = False

from holoviews.core.util import basestring

hv_version = LooseVersion(hv.__version__)


def with_hv_extension(func, extension='bokeh', logo=False):
    """If hv.extension is not loaded, load before calling function"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if extension and not getattr(hv.extension, '_loaded', False):
            hv.extension(extension, logo=logo)
        return func(*args, **kwargs)
    return wrapper


def get_ipy():
    try:
        ip = get_ipython() # noqa
    except:
        ip = None
    return ip


def check_crs(crs):
    """
    Checks if the crs represents a valid grid, projection or ESPG string.

    (Code copied from https://github.com/fmaussion/salem)

    Examples
    --------
    >>> p = check_crs('+units=m +init=epsg:26915')
    >>> p.srs
    '+proj=utm +zone=15 +datum=NAD83 +units=m +no_defs'
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

    if hasattr(proj, 'crs'):
        if proj.crs.is_geographic:
            return ccrs.PlateCarree()
    elif proj.is_latlong():  # pyproj<2.0
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

def is_tabular(data):
    if check_library(data, ['dask', 'streamz', 'pandas', 'geopandas', 'cudf']):
        return True
    elif check_library(data, 'intake'):
        from intake.source.base import DataSource
        if isinstance(data, DataSource):
            return data.container == 'dataframe'
    else:
        return False

def is_series(data):
    if not check_library(data, ['dask', 'streamz', 'pandas', 'cudf']):
        return False
    elif isinstance(data, pd.Series):
        return True
    elif check_library(data, 'streamz'):
        import streamz.dataframe as sdf
        return isinstance(data, (sdf.Series, sdf.Seriess))
    elif check_library(data, 'dask'):
        import dask.dataframe as dd
        return isinstance(data, dd.Series)
    elif check_library(data, 'cudf'):
        import cudf
        return isinstance(data, cudf.Series)
    else:
        return False

def check_library(obj, library):
    if not isinstance(library, list):
        library = [library]
    return any([obj.__module__.split('.')[0].startswith(l) for l in library])

def is_cudf(data):
    if 'cudf' in sys.modules:
        from cudf import DataFrame, Series
        return isinstance(data, (DataFrame, Series))

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

def is_ibis(data):
    if not check_library(data, 'ibis'):
        return False
    import ibis
    return isinstance(data, ibis.Expr)

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

def is_xarray_dataarray(data):
    if not check_library(data, 'xarray'):
        return False
    from xarray import DataArray
    return isinstance(data, DataArray)


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


def is_geodataframe(data):
    if 'spatialpandas' in sys.modules:
        import spatialpandas as spd
        if isinstance(data, spd.GeoDataFrame):
            return True
    return isinstance(data, pd.DataFrame) and hasattr(data, 'geom_type') and hasattr(data, 'geometry')


def process_xarray(data, x, y, by, groupby, use_dask, persist, gridded,
                   label, value_label, other_dims, kind=None):
    import xarray as xr
    if isinstance(data, xr.Dataset):
        dataset = data
    else:
        name = data.name or label or value_label
        dataset = data.to_dataset(name=name)

    all_vars = list(other_dims) if other_dims else []
    for var in [x, y, by, groupby]:
        if isinstance(var, list):
            all_vars.extend(var)
        elif isinstance(var, str):
            all_vars.append(var)

    if not gridded:
        not_found = [var for var in all_vars if var not in list(dataset.data_vars) + list(dataset.coords)]
        _, extra_vars, extra_coords = process_derived_datetime_xarray(dataset, not_found)
        dataset = dataset.assign_coords(**{var: dataset[var] for var in extra_coords})
        dataset = dataset.assign(**{var: dataset[var] for var in extra_vars})

    data_vars = list(dataset.data_vars)
    ignore = (by or []) + (groupby or [])
    dims = [c for c in dataset.coords if dataset[c].shape != () and c not in ignore][::-1]
    index_dims = [d for d in dims if d in dataset.indexes]

    if gridded:
        data = dataset
        if len(dims) < 2:
            dims += [dim for dim in list(data.dims)[::-1] if dim not in dims]
        if not (x or y):
            for c in dataset.coords:
                axis = dataset[c].attrs.get('axis', '')
                if axis.lower() == 'x':
                    x = c
                elif axis.lower() == 'y':
                    y = c
        if not (x or y):
            x, y = index_dims[:2] if len(index_dims) > 1 else dims[:2]
        elif x and not y:
            y = [d for d in dims if d != x][0]
        elif y and not x:
            x = [d for d in dims if d != y][0]
        if (len(dims) > 2 and kind not in ('table', 'dataset') and not groupby):
            dims = list(data.coords[x].dims) + list(data.coords[y].dims)
            groupby = [d for d in index_dims if d not in (x, y) and d not in dims and d not in other_dims]
    else:
        if use_dask:
            data = dataset.to_dask_dataframe()
            data = data.persist() if persist else data
        else:
            data = dataset.to_dataframe()
            if len(data.index.names) > 1:
                data = data.reset_index()
        if len(dims) == 0:
            dims = ['index']
        if x and not y:
            y = dims[0] if x in data_vars else data_vars
        elif y and not x:
            x = data_vars[0] if y in dims else dims[0]
        elif not x and not y:
            x, y = dims[0], data_vars

        for var in [x, y]:
            if isinstance(var, list):
                all_vars.extend(var)
            elif isinstance(var, str):
                all_vars.append(var)

        covered_dims = []
        for var in all_vars:
            if var in dataset.coords:
                covered_dims.extend(dataset[var].dims)
        leftover_dims = [dim for dim in index_dims
                         if dim not in covered_dims + all_vars]

        if groupby is None:
            groupby = [c for c in leftover_dims if c not in (by or [])]
    return data, x, y, by, groupby


def process_derived_datetime_xarray(data, not_found):
    from pandas.api.types import is_datetime64_any_dtype as isdate
    extra_vars = []
    extra_coords = []
    for var in not_found:
        if '.' in var:
            derived_from = var.split('.')[0]
            if isdate(data[derived_from]):
                if derived_from in data.coords:
                    extra_coords.append(var)
                else:
                    extra_vars.append(var)
    not_found = [var for var in not_found if var not in extra_vars + extra_coords]
    return not_found, extra_vars, extra_coords


def process_derived_datetime_pandas(data, not_found, indexes=None):
    from pandas.api.types import is_datetime64_any_dtype as isdate
    indexes = indexes or []
    extra_cols = {}
    for var in not_found:
        if '.' in var:
            parts = var.split('.')
            base_col = parts[0]
            dt_str = parts[-1]
            if base_col in data.columns:
                if isdate(data[base_col]):
                    extra_cols[var] = getattr(data[base_col].dt, dt_str)
            elif base_col == 'index':
                if isdate(data.index):
                    extra_cols[var] = getattr(data.index, dt_str)
            elif base_col in indexes:
                index = data.axes[indexes.index(base_col)]
                if isdate(index):
                    extra_cols[var] = getattr(index, dt_str)
    if extra_cols:
        data = data.assign(**extra_cols)
    not_found = [var for var in not_found if var not in extra_cols.keys()]

    return not_found, data


def process_dynamic_args(x, y, kind, **kwds):
    dynamic = {}
    arg_deps = []
    arg_names = []

    for k, v in list(kwds.items()) + [('x', x), ('y', y), ('kind', kind)]:
        if isinstance(v, param.Parameter):
            dynamic[k] = v
        elif panel_available and isinstance(v, pn.widgets.Widget):
            if LooseVersion(pn.__version__) < '0.6.4':
                dynamic[k] = v.param.value
            else:
                dynamic[k] = v

    for k, v in kwds.items():
        if k not in dynamic and isinstance(v, FunctionType) and hasattr(v, '_dinfo'):
            deps = v._dinfo['dependencies']
            arg_deps += list(deps)
            arg_names += list(k) * len(deps)

    return dynamic, arg_deps, arg_names


def filter_opts(eltype, options, backend='bokeh'):
    opts = getattr(hv.Store.options(backend), eltype)
    allowed = [k for g in opts.groups.values()
               for k in list(g.allowed_keywords)]
    return {k: v for k, v in options.items() if k in allowed}
