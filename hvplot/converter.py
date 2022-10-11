import difflib
from functools import partial

import param
import holoviews as hv
import pandas as pd
import numpy as np
import colorcet as cc

from bokeh.models import HoverTool
from holoviews.core.dimension import Dimension
from holoviews.core.spaces import DynamicMap, HoloMap, Callable
from holoviews.core.overlay import NdOverlay
from holoviews.core.options import Store, Cycle, Palette
from holoviews.core.layout import NdLayout
from holoviews.core.util import max_range
from holoviews.element import (
    Curve, Scatter, Area, Bars, BoxWhisker, Dataset, Distribution,
    Table, HeatMap, Image, HexTiles, QuadMesh, Bivariate, Histogram,
    Violin, Contours, Polygons, Points, Path, Labels, RGB, ErrorBars,
    VectorField, Rectangles, Segments
)
from holoviews.plotting.bokeh import OverlayPlot, colormap_generator
from holoviews.plotting.util import process_cmap
from holoviews.operation import histogram
from holoviews.streams import Buffer, Pipe
from holoviews.util.transform import dim
from packaging.version import Version
from pandas import DatetimeIndex, MultiIndex

from .backend_transforms import _transfer_opts_cur_backend
from .util import (
    filter_opts, hv_version, is_tabular, is_series, is_dask, is_intake, is_cudf,
    is_streamz, is_ibis, is_xarray, is_xarray_dataarray, process_crs,
    process_intake, process_xarray, check_library, is_geodataframe,
    process_derived_datetime_xarray, process_derived_datetime_pandas,
)
from .utilities import hvplot_extension

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
        old = {k: v for k, v in self.param.get_param_values()
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



class HoloViewsConverter:
    """
    Generic options
    ---------------
    clim: tuple
        Lower and upper bound of the color scale
    cnorm (default='linear'): str
        Color scaling which must be one of 'linear', 'log' or 'eq_hist'
    colorbar (default=False): boolean
        Enables a colorbar
    fontscale: number
        Scales the size of all fonts by the same amount, e.g. fontscale=1.5
        enlarges all fonts (title, xticks, labels etc.) by 50%
    fontsize: number or dict
        Set title, label and legend text to the same fontsize. Finer control
        by using a dict: {'title': '15pt', 'ylabel': '5px', 'ticks': 20}
    flip_xaxis/flip_yaxis: boolean
        Whether to flip the axis left to right or up and down respectively
    grid (default=False): boolean
        Whether to show a grid
    hover : boolean
        Whether to show hover tooltips, default is True unless datashade is
        True in which case hover is False by default
    hover_cols (default=[]): list or str
        Additional columns to add to the hover tool or 'all' which will
        includes all columns (including indexes if use_index is True).
    invert (default=False): boolean
        Swaps x- and y-axis
    frame_width/frame_height: int
        The width and height of the data area of the plot
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
    rescale_discrete_levels (default=True): boolean
        If `cnorm='eq_hist` and there are only a few discrete values,
        then `rescale_discrete_levels=True` (the default) decreases
        the lower limit of the autoranged span so that the values are
        rendering towards the (more visible) top of the `cmap` range, 
        thus avoiding washout of the lower values.  Has no effect if
        `cnorm!=`eq_hist`.
    responsive: boolean
        Whether the plot should responsively resize depending on the
        size of the browser. Responsive mode will only work if at
        least one dimension of the plot is left undefined, e.g. when
        width and height or width and aspect are set the plot is set
        to a fixed size, ignoring any responsive option.
    rot: number
        Rotates the axis ticks along the x-axis by the specified
        number of degrees.
    shared_axes (default=True): boolean
        Whether to link axes between plots
    transforms (default={}): dict
        A dictionary of HoloViews dim transforms to apply before plotting
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
    width (default=700)/height (default=300): int
        The width and height of the plot in pixels
    attr_labels (default=None): bool
        Whether to use an xarray object's attributes as labels, defaults to
        None to allow best effort without throwing a warning. Set to True
        to see warning if the attrs can't be found, set to False to disable
        the behavior.
    sort_date (default=True): bool
        Whether to sort the x-axis by date before plotting
    symmetric (default=None): bool
        Whether the data are symmetric around zero. If left unset, the data
        will be checked for symmetry as long as the size is less than
        ``check_symmetric_max``.
    check_symmetric_max (default=1000000):
        Size above which to stop checking for symmetry by default on the data.

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
        Whether to apply rasterization and shading (colormapping) using
        the Datashader library, returning an RGB object instead of 
        individual points
    dynspread (default=False):
        For plots generated with datashade=True or rasterize=True, 
        automatically increase the point size when the data is sparse
        so that individual points become more visible
    rasterize (default=False):
        Whether to apply rasterization using the Datashader library,
        returning an aggregated Image (to be colormapped by the 
        plotting backend) instead of individual points
    x_sampling/y_sampling (default=None):
        Specifies the smallest allowed sampling interval along the x/y axis.

    Geographic options
    ------------------
    coastline (default=False):
        Whether to display a coastline on top of the plot, setting
        coastline='10m'/'50m'/'110m' specifies a specific scale.
    crs (default=None):
        Coordinate reference system of the data specified as Cartopy
        CRS object, proj.4 string or EPSG code.
    features (default=None): dict or list
        A list of features or a dictionary of features and the scale
        at which to render it. Available features include 'borders',
        'coastline', 'lakes', 'land', 'ocean', 'rivers' and 'states'.
        Available scales include '10m'/'50m'/'110m'.
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
        can be selected by name or a tiles object or class can be passed,
        the default is 'Wikipedia'.
    """

    _gridded_types = [
        'image', 'contour', 'contourf', 'quadmesh', 'rgb', 'points',
        'dataset'
    ]

    _geom_types = ['paths', 'polygons']

    _geo_types = sorted(_gridded_types + _geom_types + [
        'points', 'vectorfield', 'labels', 'hexbin', 'bivariate'])

    _stats_types = ['hist', 'kde', 'violin', 'box', 'density']

    _data_options = [
        'x', 'y', 'kind', 'by', 'use_index', 'use_dask', 'dynamic',
        'crs', 'value_label', 'group_label', 'backlog', 'persist',
        'sort_date'
    ]

    _geo_options = [
        'geo', 'crs', 'features', 'project', 'coastline', 'tiles'
    ]

    _axis_options = [
        'width', 'height', 'shared_axes', 'grid', 'legend',
        'rot', 'xlim', 'ylim', 'xticks', 'yticks', 'colorbar',
        'invert', 'title', 'logx', 'logy', 'loglog', 'xaxis',
        'yaxis', 'xformatter', 'yformatter', 'xlabel', 'ylabel',
        'clabel', 'padding', 'responsive', 'max_height', 'max_width',
        'min_height', 'min_width', 'frame_height', 'frame_width',
        'aspect', 'data_aspect', 'fontscale'
    ]

    _style_options = [
        'color', 'alpha', 'colormap', 'fontsize', 'c', 'cmap',
        'color_key', 'cnorm', 'rescale_discrete_levels'
    ]

    _op_options = [
        'datashade', 'rasterize', 'x_sampling', 'y_sampling',
        'aggregator'
    ]

    # Options specific to a particular plot type
    _kind_options = {
        'area'     : ['y2'],
        'errorbars': ['yerr1', 'yerr2'],
        'bivariate': ['bandwidth', 'cut', 'filled', 'levels'],
        'contour'  : ['z', 'levels', 'logz'],
        'contourf' : ['z', 'levels', 'logz'],
        'dataset'  : ['columns'],
        'heatmap'  : ['C', 'reduce_function', 'logz'],
        'hexbin'   : ['C', 'reduce_function', 'gridsize', 'logz', 'min_count'],
        'hist'     : ['bins', 'bin_range', 'normed', 'cumulative'],
        'image'    : ['z', 'logz'],
        'kde'      : ['bw_method', 'ind', 'bandwidth', 'cut', 'filled'],
        'labels'   : ['text', 'c', 'xoffset', 'yoffset', 'text_font', 'text_font_size'],
        'ohlc'     : ['bar_width', 'pos_color', 'neg_color', 'line_color'],
        'points'   : ['s', 'marker', 'c', 'scale', 'logz'],
        'polygons' : ['logz', 'c'],
        'rgb'      : ['z', 'bands'],
        'scatter'  : ['s', 'c', 'scale', 'logz', 'marker'],
        'step'     : ['where'],
        'table'    : ['columns'],
        'quadmesh' : ['z', 'logz'],
        'vectorfield': ['angle', 'mag'],
    }

    # Mapping from kind to HoloViews element type
    _kind_mapping = {
        'area': Area,
        'bar': Bars,
        'barh': Bars,
        'bivariate': Bivariate,
        'box': BoxWhisker,
        'contour': Contours,
        'contourf': Polygons,
        'dataset': Dataset,
        'density': Distribution,
        'errorbars': ErrorBars,
        'hist': Histogram,
        'image': Image,
        'kde': Distribution,
        'labels': Labels,
        'line': Curve,
        'scatter': Scatter,
        'heatmap': HeatMap,
        'hexbin': HexTiles,
        'ohlc': Rectangles,
        'paths': Path,
        'points': Points,
        'polygons': Polygons,
        'quadmesh': QuadMesh,
        'rgb': RGB,
        'step': Curve,
        'table': Table,
        'vectorfield': VectorField,
        'violin': Violin
    }

    # Types which have a colorbar by default
    _colorbar_types = [
        'bivariate', 'contour', 'contourf', 'heatmap', 'image',
        'hexbin', 'quadmesh', 'polygons'
    ]

    _legend_positions = (
        "top_right", "top_left", "bottom_left", "bottom_right",
        "right", "left", "top", "bottom"
    )

    _default_plot_opts = {
        'logx': False,
        'logy': False,
        'show_legend': True,
        'legend_position': 'right',
        'show_grid': False,
        'responsive': False,
        'shared_axes': True
    }

    _default_cmaps = {
        'linear': 'kbc_r',
        'categorical': cc.palette['glasbey_category10'],
        'cyclic': 'colorwheel',
        'diverging': 'coolwarm'
    }

    def __init__(
        self, data, x, y, kind=None, by=None, use_index=True,
        group_label=None, value_label='value', backlog=1000,
        persist=False, use_dask=False, crs=None, fields={},
        groupby=None, dynamic=True, grid=None, legend=None, rot=None,
        title=None, xlim=None, ylim=None, clim=None, symmetric=None,
        logx=None, logy=None, loglog=None, hover=None, subplots=False,
        label=None, invert=False, stacked=False, colorbar=None,
        datashade=False, rasterize=False, row=None, col=None,
        debug=False, framewise=True, aggregator=None,
        projection=None, global_extent=None, geo=False,
        precompute=False, flip_xaxis=None, flip_yaxis=None,
        dynspread=False, hover_cols=[], x_sampling=None,
        y_sampling=None, project=False, tools=[], attr_labels=None,
        coastline=False, tiles=False, sort_date=True,
        check_symmetric_max=1000000, transforms={}, stream=None,
        cnorm=None, features=None, rescale_discrete_levels=None, **kwds
    ):
        # Process data and related options
        self._redim = fields
        self.use_index = use_index
        self.value_label = value_label
        self.label = label
        self._process_data(
            kind, data, x, y, by, groupby, row, col, use_dask,
            persist, backlog, label, group_label, value_label,
            hover_cols, attr_labels, transforms, stream, kwds
        )

        self.dynamic = dynamic
        self.geo = any([geo, crs, global_extent, projection, project, coastline, features])
        self.crs = self._process_crs(data, crs) if self.geo else None
        self.project = project
        self.coastline = coastline
        self.features = features
        self.tiles = tiles
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

            if isinstance(projection, str):
                all_crs = [proj for proj in dir(ccrs) if
                           callable(getattr(ccrs, proj)) and
                           proj not in ['ABCMeta', 'CRS'] and
                           proj[0].isupper() or
                           proj == 'GOOGLE_MERCATOR']
                if projection in all_crs and projection != 'GOOGLE_MERCATOR':
                    projection = getattr(ccrs, projection)()
                elif projection == 'GOOGLE_MERCATOR':
                    projection = getattr(ccrs, projection)
                else:
                    raise ValueError(
                        "Projection must be defined as cartopy CRS or "
                        "one of the following CRS string:\n {}".format(all_crs))

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

        self._backend = Store.current_backend
        if hvplot_extension.compatibility is None:
            self._backend_compat = self._backend
        else:
            self._backend_compat = hvplot_extension.compatibility

        self.stacked = stacked

        plot_opts = dict(self._default_plot_opts,
                         **self._process_plot())
        if xlim is not None:
            plot_opts['xlim'] = tuple(xlim)
        if ylim is not None:
            plot_opts['ylim'] = tuple(ylim)

        self.invert = invert
        if loglog is not None:
            logx = logx or loglog
            logy = logy or loglog
        if logx is not None:
            plot_opts['logx'] = logx
        if logy is not None:
            plot_opts['logy'] = logy

        if grid is not None:
            plot_opts['show_grid'] = grid

        if legend is not None:
            plot_opts['show_legend'] = bool(legend)

        if legend in self._legend_positions:
            plot_opts['legend_position'] = legend
        elif legend not in (True, False, None):
            raise ValueError('The legend option should be a boolean or '
                             'a valid legend position (i.e. one of %s).'
                             % list(self._legend_positions))
        plotwds = ['xticks', 'yticks', 'xlabel', 'ylabel', 'clabel',
                   'padding', 'xformatter', 'yformatter',
                   'height', 'width', 'frame_height', 'frame_width',
                   'min_width', 'min_height', 'max_width', 'max_height',
                   'fontsize', 'fontscale', 'responsive', 'shared_axes',
                   'aspect', 'data_aspect']
        for plotwd in plotwds:
            if plotwd in kwds:
                plot_opts[plotwd] = kwds.pop(plotwd)

        self._style_opts, plot_opts, kwds = self._process_style(kwds, plot_opts)

        for axis_name in ['xaxis', 'yaxis']:
            if axis_name in kwds:
                axis = kwds.pop(axis_name)
                if not axis:
                    plot_opts[axis_name] = None
                elif axis != True:
                    plot_opts[axis_name] = axis
                elif axis_name in plot_opts:
                    plot_opts.pop(axis_name, None)

        if flip_xaxis:
            plot_opts['invert_xaxis'] = True
        if flip_yaxis:
            plot_opts['invert_yaxis'] = True

        if self.geo and not plot_opts.get('data_aspect'):
            plot_opts['data_aspect'] = 1

        ignore_opts = ['responsive', 'aspect', 'data_aspect', 'frame_height', 'frame_width']
        if not any(plot_opts.get(opt) for opt in ignore_opts):
            plot_opts['width'] = plot_opts.get('width', 700)
            plot_opts['height'] = plot_opts.get('height', 300)

        if isinstance(colorbar, bool):
            plot_opts['colorbar'] = colorbar
        elif self.kind in self._colorbar_types:
            plot_opts['colorbar'] = True
        elif self.rasterize:
            plot_opts['colorbar'] = plot_opts.get('colorbar', True)
        if 'logz' in kwds and 'logz' in self._kind_options.get(self.kind, {}):
            plot_opts['logz'] = kwds.pop('logz')
        if invert:
            plot_opts['invert_axes'] = self.kind != 'barh'
        if rot:
            axis = 'yrotation' if invert else 'xrotation'
            plot_opts[axis] = rot

        tools = list(tools) or list(plot_opts.get('tools', []))
        # Disable hover for errorbars plot as Bokeh annotations can't be hovered.
        if kind == 'errorbars':
            hover = False
        elif hover is None:
            hover = not self.datashade
        if hover and not any(t for t in tools if isinstance(t, HoverTool)
                             or t in ['hover', 'vline', 'hline']):
            if hover in ['vline', 'hline']:
                tools.append(hover)
            else:
                tools.append('hover')
        plot_opts['tools'] = tools

        if self.crs and global_extent:
            plot_opts['global_extent'] = global_extent
        if projection:
            plot_opts['projection'] = process_crs(projection)
        title = title if title is not None else getattr(self, '_title', None)
        if title is not None:
            plot_opts['title'] = title
        if (self.kind in self._colorbar_types or self.rasterize or self.datashade or self._color_dim):
            try:
                if not use_dask:
                    symmetric = self._process_symmetric(symmetric, clim, check_symmetric_max)
                if self._style_opts.get('cmap') is None:
                    # Default to categorical camp if we detect categorical shading
                    if (self.datashade and (self.aggregator is None or 'count_cat' in str(self.aggregator)) and
                        ((self.by and not self.subplots) or
                         (isinstance(self.y, list) or (self.y is None and len(set(self.variables) - set(self.indexes)) > 1)))):
                        self._style_opts['cmap'] = self._default_cmaps['categorical']
                    elif symmetric:
                        self._style_opts['cmap'] = self._default_cmaps['diverging']
                    else:
                        self._style_opts['cmap'] = self._default_cmaps['linear']

                if symmetric is not None:
                    plot_opts['symmetric'] = symmetric
            except TypeError:
                pass
        if cnorm is not None:
            plot_opts['cnorm'] = cnorm
        if rescale_discrete_levels is not None and hv_version >= Version('1.15.0'):
            plot_opts['rescale_discrete_levels'] = rescale_discrete_levels

        self._plot_opts = plot_opts
        self._overlay_opts = {k: v for k, v in self._plot_opts.items()
                              if k in OverlayPlot.param.params()}

        self._norm_opts = {'framewise': framewise, 'axiswise': not plot_opts.get('shared_axes')}
        self.kwds = kwds

        # Process dimensions and labels
        self.label = label
        self._relabel = {'label': label} if label else {}
        self._dim_ranges = {'c': clim or (None, None)}

        # High-level options
        self._validate_kwds(kwds)
        if debug:
            kwds = dict(x=self.x, y=self.y, by=self.by, kind=self.kind,
                        groupby=self.groupby, grid=self.grid)
            param.main.warning('Plotting {kind} plot with parameters x: {x}, '
                               'y: {y}, by: {by}, groupby: {groupby}, row/col: {grid}'.format(**kwds))

    def _process_symmetric(self, symmetric, clim, check_symmetric_max):
        if symmetric is not None or clim is not None:
            return symmetric

        if is_xarray(self.data):
            # chunks mean it's lazily loaded; nanquantile will eagerly load
            data = self.data[self.z]
            if not getattr(data, '_in_memory', True) or data.chunks:
                return False
            if is_xarray_dataarray(data):
                if data.size > check_symmetric_max:
                    return False
            else:
                return False

        elif self._color_dim:
            data = self.data[self._color_dim]
        else:
            return

        if data.size == 0:
            return False
        
        cmin = np.nanquantile(data, 0.05)
        cmax = np.nanquantile(data, 0.95)

        return bool(cmin < 0 and cmax > 0)

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

    def _transform_columnar_data(self, data):
        renamed = {c: str(c) for c in data.columns if not isinstance(c, str)}
        if renamed:
            data = data.rename(columns=renamed)
        return data

    def _process_data(self, kind, data, x, y, by, groupby, row, col,
                      use_dask, persist, backlog, label, group_label,
                      value_label, hover_cols, attr_labels, transforms,
                      stream, kwds):
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
        self.source_data = data

        if groupby is not None and not isinstance(groupby, list):
            groupby = [groupby]
        if by is not None and not isinstance(by, list):
            by = [by]
        grid = []
        if row is not None: grid.append(row)
        if col is not None: grid.append(col)
        streaming = False
        if is_geodataframe(data):
            datatype = 'geopandas' if hasattr(data, 'geom_type') else 'spatialpandas'
            self.data = data
            if kind is None:
                if datatype == 'geopandas':
                    geom_types = {gt[5:] if 'Multi' in gt else gt for gt in data.geom_type}
                else:
                    geom_types = [type(data.geometry.dtype).__name__.replace('Multi', '').replace('Dtype', '')]
                if len(geom_types) > 1:
                    raise ValueError('The GeopandasInterface can only read dataframes which '
                                     'share a common geometry type')
                geom_type = list(geom_types)[0]
                if geom_type == 'Point':
                    kind = 'points'
                elif geom_type == 'Polygon':
                    kind = 'polygons'
                elif geom_type in ('LineString', 'LineRing', 'Line'):
                    kind = 'paths'
        elif isinstance(data, pd.DataFrame):
            datatype = 'pandas'
            self.data = data
        elif is_dask(data):
            datatype = 'dask'
            self.data = data.persist() if persist else data
        elif is_cudf(data):
            datatype = 'cudf'
            self.data = data
        elif is_ibis(data):
            datatype = 'ibis'
            self.data = data
        elif is_streamz(data):
            datatype = 'streamz'
            self.data = data.example
            if isinstance(self.data, pd.DataFrame):
                self.data = self.data.iloc[:0]
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
            if isinstance(data, xr.Dataset):
                if len(data.data_vars) == 0:
                    raise ValueError("Cannot plot an empty xarray.Dataset object.")
            if z is None:
                if isinstance(data, xr.Dataset):
                    z = list(data.data_vars)[0]
                else:
                    z = data.name or 'value'
            if gridded and isinstance(data, xr.Dataset) and not isinstance(z, list):
                data = data[z]
            self.z = z

            ignore = (groupby or []) + (by or []) + grid
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
                label, value_label, other_dims, kind=kind)

            if kind not in self._stats_types:
                if by is None: by = by_new
                if groupby is None: groupby = groupby_new

            if groupby:
                groupby = [g for g in groupby if g not in grid]

            # Add a title to hvplot.xarray plots that displays scalar coords values,
            # as done by xarray.plot()  
            if not groupby and not grid:
                if isinstance(da, xr.DataArray):
                    self._title = da._title_for_slice()
                elif isinstance(da, xr.Dataset):
                    self._title = partial(xr.DataArray._title_for_slice, da)()
                        
            self.data = data
        else:
            raise ValueError('Supplied data type %s not understood' % type(data).__name__)

        if stream is not None:
            if streaming:
                raise ValueError("Cannot supply streamz.DataFrame and stream argument.")
            self.stream = stream
            self.cb = None
            if isinstance(stream, Pipe):
                self.stream_type = 'updating'
            elif isinstance(stream, Buffer):
                self.stream_type = 'streaming'
            else:
                raise ValueError("Stream of type %s not recognized." % type(stream))
            streaming = True

        # Validate data and arguments
        if by is None: by = []
        if groupby is None: groupby = []

        if gridded_data:
            not_found = [g for g in groupby if g not in data.coords]
            not_found, _, _ = process_derived_datetime_xarray(data, not_found)
            data_vars = list(data.data_vars) if isinstance(data, xr.Dataset) else [data.name]
            indexes = list(data.coords.indexes)
            # Handle undeclared indexes
            if x is not None and x not in indexes:
                indexes.append(x)
            if y is not None and y not in indexes:
                indexes.append(y)
            for data_dim in data.dims:
                if not any(data_dim in data[c].dims for c in indexes):
                    for coord in data.coords:
                        if coord not in indexes and {data_dim} == set(data[coord].dims):
                            indexes.append(data_dim)
                            self.data = self.data.set_index({data_dim: coord})
                            if coord not in groupby+by:
                                groupby.append(data_dim)
            self.variables = list(data.coords) + data_vars
            if groupby and not_found:
                raise ValueError('The supplied groupby dimension(s) %s '
                                 'could not be found, expected one or '
                                 'more of: %s' % (not_found, list(data.coords)))
        else:
            if gridded and kind not in ('points', 'dataset'):
                raise ValueError('%s plot type requires gridded data, '
                                 'e.g. a NumPy array or xarray Dataset, '
                                 'found %s type' % (kind, type(self.data).__name__))

            if hasattr(data, 'columns') and data.columns.name and not group_label:
                group_label = data.columns.name
            elif not group_label:
                group_label = 'Variable'

            if isinstance(data.columns, pd.MultiIndex) and x in (None, 'index') and y is None and not by:
                self.data = data.stack().reset_index(1).rename(columns={'level_1': group_label})
                by = group_label
                x = 'index'

            # Determine valid indexes
            if isinstance(self.data, pd.DataFrame):
                if self.data.index.names == [None]:
                    indexes = [self.data.index.name or 'index']
                else:
                    indexes = list(self.data.index.names)
            elif hasattr(self.data, 'reset_index'):
                indexes = [c for c in self.data.reset_index().columns
                           if c not in self.data.columns]
            else:
                indexes = [c for c in self.data.columns
                           if c not in self.data.columns]

            if len(indexes) == 2 and not (x or y or by):
                if kind == 'heatmap':
                    x, y = indexes
                elif kind in ('bar', 'barh'):
                    x, by = indexes

            self.data = self._transform_columnar_data(self.data)
            self.variables = indexes + list(self.data.columns)

            # Reset groupby dimensions
            groupby_index = [g for g in groupby if g in indexes]
            if groupby_index:
                self.data = self.data.reset_index(groupby_index)

            if isinstance(by, (np.ndarray, pd.Series)):
                by_cols = []
            else:
                by_cols = by if isinstance(by, list) else [by]
            not_found = [g for g in groupby+by_cols if g not in list(self.data.columns)+indexes]
            not_found, self.data = process_derived_datetime_pandas(self.data, not_found, indexes)
            if groupby and not_found:
                raise ValueError('The supplied groupby dimension(s) %s '
                                 'could not be found, expected one or '
                                 'more of: %s' % (not_found, list(self.data.columns)))

        if transforms:
            self.data = Dataset(self.data, indexes).transform(**transforms).data

        # Set data-level options
        self.x = x
        self.y = y
        self.kind = kind or 'line'
        self.datatype = datatype
        self.gridded = gridded
        self.gridded_data = gridded_data
        self.use_dask = use_dask
        self.indexes = indexes
        self.group_label = group_label or 'Variable'
        if isinstance(by, (np.ndarray, pd.Series)):
            self.data = self.data.assign(_by=by)
            self.by = ['_by']
            self.variables.append('_by')
        elif not by:
            self.by = []
        else:
            self.by = by if isinstance(by, list) else [by]
        self.groupby = groupby
        self.grid = grid
        self.streaming = streaming

        if not hover_cols:
            self.hover_cols = []
        elif isinstance(hover_cols, list):
            self.hover_cols = hover_cols
        elif hover_cols == 'all' and self.use_index:
            self.hover_cols = self.variables
        elif hover_cols == 'all' and not self.use_index:
            self.hover_cols = [v for v in self.variables if v not in self.indexes]
        elif hover_cols !='all' and isinstance(hover_cols,str):
            self.hover_cols = [hover_cols]

        if self.datatype in ('geopandas', 'spatialpandas'):
            self.hover_cols = [c for c in self.hover_cols if c!= 'geometry']

        if da is not None and attr_labels is True or attr_labels is None:
            try:
                var_tuples = [(var, da[var].attrs) for var in da.coords]
                if isinstance(da, xr.Dataset):
                    var_tuples.extend([(var, da[var].attrs) for var in da.data_vars])
                else:
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
                if attr_labels is True:
                    param.main.param.warning('Unable to auto label using xarray attrs '
                                       'because {e}'.format(e=e))

    def _process_plot(self):
        kind = self.kind
        options = Store.options(backend='bokeh')
        elname = self._kind_mapping[kind].__name__
        plot_opts = options[elname].groups['plot'].options if elname in options else {}

        if kind.startswith('bar'):
            plot_opts['stacked'] = self.stacked

        if kind == 'hist':
            if self.stacked:
                param.main.param.warning('Stacking for histograms is not yet implemented in '
                                   'holoviews. Use bar plots if stacking is required.')

        return plot_opts

    def _process_style(self, kwds, plot_opts):
        kind = self.kind
        eltype = self._kind_mapping[kind]
        registry =  Store.registry[self._backend_compat]

        if eltype in registry:
            valid_opts = registry[eltype].style_opts
        else:
            valid_opts = []

        cmap_opts = ('cmap', 'colormap', 'color_key')
        categories = ['accent', 'category', 'dark', 'colorblind', 'pastel',
                      'set1', 'set2', 'set3', 'paired', 'glasbey']
        for opt in valid_opts:
            if (opt not in kwds or not isinstance(kwds[opt], list) or
                opt in cmap_opts):
                continue
            kwds[opt] = Cycle(kwds[opt])

        # Process style options
        options = Store.options(backend=self._backend_compat)
        elname = eltype.__name__
        style = options[elname].groups['style'].kwargs if elname in options else {}
        style_opts = {k: v for k, v in style.items() if not isinstance(v, Cycle) and k not in cmap_opts}
        style_opts.update(**{k: v for k, v in kwds.items() if k in valid_opts})

        # Color
        cmap_kwds = set(cmap_opts).intersection(kwds)
        if len(cmap_kwds) > 1:
            raise TypeError('Specify at most one of `cmap`, `colormap`, or '
                            '`color_key`.')

        cmap = kwds.pop(cmap_kwds.pop()) if cmap_kwds else None
        color = kwds.pop('color', kwds.pop('c', None))

        if color is not None:
            if (self.datashade or self.rasterize) and color in [self.x, self.y]:
                self.data = self.data.assign(_color=self.data[color])
                style_opts['color'] = color = '_color'
                self.variables.append('_color')
            elif isinstance(color, (np.ndarray, pd.Series)):
                self.data = self.data.assign(_color=color)
                style_opts['color'] = color = '_color'
                self.variables.append('_color')
            else:
                style_opts['color'] = color

            if not isinstance(color, list) and color in self.variables and \
                'c' in self._kind_options.get(kind, []):
                if self.data[color].dtype.kind in 'OSU':
                    cmap = cmap or self._default_cmaps['categorical']
                else:
                    plot_opts['colorbar'] = plot_opts.get('colorbar', True)

        if isinstance(cmap, str) and cmap in self._default_cmaps:
            cmap = self._default_cmaps[cmap]

        if cmap is not None:
            style_opts['cmap'] = cmap

        if 'color' in style_opts:
            color = style_opts['color']
        elif not isinstance(cmap, dict):
            if cmap and any(c in cmap for c in categories):
                color = process_cmap(cmap or self._default_cmaps['categorical'], categorical=True)
            else:
                color = cmap
        else:
            color = style_opts.get('color')

        for k, v in style.items():
            if isinstance(v, Cycle) and isinstance(v, str):
                if color == cmap:
                    if color not in Palette.colormaps and color.title() in Palette.colormaps:
                        color = color.title()
                    else:
                        Palette.colormaps[color] = colormap_generator(process_cmap(color))
                    style_opts[k] = Palette(color)
                elif isinstance(color, list):
                    style_opts[k] = Cycle(values=color)
                else:
                    style_opts[k] = color

        # Size
        size = kwds.pop('size', kwds.pop('s', None))
        if size is not None:
            scale = kwds.get('scale', 1)
            if (self.datashade or self.rasterize):
                param.main.param.warning(
                    'There is no reasonable way to use size (or s) with '
                    'rasterize or datashade. To aggregate along a third '
                    'dimension, set color (or c) to the desired dimension.')
            if isinstance(size, (np.ndarray, pd.Series)):
                size = np.sqrt(size) * scale
                self.data = self.data.assign(_size=size)
                style_opts['size'] = '_size'
                self.variables.append('_size')
            elif isinstance(size, str):
                style_opts['size'] = np.sqrt(dim(size)) * scale
            elif not isinstance(size, dim):
                style_opts['size'] = np.sqrt(size) * scale
        elif 'size' in valid_opts:
            style_opts['size'] = np.sqrt(30)

        # Marker
        if 'marker' in kwds and 'marker' in self._kind_options[self.kind]:
            style_opts['marker'] = kwds.pop('marker')

        return style_opts, plot_opts, kwds

    def _validate_kwds(self, kwds):
        kind_opts = self._kind_options.get(self.kind, [])
        kind = self.kind
        eltype = self._kind_mapping[kind]
        if eltype in Store.registry[self._backend_compat]:
            valid_opts = Store.registry[self._backend_compat][eltype].style_opts
        else:
            valid_opts = []
        ds_opts = ['max_px', 'threshold']
        mismatches = sorted(k for k in kwds if k not in kind_opts+ds_opts+valid_opts)
        if not mismatches:
            return

        if 'ax' in mismatches:
            mismatches.pop(mismatches.index('ax'))
            param.main.param.warning('hvPlot does not have the concept of axes, '
                               'and the ax keyword will be ignored. Compose '
                               'plots with the * operator to overlay plots or the '
                               '+ operator to lay out plots beside each other '
                               'instead.')
        if 'figsize' in mismatches:
            mismatches.pop(mismatches.index('figsize'))
            param.main.param.warning('hvPlot does not have the concept of a figure, '
                               'and the figsize keyword will be ignored. The '
                               'size of each subplot in a layout is set '
                               'individually using the width and height options.')

        combined_opts = (self._data_options + self._axis_options +
                         self._op_options +
                         self._geo_options + kind_opts + valid_opts)
        # Only add the gloabl styling options in the suggestions for bokeh
        # since they may not be supported by all the backends.
        # See e.g. alpha for Area plots with plotly:
        # https://github.com/holoviz/holoviews/issues/5226
        if self._backend_compat == 'bokeh':
            combined_opts = combined_opts + self._style_options
        for mismatch in mismatches:
            suggestions = difflib.get_close_matches(mismatch, combined_opts)
            param.main.param.warning(
                f'{mismatch} option not found for {self.kind} plot with '
                f'{self._backend_compat}; similar options include: {suggestions}'
            )

    def __call__(self, kind, x, y):
        kind = self.kind or kind
        method = getattr(self, kind)

        groups = self.groupby
        zs = self.kwds.get('z', [])
        if not isinstance(zs, list): zs = [zs]
        groups += self.grid
        if self.gridded and not kind == 'points':
            groups += self.by
        if groups or len(zs) > 1:
            if self.streaming:
                raise NotImplementedError("Streaming and groupby not yet implemented")
            data = self.data
            if not self.gridded and any(g in self.indexes for g in groups):
                data = data.reset_index()

            if self.datatype in ('geopandas', 'spatialpandas'):
                columns = [c for c in data.columns if c != 'geometry']
                shape_dims = ['Longitude', 'Latitude'] if self.geo else ['x', 'y']
                dataset = Dataset(data, kdims=shape_dims+columns)
            elif self.datatype == 'xarray':
                import xarray as xr
                if isinstance(data, xr.Dataset):
                    if kind == 'image':
                        dims_with_coords = set(data.coords.keys())
                        missing_coords =  set(self.indexes) - dims_with_coords
                        new_coords = {coord: np.arange(data[coord].shape[0])
                                      for coord in missing_coords}
                        data = data.assign_coords(**new_coords)
                    dataset = Dataset(data, self.indexes)
                else:
                    name = data.name or self.label or self.value_label
                    dataset = Dataset(data, self.indexes, name)
            else:
                dataset = Dataset(data)
            dataset = dataset.redim(**self._redim)

            if groups:
                datasets = dataset.groupby(groups, dynamic=self.dynamic)
                if len(zs) > 1:
                    dimensions = [Dimension(self.group_label, values=zs)]+datasets.kdims
                    if self.dynamic:
                        def z_wrapper(**kwargs):
                            z = kwargs.pop(self.group_label)
                            ds = datasets.select(**kwargs)
                            return ds.reindex(vdims=[ds.get_dimension(z)])
                        obj = DynamicMap(z_wrapper, kdims=dimensions)
                        def method_wrapper(ds, x, y):
                            z = ds.vdims[0].name
                            el = method(x, y, z, data=ds.data)
                            el._transforms = dataset._transforms
                            el._dataset = ds
                            return el
                        obj = obj.apply(method_wrapper, x=x, y=y, per_element=True, link_inputs=False)
                    else:
                        obj = HoloMap({(z,)+k: method(x, y, z, dataset[k])
                                       for k, v in datasets.data.items() for z in zs}, kdims=dimensions)
                else:
                    def method_wrapper(ds, x, y):
                        el = method(x, y, data=ds.data)
                        el._transforms = dataset._transforms
                        el._dataset = ds
                        return el
                    obj = datasets.apply(method_wrapper, x=x, y=y, per_element=True,
                                         link_inputs=False)
            elif len(zs) > 1:
                dimensions = [Dimension(self.group_label, values=zs)]
                if self.dynamic:
                    obj = DynamicMap(lambda z: method(x, y, z, data=dataset.data),
                                     kdims=dimensions)
                else:
                    obj = HoloMap({z: method(x, y, z, data=dataset.data) for z in zs},
                                  kdims=dimensions)
            else:
                obj = method(x, y, data=dataset.data)

            if self.gridded and self.by and not kind == 'points':
                obj = obj.layout(self.by) if self.subplots else obj.overlay(self.by)
            if self.grid:
                obj = obj.grid(self.grid).opts(shared_xaxis=True, shared_yaxis=True, backend='bokeh')
        else:
            if self.streaming:
                cb = partial(method, x, y)
                if self.cb is None:
                    cbcallable = cb
                else:
                    cbcallable = StreamingCallable(cb, periodic=self.cb)
                obj = DynamicMap(cbcallable, streams=[self.stream])
            else:
                data = self.source_data
                if self.datatype in ('geopandas', 'spatialpandas'):
                    columns = [c for c in data.columns if c != 'geometry']
                    shape_dims = ['Longitude', 'Latitude'] if self.geo else ['x', 'y']
                    dataset = Dataset(data, kdims=shape_dims+columns)
                elif self.datatype == 'xarray':
                    import xarray as xr
                    if isinstance(data, xr.Dataset):
                        dataset = Dataset(data, self.indexes)
                    else:
                        name = data.name or self.label or self.value_label
                        dataset = Dataset(data, self.indexes, name)
                else:
                    try:
                        dataset = Dataset(data, self.indexes)
                    except Exception:
                        dataset = Dataset(data)
                    dataset = dataset.redim(**self._redim)
                obj = method(x, y)
                obj._dataset = dataset

        if self.crs and self.project:
            # Apply projection before rasterizing
            import cartopy.crs as ccrs
            from geoviews import project
            projection = self._plot_opts.get('projection', ccrs.GOOGLE_MERCATOR)
            obj = project(obj, projection=projection)

        if not (self.datashade or self.rasterize):
            layers = self._apply_layers(obj)
            layers = _transfer_opts_cur_backend(layers)
            return layers
        try:
            from holoviews.operation.datashader import datashade, rasterize, dynspread
            from datashader import reductions
        except ImportError:
            raise ImportError('In order to use datashading features '
                    'the Datashader library must be available. '
                    'It can be installed with:\n  conda '
                    'install -c pyviz datashader')

        opts = dict(dynamic=self.dynamic)
        if self._plot_opts.get('width') is not None:
            opts['width'] = self._plot_opts['width']
        if self._plot_opts.get('height') is not None:
            opts['height'] = self._plot_opts['height']

        categorical = False
        if self.by and not self.subplots:
            opts['aggregator'] = reductions.count_cat(self.by[0])
            categorical = True
        elif ((isinstance(self.y, list) and len(self.y) > 1 or self.y is None and len(set(self.variables) - set(self.indexes)) > 1) and
              self.kind in ('scatter', 'line', 'area')):
            opts['aggregator'] = reductions.count_cat(self.group_label)
            categorical = True
        if self.aggregator:
            import datashader as ds
            agg = self.aggregator
            if isinstance(agg, str) and self._color_dim:
                categorical = agg == 'count_cat'
                agg = getattr(reductions, agg)(self._color_dim)
            else:
                categorical = isinstance(agg, (ds.count_cat, ds.by))
            opts['aggregator'] = agg
        elif self._color_dim:
            opts['aggregator'] = reductions.mean(self._color_dim)
        if self.precompute:
            opts['precompute'] = self.precompute
        if self.x_sampling:
            opts['x_sampling'] = self.x_sampling
        if self.y_sampling:
            opts['y_sampling'] = self.y_sampling
        if self._plot_opts.get('xlim') is not None:
            opts['x_range'] = self._plot_opts['xlim']
        if self._plot_opts.get('ylim') is not None:
            opts['y_range'] = self._plot_opts['ylim']
        if not self.dynamic:
            opts['dynamic'] = self.dynamic

        if 'cmap' in self._style_opts and self.datashade:
            levels = self._plot_opts.get('color_levels')
            cmap = self._style_opts['cmap']
            if isinstance(cmap, dict):
                opts['color_key'] = cmap
            else:
                opts['cmap'] = process_cmap(cmap, levels, categorical=categorical)

        if 'line_width' in self._style_opts:
            opts['line_width'] = self._style_opts['line_width']

        style = {}
        if self.datashade:
            operation = datashade
            if 'cmap' in opts and not 'color_key' in opts:
                opts['color_key'] = opts['cmap']
            eltype = 'RGB'
            if 'cnorm' in self._plot_opts:
                opts['cnorm'] = self._plot_opts['cnorm']
            if 'rescale_discrete_levels' in self._plot_opts:
                opts['rescale_discrete_levels'] = self._plot_opts['rescale_discrete_levels']
        else:
            operation = rasterize
            eltype = 'Image'
            if 'cmap' in self._style_opts:
                style['cmap'] = self._style_opts['cmap']
            if self._dim_ranges.get('c', (None, None)) != (None, None):
                style['clim'] = self._dim_ranges['c']

        processed = operation(obj, **opts)

        if self.dynspread:
            processed = dynspread(processed, max_px=self.kwds.get('max_px', 3),
                                  threshold=self.kwds.get('threshold', 0.5))
        
        opts = filter_opts(eltype, dict(self._plot_opts, **style), backend='bokeh')
        layers = self._apply_layers(processed).opts(eltype, **opts, backend='bokeh')
        layers = _transfer_opts_cur_backend(layers)
        return layers

    def _get_opts(self, eltype, backend='bokeh', **custom):
        opts = dict(self._plot_opts, **dict(self._style_opts, **self._norm_opts))
        opts.update(custom)
        return filter_opts(eltype, opts, backend=backend)

    def _apply_layers(self, obj):
        if self.coastline:
            import geoviews as gv
            coastline = gv.feature.coastline.clone()
            if self.coastline in ['10m', '50m', '110m']:
                coastline = coastline.opts(scale=self.coastline)
            elif self.coastline is not True:
                param.main.param.warning(
                    "coastline scale of %s not recognized, must be one "
                    "'10m', '50m' or '110m'." % self.coastline)
            obj = obj * coastline

        if self.features:
            import geoviews as gv
            for feature in reversed(self.features):
                feature_obj = getattr(gv.feature, feature)
                if feature_obj is None:
                    raise ValueError(
                        "Feature %r was not recognized, must be one of "
                        "'borders', 'coastline', 'lakes', 'land', 'ocean', "
                        "'rivers' and 'states'." % feature)
                feature_obj = feature_obj.clone()
                if isinstance(self.features, dict):
                    scale = self.features[feature]
                    if scale not in ['10m', '50m', '110m']:
                        param.main.param.warning(
                            "Feature scale of %r not recognized, "
                            "must be one of '10m', '50m' or '110m'." %
                        scale)
                    else:
                        feature_obj = feature_obj.opts(scale=scale)
                obj = feature_obj * obj

        if self.tiles:
            tile_source = 'EsriImagery' if self.tiles == 'ESRI' else self.tiles
            warning = ("%s tiles not recognized, must be one of: %s or a tile object" %
                       (tile_source, sorted(hv.element.tile_sources)))
            if tile_source is True:
                tiles = hv.element.tiles.OSM()
            elif tile_source in hv.element.tile_sources.keys():
                tiles = hv.element.tile_sources[tile_source]()
            elif tile_source in hv.element.tile_sources.values():
                tiles = tile_source()
            elif isinstance(tile_source, hv.element.tiles.Tiles):
                tiles = tile_source
            elif self.geo:
                from geoviews.element import WMTS
                if isinstance(tile_source, WMTS):
                    tiles = tile_source
                else:
                    param.main.param.warning(warning)
            else:
                param.main.param.warning(warning)
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
                elif isinstance(dim, (tuple, str)):
                    dim = Dimension(dim, **replace)
            else:
                dim = replace
            redim[k] = dim
        return redim

    def _validate_dim(self, dimension):
        if isinstance(dimension, dim):
            dimension = dimension.dimension.name
        if isinstance(dimension, str) and dimension in self.variables:
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
                dimensions.append(dimension)
        agg_col = getattr(self.aggregator, 'column', None)
        if agg_col is not None:
            if agg_col not in dimensions:
                vdims.append(agg_col)
                dimensions.append(agg_col)
        for dimension in self.hover_cols:
            if (isinstance(dimension, str) and dimension in self.variables
                and dimension not in dimensions):
                vdims.append(dimension)
        return kdims, vdims

    def _set_backends_opts(self, element, cur_opts, compat_opts):
        # Bokeh is still the main backend
        element = element.opts(**cur_opts, backend='bokeh')
        if compat_opts:
            element = element.opts(**compat_opts, backend=self._backend_compat)
        return element

    def _get_compat_opts(self, el_name, **custom):
        # Bokeh is still the main backend
        cur_opts = self._get_opts(el_name, backend='bokeh', **custom)
        if self._backend_compat != 'bokeh':
            # Don't pass custom opts to the compatibility layer
            compat_opts = self._get_opts(el_name, backend=self._backend_compat)
            compat_opts = {
                k: v for k, v in compat_opts.items() if k not in cur_opts
            }
        else:
            compat_opts = {}
        return cur_opts, compat_opts

    def _error_if_unavailable(self, kind, element=None):
        """
        Raise an error if the element is not available with the current backend.
        """
        if not element:
            element = self._kind_mapping[kind]
        if element not in Store.registry[self._backend]:
            raise NotImplementedError(
                f'{kind!r} plot not supported by the {self._backend!r} backend.'
            )

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
        
        cur_el_opts = self._get_opts(element.name, labelled=labelled, backend='bokeh')
        compat_el_opts = self._get_opts(element.name, labelled=labelled, backend=self._backend_compat)
        for opts_ in [cur_el_opts, compat_el_opts]:
            if 'color' in opts_ and opts_['color'] in data.columns:
                opts_['color'] = hv.dim(opts_['color'])
        cur_opts = {
            element.name: cur_el_opts,
            'NdOverlay': filter_opts('NdOverlay', dict(self._overlay_opts, batched=False), backend='bokeh'),
        }
        compat_opts = {
            element.name: compat_el_opts,
            'NdOverlay': filter_opts('NdOverlay', dict(self._overlay_opts), backend=self._backend_compat),
        }

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
                if any(y in self.indexes for y in ys):
                    data = data.reset_index()
                return (element(data, ([x] if x else [])+self.by, ys)
                        .relabel(**self._relabel)
                        .redim(**self._redim)
                        .opts(cur_opts, backend='bokeh')
                        .opts(compat_opts, backend=self._backend_compat))
            chart = Dataset(data, self.by+kdims, vdims).to(
                element, kdims, vdims, self.by).relabel(**self._relabel)
            chart = chart.layout() if self.subplots else chart.overlay(sort=False)
        else:
            chart = element(data, kdims, vdims).relabel(**self._relabel)
        return (chart.redim(**self._redim)
                .opts(cur_opts, backend='bokeh')
                .opts(compat_opts, backend=self._backend_compat))

    def _process_chart_x(self, data, x, y, single_y, categories=None):
        """This should happen before _process_chart_y"""
        if x is False:
            return None

        x = x or (self.x if self.x != y else None)
        if x is None:
            if self.use_index:
                xs = self.indexes
            else:
                xs = list(data.columns)
            xs = [c for c in xs if c not in self.by+self.groupby+self.grid+[y]]
            x = xs[0] if len(xs) else None

        if not x and not categories:
            raise ValueError('Could not determine what to plot. Set x explicitly')
        return x

    def _process_chart_y(self, data, x, y, single_y):
        """This should happen after _process_chart_x"""
        y = y or self.y
        if y is None:
            ys = [c for c in data.columns if c not in [x]+self.by+self.groupby+self.grid]
            if len(ys) > 1:
                # if columns have different dtypes, only include numeric columns
                from pandas.api.types import is_numeric_dtype as isnum
                num_ys = [dim for dim in ys if isnum(data[dim])]
                if len(num_ys) >= 1:
                    ys = num_ys
            y = ys[0] if len(ys) == 1 or single_y else ys
        return y

    def _process_chart_args(self, data, x, y, single_y=False, categories=None):
        if data is None:
            data = self.data
        elif not self.gridded_data:
            data = self._transform_columnar_data(data)

        x = self._process_chart_x(data, x, y, single_y, categories=categories)
        y = self._process_chart_y(data, x, y, single_y)

        # sort by date if enabled and x is a date
        if x is not None and self.sort_date and self.datatype == 'pandas':
            from pandas.api.types import is_datetime64_any_dtype as is_datetime
            if x in self.indexes:
                index = self.indexes.index(x)
                if is_datetime(data.axes[index]):
                    data = data.sort_index(axis=self.indexes.index(x))
            elif x in data.columns:
                if is_datetime(data[x]):
                    data = data.sort_values(x)

        # set index to column if needed in hover_cols
        if self.use_index and any(c for c in self.hover_cols if
                                  c in self.indexes and
                                  c not in data.columns):
            data = data.reset_index()

        # calculate any derived time
        dimensions = []
        for col in [x, y, self.by, self.hover_cols]:
            if col is not None:
                dimensions.extend(col if isinstance(col, list) else [col])

        not_found = [dim for dim in dimensions if dim not in self.variables]
        _, data = process_derived_datetime_pandas(data, not_found, self.indexes)

        return data, x, y

    def chart(self, element, x, y, data=None):
        "Helper method for simple x vs. y charts"
        data, x, y = self._process_chart_args(data, x, y)
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

        cur_opts = {
            element.name: self._get_opts(element.name, labelled=labelled, backend='bokeh'),
            'NdOverlay': filter_opts('NdOverlay', dict(self._overlay_opts, batched=False), backend='bokeh'),
        }
        compat_opts = {
            element.name: self._get_opts(element.name, labelled=labelled, backend=self._backend_compat),
            'NdOverlay': filter_opts('NdOverlay', dict(self._overlay_opts), backend=self._backend_compat),
        }

        charts = []
        for c in y:
            kdims, vdims = self._get_dimensions([x], [c])
            chart = element(data, kdims, vdims).redim(**{c: self.value_label})
            charts.append((c, chart.relabel(**self._relabel)))
        return (self._by_type(charts, self.group_label, sort=False)
                .opts(cur_opts, backend='bokeh')
                .opts(compat_opts, backend=self._backend_compat))


    def line(self, x=None, y=None, data=None):
        self._error_if_unavailable('line')
        return self.chart(Curve, x, y, data)

    def step(self, x=None, y=None, data=None):
        where = self.kwds.get('where', 'mid')
        return self.line(x, y, data).options('Curve', interpolation='steps-'+where)

    def scatter(self, x=None, y=None, data=None):
        self._error_if_unavailable('scatter')
        return self.chart(Scatter, x, y, data)

    def area(self, x=None, y=None, data=None):
        self._error_if_unavailable('area')
        areas = self.chart(Area, x, y, data)
        if self.stacked:
            areas = areas.map(Area.stack, NdOverlay)
        return areas

    def errorbars(self, x=None, y=None, data=None):
        self._error_if_unavailable('errorbars')
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

        cur_opts, compat_opts = self._get_compat_opts(element.name, labelled=labelled)

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
        return (obj.redim(**self._redim).relabel(**self._relabel)
                .apply(self._set_backends_opts, cur_opts=cur_opts, compat_opts=compat_opts))

    def bar(self, x=None, y=None, data=None):
        self._error_if_unavailable('bar')
        data, x, y = self._process_chart_args(data, x, y, categories=self.by)
        if (x or self.by) and y and (self.by or not isinstance(y, (list, tuple) or len(y) == 1)):
            y = y[0] if isinstance(y, (list, tuple)) else y
            return self.single_chart(Bars, x, y, data)
        return self._category_plot(Bars, x, list(y), data)

    def barh(self, x=None, y=None, data=None):
        return self.bar(x, y, data).opts('Bars', invert_axes=True)

    ##########################
    #   Statistical charts   #
    ##########################

    def _stats_plot(self, element, y, data=None):
        """
        Helper method to generate element from indexed dataframe.
        """
        data, x, y = self._process_chart_args(data, False, y)

        custom = {}
        if 'color' in self._style_opts:
            prefix = 'violin' if issubclass(element, Violin) else 'box'
            custom[prefix+'_fill_color'] = self._style_opts['color']
        cur_opts, compat_opts = self._get_compat_opts(element.name, **custom)
        ylim = self._plot_opts.get('ylim', (None, None))
        if not isinstance(y, (list, tuple)):
            ranges = {y: ylim}
            return (element(data, self.by, y).redim.range(**ranges).relabel(**self._relabel)
                    .apply(self._set_backends_opts, cur_opts=cur_opts, compat_opts=compat_opts))


        labelled = ['y' if self.invert else 'x'] if self.group_label != 'Group' else []
        if self.value_label != 'value':
            labelled.append('x' if self.invert else 'y')

        if 'xlabel' in self._plot_opts and 'x' not in labelled:
            labelled.append('x')
        if 'ylabel' in self._plot_opts and 'y' not in labelled:
            labelled.append('y')

        cur_opts['labelled']  = labelled

        kdims = [self.group_label]
        data = data[list(y)]
        if check_library(data, 'dask'):
            from dask.dataframe import melt
        else:
            melt = pd.melt
        df = melt(data, var_name=self.group_label, value_name=self.value_label)
        if list(y) and df[self.value_label].dtype is not data[y[0]].dtype:
            df[self.value_label] = df[self.value_label].astype(data[y[0]].dtype)
        redim = self._merge_redim({self.value_label: ylim})
        return (element(df, kdims, self.value_label).redim(**redim).relabel(**self._relabel)
                .apply(self._set_backends_opts, cur_opts=cur_opts, compat_opts=compat_opts))


    def box(self, x=None, y=None, data=None):
        self._error_if_unavailable('box')
        return self._stats_plot(BoxWhisker, y, data).redim(**self._redim)

    def violin(self, x=None, y=None, data=None):
        self._error_if_unavailable('violin')
        try:
            from holoviews.element import Violin
        except ImportError:
            raise ImportError('Violin plot requires HoloViews version >=1.10')
        return self._stats_plot(Violin, y, data).redim(**self._redim)

    def hist(self, x=None, y=None, data=None):
        self._error_if_unavailable('hist')
        data, x, y = self._process_chart_args(data, False, y)

        labelled = ['y'] if self.invert else ['x']

        if 'xlabel' in self._plot_opts and 'x' not in labelled:
            labelled.append('x')
        if 'ylabel' in self._plot_opts and 'y' not in labelled:
            labelled.append('y')

        cur_opts = {
            'Histogram': self._get_opts('Histogram', labelled=labelled, backend='bokeh'),
            'NdOverlay': filter_opts('NdOverlay', self._overlay_opts, backend='bokeh'),
        }
        compat_opts = {
            'Histogram': self._get_opts('Histogram', backend=self._backend_compat),
            'NdOverlay': filter_opts('NdOverlay', self._overlay_opts, backend=self._backend_compat),
        }
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

            ds = Dataset(data, self.by)
            if self.by:
                hist = hists = histogram(
                    ds.groupby(self.by), dimension=y, **hist_opts
                )
                hist = hists.last
                hists = hists.layout() if self.subplots else hists.overlay(sort=False)
            else:
                hists = histogram(ds, dimension=y, **hist_opts)

            return (hists.redim(**self._redim)
                    .opts(cur_opts, backend='bokeh')
                    .opts(compat_opts, backend=self._backend_compat))

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
        return (self._by_type(hists, sort=False)
                .redim(**self._redim)
                .opts(cur_opts, backend='bokeh')
                .opts(compat_opts, backend=self._backend_compat))

    def kde(self, x=None, y=None, data=None):
        self._error_if_unavailable('kde')
        bw_method = self.kwds.pop('bw_method', None)
        ind = self.kwds.pop('ind', None)
        if bw_method is not None or ind is not None:
            raise ValueError('hvplot does not support bw_method and ind')

        dist_opts = dict(self.kwds)
        data, x, y = self._process_chart_args(data, x, y)
        cur_opts = {
            'Distribution': self._get_opts('Distribution', backend='bokeh', **dist_opts),
            'Area': self._get_opts('Distribution', backend='bokeh'),
            'NdOverlay': filter_opts('NdOverlay', dict(self._overlay_opts, legend_limit=0), backend='bokeh')
        }
        compat_opts = {
            'Distribution': self._get_opts('Distribution', backend=self._backend_compat, **dist_opts),
            'Area': self._get_opts('Distribution', backend=self._backend_compat),
            'NdOverlay': filter_opts('NdOverlay', self._overlay_opts, backend=self._backend_compat)
        }

        xlim = self._plot_opts.get('xlim', (None, None))
        if not isinstance(y, (list, tuple)):
            ranges = {y: xlim}
            if self.by:
                dists = Dataset(data).to(Distribution, y, [], self.by)
                dists = dists.layout() if self.subplots else dists.overlay(sort=False)
            else:
                dists = Distribution(data, y, [])
        else:
            ranges = {self.value_label: xlim}
            data = data[y]
            df = pd.melt(data, var_name=self.group_label, value_name=self.value_label)
            ds = Dataset(df)
            if len(df):
                dists = ds.to(Distribution, self.value_label)
                dists = dists.layout() if self.subplots else dists.overlay(sort=False)
            else:
                vdim = self.value_label + ' Density'
                dists = NdOverlay({0: Area([], self.value_label, vdim)},
                                  [self.group_label])
        redim = self._merge_redim(ranges)
        return (dists
                .redim(**redim)
                .relabel(**self._relabel)
                .opts(cur_opts, backend='bokeh')
                .opts(compat_opts, backend=self._backend_compat))

    def density(self, x=None, y=None, data=None):
        return self.kde(x, y, data)

    ##########################
    #      Other charts      #
    ##########################

    def dataset(self, x=None, y=None, data=None):
        data = self.data if data is None else data
        if self.gridded:
            kdims = [self.x, self.y] if len(self.indexes) == 2 else None
            return Dataset(data, kdims=kdims).redim(**self._redim)
        else:
            return Dataset(data, self.kwds.get('columns')).redim(**self._redim)

    def heatmap(self, x=None, y=None, data=None):
        self._error_if_unavailable('heatmap')
        data = self.data if data is None else data
        cur_opts, compat_opts = self._get_compat_opts('HeatMap')

        if not (x or y) or (x == 'columns' and y in ('index', data.index.name)):
            cur_opts['labelled'] = []
            x, y = 'columns', 'index'
            data = (data.columns, data.index, data.values)
            z = ['value']
        else:
            z = self.kwds.get('C', [c for c in data.columns if c not in (x, y)][0])
            z = [z] + self.hover_cols
            self.use_index = False
            data, x, y = self._process_chart_args(data, x, y, single_y=True)

        redim = self._merge_redim({z[0]: self._dim_ranges['c']})
        hmap = HeatMap(data, [x, y], z, **self._relabel)
        if 'reduce_function' in self.kwds:
            hmap = hmap.aggregate(function=self.kwds['reduce_function'])
        return (hmap.redim(**redim)
                .apply(self._set_backends_opts, cur_opts=cur_opts, compat_opts=compat_opts))

    def hexbin(self, x=None, y=None, data=None):
        self._error_if_unavailable('hexbin')
        self.use_index = False
        data, x, y = self._process_chart_args(data, x, y, single_y=True)

        z = [self.kwds['C']] if self.kwds.get('C') else []
        z += self.hover_cols

        cur_opts, compat_opts = self._get_compat_opts('HexTiles')
        if 'reduce_function' in self.kwds:
            cur_opts['aggregator'] = self.kwds['reduce_function']
        if 'gridsize' in self.kwds:
            cur_opts['gridsize'] = self.kwds['gridsize']
        if 'min_count' in self.kwds:
            cur_opts['min_count'] = self.kwds['min_count']
        redim = self._merge_redim({(z[0] if z else 'Count'): self._dim_ranges['c']})
        element = self._get_element('hexbin')
        params = dict(self._relabel)
        if self.geo: params['crs'] = self.crs
        return (element(data, [x, y], z or [], **params).redim(**redim)
                .apply(self._set_backends_opts, cur_opts=cur_opts, compat_opts=compat_opts))

    def bivariate(self, x=None, y=None, data=None):
        self._error_if_unavailable('bivariate')
        self.use_index = False
        data, x, y = self._process_chart_args(data, x, y, single_y=True)

        cur_opts, compat_opts = self._get_compat_opts('Bivariate', **self.kwds)
        element = self._get_element('bivariate')
        return (element(data, [x, y]).redim(**self._redim)
                .apply(self._set_backends_opts, cur_opts=cur_opts, compat_opts=compat_opts))

    def ohlc(self, x=None, y=None, data=None):
        self._error_if_unavailable('ohlc', Rectangles)
        self._error_if_unavailable('ohlc', Segments)
        data = self.data if data is None else data
        if x is None:
            variables = [var for var in self.variables if var not in self.indexes]
            if data[variables[0]].dtype.kind == 'M':
                x = variables[0]
            else:
                x = self.indexes[0]
        width = self.kwds.get('bar_width', 0.5)
        if y is None:
            o, h, l, c = [col for col in data.columns if col != x][:4]
        else:
            o, h, l, c = y
        neg, pos = self.kwds.get('neg_color', 'red'), self.kwds.get('pos_color', 'green')
        color_exp = (dim(o)>dim(c)).categorize({True: neg, False: pos})
        ds = Dataset(data, [x], [o, h, l, c])
        if ds.data[x].dtype.kind in 'SUO':
            rects = Rectangles(ds, [x, o, x, c])
        else:
            if len(ds):
                sampling = np.min(np.diff(ds[x])) * width/2.
                ds = ds.transform(lbound=dim(x)-sampling, ubound=dim(x)+sampling)
            else:
                ds = ds.transform(lbound=dim(x), ubound=dim(x))
            rects = Rectangles(ds, ['lbound', o, 'ubound', c])
        segments = Segments(ds, [x, l, x, h])
        rect_cur_opts, rect_compat_opts = self._get_compat_opts('Rectangles')
        rect_cur_opts.pop('tools')
        rect_cur_opts['color'] = color_exp
        seg_cur_opts, seg_compat_opts = self._get_compat_opts('Segments')
        tools = seg_cur_opts.pop('tools', [])
        if 'hover' in tools:
            tools[tools.index('hover')] = HoverTool(tooltips=[
                (x, '@{%s}' % x), ('Open', '@{%s}' % o), ('High', '@{%s}' % h),
                ('Low', '@{%s}' % l), ('Close', '@{%s}' % c)
            ])
        seg_cur_opts['tools'] = tools
        seg_cur_opts ['color'] = self.kwds.get('line_color', 'black')
        if 'xlabel' not in seg_cur_opts:
            seg_cur_opts['xlabel'] = '' if x == 'index' else x
        if 'ylabel' not in seg_cur_opts:
            seg_cur_opts['ylabel'] = ''
        segments = (
            segments.redim(**self._redim)
            .apply(self._set_backends_opts,
                   cur_opts=seg_cur_opts, compat_opts=seg_compat_opts)
        )
        rects = (
            rects.redim(**self._redim)
            .apply(self._set_backends_opts,
                   cur_opts=rect_cur_opts, compat_opts=rect_compat_opts)
        )
        return segments * rects

    def table(self, x=None, y=None, data=None):
        self._error_if_unavailable('table')
        data = self.data if data is None else data
        if isinstance(data.index, (DatetimeIndex, MultiIndex)):
            data = data.reset_index()

        cur_opts, compat_opts = self._get_compat_opts('Table')
        element = self._get_element('table')
        return (element(data, self.kwds.get('columns'), []).redim(**self._redim)
                .apply(self._set_backends_opts, cur_opts=cur_opts, compat_opts=compat_opts))

    def labels(self, x=None, y=None, data=None):
        self._error_if_unavailable('labels')
        self.use_index = False
        data, x, y = self._process_chart_args(data, x, y, single_y=True)

        text = self.kwds.get('text', [c for c in data.columns if c not in (x, y)][0])
        kdims, vdims = self._get_dimensions([x, y], [text])
        cur_opts, compat_opts = self._get_compat_opts('Labels')
        element = self._get_element('labels')
        return (element(data, kdims, vdims).redim(**self._redim)
                .apply(self._set_backends_opts, cur_opts=cur_opts, compat_opts=compat_opts))

    ##########################
    #     Gridded plots      #
    ##########################

    def _process_gridded_args(self, data, x, y, z):
        data = self.data if data is None else data
        x = x or self.x
        y = y or self.y
        z = z or self.kwds.get('z')

        if is_xarray(data):
            import xarray as xr
            if isinstance(data, xr.DataArray):
                data = data.to_dataset(name=data.name or 'value')
        if is_tabular(data):
            if self.use_index and any(c for c in self.hover_cols if
                                      c in self.indexes and
                                      c not in data.columns):
                data = data.reset_index()
            # calculate any derived time
            dimensions = []
            for dimension in [x, y, self.by, self.hover_cols]:
                if dimension is not None:
                    dimensions.extend(dimension if isinstance(dimension, list) else [dimension])

            not_found = [dim for dim in dimensions if dim not in self.variables]
            _, data = process_derived_datetime_pandas(data, not_found, self.indexes)

        return data, x, y, z

    def _get_element(self, kind):
        element = self._kind_mapping[kind]
        if self.geo:
            import geoviews
            element = getattr(geoviews, element.__name__)
        return element

    def image(self, x=None, y=None, z=None, data=None):
        self._error_if_unavailable('image')
        data, x, y, z = self._process_gridded_args(data, x, y, z)
        if not (x and y):
            x, y = list(data.dims)[::-1]
        if not z:
            z = list(data.data_vars)[0]
        z = [z] + self.hover_cols

        params = dict(self._relabel)
        cur_opts, compat_opts = self._get_compat_opts('Image')
        redim = self._merge_redim({z[0]: self._dim_ranges['c']})

        element = self._get_element('image')
        if self.geo: params['crs'] = self.crs
        return (element(data, [x, y], z, **params).redim(**redim)
                .apply(self._set_backends_opts, cur_opts=cur_opts, compat_opts=compat_opts))

    def rgb(self, x=None, y=None, z=None, data=None):
        self._error_if_unavailable('rgb')
        data, x, y, z = self._process_gridded_args(data, x, y, z)

        coords = [c for c in data.coords if c not in self.by+self.groupby+self.grid]
        if len(coords) < 3:
            raise ValueError('Data must be 3D array to be converted to RGB.')
        x = x or coords[2]
        y = y or coords[1]
        bands = self.kwds.get('bands', coords[0])
        if z is None:
            z = list(data.data_vars)[0]
        data = data[z]
        nbands = len(data.coords[bands])
        if nbands < 3:
            raise ValueError('Selected bands coordinate (%s) has only %d channels,'
                             'expected at least three channels to convert to RGB.' %
                             (bands, nbands))

        params = dict(self._relabel)
        xres, yres = data.attrs['res'] if 'res' in data.attrs else (1, 1)
        xs = data.coords[x][::-1] if xres < 0 else data.coords[x]
        ys = data.coords[y][::-1] if yres < 0 else data.coords[y]
        eldata = (xs, ys)
        for b in range(nbands):
            eldata += (data.isel(**{bands: b}).values,)

        element = self._get_element('rgb')
        cur_opts, compat_opts = self._get_compat_opts('RGB')
        if self.geo: params['crs'] = self.crs
        rgb = element(eldata, [x, y], element.vdims[:nbands], **params)
        return (rgb.redim(**self._redim)
                .apply(self._set_backends_opts, cur_opts=cur_opts, compat_opts=compat_opts))

    def quadmesh(self, x=None, y=None, z=None, data=None):
        self._error_if_unavailable('quadmesh')
        data, x, y, z = self._process_gridded_args(data, x, y, z)

        if not (x and y):
            x, y = list(k for k, v in data.coords.items() if v.size > 1)
        if not z:
            z = list(data.data_vars)[0]
        z = [z] + self.hover_cols

        params = dict(self._relabel)
        redim = self._merge_redim({z[0]: self._dim_ranges['c']})

        element = self._get_element('quadmesh')
        cur_opts, compat_opts = self._get_compat_opts('QuadMesh')
        if self.geo: params['crs'] = self.crs
        return (element(data, [x, y], z, **params).redim(**redim)
                .apply(self._set_backends_opts, cur_opts=cur_opts, compat_opts=compat_opts))

    def contour(self, x=None, y=None, z=None, data=None, filled=False):
        self._error_if_unavailable('contour')
        from holoviews.operation import contours

        if 'projection' in self._plot_opts:
            import cartopy.crs as ccrs
            t = self._plot_opts['projection']
            if isinstance(t, ccrs.CRS) and not isinstance(t, ccrs.Projection):
                raise ValueError('invalid transform:'
                                 ' Spherical contouring is not supported - '
                                 ' consider using PlateCarree/RotatedPole.')

        cur_opts, compat_opts = self._get_compat_opts('Contours')
        qmesh = self.quadmesh(x, y, z, data)

        if self.geo:
            # Apply projection before contouring
            import cartopy.crs as ccrs
            from geoviews import project
            projection = self._plot_opts.get('projection', ccrs.GOOGLE_MERCATOR)
            qmesh = project(qmesh, projection=projection)

        if filled:
            cur_opts['line_alpha'] = 0
        if cur_opts['colorbar']:
            cur_opts['show_legend'] = False
        levels = self.kwds.get('levels', 5)
        if isinstance(levels, int):
            cur_opts['color_levels'] = levels
        return (contours(qmesh, filled=filled, levels=levels)
                .apply(self._set_backends_opts, cur_opts=cur_opts, compat_opts=compat_opts))

    def contourf(self, x=None, y=None, z=None, data=None):
        self._error_if_unavailable('contourf')
        contourf = self.contour(x, y, z, data, filled=True)
        # The holoviews contours operation used in self.contour adapts
        # the value dim range, so we need to redimension it if the user
        # has asked for it by setting `clim`. Internally an unset `clim`
        # is identified by `(None, None)`.
        if self._dim_ranges['c'] != (None, None):
            z_name = contourf.vdims[0].name
            redim = {z_name: self._dim_ranges['c']}
        else:
            redim = {}
        return contourf.redim.range(**redim)

    def vectorfield(self, x=None, y=None, angle=None, mag=None, data=None):
        self._error_if_unavailable('vectorfield')
        data, x, y, _ = self._process_gridded_args(data, x, y, z=None)

        if not (x and y):
            x, y = list(k for k, v in data.coords.items() if v.size > 1)

        angle = self.kwds.get('angle')
        mag = self.kwds.get('mag')
        z = [angle, mag] + self.hover_cols
        redim = self._merge_redim({z[1]: self._dim_ranges['c']})
        params = dict(self._relabel)

        element = self._get_element('vectorfield')
        cur_opts, compat_opts = self._get_compat_opts('VectorField')
        if self.geo: params['crs'] = self.crs
        return (element(data, [x, y], z, **params).redim(**redim)
                .apply(self._set_backends_opts, cur_opts=cur_opts, compat_opts=compat_opts))

    ##########################
    #    Geometry plots      #
    ##########################

    def _geom_plot(self, x=None, y=None, data=None, kind='polygons'):
        data, x, y, _ = self._process_gridded_args(data, x, y, z=None)
        params = dict(self._relabel)

        if not (x and y):
            if is_geodataframe(data):
                x, y = ('Longitude', 'Latitude') if self.geo else ('x', 'y')
            elif self.gridded_data:
                x, y = self.variables[:2:-1]
            else:
                x, y = data.columns[:2]

        redim = self._merge_redim({self._color_dim: self._dim_ranges['c']} if self._color_dim else {})
        kdims, vdims = self._get_dimensions([x, y], [])
        if self.gridded_data:
            vdims = Dataset(data).vdims
        element = self._get_element(kind)
        cur_opts, compat_opts = self._get_compat_opts(element.name)
        for opts_ in [cur_opts, compat_opts]:
            if 'color' in opts_ and opts_['color'] in vdims:
                opts_['color'] = hv.dim(opts_['color'])
        if self.geo: params['crs'] = self.crs
        if self.by:
            obj = Dataset(data).to(element, kdims, vdims, self.by, **params).overlay(sort=False)
        else:
            obj = element(data, kdims, vdims, **params)

        return (obj.redim(**redim)
                .opts({element.name: cur_opts}, backend='bokeh')
                .opts({element.name: compat_opts}, backend=self._backend_compat))

    def polygons(self, x=None, y=None, data=None):
        self._error_if_unavailable('polygons')
        return self._geom_plot(x, y, data, kind='polygons')

    def paths(self, x=None, y=None, data=None):
        self._error_if_unavailable('paths')
        return self._geom_plot(x, y, data, kind='paths')

    def points(self, x=None, y=None, data=None):
        self._error_if_unavailable('points')
        return self._geom_plot(x, y, data, kind='points')
