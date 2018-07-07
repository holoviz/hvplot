from __future__ import absolute_import

from functools import partial
import difflib

import param
import holoviews as hv
import pandas as pd
import numpy as np

from holoviews.core.dimension import Dimension
from holoviews.core.spaces import DynamicMap, HoloMap, Callable
from holoviews.core.overlay import NdOverlay
from holoviews.core.options import Store, Cycle
from holoviews.core.layout import NdLayout
from holoviews.element import (
    Curve, Scatter, Area, Bars, BoxWhisker, Dataset, Distribution,
    Table, HeatMap, Image, HexTiles, QuadMesh, Bivariate, Histogram,
    Violin, Contours, Polygons, Points, Path
)
from holoviews.plotting.util import process_cmap
from holoviews.operation import histogram
from holoviews.streams import Buffer, Pipe

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



class HoloViewsConverter(param.Parameterized):

    _gridded_types = ['image', 'contour', 'contourf', 'quadmesh']

    _stats_types = ['hist', 'kde', 'violin', 'box']

    _data_options = ['x', 'y', 'kind', 'by', 'use_index', 'use_dask',
                     'dynamic', 'crs', 'value_label', 'group_label',
                     'backlog', 'persist']

    _axis_options = ['width', 'height', 'shared_axes', 'grid', 'legend',
                     'rot', 'xlim', 'ylim', 'xticks', 'yticks', 'colorbar',
                     'invert', 'title', 'logx', 'logy', 'loglog', 'xaxis',
                     'yaxis']

    _style_options = ['color', 'alpha', 'colormap', 'fontsize', 'c']

    _op_options = ['datashade', 'rasterize', 'xsampling', 'ysampling', 'aggregator']

    _kind_options = {
        'scatter'  : ['s', 'marker', 'c', 'scale', 'logz'],
        'step'     : ['where'],
        'area'     : ['y2'],
        'hist'     : ['bins', 'bin_range', 'normed', 'cumulative'],
        'heatmap'  : ['C', 'reduce_function', 'logz'],
        'hexbin'   : ['C', 'reduce_function', 'gridsize', 'logz'],
        'dataset'  : ['columns'],
        'table'    : ['columns'],
        'image'    : ['z', 'logz'],
        'quadmesh' : ['z', 'logz'],
        'contour'  : ['z', 'levels', 'logz'],
        'contourf' : ['z', 'levels', 'logz'],
        'points'   : ['s', 'marker', 'c', 'scale', 'logz'],
        'polygons'    : ['logz', 'c']
    }

    _kind_mapping = {
        'line': Curve, 'scatter': Scatter, 'heatmap': HeatMap,
        'bivariate': Bivariate, 'quadmesh': QuadMesh, 'hexbin': HexTiles,
        'image': Image, 'table': Table, 'hist': Histogram, 'dataset': Dataset,
        'kde': Distribution, 'area': Area, 'box': BoxWhisker, 'violin': Violin,
        'bar': Bars, 'barh': Bars, 'contour': Contours, 'contourf': Polygons,
        'points': Points, 'polygons': Polygons, 'paths': Path, 'step': Curve
    }

    _colorbar_types = ['image', 'hexbin', 'heatmap', 'quadmesh', 'bivariate',
                       'contour', 'contourf', 'polygons']

    def __init__(self, data, x, y, kind=None, by=None, use_index=True,
                 group_label='Variable', value_label='value',
                 backlog=1000, persist=False, use_dask=False,
                 crs=None, fields={}, groupby=None, dynamic=True,
                 width=700, height=300, shared_axes=True,
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
                 dynspread=False, hover_cols=[], **kwds):

        # Process data and related options
        self._process_data(kind, data, x, y, by, groupby, row, col,
                           use_dask, persist, backlog, label, value_label,
                           hover_cols, kwds)
        self.use_index = use_index
        self.value_label = value_label
        self.group_label = group_label
        self.dynamic = dynamic
        self.geo = geo or crs or global_extent or projection
        self.crs = process_crs(crs) if self.geo else None
        self.row = row
        self.col = col

        # Operations
        self.datashade = datashade
        self.rasterize = rasterize
        self.dynspread = dynspread
        self.aggregator = aggregator
        self.precompute = precompute

        # By type
        self.subplots = subplots
        self._by_type = NdLayout if subplots else NdOverlay

        # Process options
        style_opts, plot_opts, kwds = self._process_style(colormap, kwds)
        self.stacked = stacked
        self.invert = invert
        plot_opts['logx'] = logx or loglog
        plot_opts['logy'] = logy or loglog
        plot_opts['show_grid'] = grid
        plot_opts['shared_axes'] = shared_axes
        plot_opts['show_legend'] = legend
        if xticks:
            plot_opts['xticks'] = xticks
        if yticks:
            plot_opts['yticks'] = yticks
        if not xaxis:
            plot_opts['xaxis'] = None
        if not yaxis:
            plot_opts['yaxis'] = None
        if flip_xaxis:
            plot_opts['invert_xaxis'] = True
        if flip_yaxis:
            plot_opts['invert_yaxis'] = True
        if width:
            plot_opts['width'] = width
        if height:
            plot_opts['height'] = height
        if fontsize:
            plot_opts['fontsize'] = fontsize
        if isinstance(colorbar, bool):
            plot_opts['colorbar'] = colorbar
        elif self.kind in self._colorbar_types:
            plot_opts['colorbar'] = True
        if invert:
            plot_opts['invert_axes'] = kind != 'barh'
        if rot:
            axis = 'yrotation' if invert else 'xrotation'
            plot_opts[axis] = rot
        if hover:
            plot_opts['tools'] = ['hover']

        if self.crs and global_extent:
            plot_opts['global_extent'] = global_extent
        if projection:
            plot_opts['projection'] = process_crs(projection)
        plot_opts['legend_position'] = 'right'
        if title is not None:
            plot_opts['title_format'] = title
        self._plot_opts = plot_opts
        options = Store.options(backend='bokeh')
        el_type = self._kind_mapping[self.kind].__name__
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
        self._dim_ranges = {'x': xlim or (None, None),
                            'y': ylim or (None, None),
                            'c': clim or (None, None)}
        self._redim = fields

        # High-level options
        self._validate_kwds(kwds)
        if debug:
            kwds = dict(x=self.x, y=self.y, by=self.by, kind=self.kind,
                        groupby=self.groupby)
            self.warning('Plotting {kind} plot with parameters x: {x}, '
                         'y: {y}, by: {by}, groupby: {groupby}'.format(**kwds))


    def _process_data(self, kind, data, x, y, by, groupby, row, col,
                      use_dask, persist, backlog, label, value_label,
                      hover_cols, kwds):
        gridded = kind in self._gridded_types
        gridded_data = False

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
            if is_geopandas(data) and kind is None:
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
            self.data = data.persist() if persist else data
        elif is_streamz(data):
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
            dims = [c for c in data.coords if data[c].shape != ()
                    and c not in ignore]
            if kind is None and (not (x or y) or all(c in data.coords for c in (x, y))):
                if len(dims) == 1:
                    kind = 'line'
                elif len(dims) == 2 or (x and y):
                    kind = 'image'
                    gridded = True
                else:
                    kind = 'hist'

            if gridded:
                gridded_data = True
            data, x, y, by_new, groupby_new = process_xarray(data, x, y, by, groupby,
                                                             use_dask, persist, gridded,
                                                             label, value_label)

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

        if gridded:
            if not gridded_data:
                raise ValueError('%s plot type requires gridded data, '
                                 'e.g. a NumPy array or xarray Dataset, '
                                 'found %s type' % (kind, type(self.data).__name__))
            not_found = [g for g in groupby if g not in data.coords]
            data_vars = list(data.data_vars) if isinstance(data, xr.Dataset) else [data.name]
            indexes = list(data.coords)
            self.variables = list(data.coords) + data_vars
            if groupby and not_found:
                raise ValueError('The supplied groupby dimension(s) %s '
                                 'could not be found, expected one or '
                                 'more of: %s' % (not_found, list(data.coords)))
        else:
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
            renamed = {c: str(c) for c in data.columns if not isinstance(c, hv.util.basestring)}
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
        self.gridded = gridded
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


    def _process_style(self, colormap, kwds):
        style_opts, plot_options = {}, {}
        kind = self.kind

        # Process style options
        if 'cmap' in kwds and colormap:
            raise TypeError("Only specify one of `cmap` and `colormap`.")
        elif 'cmap' in kwds:
            cmap = kwds.pop('cmap')
        else:
            cmap = colormap

        if 'color' in kwds or 'c' in kwds:
            color = kwds.pop('color', kwds.pop('c', None))
            if isinstance(color, (np.ndarray, pd.Series)):
                self.data['_color'] = color
                kwds['c'] = '_color'
            elif isinstance(color, list):
                style_opts['color'] = color
            else:
                style_opts['color'] = color
                if 'c' in self._kind_options.get(kind, []) and (color in self.variables):
                    kwds['c'] = color
                    if self.data[color].dtype.kind in 'OSU':
                        cmap = cmap or 'Category10'
                    else:
                        plot_options['colorbar'] = True
        if 'size' in kwds or 's' in kwds:
            size = kwds.pop('size', kwds.pop('s', None))
            if isinstance(size, (np.ndarray, pd.Series)):
                self.data['_size'] = np.sqrt(size)
                kwds['s'] = '_size'
            elif isinstance(size, hv.util.basestring):
                kwds['s'] = size
                if 'scale' in kwds:
                    style_opts['size'] = kwds['scale']
            else:
                style_opts['size'] = np.sqrt(size)
        else:
            style_opts['size'] = np.sqrt(30)
        if 'alpha' in kwds:
            style_opts['alpha'] = kwds.pop('alpha')
        if cmap:
            style_opts['cmap'] = cmap
        if 'logz' in kwds:
            plot_options['logz'] = kwds['logz']
        return style_opts, plot_options, kwds


    def _validate_kwds(self, kwds):
        kind_opts = self._kind_options.get(self.kind, [])
        ds_opts = ['max_px', 'threshold']
        mismatches = sorted([k for k in kwds if k not in kind_opts+ds_opts])
        if not mismatches:
            return

        if 'ax' in mismatches:
            mismatches.pop(mismatches.index('ax'))
            self.warning('hvPlot does not have the concept of axes, '
                         'and the ax keyword will be ignored. Compose '
                         'plots with the * operator to overlay plots '
                         '+ operator to lay out plots beside each other '
                         'instead.')
        if 'figsize' in mismatches:
            mismatches.pop(mismatches.index('figsize'))
            self.warning('hvPlot does not have the concept of a figure, '
                         'and the figsize keyword will be ignored. The '
                         'size of each subplot in a layout is set '
                         'individually using the width and height options.')

        combined_opts = (self._data_options + self._axis_options +
                         self._style_options + self._op_options + kind_opts)
        for mismatch in mismatches:
            suggestions = difflib.get_close_matches(mismatch, combined_opts)
            self.warning('%s option not found for %s plot, similar options '
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
            dataset = Dataset(data)
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

        if not (self.datashade or self.rasterize):
            return obj

        try:
            from holoviews.operation.datashader import datashade, rasterize, dynspread
            from datashader import count_cat
        except:
            raise ImportError('Datashading is not available')

        opts = dict(width=self._plot_opts['width'], height=self._plot_opts['height'],
                    dynamic=self.dynamic)
        if 'cmap' in self._style_opts and self.datashade:
            levels = self._plot_opts.get('color_levels')
            opts['cmap'] = process_cmap(self._style_opts['cmap'], levels)
            opts['color_key'] = opts['cmap']
        if self.by:
            opts['aggregator'] = count_cat(self.by[0])
        if self.aggregator:
            opts['aggregator'] = self.aggregator
        if self.precompute:
            opts['precompute'] = self.precompute
        style = {}
        if self.datashade:
            operation = datashade
            eltype = 'RGB'
        else:
            operation = rasterize
            eltype = 'Image'
            if 'cmap' in self._style_opts:
                style['cmap'] = self._style_opts['cmap']

        if self.crs:
            # Apply projection before rasterizing
            import cartopy.crs as ccrs
            from geoviews import project
            projection = self._plot_opts.get('projection', ccrs.GOOGLE_MERCATOR)
            obj = project(obj, projection=projection)

        processed = operation(obj, **opts)

        if self.dynspread:
            if self.datashade:
                processed = dynspread(processed, max_px=self.kwds.get('max_px', 3),
                                      threshold=self.kwds.get('threshold', 0.5))
            else:
                self.warning('dynspread may only be applied on datashaded plots, '
                             'use datashade=True instead of rasterize=True.')
        return processed.opts({eltype: {'plot': self._plot_opts, 'style': style}})


    def dataset(self, x=None, y=None, data=None):
        data = self.data if data is None else data
        return Dataset(data, self.kwds.get('columns'), []).redim(**self._redim)


    ##########################
    #     Simple charts      #
    ##########################

    def single_chart(self, element, x, y, data=None):
        labelled = ['y' if self.invert else 'x'] if x != 'index' else []
        if not self.is_series:
            labelled.append('x' if self.invert else 'y')
        elif not self.label:
            self._relabel['label'] = y

        opts = {element.__name__: dict(
            plot=dict(self._plot_opts, labelled=labelled),
            norm=self._norm_opts, style=self._style_opts
        )}
        ranges = {y: self._dim_ranges['y']}
        if x:
            ranges[x] = self._dim_ranges['x']

        data = self.data if data is None else data
        ys = [y]
        if element is Area and self.kwds.get('y2'):
            ys += [self.kwds['y2']]
        for p in 'cs':
            if p in self.kwds and self.kwds[p] in data.columns:
                ys += [self.kwds[p]]
        ys += self.hover_cols

        if self.by:
            if element is Bars:
                return element(data, [x]+self.by, ys).relabel(**self._relabel).redim.range(**ranges).redim(**self._redim).opts(opts)
            chart = Dataset(data, self.by+[x], ys).to(element, x, ys, self.by).relabel(**self._relabel)
            chart = chart.layout() if self.subplots else chart.overlay().options(batched=False)
        else:
            chart = element(data, x, ys).relabel(**self._relabel)
        return chart.redim.range(**ranges).redim(**self._redim).opts(opts)

    def _process_args(self, data, x, y):
        data = (self.data if data is None else data)
        x = x or self.x
        if not x and self.use_index:
            x = self.indexes[0]
        elif not x:
            raise ValueError('Could not determine what to plot. Expected '
                             'x to be declared or use_index to be enabled.')

        y = y or self.y
        if not y:
            ys = [c for c in data.columns if c not in [x]+self.by+self.groupby]
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
        opts = dict(plot=dict(self._plot_opts, labelled=labelled),
                    norm=self._norm_opts, style=self._style_opts)
        charts = []
        for c in y:
            chart = element(data, x, [c]+self.hover_cols).redim(**{c: self.value_label})
            ranges = {x: self._dim_ranges['x'], self.value_label: self._dim_ranges['y']}
            charts.append((c, chart.relabel(**self._relabel)
                           .redim.range(**ranges).opts(**opts)))
        return self._by_type(charts, self.group_label, sort=False).options('NdOverlay', batched=False)

    def line(self, x, y, data=None):
        return self.chart(Curve, x, y, data)

    def step(self, x, y, data=None):
        where = self.kwds.get('where', 'mid')
        return self.line(x, y, data).options('Curve', interpolation='steps-'+where)

    def scatter(self, x, y, data=None):
        scatter = self.chart(Scatter, x, y, data)
        opts = {}
        if 'c' in self.kwds:
            opts['color_index'] = self.kwds['c']
        if 's' in self.kwds:
            opts['size_index'] = self.kwds['s']
        if 'marker' in self.kwds:
            opts['marker'] = self.kwds['marker']
        return scatter.options('Scatter', **opts) if opts else scatter

    def area(self, x, y, data=None):
        areas = self.chart(Area, x, y, data)
        if self.stacked:
            areas = areas.map(Area.stack, NdOverlay)
        return areas

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

        opts = {'plot': dict(self._plot_opts, labelled=labelled),
                'style': dict(self._style_opts),
                'norm': self._norm_opts}
        ranges = {self.value_label: self._dim_ranges['y']}

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
        return (element(df, kdims, [self.value_label]+self.hover_cols).redim.range(**ranges)
                .redim(**self._redim).relabel(**self._relabel).opts(**opts))

    def bar(self, x, y, data=None):
        data, x, y = self._process_args(data, x, y)
        if x and y and not isinstance(y, (list, tuple)):
            return self.single_chart(Bars, x, y, data)
        elif x and y and len(y) == 1:
            return self.single_chart(Bars, x, y[0], data)
        stack_index = 1 if self.stacked else None
        opts = {'Bars': {'stack_index': stack_index, 'show_legend': bool(stack_index)}}
        return self._category_plot(Bars, x, list(y), data).opts(plot=opts)

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

        opts = {'plot': dict(self._plot_opts), # labelled=[]),
                'norm': self._norm_opts, 'style': self._style_opts}
        if not isinstance(y, (list, tuple)):
            ranges = {y: self._dim_ranges['y']}
            return (element(data, self.by, y).redim.range(**ranges)
                .relabel(**self._relabel).opts(**opts))

        labelled = ['y' if self.invert else 'x'] if self.group_label != 'Group' else []
        if self.value_label != 'value':
            labelled.append('x' if self.invert else 'y')
        opts['plot']['labelled'] = labelled

        kdims = [self.group_label]
        ranges = {self.value_label: self._dim_ranges['y']}
        data = data[list(y)]
        if check_library(data, 'dask'):
            from dask.dataframe import melt
        else:
            melt = pd.melt
        df = melt(data, var_name=self.group_label, value_name=self.value_label)
        return (element(df, kdims, self.value_label).redim.range(**ranges)
                .redim(**self._redim).relabel(**self._relabel).opts(**opts))

    def box(self, x, y, data=None):
        return self._stats_plot(BoxWhisker, y, data)

    def violin(self, x, y, data=None):
        try:
            from holoviews.element import Violin
        except ImportError:
            raise ImportError('Violin plot requires HoloViews version >=1.10')
        return self._stats_plot(Violin, y, data)

    def hist(self, x, y, data=None):
        data, x, y = self._process_args(data, x, y)

        labelled = ['y'] if self.invert else ['x']
        plot_opts = dict(self._plot_opts, labelled=labelled)
        opts = dict(plot=plot_opts, style=self._style_opts,
                    norm=self._norm_opts)
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
            if self.stacked and not self.subplots and not 'bin_range' in self.kwds:
                ys = data[y]
                hist_opts['bin_range'] = (ys.min(), ys.max())

            ds = Dataset(data, self.by, y)
            hist = hists = histogram(ds.to(Dataset, [], y, self.by), **hist_opts)
            if self.by:
                hist = hists.last
                hists = hists.layout() if self.subplots else hists.overlay()
            ranges = {hist.kdims[0].name: self._dim_ranges['x'],
                      hist.vdims[0].name: self._dim_ranges['y']}
            return hists.opts({'Histogram': opts}).redim(**self._redim).redim.range(**ranges)

        ds = Dataset(data)
        hists = []
        for col in y:
            hist = histogram(ds, dimension=col, **hist_opts)
            ranges = {hist.kdims[0].name: self._dim_ranges['x'],
                      hist.vdims[0].name: self._dim_ranges['y']}
            hists.append((col, hist.redim.range(**ranges)
                          .relabel(**self._relabel).opts(**opts)))
        return self._by_type(hists, sort=False).redim(**self._redim)

    def kde(self, x, y, data=None):
        data, x, y = self._process_args(data, x, y)
        opts = dict(plot=self._plot_opts, style=self._style_opts, norm=self._norm_opts)
        opts = {'Distribution': opts, 'Area': opts,
                'NdOverlay': {'plot': dict(self._plot_opts, legend_limit=0)}}

        if not isinstance(y, (list, tuple)):
            ranges = {y: self._dim_ranges['x']}
            if self.by:
                dists = Dataset(data).to(Distribution, y, [], self.by)
                dists = dists.layout() if self.subplots else dists.overlay()
            else:
                dists = Distribution(data, y, [])
        else:
            ranges = {self.value_label: self._dim_ranges['x']}
            data = data[y]
            df = pd.melt(data, var_name=self.group_label, value_name=self.value_label)
            ds = Dataset(df)
            if len(df):
                dists = ds.to(Distribution, self.value_label).overlay()
            else:
                vdim = self.value_label + ' Density'
                dists = NdOverlay({0: Area([], self.value_label, vdim)},
                                  [self.group_label])
        return dists.redim(**self._redim).redim.range(**ranges).relabel(**self._relabel).opts(opts)


    ##########################
    #      Other charts      #
    ##########################

    def heatmap(self, x, y, data=None):
        data = self.data if data is None else data
        if not x: x = self.x or data.columns[0]
        if not y: y = self.y or data.columns[1]
        z = self.kwds.get('C', [c for c in data.columns if c not in (x, y)][0])
        z = [z] + self.hover_cols

        opts = dict(plot=self._plot_opts, norm=self._norm_opts, style=self._style_opts)
        hmap = HeatMap(data, [x, y], z).redim(**self._redim).opts(**opts)
        if 'reduce_function' in self.kwds:
            return hmap.aggregate(function=self.kwds['reduce_function'])
        return hmap

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
        return HexTiles(data, [x, y], z or []).redim(**self._redim).opts(**opts)

    def bivariate(self, x, y, data=None):
        data = self.data if data is None else data
        if not x: x = data.columns[0]
        if not y: y = data.columns[1]

        opts = dict(plot=self._plot_opts, norm=self._norm_opts, style=self._style_opts)
        return Bivariate(data, [x, y]).redim(**self._redim).opts(**opts)

    def table(self, x=None, y=None, data=None):
        allowed = ['width', 'height']
        opts = {k: v for k, v in self._plot_opts.items() if k in allowed}
        data = self.data if data is None else data
        return Table(data, self.kwds.get('columns'), []).redim(**self._redim).opts(plot=opts)

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
        ranges = {x: self._dim_ranges['x'], y: self._dim_ranges['y'], z[0]: self._dim_ranges['c']}

        element = self._get_element('image')
        if self.geo: params['crs'] = self.crs
        return element(data, [x, y], z, **params).redim(**self._redim).redim.range(**ranges).opts(**opts)

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
        ranges = {x: self._dim_ranges['x'], y: self._dim_ranges['y'], z[0]: self._dim_ranges['c']}

        element = self._get_element('quadmesh')
        if self.geo: params['crs'] = self.crs
        return element(data, [x, y], z, **params).redim(**self._redim).redim.range(**ranges).opts(**opts)

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

        x = x or self.x
        y = y or self.y
        if hasattr(data, 'geom_type') and not (x and y):
            x, y = 'Longitude', 'Latitude'

        plot_opts = dict(self._plot_opts)
        ranges = {x: self._dim_ranges['x'], y: self._dim_ranges['y']}
        if 'c' in self.kwds:
            plot_opts['color_index'] = self.kwds['c']
            ranges[self.kwds['c']] = self._dim_ranges['c']
        if 's' in self.kwds:
            plot_opts['size_index'] = self.kwds['s']
        if 'marker' in self.kwds:
            plot_opts['marker'] = self.kwds['marker']
        opts = dict(plot=plot_opts, style=self._style_opts, norm=self._norm_opts)

        element = self._get_element('points')
        if self.geo: params['crs'] = self.crs
        vdims = [self.kwds['c']] if 'c' in self.kwds else []
        if 's' in self.kwds:
            vdims.append(self.kwds['s'])
        vdims = vdims + self.hover_cols
        params['vdims'] = vdims
        return element(data, [x, y], **params).redim(**self._redim).redim.range(**ranges).opts(**opts)

    ##########################
    #    Geometry plots      #
    ##########################

    def _geom_plot(self, x=None, y=None, data=None, kind='polygons'):
        data = self.data if data is None else data
        try:
            import geopandas as gpd
        except:
            raise ImportError('Geometry plots require geopandas, ensure '
                              'it is installed.')
        if not isinstance(data, gpd.GeoDataFrame):
            raise ValueError('Geometry plots only supported on geopandas '
                             'GeoDataFrame objects.')
        params = dict(self._relabel)

        x = x or self.x
        y = y or self.y
        if hasattr(data, 'geom_type') and not (x and y):
            x, y = 'Longitude', 'Latitude'

        plot_opts = dict(self._plot_opts)
        ranges = {x: self._dim_ranges['x'], y: self._dim_ranges['y']}
        if 'c' in self.kwds:
            plot_opts['color_index'] = self.kwds['c']
            ranges[self.kwds['c']] = self._dim_ranges['c']
        plot_opts['show_legend'] = False
        opts = dict(plot=plot_opts, style=self._style_opts, norm=self._norm_opts)

        element = self._get_element(kind)
        if self.geo: params['crs'] = self.crs
        params['vdims'] = [c for c in data.columns if c != 'geometry']
        return element(data, [x, y], **params).redim(**self._redim).redim.range(**ranges).opts(**opts)

    def polygons(self, x=None, y=None, data=None):
        return self._geom_plot(x, y, data, kind='polygons')

    def paths(self, x=None, y=None, data=None):
        return self._geom_plot(x, y, data, kind='paths')
