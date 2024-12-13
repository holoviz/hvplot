"""
Provides utilities to convert data and projections
"""

import sys

from collections.abc import Hashable

from functools import wraps
from packaging.version import Version
from types import FunctionType

import bokeh
import numpy as np
import pandas as pd
import param
import holoviews as hv

try:
    import panel as pn

    panel_available = True
except ImportError:
    panel_available = False

hv_version = Version(hv.__version__)
bokeh_version = Version(bokeh.__version__)
_fugue_ipython = None  # To be set to True in tests to mock ipython


def with_hv_extension(func, extension='bokeh', logo=False):
    """If hv.extension is not loaded, load before calling function"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if extension and not getattr(hv.extension, '_loaded', False):
            from . import hvplot_extension

            hvplot_extension(extension, logo=logo)
        return func(*args, **kwargs)

    return wrapper


def get_ipy():
    try:
        ip = get_ipython()  # noqa
    except NameError:
        ip = None
    return ip


def check_crs(crs):
    """
    Checks if the crs represents a valid grid, projection or ESPG string.

    (Code copied and adapted from https://github.com/fmaussion/salem)

    Examples
    --------
    >>> p = check_crs('epsg:26915 +units=m')
    >>> p.srs
    '+proj=utm +zone=15 +datum=NAD83 +units=m +no_defs'
    >>> p = check_crs('wrong')
    >>> p is None
    True

    Returns
    -------
    A valid crs if possible, otherwise None.
    """
    import pyproj

    try:
        crs_type = pyproj.crs.CRS
    except AttributeError:

        class Dummy:
            pass

        crs_type = Dummy

    if isinstance(crs, pyproj.Proj):
        out = crs
    elif isinstance(crs, crs_type):
        out = pyproj.Proj(crs.to_wkt(), preserve_units=True)
    elif isinstance(crs, dict) or isinstance(crs, str):
        if isinstance(crs, str):
            try:
                crs = pyproj.CRS.from_wkt(crs)
            except RuntimeError:
                # quick fix for https://github.com/pyproj4/pyproj/issues/345
                crs = crs.replace(' ', '').replace('+', ' +')
        try:
            out = pyproj.Proj(crs, preserve_units=True)
        except RuntimeError:
            try:
                out = pyproj.Proj(init=crs, preserve_units=True)
            except RuntimeError:
                out = None
    else:
        out = None
    return out


def proj_is_latlong(proj):
    """Shortcut function because of deprecation."""

    try:
        return proj.is_latlong()
    except AttributeError:
        return proj.crs.is_geographic


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

    input_proj = proj
    proj = check_crs(input_proj)
    if proj is None:
        raise ValueError(f'Invalid proj projection {input_proj!r}')

    srs = proj.srs
    if has_gdal:
        import warnings

        with warnings.catch_warnings():
            # Avoiding this warning could be done by setting osr.UseExceptions(),
            # except there might be a risk to break the code of users leveraging
            # GDAL on their side or through other libraries. So we just silence it.
            warnings.filterwarnings(
                'ignore',
                category=FutureWarning,
                message=r'Neither osr\.UseExceptions\(\) nor osr\.DontUseExceptions\(\) has '
                r'been explicitly called\. In GDAL 4\.0, exceptions will be enabled '
                'by default',
            )
            # this is more robust, as srs could be anything (espg, etc.)
            s1 = osr.SpatialReference()
            s1.ImportFromProj4(proj.srs)
            if s1.ExportToProj4():
                srs = s1.ExportToProj4()

    km_proj = {
        'lon_0': 'central_longitude',
        'lat_0': 'central_latitude',
        'x_0': 'false_easting',
        'y_0': 'false_northing',
        'lat_ts': 'latitude_true_scale',
        'o_lon_p': 'central_rotated_longitude',
        'o_lat_p': 'pole_latitude',
        'k': 'scale_factor',
        'zone': 'zone',
    }
    km_globe = {
        'a': 'semimajor_axis',
        'b': 'semiminor_axis',
    }
    km_std = {
        'lat_1': 'lat_1',
        'lat_2': 'lat_2',
    }
    kw_proj = {}
    kw_globe = {}
    kw_std = {}
    for s in srs.split('+'):
        s = s.split('=')
        if len(s) != 2:
            continue
        k = s[0].strip()
        v = s[1].strip()
        try:
            v = float(v)
        except Exception:
            pass
        if k == 'proj':
            if v == 'longlat':
                cl = ccrs.PlateCarree
            elif v == 'tmerc':
                cl = ccrs.TransverseMercator
                kw_proj['approx'] = True
            elif v == 'lcc':
                cl = ccrs.LambertConformal
            elif v == 'merc':
                cl = ccrs.Mercator
            elif v == 'utm':
                cl = ccrs.UTM
            elif v == 'stere':
                cl = ccrs.Stereographic
            elif v == 'ob_tran':
                cl = ccrs.RotatedPole
            else:
                raise NotImplementedError(f'Unknown projection {v}')
        if k in km_proj:
            if k == 'zone':
                v = int(v)
            kw_proj[km_proj[k]] = v
        if k in km_globe:
            kw_globe[km_globe[k]] = v
        if k in km_std:
            kw_std[km_std[k]] = v

    globe = None
    if kw_globe:
        globe = ccrs.Globe(ellipse='sphere', **kw_globe)
    if kw_std:
        kw_proj['standard_parallels'] = (kw_std['lat_1'], kw_std['lat_2'])

    # mercatoooor
    if cl.__name__ == 'Mercator':
        kw_proj.pop('false_easting', None)
        kw_proj.pop('false_northing', None)
        if 'scale_factor' in kw_proj:
            kw_proj.pop('latitude_true_scale', None)
    elif cl.__name__ == 'Stereographic':
        kw_proj.pop('scale_factor', None)
        if 'latitude_true_scale' in kw_proj:
            kw_proj['true_scale_latitude'] = kw_proj['latitude_true_scale']
            kw_proj.pop('latitude_true_scale', None)
    elif cl.__name__ == 'RotatedPole':
        if 'central_longitude' in kw_proj:
            kw_proj['pole_longitude'] = kw_proj['central_longitude'] - 180
            kw_proj.pop('central_longitude', None)
    else:
        kw_proj.pop('latitude_true_scale', None)

    try:
        return cl(globe=globe, **kw_proj)
    except TypeError:
        del kw_proj['approx']

    return cl(globe=globe, **kw_proj)


def process_crs(crs):
    """
    Parses cartopy CRS definitions defined in one of a few formats:

      1. EPSG codes:   Defined as string of the form "EPSG: {code}" or an integer
      2. proj.4 string: Defined as string of the form "{proj.4 string}"
      3. cartopy.crs.CRS instance
      3. pyproj.Proj or pyproj.CRS instance
      4. WKT string:    Defined as string of the form "{WKT string}"
      5. None defaults to crs.PlateCaree
    """
    missing = []
    try:
        import cartopy.crs as ccrs
    except ImportError:
        missing.append('cartopy')
    try:
        import geoviews as gv  # noqa
    except ImportError:
        missing.append('geoviews')
    try:
        import pyproj
    except ImportError:
        missing.append('pyproj')
    if missing:
        raise ImportError(f'Geographic projection support requires: {", ".join(missing)}.')

    if crs is None:
        return ccrs.PlateCarree()
    elif isinstance(crs, ccrs.CRS):
        return crs
    elif isinstance(crs, str):
        all_crs = [
            proj
            for proj in dir(ccrs)
            if callable(getattr(ccrs, proj))
            and proj not in ['ABCMeta', 'CRS']
            and proj[0].isupper()
            or proj == 'GOOGLE_MERCATOR'
        ]
        if crs in all_crs and crs != 'GOOGLE_MERCATOR':
            return getattr(ccrs, crs)()
        elif crs == 'GOOGLE_MERCATOR':
            return getattr(ccrs, crs)
    elif isinstance(crs, pyproj.CRS):
        crs = crs.to_wkt()

    errors = []
    if isinstance(crs, (str, int, pyproj.Proj)):
        wkt = crs
        if isinstance(crs, (str, int)):  # epsg codes
            try:
                wkt = pyproj.CRS.from_epsg(crs).to_wkt()
            except Exception as e:
                errors.append(e)
        try:
            return proj_to_cartopy(wkt)  # should be all proj4 or wkt strings
        except Exception as e:
            errors.append(e)

    if isinstance(crs, (str, int)):
        if isinstance(crs, str):
            # pyproj does not expect epsg to be prefixed with `EPSG:`
            crs = crs.upper().replace('EPSG:', '').strip()
        try:
            return ccrs.epsg(crs)
        except Exception as e:
            errors.append(e)

    raise ValueError(
        'Projection must be defined as a EPSG code, proj4 string, '
        'WKT string, cartopy CRS instance, cartopy CRS class name string, '
        'pyproj.Proj, or pyproj.CRS.'
    ) from Exception(*errors)


def is_list_like(obj):
    """
    Adapted from pandas' is_list_like cython function.
    """
    return (
        # equiv: `isinstance(obj, abc.Iterable)`
        hasattr(obj, '__iter__')
        and not isinstance(obj, type)
        # we do not count strings/unicode/bytes as list-like
        and not isinstance(obj, (str, bytes))
        # exclude zero-dimensional numpy arrays, effectively scalars
        and not (isinstance(obj, np.ndarray) and obj.ndim == 0)
    )


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
    return any([obj.__module__.split('.')[0].startswith(lib) for lib in library])


def is_cudf(data):
    if 'cudf' in sys.modules:
        from cudf import DataFrame, Series

        return isinstance(data, (DataFrame, Series))


def is_dask(data):
    if not check_library(data, 'dask'):
        return False
    import dask.dataframe as dd

    return isinstance(data, (dd.DataFrame, dd.Series))


def is_duckdb(data):
    if not check_library(data, 'duckdb'):
        return False
    import duckdb

    return isinstance(data, (duckdb.DuckDBPyRelation, duckdb.DuckDBPyConnection))


def is_polars(data):
    if not check_library(data, 'polars'):
        return False
    import polars as pl

    return isinstance(data, (pl.DataFrame, pl.Series, pl.LazyFrame))


def is_intake(data):
    if 'intake' not in sys.modules:
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


def is_lazy_data(data):
    """Check if data is lazy

    This checks if the datatype is Dask, Ibis, or Polars' LazyFrame.
    It is useful to avoid eager evaluation of the data.
    """
    if is_dask(data) or is_ibis(data):
        return True
    elif is_polars(data):
        import polars as pl

        return isinstance(data, pl.LazyFrame)
    return False


def is_xarray_dataarray(data):
    if not check_library(data, 'xarray'):
        return False
    from xarray import DataArray

    return isinstance(data, DataArray)


def support_index(data):
    """
    HoloViews added in v1.19.0 support for retaining Pandas indexes (no longer
    calling .reset_index()).

    Update this utility when other data interfaces support that (geopandas, dask, etc.)
    """
    return type(data) is pd.DataFrame


def process_intake(data, use_dask):
    if data.container not in ('dataframe', 'xarray'):
        raise NotImplementedError(
            'Plotting interface currently only '
            'supports DataSource objects declaring '
            'a dataframe or xarray container.'
        )
    if use_dask:
        data = data.to_dask()
    else:
        data = data.read()
    return data


def is_geodataframe(data):
    if 'spatialpandas' in sys.modules:
        import spatialpandas as spd

        if isinstance(data, (spd.GeoDataFrame, spd.dask.DaskGeoDataFrame)):
            return True
    return (
        isinstance(data, pd.DataFrame) and hasattr(data, 'geom_type') and hasattr(data, 'geometry')
    )


def process_xarray(
    data, x, y, by, groupby, use_dask, persist, gridded, label, value_label, other_dims, kind=None
):
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
        not_found = [
            var for var in all_vars if var not in list(dataset.data_vars) + list(dataset.coords)
        ]
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
        if len(dims) > 2 and kind not in ('table', 'dataset') and not groupby:
            dims = list(data.coords[x].dims) + list(data.coords[y].dims)
            groupby = [
                d for d in index_dims if d not in (x, y) and d not in dims and d not in other_dims
            ]
    else:
        if use_dask:
            data = dataset.to_dask_dataframe()
            data = data.persist() if persist else data
        else:
            data = dataset.to_dataframe()
            if not support_index(data) and len(data.index.names) > 1:
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
        leftover_dims = [dim for dim in index_dims if dim not in covered_dims + all_vars]

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
            dynamic[k] = v

    for k, v in kwds.items():
        if k not in dynamic and isinstance(v, FunctionType) and hasattr(v, '_dinfo'):
            deps = v._dinfo['dependencies']
            arg_deps += list(deps)
            arg_names += list(k) * len(deps)

    return dynamic, arg_deps, arg_names


def filter_opts(eltype, options, backend='bokeh'):
    opts = getattr(hv.Store.options(backend), eltype)
    allowed = [k for g in opts.groups.values() for k in list(g.allowed_keywords)]
    opts = {k: v for k, v in options.items() if k in allowed}
    return opts


def _flatten(line):
    """
    Flatten an arbitrarily nested sequence.

    Inspired by: pd.core.common.flatten

    Parameters
    ----------
    line : sequence
        The sequence to flatten

    Notes
    -----
    This only flattens list, tuple, and dict sequences.

    Returns
    -------
    flattened : generator
    """

    for element in line:
        if any(isinstance(element, tp) for tp in (list, tuple, dict)):
            yield from _flatten(element)
        else:
            yield element


def _convert_col_names_to_str(data):
    """
    Convert column names to string.
    """
    # There's no generic way to rename columns across tabular object types.
    # `columns` could refer to anything else on the object, e.g. a dim
    # on an xarray DataArray. So this may need to be stricter.
    if not hasattr(data, 'columns') or not hasattr(data, 'rename'):
        return data
    renamed = {
        c: str(c) for c in data.columns if not isinstance(c, str) and isinstance(c, Hashable)
    }
    if renamed:
        data = data.rename(columns=renamed)
    return data


def instantiate_crs_str(crs_str: str, **kwargs):
    """
    Instantiate a cartopy.crs.Projection from a string.
    """
    import cartopy.crs as ccrs

    if crs_str.upper() == 'GOOGLE_MERCATOR':
        return ccrs.GOOGLE_MERCATOR
    return getattr(ccrs, crs_str)(**kwargs)


def import_datashader():
    datashader = None
    try:
        import datashader
    except ModuleNotFoundError:
        raise ModuleNotFoundError(
            'The `datashader` package must be installed in order to use '
            'datashading features. Install it with pip or conda.'
        ) from None
    return datashader


def import_geoviews():
    geoviews = None
    try:
        import geoviews
    except ModuleNotFoundError:
        raise ModuleNotFoundError(
            'The `geoviews` package must be installed in order to use '
            'geographic features. Install it with pip or conda.'
        ) from None
    return geoviews


def relabel(hv_obj, **kwargs):
    """Conditionally relabel a HoloViews object"""
    if kwargs:
        hv_obj = hv_obj.relabel(**kwargs)
    return hv_obj


def redim_(hv_obj, **kwargs):
    """Conditionally redim a HoloViews object"""
    if kwargs:
        hv_obj = hv_obj.redim(**kwargs)
    return hv_obj


def relabel_redim(hv_obj, relabel_kwargs, redim_kwargs):
    """Conditionally relabel and/or redim a HoloViews object"""
    if relabel_kwargs:
        hv_obj = hv_obj.relabel(**relabel_kwargs)
    if redim_kwargs:
        hv_obj = hv_obj.redim(**redim_kwargs)
    return hv_obj


def is_mpl_cmap(obj):
    """Check if the object is a Matplotlib LinearSegmentedColormap."""
    if 'matplotlib' not in sys.modules:
        return False
    from matplotlib.colors import LinearSegmentedColormap

    return isinstance(obj, LinearSegmentedColormap)
