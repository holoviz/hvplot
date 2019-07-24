from __future__ import absolute_import

from functools import partial
import difflib

import param
import holoviews as hv
import pandas as pd
import numpy as np

from bokeh.models import HoverTool
from holoviews.core.dimension import Dimension
from holoviews.core.spaces import DynamicMap, HoloMap, Callable
from holoviews.core.overlay import NdOverlay
from holoviews.core.options import Store, Cycle
from holoviews.core.layout import NdLayout
from holoviews.core.util import max_range, basestring
from holoviews.element import (
    Curve, Scatter, Area, Bars, BoxWhisker, Dataset, Distribution,
    Table, HeatMap, Image, HexTiles, QuadMesh, Bivariate, Histogram,
    Violin, Contours, Polygons, Points, Path, Labels, RGB, ErrorBars,
    VectorField
)
from holoviews.plotting.bokeh import OverlayPlot
from holoviews.plotting.util import process_cmap
from holoviews.operation import histogram
from holoviews.streams import Buffer, Pipe
from holoviews.util.transform import dim

from .util import (
    is_series, is_dask, is_intake, is_streamz, is_xarray, process_crs,
    process_intake, process_xarray, check_library, is_geopandas
)

renderer = hv.renderer('bokeh')


class StreamingCallable(Callable):
    """
    StreamingCallable is a DynamicMap callback wrapper which keeps
    a handle to start and stop a dynamic stream.
    """

    periodic = param.Parameter()

    def clone(self, callable=None, **overrides):
        """
        Allows making a copy of the Callable optionally overriding
        the callable and other parameters.
        """
        old = {k: v for k, v in self.get_param_values()
               if k not in ['callable', 'name']}
        params = dict(old, **overrides)
        callable = self.callable if callable is None else callable
        return self.__class__(callable, **params)

    def start(self):
        """
        Start the periodic callback
        """
        if not self.periodic._running:
            self.periodic.start()
        else:
            raise Exception('PeriodicCallback already running.')

    def stop(self):
        """
        Stop the periodic callback
        """
        if self.periodic._running:
            self.periodic.stop()
        else:
            raise Exception('PeriodicCallback not running.')



