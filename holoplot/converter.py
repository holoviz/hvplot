from __future__ import absolute_import
from functools import partial
from distutils.version import LooseVersion

import param
import holoviews as hv
import pandas as pd

from holoviews.core.spaces import DynamicMap, Callable
from holoviews.core.overlay import NdOverlay
from holoviews.core.layout import NdLayout
from holoviews.element import (
    Curve, Scatter, Area, Bars, BoxWhisker, Dataset, Distribution,
    Table, HeatMap
)
from holoviews.operation import histogram
from holoviews.streams import Buffer, Pipe

try:
    import streamz.dataframe as sdf
except ImportError:
    sdf = None

try:
    from intake.source.base import DataSource
except ImportError:
    DataSource = None

try:
    from tornado.ioloop import PeriodicCallback
    from tornado import gen
except ImportError:
    gen = None

try:
    import dask.dataframe as dd
except ImportError:
    dd = None

try:
    import bokeh
    if LooseVersion(bokeh.__version__) <= '0.12.14':
        import warnings
        # Ignore NumPy future warnings triggered by bokeh
        warnings.simplefilter(action='ignore', category=FutureWarning)
except:
    pass

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


def streaming(method):
    """
    Decorator to add streaming support to plots.
    """
    def streaming_plot(*args, **kwargs):
        self = args[0]
        if self.streaming:
            cbcallable = StreamingCallable(partial(method, *args, **kwargs),
                                           periodic=self.cb)
            return DynamicMap(cbcallable, streams=[self.stream])
        return method(*args, **kwargs)
    return streaming_plot


def datashading(method):
    """
    Decorator to add datashading support to a plot.
    """
    def datashading_plot(*args, **kwargs):
        self = args[0]
        plot = method(*args, **kwargs)
        if not self.datashade:
            return plot
        try:
            from holoviews.operation.datashader import datashade
            from datashader import count_cat
        except:
            raise ImportError('Datashading is not available')
        opts = dict(width=self._plot_opts['width'], height=self._plot_opts['height'])
        if 'cmap' in self._style_opts:
            opts['cmap'] = self._style_opts['cmap']
        if self.by:
            opts['aggregator'] = count_cat(self.by)
        return datashade(plot, **opts).opts(plot=self._plot_opts)
    return datashading_plot


