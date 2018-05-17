from __future__ import absolute_import

from functools import partial
from distutils.version import LooseVersion
import difflib

import param
import holoviews as hv
import pandas as pd
import numpy as np

from holoviews.core.spaces import DynamicMap, Callable
from holoviews.core.overlay import NdOverlay
from holoviews.core.options import Store, Cycle
from holoviews.core.layout import NdLayout
from holoviews.element import (
    Curve, Scatter, Area, Bars, BoxWhisker, Dataset, Distribution,
    Table, HeatMap, Image, HexTiles, QuadMesh, Bivariate, Histogram,
    Violin, Contours, Polygons
)
from holoviews.plotting.util import process_cmap
from holoviews.operation import histogram
from holoviews.streams import Buffer, Pipe

try:
    import bokeh
    if LooseVersion(bokeh.__version__) <= '0.12.14':
        import warnings
        # Ignore NumPy future warnings triggered by bokeh
        warnings.simplefilter(action='ignore', category=FutureWarning)
except:
    pass

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


def process_xarray(data, x, y, by, groupby, use_dask, persist, gridded):
    import xarray as xr
    dataset = data
    data_vars = list(dataset.data_vars) if isinstance(data, xr.Dataset) else [data.name]
    ignore = (by or []) + (groupby or [])
    dims = [c for c in data.coords if data[c].shape != () and c not in ignore][::-1]

    if gridded:
        data = dataset
        if not (x or y):
            x, y = dims[:2]
        elif x and not y:
            y = [d for d in dims if d != x][0]
        elif y and not x:
            x = [d for d in dims if d != y][0]
        if len(dims) > 2 and not groupby:
            groupby = [d for d in dims if d not in (x, y)]
    else:
        if use_dask:
            dataset = dataset if isinstance(dataset, xr.Dataset) else dataset.to_dataset()
            data = dataset.to_dask_dataframe()
            data = data.persist() if persist else data
        else:
            data = dataset.to_dataframe()
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

    _op_options = ['datashade', 'rasterize', 'xsampling', 'ysampling']

    _kind_options = {
        'scatter'  : ['s', 'marker', 'c', 'scale'],
        'hist'     : ['bins', 'bin_range', 'normed'],
        'heatmap'  : ['C', 'reduce_function'],
        'hexbin'   : ['C', 'reduce_function', 'gridsize'],
        'dataset'  : ['columns'],
        'table'    : ['columns'],
        'image'    : ['z'],
        'quadmesh' : ['z'],
        'contour'  : ['z', 'levels'],
        'contourf'  : ['z', 'levels']
    }

    _kind_mapping = {
        'line': Curve, 'scatter': Scatter, 'heatmap': HeatMap,
        'bivariate': Bivariate, 'quadmesh': QuadMesh, 'hexbin': HexTiles,
        'image': Image, 'table': Table, 'hist': Histogram, 'dataset': Dataset,
        'kde': Distribution, 'area': Area, 'box': BoxWhisker, 'violin': Violin,
        'bar': Bars, 'barh': Bars, 'contour': Contours, 'contourf': Polygons
    }

    _colorbar_types = ['image', 'hexbin', 'heatmap', 'quadmesh', 'bivariate',
                       'contours']

    def __init__(self, data, x, y, kind=None, by=None, use_index=True,
                 group_label='Group', value_label='value',
                 backlog=1000, persist=False, use_dask=False,
                 crs=None, fields={}, groupby=None, dynamic=True,
                 width=700, height=300, shared_axes=True,
                 grid=False, legend=True, rot=None, title=None,
                 xlim=None, ylim=None, xticks=None, yticks=None,
                 logx=False, logy=False, loglog=False, hover=True,
                 subplots=False, label=None, invert=False,
                 stacked=False, colorbar=None, fontsize=None,
                 colormap=None, datashade=False, rasterize=False,
                 row=None, col=None, figsize=None, debug=False,
                 xaxis=True, yaxis=True, framewise=True, **kwds):

        # Process data and related options
        self._process_data(kind, data, x, y, by, groupby, row, col,
                           use_dask, persist, backlog, kwds)
        self.use_index = use_index
        self.value_label = value_label
        self.group_label = group_label
        self.dynamic = dynamic
        self.crs = crs
        self.row = row
        self.col = col

        # Operations
        self.datashade = datashade
        self.rasterize = rasterize

        # By type
        self.subplots = subplots
        self._by_type = NdLayout if subplots else NdOverlay

        # Process options
        style_opts, plot_opts, kwds = self._process_style(kind, colormap, kwds)
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
                cycle = process_cmap(colormap or 'Category10', categorical=True)
            elif not isinstance(color, (Cycle, list)):
                continue
            style_opts[opt] = Cycle(values=cycle) if isinstance(cycle, list) else cycle
        self._style_opts = style_opts
        self._norm_opts = {'framewise': framewise, 'axiswise': not shared_axes}
        self.kwds = kwds

        # Process dimensions and labels
        self.label = label
        self._relabel = {'label': label} if label else {}
        self._dim_ranges = {'x': xlim or (None, None),
                            'y': ylim or (None, None)}
        self._redim = fields

        # High-level options
        self._validate_kwds(kwds)
        if debug:
            kwds = dict(x=self.x, y=self.y, by=self.by, kind=self.kind,
                        groupby=self.groupby)
            self.warning('Plotting {kind} plot with parameters x: {x}, '
                         'y: {y}, by: {by}, groupby: {groupby}'.format(**kwds))


    def _process_data(self, kind, data, x, y, by, groupby, row, col, use_dask, persist, backlog, kwds):
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
            if gridded and isinstance(data, xr.Dataset):
                data = data[kwds.get('z', list(data.data_vars)[0])]

            ignore = (groupby or []) + (by or [])
            dims = [c for c in data.coords if data[c].shape != ()
                    and c not in ignore]
            if kind is None and not (x or y):
                if len(dims) == 1:
                    kind = 'line'
                elif len(dims) == 2:
                    kind = 'image'
                    gridded = True
                else:
                    kind = 'hist'

            if gridded:
                gridded_data = True
            data, x, y, by_new, groupby_new = process_xarray(data, x, y, by, groupby,
                                                             use_dask, persist, gridded)
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
                    indexes = self.data.index.names
            else:
                indexes = [data.index.name or 'index']

            # Rename non-string columns
            renamed = {c: str(c) for c in data.columns if not isinstance(c, hv.util.basestring)}
            if renamed:
                self.data = self.data.rename(columns=renamed)

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
        self.use_dask = use_dask
        if isinstance(by, (np.ndarray, pd.Series)):
            self.data['by'] = by
            self.by = ['by']
        elif not by:
            self.by = []
        else:
            self.by = by if isinstance(by, list) else [by]
        self.groupby = groupby
        self.streaming = streaming


    def _process_style(self, kind, colormap, kwds):
        style_opts, plot_options = {}, {}

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
                if 'c' in self._kind_options.get(kind, []):
                    kwds['c'] = color
                    if (color in self.data.columns):
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
        return style_opts, plot_options, kwds


    def _validate_kwds(self, kwds):
        kind_opts = self._kind_options.get(self.kind, [])
        mismatches = sorted([k for k in kwds if k not in kind_opts])
        if not mismatches:
            return
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
        grid = []
        if self.row: grid.append(self.row)
        if self.col: grid.append(self.col)
        groups += grid
        if groups:
            if self.streaming:
                raise NotImplementedError("Streaming and groupby not yet implemented")
            else:
                dataset = Dataset(self.data).groupby(self.groupby, dynamic=self.dynamic)
                obj = dataset.map(lambda ds: getattr(self, kind)(x, y, data=ds.data), [Dataset])
            if grid:
                obj = obj.grid(grid).options(shared_xaxis=True, shared_yaxis=True)
        else:
            if self.streaming:
                cbcallable = StreamingCallable(partial(method, x, y),
                                               periodic=self.cb)
                obj = DynamicMap(cbcallable, streams=[self.stream])
            else:
                obj = method(x, y)

        if not self.datashade or self.rasterize:
            return obj

        try:
            from holoviews.operation.datashader import datashade, rasterize
            from datashader import count_cat
        except:
            raise ImportError('Datashading is not available')

        opts = dict(width=self._plot_opts['width'], height=self._plot_opts['height'])
        if 'cmap' in self._style_opts and self.datashade:
            opts['cmap'] = self._style_opts['cmap']
        if self.by:
            opts['aggregator'] = count_cat(self.by[0])
        operation = datashade if self.datashade else rasterize
        return operation(obj, **opts).opts(plot=self._plot_opts)


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
        for p in 'cs':
            if p in self.kwds and self.kwds[p] in data.columns:
                ys += [self.kwds[p]]

        if self.by:
            chart = Dataset(data, self.by+[x], ys).to(element, x, ys, self.by).relabel(**self._relabel)
            chart = chart.layout() if self.subplots else chart.overlay()
        else:
            chart = element(data, x, ys).relabel(**self._relabel)
        return chart.redim.range(**ranges).redim(**self._redim).opts(opts)

    def _process_args(self, data, x, y):
        data = (self.data if data is None else data)
        x = x or self.x
        if not x and self.use_index:
            x = data.index.name or 'index'
        elif not x:
            raise ValueError('Could not determine what to plot. Expected '
                             'x to be declared or use_index to be enabled.')
        y = y or self.y
        if not y:
            if len(data.columns) == 1:
                y = data.columns[0]
            else:
                y = [c for c in data.columns if c != x]
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
            chart = element(data, x, c).redim(**{c: self.value_label})
            ranges = {x: self._dim_ranges['x'], self.value_label: self._dim_ranges['y']}
            charts.append((c, chart.relabel(**self._relabel)
                           .redim.range(**ranges).opts(**opts)))
        return self._by_type(charts, self.group_label, sort=False)

    def line(self, x, y, data=None):
        return self.chart(Curve, x, y, data)

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
        if any((v in [data.index.names]+['index']) or v == data.index.name for v in id_vars):
            data = data.reset_index()
        data = data[y+[x]]

        if check_library(data, 'dask'):
            from dask.dataframe import melt
        else:
            melt = pd.melt

        df = melt(data, id_vars=[x], var_name=self.group_label, value_name=self.value_label)
        kdims = [x, self.group_label]
        return (element(df, kdims, self.value_label).redim.range(**ranges)
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
        hist_opts = {'num_bins': self.kwds.get('bins', 10),
                     'bin_range': self.kwds.get('bin_range', None),
                     'normed': self.kwds.get('normed', False)}

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
        if not x: x = data.columns[0]
        if not y: y = data.columns[1]
        z = self.kwds.get('C', data.columns[2])

        opts = dict(plot=self._plot_opts, norm=self._norm_opts, style=self._style_opts)
        hmap = HeatMap(data, [x, y], z).redim(**self._redim).opts(**opts)
        if 'reduce_function' in self.kwds:
            return hmap.aggregate(function=self.kwds['reduce_function'])
        return hmap

    def hexbin(self, x, y, data=None):
        data = self.data if data is None else data
        if not x: x = data.columns[0]
        if not y: y = data.columns[1]
        z = self.kwds.get('C')

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

    def image(self, x=None, y=None, data=None):
        import xarray as xr
        data = self.data if data is None else data

        z = self.kwds.get('z')
        x = x or self.x
        y = y or self.y
        if not (x and y):
            x, y = list(data.dims)[::-1]
        if not z:
            z = list(data.data_vars)[0] if isinstance(data, xr.Dataset) else [data.name]

        params = dict(self._relabel)
        opts = dict(plot=self._plot_opts, style=self._style_opts, norm=self._norm_opts)

        element = Image
        if self.crs is not None:
            try:
                from geoviews import Image as element
            except:
                raise Exception('Coordinate reference system (crs) can only be declared '
                                'if GeoViews is available.')
            params['crs'] = self.crs
        return element(data, [x, y], z, **params).redim(**self._redim).opts(**opts)

    def quadmesh(self, x=None, y=None, data=None):
        import xarray as xr
        data = self.data if data is None else data

        z = self.kwds.get('z')
        x = x or self.x
        y = y or self.y
        if not (x and y):
            x, y = list([k for k, v in data.coords.items() if v.size > 1])
        if not z:
            z = list(data.data_vars)[0] if isinstance(data, xr.Dataset) else [data.name]

        params = dict(self._relabel)
        opts = dict(plot=self._plot_opts, style=self._style_opts, norm=self._norm_opts)

        element = QuadMesh
        if self.crs is not None:
            try:
                from geoviews import QuadMesh as element
            except:
                raise Exception('Coordinate reference system (crs) can only be declared '
                                'if GeoViews is available.')
            params['crs'] = self.crs
        return element(data, [x, y], z, **params).redim(**self._redim).opts(**opts)

    def contour(self, x=None, y=None, data=None):
        from holoviews.operation import contours 
        opts = dict(plot=self._plot_opts, style=self._style_opts, norm=self._norm_opts)
        image = self.image(x, y, data)
        return contours(image, levels=self.kwds.get('levels', 5)).opts(**opts)

    def contourf(self, x=None, y=None, data=None):
        from holoviews.operation import contours 
        opts = dict(plot=self._plot_opts, style=self._style_opts, norm=self._norm_opts)
        image = self.image(x, y, data)
        return contours(image, levels=self.kwds.get('levels', 5), filled=True).opts(**opts)