class HoloViewsConverter(object):
    """
    Generic options
    ---------------
    colorbar (default=False): boolean
        Enables colorbar
    flip_xaxis/flip_yaxis: boolean
        Whether to flip the axis left to right or up and down respectively
    grid (default=False): boolean
        Whether to show a grid
    hover (default=True): boolean
        Whether to show hover tooltips
    hover_cols (default=[]): list
        Additional columns to add to the hover tool
    invert (default=False): boolean
        Swaps x- and y-axis
    legend (default=True): boolean or str
        Whether to show a legend, or a legend position
        ('top', 'bottom', 'left', 'right')
    logx/logy (default=False): boolean
        Enables logarithmic x- and y-axis respectively
    logz (default=False): boolean
        Enables logarithmic colormapping
    loglog (default=False): boolean
        Enables logarithmic x- and y-axis
    max_width/max_height: int
        The maximum width and height of the plot for responsive modes
    min_width/min_height: int
        The minimum width and height of the plot for responsive modes
    padding: number or tuple
        Fraction by which to increase auto-ranged extents to make
        datapoints more visible around borders. Supports tuples to
        specify different amount of padding for x- and y-axis and
        tuples of tuples to specify different amounts of padding for
        upper and lower bounds.
    responsive: boolean
        Whether the plot should responsively resize depending on the
        size of the browser. Responsive mode will only work if at
        least one dimension of the plot is left undefined, e.g. when
        width and height or width and aspect are set the plot is set
        to a fixed size, ignoring any responsive option.
    rot: number
        Rotates the axis ticks along the x-axis by the specified
        number of degrees.
    shared_axes (default=False): boolean
        Whether to link axes between plots
    title (default=''): str
        Title for the plot
    tools (default=[]): list
        List of tool instances or strings (e.g. ['tap', box_select'])
    xaxis/yaxis: str or None
        Whether to show the x/y-axis and whether to place it at the
        'top'/'bottom' and 'left'/'right' respectively.
    xformatter/yformatter (default=None): str or TickFormatter
        Formatter for the x-axis and y-axis (accepts printf formatter,
        e.g. '%.3f', and bokeh TickFormatter)
    xlabel/ylabel/clabel (default=None): str
        Axis labels for the x-axis, y-axis, and colorbar
    xlim/ylim (default=None): tuple or list
        Plot limits of the x- and y-axis
    xticks/yticks (default=None): int or list
        Ticks along x- and y-axis specified as an integer, list of
        ticks positions, or list of tuples of the tick positions and labels
    width (default=800)/height (default=300): int
        The width and height of the plot in pixels
    attr_labels (default=True): bool
        Whether to use an xarray object's attributes as labels
    sort_date (default=True): bool
        Whether to sort the x-axis by date before plotting

    Datashader options
    ------------------
    aggregator (default=None):
        Aggregator to use when applying rasterize or datashade operation
        (valid options include 'mean', 'count', 'min', 'max' and more, and
        datashader reduction objects)
    dynamic (default=True):
        Whether to return a dynamic plot which sends updates on widget and
        zoom/pan events or whether all the data should be embedded
        (warning: for large groupby operations embedded data can become
        very large if dynamic=False)
    datashade (default=False):
        Whether to apply rasterization and shading using datashader
        library returning an RGB object
    dynspread (default=False):
        Allows plots generated with datashade=True to increase the point
        size to make sparse regions more visible
    rasterize (default=False):
        Whether to apply rasterization using the datashader library
        returning an aggregated Image
    x_sampling/y_sampling (default=None):
        Declares a minimum sampling density beyond.

    Geographic options
    ------------------
    coastline (default=False):
        Whether to display a coastline on top of the plot, setting
        coastline='10m'/'50m'/'110m' specifies a specific scale.
    crs (default=None):
        Coordinate reference system of the data specified as Cartopy
        CRS object, proj.4 string or EPSG code.
    geo (default=False):
        Whether the plot should be treated as geographic (and assume
        PlateCarree, i.e. lat/lon coordinates).
    global_extent (default=False):
        Whether to expand the plot extent to span the whole globe.
    project (default=False):
        Whether to project the data before plotting (adds initial
        overhead but avoids projecting data when plot is dynamically
        updated).
    tiles (default=False):
        Whether to overlay the plot on a tile source. Tiles sources
        can be selected by name, the default is 'Wikipedia'.
    """

    _gridded_types = ['image', 'contour', 'contourf', 'quadmesh', 'rgb', 'points']

    _geom_types = ['paths', 'polygons']

    _geo_types = sorted(_gridded_types + _geom_types + [
        'points', 'vectorfield', 'labels', 'hexbin', 'bivariate'])

    _stats_types = ['hist', 'kde', 'violin', 'box']

    _data_options = ['x', 'y', 'kind', 'by', 'use_index', 'use_dask',
                     'dynamic', 'crs', 'value_label', 'group_label',
                     'backlog', 'persist']

    _axis_options = ['width', 'height', 'shared_axes', 'grid', 'legend',
                     'rot', 'xlim', 'ylim', 'xticks', 'yticks', 'colorbar',
                     'invert', 'title', 'logx', 'logy', 'loglog', 'xaxis',
                     'yaxis', 'xformatter', 'yformatter', 'xlabel', 'ylabel',
                     'clabel', 'padding']

    _style_options = ['color', 'alpha', 'colormap', 'fontsize', 'c']

    _op_options = ['datashade', 'rasterize', 'x_sampling', 'y_sampling',
                   'aggregator']

    _kind_options = {
        'scatter'  : ['s', 'c', 'scale', 'logz', 'marker'],
        'step'     : ['where'],
        'area'     : ['y2'],
        'errorbars': ['yerr1', 'yerr2'],
        'hist'     : ['bins', 'bin_range', 'normed', 'cumulative'],
        'heatmap'  : ['C', 'reduce_function', 'logz'],
        'hexbin'   : ['C', 'reduce_function', 'gridsize', 'logz', 'min_count'],
        'dataset'  : ['columns'],
        'table'    : ['columns'],
        'image'    : ['z', 'logz'],
        'rgb'      : ['z', 'bands'],
        'quadmesh' : ['z', 'logz'],
        'contour'  : ['z', 'levels', 'logz'],
        'contourf' : ['z', 'levels', 'logz'],
        'vectorfield': ['angle', 'mag'],
        'points'   : ['s', 'marker', 'c', 'scale', 'logz'],
        'polygons' : ['logz', 'c'],
        'labels'   : ['text', 'c', 's']
    }

    _kind_mapping = {
        'line': Curve, 'scatter': Scatter, 'heatmap': HeatMap,
        'bivariate': Bivariate, 'quadmesh': QuadMesh, 'hexbin': HexTiles,
        'image': Image, 'table': Table, 'hist': Histogram, 'dataset': Dataset,
        'kde': Distribution, 'area': Area, 'box': BoxWhisker, 'violin': Violin,
        'bar': Bars, 'barh': Bars, 'contour': Contours, 'contourf': Polygons,
        'points': Points, 'polygons': Polygons, 'paths': Path, 'step': Curve,
        'labels': Labels, 'rgb': RGB, 'errorbars': ErrorBars,
        'vectorfield': VectorField,
    }

    _colorbar_types = ['image', 'hexbin', 'heatmap', 'quadmesh', 'bivariate',
                       'contour', 'contourf', 'polygons']

    _legend_positions = ("top_right", "top_left", "bottom_left",
                         "bottom_right", "right", "left", "top",
                         "bottom")

    def __init__(self, data, x, y, kind=None, by=None, use_index=True,
                 group_label='Variable', value_label='value',
                 backlog=1000, persist=False, use_dask=False,
                 crs=None, fields={}, groupby=None, dynamic=True,
                 width=None, height=None, shared_axes=True,
                 grid=False, legend=True, rot=None, title=None,
                 xlim=None, ylim=None, clim=None, xticks=None, yticks=None,
                 logx=False, logy=False, loglog=False, hover=True,
                 subplots=False, label=None, invert=False,
                 stacked=False, colorbar=None, fontsize=None,
                 colormap=None, datashade=False, rasterize=False,
                 row=None, col=None, figsize=None, debug=False,
                 xaxis=True, yaxis=True, framewise=True, aggregator=None,
                 projection=None, global_extent=False, geo=False,
                 precompute=False, flip_xaxis=False, flip_yaxis=False,
                 dynspread=False, hover_cols=[], x_sampling=None,
                 y_sampling=None, project=False, xlabel=None, ylabel=None,
                 clabel=None, xformatter=None, yformatter=None, tools=[],
                 padding=None, responsive=False, min_width=None,
                 min_height=None, max_height=None, max_width=None,
                 attr_labels=True, coastline=False, tiles=False,
                 sort_date=True, **kwds):

        # Process data and related options
        self._redim = fields
        self._process_data(kind, data, x, y, by, groupby, row, col,
                           use_dask, persist, backlog, label, value_label,
                           hover_cols, attr_labels, kwds)
        self.use_index = use_index
        self.value_label = value_label
        self.group_label = group_label
        self.dynamic = dynamic
        self.geo = geo or crs or global_extent or projection or project
        self.crs = self._process_crs(data, crs) if self.geo else None
        self.project = project
        self.coastline = coastline
        self.tiles = tiles
        self.row = row
        self.col = col
        self.sort_date = sort_date

        # Import geoviews if geo-features requested
        if self.geo or self.datatype == 'geopandas':
            try:
                import geoviews # noqa
            except ImportError:
                raise ImportError('In order to use geo-related features '
                                  'the geoviews library must be available. '
                                  'It can be installed with:\n  conda '
                                  'install -c pyviz geoviews')
        if self.geo:
            if self.kind not in self._geo_types:
                param.main.warning(
                    "geo option cannot be used with kind=%r plot "
                    "type. Geographic plots are only supported for "
                    "following plot types: %r" % (self.kind, self._geo_types))
            from cartopy import crs as ccrs
            from geoviews.util import project_extents
            proj_crs = projection or ccrs.GOOGLE_MERCATOR
            if self.crs != proj_crs:
                px0, py0, px1, py1 = ccrs.GOOGLE_MERCATOR.boundary.bounds
                x0, x1 = xlim or (px0, px1)
                y0, y1 = ylim or (py0, py1)
                extents = (x0, y0, x1, y1)
                x0, y0, x1, y1 = project_extents(extents, self.crs, proj_crs)
                if xlim:
                    xlim = (x0, x1)
                if ylim:
                    ylim = (y0, y1)

        # Operations
        self.datashade = datashade
        self.rasterize = rasterize
        self.dynspread = dynspread
        self.aggregator = aggregator
        self.precompute = precompute
        self.x_sampling = x_sampling
        self.y_sampling = y_sampling

        # By type
        self.subplots = subplots
        self._by_type = NdLayout if subplots else NdOverlay

        # Process options
        self.stacked = stacked
        style_opts, plot_opts, kwds = self._process_style(colormap, kwds)
        self.invert = invert
        plot_opts['logx'] = logx or loglog
        plot_opts['logy'] = logy or loglog
        plot_opts['show_grid'] = grid
        plot_opts['shared_axes'] = shared_axes
        plot_opts['show_legend'] = bool(legend)

        if legend in self._legend_positions:
            plot_opts['legend_position'] = legend
        elif legend in (True, False, None):
            plot_opts['legend_position'] = 'right'
        else:
            raise ValueError('The legend option should be a boolean or '
                             'a valid legend position (i.e. one of %s).'
                             % list(self._legend_positions))

        if xticks:
            plot_opts['xticks'] = xticks
        if yticks:
            plot_opts['yticks'] = yticks
        if not xaxis:
            plot_opts['xaxis'] = None
        elif xaxis != True:
            plot_opts['xaxis'] = xaxis
        if not yaxis:
            plot_opts['yaxis'] = None
        elif yaxis != True:
            plot_opts['yaxis'] = yaxis
        if xlabel is not None:
            plot_opts['xlabel'] = xlabel
        if ylabel is not None:
            plot_opts['ylabel'] = ylabel
        if clabel is not None:
            plot_opts['clabel'] = clabel
        if xlim is not None:
            plot_opts['xlim'] = tuple(xlim)
        if ylim is not None:
            plot_opts['ylim'] = tuple(ylim)
        if padding is not None:
            plot_opts['padding'] = padding
        if xformatter is not None:
            plot_opts['xformatter'] = xformatter
        if yformatter is not None:
            plot_opts['yformatter'] = yformatter
        if flip_xaxis:
            plot_opts['invert_xaxis'] = True
        if flip_yaxis:
            plot_opts['invert_yaxis'] = True
        if responsive:
            if width:
                plot_opts['width'] = width
            if height:
                plot_opts['height'] = height
        else:
            plot_opts['width'] = width or 700
            plot_opts['height'] = height or 300
        if min_width is not None:
            plot_opts['min_width'] = min_width
        if min_height is not None:
            plot_opts['min_height'] = min_height
        if max_width is not None:
            plot_opts['max_width'] = max_width
        if max_height is not None:
            plot_opts['max_height'] = max_height
        if responsive:
            plot_opts['responsive'] = responsive
        if fontsize:
            plot_opts['fontsize'] = fontsize
        if isinstance(colorbar, bool):
            plot_opts['colorbar'] = colorbar
        elif self.kind in self._colorbar_types:
            plot_opts['colorbar'] = True
        if 'logz' in kwds and 'logz' in self._kind_options.get(self.kind, {}):
            plot_opts['logz'] = kwds.pop('logz')
        if invert:
            plot_opts['invert_axes'] = self.kind != 'barh'
        if rot:
            axis = 'yrotation' if invert else 'xrotation'
            plot_opts[axis] = rot

        tools = list(tools)
        if hover and not any(t for t in tools if isinstance(t, HoverTool)
                             or t == 'hover'):
            tools.append('hover')
        plot_opts['tools'] = tools

        if self.crs and global_extent:
            plot_opts['global_extent'] = global_extent
        if projection:
            plot_opts['projection'] = process_crs(projection)
        if title is not None:
            plot_opts['title_format'] = title
        self._plot_opts = plot_opts
        self._overlay_opts = {k: v for k, v in plot_opts.items()
                              if k in OverlayPlot.params()}
        options = Store.options(backend='bokeh')
        el_type = self._kind_mapping[self.kind].__name__
        if el_type in options:
            style = options[el_type].groups['style']
            cycled_opts = [k for k, v in style.kwargs.items() if isinstance(v, Cycle)]
            for opt in cycled_opts:
                color = style_opts.get('color', None)
                if color is None:
                    color = process_cmap(colormap or 'Category10', categorical=True)
                style_opts[opt] = Cycle(values=color) if isinstance(color, list) else color
        self._style_opts = style_opts
        self._norm_opts = {'framewise': framewise, 'axiswise': not shared_axes}
        self.kwds = kwds

        # Process dimensions and labels
        self.label = label
        self._relabel = {'label': label} if label else {}
        self._dim_ranges = {'c': clim or (None, None)}

        # High-level options
        self._validate_kwds(kwds)
        if debug:
            kwds = dict(x=self.x, y=self.y, by=self.by, kind=self.kind,
                        groupby=self.groupby)
            param.main.warning('Plotting {kind} plot with parameters x: {x}, '
                               'y: {y}, by: {by}, groupby: {groupby}'.format(**kwds))


    def _process_crs(self, data, crs):
        """Given crs as proj4 string, data.attr, or cartopy.crs return cartopy.crs
        """
        # get the proj string: either the value of data.attrs[crs] or crs itself
        _crs = getattr(data, 'attrs', {}).get(crs or 'crs', crs)
        try:
            return process_crs(_crs)
        except ValueError:
            # only raise error if crs was specified in kwargs
            if crs:
                raise ValueError(
                    "'{}' must be either a valid crs or an reference to "
                    "a `data.attr` containing a valid crs.".format(crs))

    def _process_data(self, kind, data, x, y, by, groupby, row, col,
                      use_dask, persist, backlog, label, value_label,
                      hover_cols, attr_labels, kwds):
        gridded = kind in self._gridded_types
        gridded_data = False
        da = None

        # Validate DataSource
        self.data_source = data
        self.is_series = is_series(data)
        if self.is_series:
            data = data.to_frame()
        if is_intake(data):
            data = process_intake(data, use_dask or persist)

        if groupby is not None and not isinstance(groupby, list):
            groupby = [groupby]
        if by is not None and not isinstance(by, list):
            by = [by]

        streaming = False
        if isinstance(data, pd.DataFrame):
            self.data = data
            datatype = 'pandas'
            if is_geopandas(data) and kind is None:
                datatype = 'geopandas'
                geom_types = set([gt[5:] if 'Multi' in gt else gt for gt in data.geom_type])
                if len(geom_types) > 1:
                    raise ValueError('The GeopandasInterface can only read dataframes which '
                                     'share a common geometry type')
                geom_type = list(geom_types)[0]
                if geom_type == 'Point':
                    kind = 'points'
                elif geom_type == 'Polygon':
                    kind = 'polygons'
                elif geom_type in ('LineString', 'LineRing'):
                    kind = 'paths'
        elif is_dask(data):
            datatype = 'dask'
            self.data = data.persist() if persist else data
        elif is_streamz(data):
            datatype = 'streamz'
            self.data = data.example
            self.stream_type = data._stream_type
            streaming = True
            self.cb = data
            if data._stream_type == 'updating':
                self.stream = Pipe(data=self.data)
            else:
                self.stream = Buffer(data=self.data, length=backlog, index=False)
            data.stream.gather().sink(self.stream.send)
        elif is_xarray(data):
            import xarray as xr
            z = kwds.get('z')
            if z is None and isinstance(data, xr.Dataset):
                z = list(data.data_vars)[0]
            if gridded and isinstance(data, xr.Dataset) and not isinstance(z, list):
                data = data[z]

            ignore = (groupby or []) + (by or [])
            coords = [c for c in data.coords if data[c].shape != ()
                      and c not in ignore]
            dims = [c for c in data.dims if data[c].shape != ()
                    and c not in ignore]

            if kind is None and (not (x or y) or all(c in data.coords for c in (x, y))):
                if list(data.coords) == ['band', 'y', 'x']:
                    kind = 'rgb'
                    gridded = True
                elif len(coords) == 1:
                    kind = 'line'
                elif len(coords) == 2 or (x and y) or len([c for c in coords if c in dims]) == 2:
                    kind = 'image'
                    gridded = True
                else:
                    kind = 'hist'

            datatype = 'dask' if use_dask else 'pandas'
            if gridded:
                datatype = 'xarray'
                gridded_data = True
            if kind == 'rgb':
                if 'bands' in kwds:
                    other_dims = [kwds['bands']]
                else:
                    other_dims = [d for d in data.coords if d not in (groupby or [])][0]
            else:
                other_dims = []
            da = data
            data, x, y, by_new, groupby_new = process_xarray(
                data, x, y, by, groupby, use_dask, persist, gridded,
                label, value_label, other_dims)

            if kind not in self._stats_types:
                if by is None: by = by_new
                if groupby is None: groupby = groupby_new

            if groupby:
                groupby = [g for g in groupby if g not in (row, col)]
            self.data = data
        else:
            raise ValueError('Supplied data type %s not understood' % type(data).__name__)

        # Validate data and arguments
        if by is None: by = []
        if groupby is None: groupby = []

        if gridded_data:
            not_found = [g for g in groupby if g not in data.coords]
            data_vars = list(data.data_vars) if isinstance(data, xr.Dataset) else [data.name]
            indexes = list(data.coords)
            self.variables = list(data.coords) + data_vars
            if groupby and not_found:
                raise ValueError('The supplied groupby dimension(s) %s '
                                 'could not be found, expected one or '
                                 'more of: %s' % (not_found, list(data.coords)))
        else:
            if gridded and not kind == 'points':
                raise ValueError('%s plot type requires gridded data, '
                                 'e.g. a NumPy array or xarray Dataset, '
                                 'found %s type' % (kind, type(self.data).__name__))

            # Determine valid indexes
            if isinstance(self.data, pd.DataFrame):
                if self.data.index.names == [None]:
                    indexes = [self.data.index.name or 'index']
                else:
                    indexes = list(self.data.index.names)
            else:
                indexes = [c for c in self.data.reset_index().columns
                           if c not in self.data.columns]

            if len(indexes) == 2 and not (x or y or by):
                if kind == 'heatmap':
                    x, y = indexes
                elif kind in ('bar', 'barh'):
                    x, by = indexes

            # Rename non-string columns
            renamed = {c: str(c) for c in data.columns if not isinstance(c, basestring)}
            if renamed:
                self.data = self.data.rename(columns=renamed)
            self.variables = indexes + list(self.data.columns)

            # Reset groupby dimensions
            groupby_index = [g for g in groupby if g in indexes]
            if groupby_index:
                self.data = self.data.reset_index(groupby_index)
            not_found = [g for g in groupby if g not in list(self.data.columns)+indexes]
            if groupby and not_found:
                raise ValueError('The supplied groupby dimension(s) %s '
                                 'could not be found, expected one or '
                                 'more of: %s' % (not_found, list(self.data.columns)))
        # Set data-level options
        self.x = x
        self.y = y
        self.kind = kind or 'line'
        self.datatype = datatype
        self.gridded = gridded
        self.gridded_data = gridded_data
        self.use_dask = use_dask
        self.indexes = indexes
        if isinstance(by, (np.ndarray, pd.Series)):
            self.data['by'] = by
            self.by = ['by']
        elif not by:
            self.by = []
        else:
            self.by = by if isinstance(by, list) else [by]
        self.groupby = groupby
        self.streaming = streaming
        self.hover_cols = hover_cols

        if da is not None and attr_labels:
            try:
                var_tuples = [(var, da[var].attrs) for var in da.coords]
                var_tuples.append((da.name, da.attrs))
                labels = {}
                units = {}
                for var_name, var_attrs in var_tuples:
                    if var_name is None:
                        var_name = 'value'
                    if 'long_name' in var_attrs:
                        labels[var_name] = var_attrs['long_name']
                    if 'units' in var_attrs:
                        units[var_name] = var_attrs['units']
                self._redim = self._merge_redim(labels, 'label')
                self._redim = self._merge_redim(units, 'unit')
            except Exception as e:
                param.main.warning('Unable to auto label using xarray attrs '
                                   'because {e}; suppress this warning '
                                   'with attr_labels=False.'.format(e=e))

    def _process_style(self, colormap, kwds):
        plot_options = {}
        kind = self.kind
        eltype = self._kind_mapping[kind]
        if eltype in Store.registry['bokeh']:
            valid_opts = Store.registry['bokeh'][eltype].style_opts
        else:
            valid_opts = []

        for opt in valid_opts:
            if opt not in kwds or not isinstance(kwds[opt], list) or opt == 'cmap':
                continue
            kwds[opt] = Cycle(kwds[opt])

        style_opts = {kw: kwds[kw] for kw in list(kwds) if kw in valid_opts}

        # Process style options
        if 'cmap' in kwds and colormap:
            raise TypeError("Only specify one of `cmap` and `colormap`.")
        elif 'cmap' in kwds:
            cmap = kwds.pop('cmap')
        else:
            cmap = colormap

        if kind.startswith('bar'):
            plot_options['stacked'] = self.stacked

        # Color
        if 'color' in kwds or 'c' in kwds:
            color = kwds.pop('color', kwds.pop('c', None))
            if isinstance(color, (np.ndarray, pd.Series)):
                self.data['_color'] = color
                style_opts['color'] = '_color'
            elif isinstance(color, list):
                style_opts['color'] = color
            else:
                style_opts['color'] = color
                if 'c' in self._kind_options.get(kind, []) and (color in self.variables):
                    if self.data[color].dtype.kind in 'OSU':
                        cmap = cmap or 'Category10'
                    else:
                        plot_options['colorbar'] = True

        # Size
        if 'size' in kwds or 's' in kwds:
            size = kwds.pop('size', kwds.pop('s', None))
            if isinstance(size, (np.ndarray, pd.Series)):
                self.data['_size'] = np.sqrt(size)
                style_opts['size'] = '_size'
            elif isinstance(size, basestring):
                style_opts['size'] = np.sqrt(dim(size)*kwds.get('scale', 1))
            elif not isinstance(size, dim):
                style_opts['size'] = np.sqrt(size)
        elif 'size' in valid_opts:
            style_opts['size'] = np.sqrt(30)

        # Marker
        if 'marker' in kwds and 'marker' in self._kind_options[self.kind]:
            style_opts['marker'] = kwds.pop('marker')

        # Alpha
        if 'marker' in kwds:
            style_opts['alpha'] = kwds.pop('alpha')

        if cmap:
            style_opts['cmap'] = cmap

        return style_opts, plot_options, kwds


    def _validate_kwds(self, kwds):
        kind_opts = self._kind_options.get(self.kind, [])
        kind = self.kind
        eltype = self._kind_mapping[kind]
        if eltype in Store.registry['bokeh']:
            valid_opts = Store.registry['bokeh'][eltype].style_opts
        else:
            valid_opts = []
        ds_opts = ['max_px', 'threshold']
        mismatches = sorted([k for k in kwds if k not in kind_opts+ds_opts+valid_opts])
        if not mismatches:
            return

        if 'ax' in mismatches:
            mismatches.pop(mismatches.index('ax'))
            param.main.warning('hvPlot does not have the concept of axes, '
                               'and the ax keyword will be ignored. Compose '
                               'plots with the * operator to overlay plots or the '
                               '+ operator to lay out plots beside each other '
                               'instead.')
        if 'figsize' in mismatches:
            mismatches.pop(mismatches.index('figsize'))
            param.main.warning('hvPlot does not have the concept of a figure, '
                               'and the figsize keyword will be ignored. The '
                               'size of each subplot in a layout is set '
                               'individually using the width and height options.')

        combined_opts = (self._data_options + self._axis_options +
                         self._style_options + self._op_options + kind_opts +
                         valid_opts)
        for mismatch in mismatches:
            suggestions = difflib.get_close_matches(mismatch, combined_opts)
            param.main.warning('%s option not found for %s plot; similar options '
                               'include: %r' % (mismatch, self.kind, suggestions))

    def __call__(self, kind, x, y):
        kind = self.kind or kind
        method = getattr(self, kind)

        groups = self.groupby
        zs = self.kwds.get('z', [])
        if not isinstance(zs, list): zs = [zs]
        grid = []
        if self.row: grid.append(self.row)
        if self.col: grid.append(self.col)
        groups += grid
        if groups or len(zs) > 1:
            if self.streaming:
                raise NotImplementedError("Streaming and groupby not yet implemented")
            data = self.data
            if not self.gridded and any(g in self.indexes for g in groups):
                data = data.reset_index()

            if self.datatype == 'geopandas':
                columns = [c for c in data.columns if c != 'geometry']
                shape_dims = ['Longitude', 'Latitude'] if self.geo else ['x', 'y']
                dataset = Dataset(data, kdims=shape_dims+columns).redim(**self._redim)
            else:
                dataset = Dataset(data).redim(**self._redim)
            if groups:
                dataset = dataset.groupby(groups, dynamic=self.dynamic)
                if len(zs) > 1:
                    dimensions = [Dimension(self.group_label, values=zs)]+dataset.kdims
                    if self.dynamic:
                        obj = DynamicMap(lambda *args: getattr(self, kind)(x, y, args[0], dataset[args[1:]].data),
                                         kdims=dimensions)
                    else:
                        obj = HoloMap({(z,)+k: getattr(self, kind)(x, y, z, dataset[k])
                                       for k, v in dataset.data.items() for z in zs}, kdims=dimensions)
                else:
                    obj = dataset.map(lambda ds: getattr(self, kind)(x, y, data=ds.data), Dataset)
            elif len(zs) > 1:
                if self.dynamic:
                    dataset = DynamicMap(lambda z: getattr(self, kind)(x, y, z, data=dataset.data),
                                         kdims=[Dimension(self.group_label, values=zs)])
                else:
                    dataset = HoloMap({z: getattr(self, kind)(x, y, z, data=dataset.data) for z in zs},
                                      kdims=[self.group_label])
            else:
                obj = getattr(self, kind)(x, y, data=dataset.data)
            if grid:
                obj = obj.grid(grid).options(shared_xaxis=True, shared_yaxis=True)
        else:
            if self.streaming:
                cbcallable = StreamingCallable(partial(method, x, y),
                                               periodic=self.cb)
                obj = DynamicMap(cbcallable, streams=[self.stream])
            else:
                obj = method(x, y)

        if self.crs and self.project:
            # Apply projection before rasterizing
            import cartopy.crs as ccrs
            from geoviews import project
            projection = self._plot_opts.get('projection', ccrs.GOOGLE_MERCATOR)
            obj = project(obj, projection=projection)

        if not (self.datashade or self.rasterize):
            return self._apply_layers(obj)

        try:
            from holoviews.operation.datashader import datashade, rasterize, dynspread
            from datashader import reductions
        except:
            raise ImportError('Datashading is not available')

        opts = dict(width=self._plot_opts['width'], height=self._plot_opts['height'],
                    dynamic=self.dynamic)
        if 'cmap' in self._style_opts and self.datashade:
            levels = self._plot_opts.get('color_levels')
            cmap = self._style_opts['cmap']
            if isinstance(cmap, dict):
                opts['color_key'] = cmap
            else:
                opts['cmap'] = process_cmap(cmap, levels)

        if self.by:
            opts['aggregator'] = reductions.count_cat(self.by[0])
        if self.aggregator:
            agg = self.aggregator
            if isinstance(agg, basestring) and self._color_dim:
                agg = getattr(reductions, agg)(self._color_dim)
            opts['aggregator'] = agg
        elif self._color_dim:
            opts['aggregator'] = reductions.mean(self._color_dim)
        if self.precompute:
            opts['precompute'] = self.precompute
        if self.x_sampling:
            opts['x_sampling'] = self.x_sampling
        if self.y_sampling:
            opts['y_sampling'] = self.y_sampling
        if not self.dynamic:
            opts['dynamic'] = self.dynamic

        style = {}
        if self.datashade:
            operation = datashade
            eltype = 'RGB'
        else:
            operation = rasterize
            eltype = 'Image'
            if 'cmap' in self._style_opts:
                style['cmap'] = self._style_opts['cmap']

        processed = operation(obj, **opts)

        if self.dynspread:
            if self.datashade:
                processed = dynspread(processed, max_px=self.kwds.get('max_px', 3),
                                      threshold=self.kwds.get('threshold', 0.5))
            else:
                param.main.warning('dynspread may only be applied on datashaded plots, '
                                   'use datashade=True instead of rasterize=True.')
        return self._apply_layers(processed).opts({eltype: {'plot': self._plot_opts, 'style': style}})

    def _apply_layers(self, obj):
        if self.coastline:
            import geoviews as gv
            coastline = gv.feature.coastline()
            if self.coastline in ['10m', '50m', '110m']:
                coastline = coastline.opts(scale=self.coastline)
            elif self.coastline is not True:
                param.main.warning("coastline scale of %s not recognized, "
                                   "must be one of '10m', '50m' or '110m'." %
                                   self.coastline)
            obj = obj * coastline
        if self.tiles:
            tile_source = 'EsriImagery' if self.tiles == 'ESRI' else self.tiles
            if tile_source in hv.element.tile_sources:
                tiles = hv.element.tile_sources[tile_source]()
            else:
                tiles = hv.element.tiles.Wikipedia()
                if tile_source is not True:
                    param.main.warning(
                        "%s tiles not recognized, must be one of: %s" %
                        (tile_source, sorted(hv.element.tile_sources)))
            obj = tiles * obj
        return obj

    def _merge_redim(self, ranges, attr='range'):
        redim = dict(self._redim)
        for k, r in ranges.items():
            replace = {attr: r}
            if k in redim:
                dim = redim[k]
                if isinstance(dim, Dimension):
                    dim = dim.clone(**replace)
                elif isinstance(dim, dict) and 'range' not in dim:
                    dim = dict(dim, **replace)
                elif isinstance(dim, (tuple, basestring)):
                    dim = Dimension(dim, **replace)
            else:
                dim = replace
            redim[k] = dim
        return redim

    def _validate_dim(self, dimension):
        if isinstance(dimension, dim):
            dimension = dimension.dimension.name
        if isinstance(dimension, basestring) and dimension in self.variables:
            return dimension

    @property
    def _color_dim(self):
        return self._validate_dim(self._style_opts.get('color'))

    def _get_dimensions(self, kdims, vdims):
        for style in ('color', 'size', 'marker', 'alpha'):
            dimension = self._style_opts.get(style)
            dimensions = (kdims if kdims else []) + vdims
            dimension = self._validate_dim(dimension)
            if dimension is None:
                continue
            elif dimension not in dimensions:
                vdims.append(dimension)
        for c in self.hover_cols:
            if (isinstance(dimension, basestring) and dimension in self.variables
                and dimension not in dimensions):
                vdims.append(c)
        return kdims, vdims

    ##########################
    #     Simple charts      #
    ##########################

    def single_chart(self, element, x, y, data=None):
        labelled = ['y' if self.invert else 'x'] if x != 'index' else []
        if not self.is_series:
            labelled.append('x' if self.invert else 'y')
        elif not self.label:
            self._relabel['label'] = y

        if 'xlabel' in self._plot_opts and 'x' not in labelled:
            labelled.append('x')
        if 'ylabel' in self._plot_opts and 'y' not in labelled:
            labelled.append('y')

        opts = {element.__name__: dict(
            plot=dict(self._plot_opts, labelled=labelled),
            norm=self._norm_opts, style=self._style_opts),
            'NdOverlay': dict(plot=dict(self._overlay_opts, batched=False))}

        ys = [y]
        if element is Area and self.kwds.get('y2'):
            ys += [self.kwds['y2']]
        if element is ErrorBars and self.kwds.get('yerr1') and self.kwds.get('yerr2'):
            ys += [self.kwds['yerr1'], self.kwds['yerr2']]
        elif element is ErrorBars and self.kwds.get('yerr1'):
            ys += [self.kwds['yerr1']]
        kdims, vdims = self._get_dimensions([x], ys)

        if self.by:
            if element is Bars and not self.subplots:
                return (element(data, [x]+self.by, ys)
                        .relabel(**self._relabel)
                        .redim(**self._redim)
                        .opts(opts))
            chart = Dataset(data, self.by+kdims, vdims).to(
                element, kdims, vdims, self.by).relabel(**self._relabel)
            chart = chart.layout() if self.subplots else chart.overlay()
        else:
            chart = element(data, kdims, vdims).relabel(**self._relabel)
        return chart.redim(**self._redim).opts(opts)

    def _process_args(self, data, x, y):
        data = (self.data if data is None else data)
        x = x or self.x
        if not x and self.use_index:
            x = self.indexes[0]
        elif not x:
            raise ValueError('Could not determine what to plot. Expected '
                             'x to be declared or use_index to be enabled.')
        if self.sort_date and self.datatype == 'pandas':
            from pandas.api.types import is_datetime64_any_dtype as is_datetime
            if x in self.indexes:
                index = self.indexes.index(x)
                if is_datetime(data.axes[index]):
                    data = data.sort_index(axis=self.indexes.index(x))
            elif is_datetime(data[x]):
                data = data.sort_values(x)

        y = y or self.y
        if not y:
            ys = [c for c in data.columns if c not in [x]+self.by+self.groupby]
            if len(ys) > 1:
                # if columns have different dtypes, only include numeric columns
                from pandas.api.types import is_numeric_dtype as isnum
                num_ys = [col for col in data.columns if isnum(data[col])]
                if len(num_ys) >= 1:
                    ys = num_ys
            y = ys[0] if len(ys) == 1 else ys

        return data, x, y

    def chart(self, element, x, y, data=None):
        "Helper method for simple x vs. y charts"
        data, x, y = self._process_args(data, x, y)
        if x and y and not isinstance(y, (list, tuple)):
            return self.single_chart(element, x, y, data)
        elif x and y and len(y) == 1:
            return self.single_chart(element, x, y[0], data)

        labelled = ['y' if self.invert else 'x'] if x != 'index' else []
        if self.value_label != 'value':
            labelled.append('x' if self.invert else 'y')

        if 'xlabel' in self._plot_opts and 'x' not in labelled:
            labelled.append('x')
        if 'ylabel' in self._plot_opts and 'y' not in labelled:
            labelled.append('y')

        opts = {element.__name__: dict(plot=dict(self._plot_opts, labelled=labelled),
                                       norm=self._norm_opts, style=self._style_opts),
                'NdOverlay': dict(plot=dict(self._overlay_opts, batched=False))}
        charts = []
        for c in y:
            kdims, vdims = self._get_dimensions([x], [c])
            chart = element(data, kdims, vdims).redim(**{c: self.value_label})
            charts.append((c, chart.relabel(**self._relabel)))
        return self._by_type(charts, self.group_label, sort=False).opts(opts)

    def line(self, x, y, data=None):
        return self.chart(Curve, x, y, data)

    def step(self, x, y, data=None):
        where = self.kwds.get('where', 'mid')
        return self.line(x, y, data).options('Curve', interpolation='steps-'+where)

    def scatter(self, x, y, data=None):
        return self.chart(Scatter, x, y, data)

    def area(self, x, y, data=None):
        areas = self.chart(Area, x, y, data)
        if self.stacked:
            areas = areas.map(Area.stack, NdOverlay)
        return areas

    def errorbars(self, x, y, data=None):
        return self.chart(ErrorBars, x, y, data)

    ##########################
    #  Categorical charts    #
    ##########################

    def _category_plot(self, element, x, y, data):
        """
        Helper method to generate element from indexed dataframe.
        """
        labelled = ['y' if self.invert else 'x'] if x != 'index' else []
        if self.value_label != 'value':
            labelled.append('x' if self.invert else 'y')

        if 'xlabel' in self._plot_opts and 'x' not in labelled:
            labelled.append('x')
        if 'ylabel' in self._plot_opts and 'y' not in labelled:
            labelled.append('y')

        opts = {'plot': dict(self._plot_opts, labelled=labelled),
                'style': dict(self._style_opts),
                'norm': self._norm_opts}

        id_vars = [x]
        if any(v in self.indexes for v in id_vars):
            data = data.reset_index()
        data = data[y+[x]]

        if check_library(data, 'dask'):
            from dask.dataframe import melt
        else:
            melt = pd.melt

        df = melt(data, id_vars=[x], var_name=self.group_label, value_name=self.value_label)
        kdims = [x, self.group_label]
        vdims = [self.value_label]+self.hover_cols
        if self.subplots:
            obj = Dataset(df, kdims, vdims).to(element, x).layout()
        else:
            obj = element(df, kdims, vdims)
        return (obj.redim(**self._redim)
                .relabel(**self._relabel).opts(**opts))

    def bar(self, x, y, data=None):
        data, x, y = self._process_args(data, x, y)
        if x and y and (self.by or not isinstance(y, (list, tuple) or len(y) == 1)):
            y = y[0] if isinstance(y, (list, tuple)) else y
            return self.single_chart(Bars, x, y, data)
        return self._category_plot(Bars, x, list(y), data)

    def barh(self, x, y, data=None):
        return self.bar(x, y, data).opts(plot={'Bars': dict(invert_axes=True)})

    ##########################
    #   Statistical charts   #
    ##########################

    def _stats_plot(self, element, y, data=None):
        """
        Helper method to generate element from indexed dataframe.
        """
        data, x, y = self._process_args(data, None, y)

        opts = {'plot': dict(self._plot_opts), 'norm': self._norm_opts,
                'style': self._style_opts}

        ylim = self._plot_opts.get('ylim', (None, None))
        if not isinstance(y, (list, tuple)):
            ranges = {y: ylim}
            return (element(data, self.by, y).redim.range(**ranges)
                    .relabel(**self._relabel).opts(**opts))

        labelled = ['y' if self.invert else 'x'] if self.group_label != 'Group' else []
        if self.value_label != 'value':
            labelled.append('x' if self.invert else 'y')

        if 'xlabel' in self._plot_opts and 'x' not in labelled:
            labelled.append('x')
        if 'ylabel' in self._plot_opts and 'y' not in labelled:
            labelled.append('y')

        opts['plot']['labelled'] = labelled

        kdims = [self.group_label]
        data = data[list(y)]
        if check_library(data, 'dask'):
            from dask.dataframe import melt
        else:
            melt = pd.melt
        df = melt(data, var_name=self.group_label, value_name=self.value_label)
        redim = self._merge_redim({self.value_label: ylim})
        return (element(df, kdims, self.value_label).redim(**redim)
                .relabel(**self._relabel).opts(**opts))

    def box(self, x, y, data=None):
        return self._stats_plot(BoxWhisker, y, data).redim(**self._redim)

    def violin(self, x, y, data=None):
        try:
            from holoviews.element import Violin
        except ImportError:
            raise ImportError('Violin plot requires HoloViews version >=1.10')
        return self._stats_plot(Violin, y, data).redim(**self._redim)

    def hist(self, x, y, data=None):
        data, x, y = self._process_args(data, x, y)

        labelled = ['y'] if self.invert else ['x']

        if 'xlabel' in self._plot_opts and 'x' not in labelled:
            labelled.append('x')
        if 'ylabel' in self._plot_opts and 'y' not in labelled:
            labelled.append('y')

        plot_opts = dict(self._plot_opts, labelled=labelled)
        opts = {'Histogram': dict(
            plot=plot_opts, style=self._style_opts, norm=self._norm_opts),
                'NdOverlay': dict(plot=self._overlay_opts)}
        hist_opts = {'bin_range': self.kwds.get('bin_range', None),
                     'normed': self.kwds.get('normed', False),
                     'cumulative': self.kwds.get('cumulative', False)}
        if 'bins' in self.kwds:
            bins = self.kwds['bins']
            if isinstance(bins, int):
                hist_opts['num_bins'] = bins
            else:
                hist_opts['bins'] = bins

        if not isinstance(y, (list, tuple)):
            if not 'bin_range' in self.kwds:
                ys = data[y]
                ymin, ymax = (ys.min(), ys.max())
                if is_dask(ys):
                    ymin, ymax = ymin.compute(), ymax.compute()
                hist_opts['bin_range'] = ymin, ymax

            ds = Dataset(data, self.by, y)
            hist = hists = histogram(ds.to(Dataset, [], y, self.by), **hist_opts)
            if self.by:
                hist = hists.last
                hists = hists.layout() if self.subplots else hists.overlay()
            return hists.opts(opts).redim(**self._redim)

        ranges = []
        for col in y:
            if not 'bin_range' in self.kwds:
                ys = data[col]
                ymin, ymax = (ys.min(), ys.max())
                if is_dask(ys):
                    ymin, ymax = ymin.compute(), ymax.compute()
                ranges.append((ymin, ymax))
        if ranges:
            hist_opts['bin_range'] = max_range(ranges)

        ds = Dataset(data)
        hists = []
        for col in y:
            hist = histogram(ds, dimension=col, **hist_opts)
            hists.append((col, hist.relabel(**self._relabel)))
        return (self._by_type(hists, sort=False).redim(**self._redim).opts(opts))

    def kde(self, x, y, data=None):
        data, x, y = self._process_args(data, x, y)
        opts = dict(plot=self._plot_opts, style=self._style_opts, norm=self._norm_opts)
        opts = {'Distribution': opts, 'Area': opts,
                'NdOverlay': {'plot': dict(self._overlay_opts, legend_limit=0)}}

        xlim = self._plot_opts.get('xlim', (None, None))
        if not isinstance(y, (list, tuple)):
            ranges = {y: xlim}
            if self.by:
                dists = Dataset(data).to(Distribution, y, [], self.by)
                dists = dists.layout() if self.subplots else dists.overlay()
            else:
                dists = Distribution(data, y, [])
        else:
            ranges = {self.value_label: xlim}
            data = data[y]
            df = pd.melt(data, var_name=self.group_label, value_name=self.value_label)
            ds = Dataset(df)
            if len(df):
                dists = ds.to(Distribution, self.value_label).overlay()
            else:
                vdim = self.value_label + ' Density'
                dists = NdOverlay({0: Area([], self.value_label, vdim)},
                                  [self.group_label])
        redim = self._merge_redim(ranges)
        return (dists.redim(redim).relabel(**self._relabel).opts(opts))

    ##########################
    #      Other charts      #
    ##########################

    def dataset(self, x=None, y=None, data=None):
        data = self.data if data is None else data
        return Dataset(data, self.kwds.get('columns'), []).redim(**self._redim)

    def heatmap(self, x, y, data=None):
        data = self.data if data is None else data
        opts = dict(plot=self._plot_opts, norm=self._norm_opts, style=self._style_opts)
        if not (x or y) or (x == 'columns' and y in ('index', data.index.name)):
            opts['plot']['labelled'] = []
            x, y = 'columns', 'index'
            data = (data.columns, data.index, data.values)
            z = ['value']
        else:
            if not x: x = self.x or data.columns[0]
            if not y: y = self.y or data.columns[1]
            z = self.kwds.get('C', [c for c in data.columns if c not in (x, y)][0])
            z = [z] + self.hover_cols
        redim = self._merge_redim({z[0]: self._dim_ranges['c']})
        hmap = HeatMap(data, [x, y], z, **self._relabel)
        if 'reduce_function' in self.kwds:
            hmap = hmap.aggregate(function=self.kwds['reduce_function'])
        return hmap.redim(**redim).opts(**opts)

    def hexbin(self, x, y, data=None):
        data = self.data if data is None else data
        if not x: x = data.columns[0]
        if not y: y = data.columns[1]
        z = [self.kwds['C']] if self.kwds.get('C') else []
        z += self.hover_cols

        opts = dict(plot=self._plot_opts, norm=self._norm_opts, style=self._style_opts)
        if 'reduce_function' in self.kwds:
            opts['plot']['aggregator'] = self.kwds['reduce_function']
        if 'gridsize' in self.kwds:
            opts['plot']['gridsize'] = self.kwds['gridsize']
        if 'min_count' in self.kwds:
            opts['plot']['min_count'] = self.kwds['min_count']
        redim = self._merge_redim({(z[0] if z else 'Count'): self._dim_ranges['c']})
        element = self._get_element('hexbin')
        params = dict(self._relabel)
        if self.geo: params['crs'] = self.crs
        return element(data, [x, y], z or [], **params).redim(**redim).opts(**opts)

    def bivariate(self, x, y, data=None):
        data = self.data if data is None else data
        if not x: x = data.columns[0]
        if not y: y = data.columns[1]

        opts = dict(plot=self._plot_opts, norm=self._norm_opts, style=self._style_opts)
        return (Bivariate(data, [x, y]).redim(**self._redim).opts(**opts))

    def table(self, x=None, y=None, data=None):
        allowed = ['width', 'height']
        opts = {k: v for k, v in self._plot_opts.items() if k in allowed}
        data = self.data if data is None else data
        return Table(data, self.kwds.get('columns'), []).redim(**self._redim).opts(plot=opts)

    def labels(self, x, y, data=None):
        data = self.data if data is None else data
        if not x: x = self.x or data.columns[0]
        if not y: y = self.y or data.columns[1]
        text = self.kwds.get('text', [c for c in data.columns if c not in (x, y)][0])
        style = self._style_opts
        kdims, vdims = self._get_dimensions([x, y], [text])
        opts = dict(plot=self._plot_opts, norm=self._norm_opts, style=style)
        return Labels(data, kdims, vdims).redim(**self._redim).opts(**opts)

    ##########################
    #     Gridded plots      #
    ##########################

    def _get_element(self, kind):
        element = self._kind_mapping[kind]
        if self.geo:
            import geoviews
            element = getattr(geoviews, element.__name__)
        return element

    def image(self, x=None, y=None, z=None, data=None):
        import xarray as xr
        data = self.data if data is None else data

        z = z or self.kwds.get('z')
        x = x or self.x
        y = y or self.y
        if not (x and y):
            x, y = list(data.dims)[::-1]
        if not z:
            z = list(data.data_vars)[0] if isinstance(data, xr.Dataset) else data.name
        z = [z] + self.hover_cols

        params = dict(self._relabel)
        opts = dict(plot=self._plot_opts, style=self._style_opts, norm=self._norm_opts)
        redim = self._merge_redim({z[0]: self._dim_ranges['c']})

        element = self._get_element('image')
        if self.geo: params['crs'] = self.crs
        return element(data, [x, y], z, **params).redim(**redim).opts(**opts)

    def rgb(self, x=None, y=None, data=None):
        data = self.data if data is None else data

        coords = [c for c in data.coords if c not in self.groupby+self.by]
        if len(coords) < 3:
            raise ValueError('Data must be 3D array to be converted to RGB.')
        x = x or coords[2]
        y = y or coords[1]
        bands = self.kwds.get('bands', coords[0])
        z = self.kwds.get('z')
        if z is None:
            z = list(data.data_vars)[0]
        data = data[z]
        nbands = len(data.coords[bands])
        if nbands < 3:
            raise ValueError('Selected bands coordinate (%s) has only %d channels,'
                             'expected at least three channels to convert to RGB.' %
                             (bands, nbands))

        params = dict(self._relabel)
        opts = dict(plot=self._plot_opts, style=self._style_opts, norm=self._norm_opts)
        if self.geo: params['crs'] = self.crs
        xres, yres = data.attrs['res'] if 'res' in data.attrs else (1, 1)
        xs = data.coords[x][::-1] if xres < 0 else data.coords[x]
        ys = data.coords[y][::-1] if yres < 0 else data.coords[y]
        eldata = (xs, ys)
        for b in range(nbands):
            eldata += (data.isel(**{bands: b}).values,)
        rgb = RGB(eldata, [x, y], RGB.vdims[:nbands], **params)
        return rgb.redim(**self._redim).opts(**opts)

    def quadmesh(self, x=None, y=None, z=None, data=None):
        import xarray as xr
        data = self.data if data is None else data

        z = z or self.kwds.get('z')
        x = x or self.x
        y = y or self.y
        if not (x and y):
            x, y = list([k for k, v in data.coords.items() if v.size > 1])
        if not z:
            z = list(data.data_vars)[0] if isinstance(data, xr.Dataset) else data.name
        z = [z] + self.hover_cols

        params = dict(self._relabel)
        opts = dict(plot=self._plot_opts, style=self._style_opts, norm=self._norm_opts)
        redim = self._merge_redim({z[0]: self._dim_ranges['c']})

        element = self._get_element('quadmesh')
        if self.geo: params['crs'] = self.crs
        return element(data, [x, y], z, **params).redim(**redim).opts(**opts)

    def contour(self, x=None, y=None, z=None, data=None, filled=False):
        from holoviews.operation import contours

        if 'projection' in self._plot_opts:
            import cartopy.crs as ccrs
            t = self._plot_opts['projection']
            if isinstance(t, ccrs.CRS) and not isinstance(t, ccrs.Projection):
                raise ValueError('invalid transform:'
                                 ' Spherical contouring is not supported - '
                                 ' consider using PlateCarree/RotatedPole.')

        opts = dict(plot=self._plot_opts, style=self._style_opts, norm=self._norm_opts)
        qmesh = self.quadmesh(x, y, z, data)

        if self.geo:
            # Apply projection before rasterizing
            import cartopy.crs as ccrs
            from geoviews import project
            projection = self._plot_opts.get('projection', ccrs.GOOGLE_MERCATOR)
            qmesh = project(qmesh, projection=projection)

        if filled:
            opts['style']['line_alpha'] = 0

        if opts['plot']['colorbar']:
            opts['plot']['show_legend'] = False
        levels = self.kwds.get('levels', 5)
        if isinstance(levels, int):
            opts['plot']['color_levels'] = levels
        return contours(qmesh, filled=filled, levels=levels).opts(**opts)

    def contourf(self, x=None, y=None, z=None, data=None):
        return self.contour(x, y, z, data, filled=True)

    def points(self, x=None, y=None, data=None):
        data = self.data if data is None else data
        params = dict(self._relabel)

        x = x if x is not None else self.x
        y = y if y is not None else self.y

        if hasattr(data, 'geom_type') and not (x and y):
            x, y = 'Longitude', 'Latitude'
        elif not (x and y):
            if self.gridded_data:
                x, y = self.variables[:2:-1]
            else:
                x, y = data.columns[:2]

        opts = dict(plot=self._plot_opts, style=self._style_opts, norm=self._norm_opts)
        redim = self._merge_redim({self._color_dim: self._dim_ranges['c']} if self._color_dim else {})
        kdims, vdims = self._get_dimensions([x, y], [])
        element = self._get_element('points')
        if self.geo: params['crs'] = self.crs
        if self.by:
            obj = Dataset(data).to(element, kdims, vdims, self.by, **params).overlay()
        else:
            obj = element(data, kdims, vdims, **params)
        return obj.redim(**redim).opts({'Points': opts})

    def vectorfield(self, x=None, y=None, angle=None, mag=None, data=None):
        data = self.data if data is None else data

        x = x or self.x
        y = y or self.y
        if not (x and y):
            x, y = list([k for k, v in data.coords.items() if v.size > 1])

        angle = self.kwds.get('angle')
        mag = self.kwds.get('mag')
        z = [angle, mag] + self.hover_cols
        redim = self._merge_redim({z[1]: self._dim_ranges['c']})
        params = dict(self._relabel)
        opts = dict(plot=self._plot_opts, style=self._style_opts, norm=self._norm_opts)

        element = self._get_element('vectorfield')
        if self.geo: params['crs'] = self.crs
        return element(data, [x, y], z, **params).redim(**redim).opts(**opts)

    ##########################
    #    Geometry plots      #
    ##########################

    def _geom_plot(self, x=None, y=None, data=None, kind='polygons'):
        data = self.data if data is None else data
        params = dict(self._relabel)

        x = x or self.x
        y = y or self.y
        is_gpd = is_geopandas(data)
        if not (x and y):
            if is_gpd:
                x, y = ('Longitude', 'Latitude') if self.geo else ('x', 'y')
            else:
                x, y = data.columns[:2]

        plot_opts = dict(self._plot_opts)
        ranges = {self._color_dim: self._dim_ranges['c']} if self._color_dim else {}
        redim = self._merge_redim(ranges)
        plot_opts['show_legend'] = False
        opts = dict(plot=plot_opts, style=self._style_opts, norm=self._norm_opts)

        element = self._get_element(kind)
        if self.geo: params['crs'] = self.crs
        params['vdims'] = [c for c in data.columns if c != 'geometry']
        return element(data, [x, y], **params).redim(**redim).opts(**opts)

    def polygons(self, x=None, y=None, data=None):
        return self._geom_plot(x, y, data, kind='polygons')

    def paths(self, x=None, y=None, data=None):
        return self._geom_plot(x, y, data, kind='paths')