class HoloViewsConverter(object):

    def __init__(self, data, kind=None, by=None, width=700,
                 height=300, shared_axes=False, columns=None,
                 grid=False, legend=True, rot=None, title=None,
                 xlim=None, ylim=None, xticks=None, yticks=None,
                 fontsize=None, colormap=None, stacked=False,
                 logx=False, logy=False, loglog=False, hover=True,
                 style_opts={}, plot_opts={}, use_index=True,
                 value_label='value', group_label='Group',
                 colorbar=False, streaming=False, backlog=1000,
                 timeout=1000, persist=False, use_dask=False,
                 datashade=False, subplots=False, label=None, **kwds):

        self.streaming = streaming
        self.use_dask = use_dask

        # Validate DataSource
        self.data_source = data
        if isinstance(data, pd.Series) or (sdf and isinstance(data, (sdf.Series, sdf.Seriess))):
            data = data.to_frame()
        if isinstance(data, pd.DataFrame):
            self.data = data
        elif DataSource and isinstance(data, DataSource):
            if data.container != 'dataframe':
                raise NotImplementedError('Plotting interface currently only '
                                          'supports DataSource objects with '
                                          'dataframe container.')
            if streaming:
                self.data = data.read()
                self.stream = Buffer(self.data, length=backlog, index=False)
                if gen is None:
                    raise ImportError('Streaming support requires tornado.')
                @gen.coroutine
                def f():
                    self.stream.send(data.read())
                self.cb = PeriodicCallback(f, timeout)
            elif (use_dask or persist) and dd is not None:
                ddf = data.to_dask()
                self.data = ddf.persist() if persist else ddf
            else:
                self.data = data.read()
        elif sdf and (data, sdf.DataFrame, sdf.Series, sdf.DataFrames, sdf.Seriess):
            self.data = data.example
            self.stream_type = data._stream_type
            self.streaming = True
            self.cb = data
            if data._stream_type == 'updating':
                self.stream = Pipe(data=self.data)
            else:
                self.stream = Buffer(data=self.data, length=backlog, index=False)
            data.stream.gather().sink(self.stream.send)


        # High-level options
        self.by = by or []
        self.columns = columns
        self.stacked = stacked
        self.use_index = use_index
        self.kwds = kwds
        self.value_label = value_label
        self.group_label = group_label
        self.datashade = datashade

        # By type
        self._by_type = NdLayout if subplots else NdOverlay

        # Process style options
        if 'cmap' in kwds and colormap:
            raise TypeError("Only specify one of `cmap` and `colormap`.")
        elif 'cmap' in kwds:
            cmap = kwds.pop('cmap')
        else:
            cmap = colormap

        self._style_opts = dict(**style_opts)
        if cmap:
            self._style_opts['cmap'] = cmap
        if 'color' in kwds:
            self._style_opts['color'] = kwds.pop('color')
        if 'size' in kwds:
            self._style_opts['size'] = kwds.pop('size')
        if 'alpha' in kwds:
            self._style_opts['alpha'] = kwds.pop('alpha')

        # Process plot options
        plot_options = dict(plot_opts)
        plot_options['logx'] = logx or loglog
        plot_options['logy'] = logy or loglog
        plot_options['show_grid'] = grid
        plot_options['shared_axes'] = shared_axes
        plot_options['show_legend'] = legend
        if xticks:
            plot_options['xticks'] = xticks
        if yticks:
            plot_options['yticks'] = yticks
        if width:
            plot_options['width'] = width
        if height:
            plot_options['height'] = height
        if fontsize:
            plot_options['fontsize'] = fontsize
        if colorbar:
            plot_options['colorbar'] = colorbar
        if self.kwds.get('vert', False):
            plot_options['invert_axes'] = True
        if rot:
            if (kind == 'barh' or kwds.get('orientation') == 'horizontal'
                or kwds.get('vert')):
                axis = 'yrotation'
            else:
                axis = 'xrotation'
            plot_options[axis] = rot
        if hover:
            plot_options['tools'] = ['hover']
        plot_options['legend_position'] = 'right'
        if title is not None:
            plot_options['title_format'] = title
        self._hover = hover
        self._plot_opts = plot_options

        self._relabel = {'label': label}
        self._dim_ranges = {'x': xlim or (None, None),
                            'y': ylim or (None, None)}
        self._norm_opts = {'framewise': True}


    def __call__(self, kind, x, y):
        return getattr(self, kind)(x, y)


    ##########################
    #     Simple charts      #
    ##########################

    def single_chart(self, element, x, y, data=None):
        opts = {element.__name__: dict(plot=self._plot_opts, norm=self._norm_opts,
                                       style=self._style_opts)}
        ranges = {y: self._dim_ranges['y']}
        if x:
            ranges[x] = self._dim_ranges['x']

        data = self.data if data is None else data
        ys = [y]
        if 'c' in self.kwds and self.kwds['c'] in data.columns:
            ys += [self.kwds['c']]

        if self.by:
            chart = Dataset(data, [self.by, x], ys).to(element, x, ys, self.by).overlay()
        else:
            chart = element(data, x, ys)
        return chart.redim.range(**ranges).relabel(**self._relabel).opts(opts)


    def chart(self, element, x, y, data=None):
        "Helper method for simple x vs. y charts"
        data = (self.data if data is None else data)
        if not x and not y and len(data.columns) == 1:
            x = data.index.name or 'index'
            y = data.columns[0]
        if x and y:
            return self.single_chart(element, x, y, data)

        # Note: Loading dask dataframe into memory due to rename bug
        if self.use_dask: data = data.compute()
        opts = dict(plot=dict(self._plot_opts, labelled=['x']),
                    norm=self._norm_opts, style=self._style_opts)

        if self.use_index or x:
            if self.use_index is not None and isinstance(self.use_index, bool):
                x = x or data.index.name or 'index'
            else:
                x = self.use_index
            columns = [c for c in self.columns or data.columns if c != x]
            renamed = {c: 'Dimension_%d' % c for c in columns if isinstance(c, int)}
            if renamed:
                data = data.rename(columns=renamed)
            charts = {}
            for c in columns:
                c = renamed.get(c, c)
                chart = element(data, x, c).redim(**{c: self.value_label})
                ranges = {x: self._dim_ranges['x'], c: self._dim_ranges['y']}
                charts[c] = (chart.relabel(**self._relabel)
                             .redim.range(**ranges).opts(**opts))
            if len(charts) == 1:
                return charts[c].redim(**{self.value_label: c})
            return self._by_type(charts, self.group_label)
        else:
            raise ValueError('Could not determine what to plot. Expected '
                             'either x and y parameters to be declared '
                             'or use_index to be enabled.')


    @datashading
    @streaming
    def line(self, x, y, data=None):
        return self.chart(Curve, x, y, data)


    @datashading
    @streaming
    def scatter(self, x, y, data=None):
        scatter = self.chart(Scatter, x, y, data)
        if 'c' in self.kwds:
            color_opts = {'Scatter': {'color_index': self.kwds['c']}}
            return scatter.opts(plot=color_opts)
        return scatter


    @streaming
    def area(self, x, y, data=None):
        areas = self.chart(Area, x, y, data)
        if self.stacked:
            areas = areas.map(Area.stack, NdOverlay)
        return areas

    ##########################
    #  Categorical charts    #
    ##########################

    def _category_plot(self, element, data=None):
        """
        Helper method to generate element from indexed dataframe.
        """
        data = self.data if data is None else data
        if isinstance(self.use_index, bool):
            index = data.index.name or 'index'
        else:
            index = self.use_index

        id_vars = [index]
        invert = not self.kwds.get('vert', True)
        opts = {'plot': dict(self._plot_opts, labelled=[]),
                'norm': self._norm_opts}
        ranges = {self.value_label: self._dim_ranges['y']}

        if self.columns:
            data = data[self.columns+id_vars]

        melt = dd.melt if dd and isinstance(data, dd.DataFrame) else pd.melt
        if any(v in [data.index.names]+['index'] for v in id_vars):
            data = data.reset_index()
        df = melt(data, id_vars=id_vars, var_name=self.group_label,
                  value_name=self.value_label)
        kdims = [index]
        if len(df[self.group_label].unique()) > 1:
            kdims += [self.group_label]
        elif not 'color_index' in opts['plot']:
            opts['plot']['color_index'] = 0
        return (element(df, kdims, self.value_label).redim.range(**ranges)
                .relabel(**self._relabel).opts(**opts))


    @streaming
    def bar(self, x, y, data=None):
        if x and y:
            return self.single_chart(Bars, x, y, data)
        elif self.use_index:
            stack_index = 1 if self.stacked else None
            opts = {'Bars': {'stack_index': stack_index}}
            return self._category_plot(Bars, data).opts(plot=opts)
        else:
            raise ValueError('Could not determine what to plot. Expected '
                             'either x and y parameters to be declared '
                             'or use_index to be enabled.')

    @streaming
    def barh(self, x, y, data=None):
        return self.bar(x, y, data).opts(plot={'Bars': dict(invert_axes=True)})

    ##########################
    #   Statistical charts   #
    ##########################

    def _stats_plot(self, element, y, data=None):
        """
        Helper method to generate element from indexed dataframe.
        """
        data = self.data if data is None else data

        opts = {'plot': dict(self._plot_opts, labelled=[]),
                'norm': self._norm_opts, 'style': self._style_opts}
        if y:
            ranges = {y: self._dim_ranges['y']}
            kdims = [self.by] if self.by else []
            return (element(data, kdims, y).redim.range(**ranges)
                .relabel(**self._relabel).opts(**opts))

        kdims = [self.group_label]
        ranges = {self.value_label: self._dim_ranges['y']}
        if self.columns:
            data = data[self.columns]
        melt = dd.melt if dd and isinstance(data, dd.DataFrame) else pd.melt
        df = melt(data, var_name=self.group_label, value_name=self.value_label)
        return (element(df, kdims, self.value_label).redim.range(**ranges)
                .relabel(**self._relabel).opts(**opts))


    @streaming
    def box(self, x, y, data=None):
        return self._stats_plot(BoxWhisker, y, data)


    @streaming
    def violin(self, x, y, data=None):
        try:
            from holoviews.element import Violin
        except ImportError:
            raise ImportError('Violin plot requires HoloViews version >=1.10')
        return self._stats_plot(Violin, y, data)


    @streaming
    def hist(self, x, y, data=None):
        plot_opts = dict(self._plot_opts)
        invert = self.kwds.get('orientation', False) == 'horizontal'
        opts = dict(plot=dict(plot_opts, labelled=['x'], invert_axes=invert),
                    style=self._style_opts, norm=self._norm_opts)
        hist_opts = {'num_bins': self.kwds.get('bins', 10),
                     'bin_range': self.kwds.get('bin_range', None),
                     'normed': self.kwds.get('normed', False)}

        data = self.data if data is None else data
        if y and self.by:
            ds = Dataset(data, [self.by], y)
            return histogram(ds.to(Dataset, [], y, self.by), **hist_opts).\
                overlay().opts({'Histogram': opts})
        elif y or len(data.columns) == 1:
            y = y or data.columns[0]
            ds = Dataset(data, [], y)
            return histogram(ds, dimension=y, **hist_opts).\
                opts({'Histogram': opts})

        ds = Dataset(data)
        hists = {}
        columns = self.columns or data.columns
        for col in columns:
            hist = histogram(ds, dimension=col, **hist_opts)
            ranges = {hist.vdims[0].name: self._dim_ranges['y']}
            hists[col] = (hist.redim.range(**ranges)
                          .relabel(**self._relabel).opts(**opts))
        return NdOverlay(hists)


    @streaming
    def kde(self, x, y, data=None):
        data = self.data if data is None else data
        plot_opts = dict(self._plot_opts)
        invert = self.kwds.get('orientation', False) == 'horizontal'
        opts = dict(plot=dict(plot_opts, invert_axes=invert),
                    style=self._style_opts, norm=self._norm_opts)
        opts = {'Distribution': opts, 'Area': opts,
                'NdOverlay': {'plot': dict(plot_opts, legend_limit=0)}}

        if y and self.by:
            ds = Dataset(data)
            return ds.to(Distribution, y, [], self.by).overlay().opts(opts)
        elif y or len(data.columns) == 1:
            y = y or data.columns[0]
            return Distribution(data, y, []).opts(opts)

        if self.columns:
            data = data[self.columns]
        df = pd.melt(data, var_name=self.group_label, value_name=self.value_label)
        ds = Dataset(df)
        if len(df):
            overlay = ds.to(Distribution, self.value_label).overlay()
        else:
            vdim = self.value_label + ' Density'
            overlay = NdOverlay({0: Area([], self.value_label, vdim)},
                                [self.group_label])
        return overlay.relabel(**self._relabel).opts(opts)


    ##########################
    #      Other charts      #
    ##########################

    @streaming
    def heatmap(self, x, y, data=None):
        data = data or self.data
        if not x: x = data.columns[0]
        if not y: y = data.columns[1]
        z = self.kwds.get('C', data.columns[2])

        opts = dict(plot=self._plot_opts, norm=self._norm_opts, style=self._style_opts)
        hmap = HeatMap(data, [x, y], z).opts(**opts)
        if 'reduce_function' in self.kwds:
            return hmap.aggregate(function=self.kwds['reduce_function'])
        return hmap


    @streaming
    def table(self, x=None, y=None, data=None):
        allowed = ['width', 'height']
        opts = {k: v for k, v in self._plot_opts.items() if k in allowed}

        data = self.data if data is None else data
        return Table(data, self.columns, []).opts(plot=opts)
