from __future__ import absolute_import
from collections import defaultdict

import param
try:
    import panel as pn
    panel_available = True
except:
    panel_available = False

from ..converter import HoloViewsConverter
from ..util import process_dynamic_args


class hvPlotBase(object):
    __all__ = []

    def __init__(self, data, custom_plots={}, **metadata):
        self._data = data
        self._plots = custom_plots
        self._metadata = metadata

    def __call__(self, x=None, y=None, kind=None, **kwds):
        """
        Default plot method (for more detailed options use specific
        plot method, e.g. df.hvplot.line)

        Parameters
        ----------
        x, y : string, optional
            Field name in the data to draw x- and y-positions from
        kind : string, optional
            The kind of plot to generate, e.g. 'line', 'scatter', etc.
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`hvplot.converter.HoloViewsConverter`.
        Returns
        -------
        HoloViews object: Object representing the requested visualization
        """
        if isinstance(kind, str) and kind not in self.__all__:
            raise NotImplementedError("kind='{kind}' for data of type {type}".format(
                kind=kind, type=type(self._data)))

        if panel_available:
            panel_args = ['widgets', 'widget_location', 'widget_layout', 'widget_type']
            panel_dict = {}
            for k in panel_args:
                if k in kwds:
                    panel_dict[k] = kwds.pop(k)
            dynamic, arg_deps, arg_names = process_dynamic_args(x, y, kind, **kwds)
            if dynamic or arg_deps:
                @pn.depends(*arg_deps, **dynamic)
                def callback(*args, **dyn_kwds):
                    xd = dyn_kwds.pop('x', x)
                    yd = dyn_kwds.pop('y', y)
                    kindd = dyn_kwds.pop('kind', kind)

                    combined_kwds = dict(kwds, **dyn_kwds)
                    fn_args = defaultdict(list)
                    for name, arg in zip(arg_names, args):
                        fn_args[(name, kwds[name])].append(arg)
                    for (name, fn), args in fn_args.items():
                        combined_kwds[name] = fn(*args)
                    plot = self._get_converter(xd, yd, kindd, **combined_kwds)(kindd, xd, yd)
                    return pn.panel(plot, **panel_dict)
                return pn.panel(callback)
            if panel_dict:
                plot = self._get_converter(x, y, kind, **kwds)(kind, x, y)
                return pn.panel(plot, **panel_dict)

        return self._get_converter(x, y, kind, **kwds)(kind, x, y)

    def _get_converter(self, x=None, y=None, kind=None, **kwds):
        params = dict(self._metadata, **kwds)
        x = x or params.pop('x', None)
        y = y or params.pop('y', None)
        kind = kind or params.pop('kind', None)
        return HoloViewsConverter(
            self._data, x, y, kind=kind, **params
        )

    def __dir__(self):
        """
        List default attributes and custom defined plots.
        """
        dirs = super(hvPlotBase, self).__dir__()
        return sorted(list(dirs)+list(self._plots))

    def __getattribute__(self, name):
        """
        Custom getattribute to expose user defined subplots.
        """
        plots = object.__getattribute__(self, '_plots')
        if name in plots:
            plot_opts = plots[name]
            if 'kind' in plot_opts and name in HoloViewsConverter._kind_mapping:
                param.main.warning("Custom options for existing plot types should not "
                                   "declare the 'kind' argument. The .%s plot method "
                                   "was unexpectedly customized with kind=%r."
                                   % (plot_opts['kind'], name))
                plot_opts['kind'] = name
            return hvPlotBase(self._data, **dict(self._metadata, **plot_opts))
        return super(hvPlotBase, self).__getattribute__(name)


class hvPlotTabular(hvPlotBase):
    __all__ = [
        'line',
        'step',
        'scatter',
        'area',
        'errorbars',
        'heatmap',
        'hexbin',
        'bivariate',
        'bar',
        'barh',
        'box',
        'violin',
        'hist',
        'kde',
        'density',
        'table',
        'dataset',
        'points',
        'vectorfield',
        'polygons',
        'paths',
        'labels'
    ]

    def line(self, x=None, y=None, **kwds):
        """
        Line plot

        Parameters
        ----------
        x, y : string, optional
            Field name to draw x- and y-positions from
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`hvplot.converter.HoloViewsConverter`.
        Returns
        -------
        HoloViews object: Object representing the requested visualization
        """
        return self(x, y, kind='line', **kwds)

    def step(self, x=None, y=None, where='mid', **kwds):
        """
        Step plot

        Parameters
        ----------
        x, y : string, optional
            Field name to draw x- and y-positions from
        where : string, optional
            Defines where the steps are placed (options: 'mid' (default), 'pre' and 'post')
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`hvplot.converter.HoloViewsConverter`.
        Returns
        -------
        HoloViews object: Object representing the requested visualization
        """
        return self(x, y, kind='step', where=where, **kwds)

    def scatter(self, x=None, y=None, **kwds):
        """
        Scatter plot

        Parameters
        ----------
        x, y : string, optional
            Field name to draw x- and y-positions from
        c: string, optional
            Name of the field to color points by
        s: string, optional
            Name of the field to scale point size by
        scale: number, optional
            Scaling factor to apply to point scaling
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`hvplot.converter.HoloViewsConverter`.
        Returns
        -------
        obj : HoloViews object
            The HoloViews representation of the plot.
        """
        return self(x, y, kind='scatter', **kwds)

    def area(self, x=None, y=None, y2=None, stacked=True, **kwds):
        """
        Area plot

        Parameters
        ----------
        x, y, y2 : string, optional
            Field name to draw x- and y-positions from
        stacked : boolean
            Whether to stack multiple areas
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`hvplot.converter.HoloViewsConverter`.
        Returns
        -------
        obj : HoloViews object
            The HoloViews representation of the plot.
        """
        if 'alpha' not in kwds and not stacked:
            kwds['alpha'] = 0.5
        return self(x, y, y2=y2, kind='area', stacked=stacked, **kwds)

    def errorbars(self, x=None, y=None, yerr1=None, yerr2=None, **kwds):
        """
        ErrorBars plot

        Parameters
        ----------
        x, y, y2 : string, optional
            Field name to draw x- and y-positions from
        yerr1 : string, optional
            Field name to draw symmetric / negative errors from
        yerr2 : string, optional
            Field name to draw positive errors from
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`hvplot.converter.HoloViewsConverter`.
        Returns
        -------
        obj : HoloViews object
            The HoloViews representation of the plot.
        """
        return self(x, y, kind='errorbars',
                    yerr1=yerr1, yerr2=yerr2, **kwds)

    def heatmap(self, x=None, y=None, C=None, colorbar=True, **kwds):
        """
        HeatMap plot

        Parameters
        ----------
        x, y : string, optional
            Field name to draw x- and y-positions from
        C : string
            Field to draw heatmap color from
        colorbar: boolean
            Whether to display a colorbar
        reduce_function : function
            Function to compute statistics for heatmap
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`hvplot.converter.HoloViewsConverter`.
        Returns
        -------
        obj : HoloViews object
            The HoloViews representation of the plot.
        """
        return self(x, y, kind='heatmap', C=C, colorbar=colorbar, **kwds)

    def hexbin(self, x=None, y=None, C=None, colorbar=True, **kwds):
        """
        HexBin plot

        Parameters
        ----------
        x, y : string, optional
            Field name to draw x- and y-positions from
        C : string
            Field to draw heatmap color from
        colorbar: boolean
            Whether to display a colorbar
        reduce_function : function
            Function to compute statistics for hexbins
        min_count : number
            The display threshold before a bin is shown, by default bins with
            a count of less than 1 are hidden
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`hvplot.converter.HoloViewsConverter`.
        Returns
        -------
        obj : HoloViews object
            The HoloViews representation of the plot.
        """
        return self(x, y, kind='hexbin', C=C, colorbar=colorbar, **kwds)

    def bivariate(self, x=None, y=None, colorbar=True, **kwds):
        """
        Bivariate plot for 2D density

        Parameters
        ----------
        x, y : string, optional
            Field name to draw x- and y-positions from
        colorbar: boolean
            Whether to display a colorbar
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`hvplot.converter.HoloViewsConverter`.
        Returns
        -------
        obj : HoloViews object
            The HoloViews representation of the plot.
        """
        return self(x, y, kind='bivariate', colorbar=colorbar, **kwds)

    def bar(self, x=None, y=None, **kwds):
        """
        Bars plot

        Parameters
        ----------
        x, y : string, optional
            Field name to draw x- and y-positions from
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`hvplot.converter.HoloViewsConverter`.
        Returns
        -------
        obj : HoloViews object
            The HoloViews representation of the plot.
        """
        return self(x, y, kind='bar', **kwds)

    def barh(self, x=None, y=None, **kwds):
        """
        Horizontal bar plot

        Parameters
        ----------
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`hvplot.converter.HoloViewsConverter`.
        Returns
        -------
        obj : HoloViews object
            The HoloViews representation of the plot.
        """
        return self(x, y, kind='barh', **kwds)

    def box(self, y=None, by=None, **kwds):
        """
        Boxplot

        Parameters
        ----------
        y : string or sequence
            Column in the DataFrame to compute distribution on.
        by : string or sequence
            Column in the DataFrame to group by.
        kwds : optional
            Keyword arguments to pass on to
            :py:meth:`hvplot.converter.HoloViewsConverter`.
        Returns
        -------
        obj : HoloViews object
            The HoloViews representation of the plot.
        """
        return self(kind='box', x=None, y=y, by=by, **dict(kwds, hover=False))

    def violin(self, y=None, by=None, **kwds):
        """
        Boxplot

        Parameters
        ----------
        y : string or sequence
            Column in the DataFrame to compute distribution on.
        by : string or sequence
            Column in the DataFrame to group by.
        kwds : optional
            Keyword arguments to pass on to
            :py:meth:`hvplot.converter.HoloViewsConverter`.
        Returns
        -------
        obj : HoloViews object
            The HoloViews representation of the plot.
        """
        return self(kind='violin', x=None, y=y, by=by, **dict(kwds, hover=False))

    def hist(self, y=None, by=None, **kwds):
        """
        Histogram

        Parameters
        ----------
        y : string or sequence
            Column in the DataFrame to compute distribution on.
        by : string or sequence
            Column in the DataFrame to group by.
        kwds : optional
            Keyword arguments to pass on to
            :py:meth:`hvplot.converter.HoloViewsConverter`.
        Returns
        -------
        obj : HoloViews object
            The HoloViews representation of the plot.
        """
        return self(kind='hist', x=None, y=y, by=by, **kwds)

    def kde(self, y=None, by=None, **kwds):
        """
        KDE

        Parameters
        ----------
        y : string or sequence
            Column in the DataFrame to compute distribution on.
        by : string or sequence
            Column in the DataFrame to group by.
        kwds : optional
            Keyword arguments to pass on to
            :py:meth:`hvplot.converter.HoloViewsConverter`.
        Returns
        -------
        obj : HoloViews object
            The HoloViews representation of the plot.
        """
        return self(kind='kde', x=None, y=y, by=by, **kwds)

    def density(self, y=None, by=None, **kwds):
        """
        alias for KDE

        Parameters
        ----------
        y : string or sequence
            Column in the DataFrame to compute distribution on.
        by : string or sequence
            Column in the DataFrame to group by.
        kwds : optional
            Keyword arguments to pass on to
            :py:meth:`hvplot.converter.HoloViewsConverter`.
        Returns
        -------
        obj : HoloViews object
            The HoloViews representation of the plot.
        """
        return self(kind='kde', x=None, y=y, by=by, **kwds)

    def table(self, columns=None, **kwds):
        """
        Table

        Parameters
        ----------
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`hvplot.converter.HoloViewsConverter`.
        Returns
        -------
        obj : HoloViews object
            The HoloViews representation of the plot.
        """
        return self(kind='table', **dict(kwds, columns=columns))

    def dataset(self, columns=None, **kwds):
        """
        Dataset

        Parameters
        ----------
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`hvplot.converter.HoloViewsConverter`.
        Returns
        -------
        obj : HoloViews object
            The HoloViews representation of the plot.
        """
        return self(kind='dataset', **dict(kwds, columns=columns))

    def points(self, x=None, y=None, **kwds):
        """
        Point plot use for 2D coordinate systems

        Parameters
        ----------
        x, y : string, optional
            The coordinate variable along the x- and y-axis
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`hvplot.converter.HoloViewsConverter`.
        Returns
        -------
        obj : HoloViews object
            The HoloViews representation of the plot.
        """
        return self(x, y, kind='points', **kwds)

    def vectorfield(self, x=None, y=None, angle=None, mag=None, **kwds):
        """
        Vectorfield plot

        Parameters
        ----------
        x, y : string, optional
            Field name to draw x- and y-positions from
        mag : string, optional
            Magnitude
        angle : string, optional
            Angle
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`hvplot.converter.HoloViewsConverter`.
        Returns
        -------
        obj : HoloViews object
            The HoloViews representation of the plot.
        """
        return self(x, y, angle=angle, mag=mag, kind='vectorfield', **kwds)

    def polygons(self, x=None, y=None, c=None, **kwds):
        """
        Polygon plot for geopandas dataframes

        Parameters
        ----------
        c: string, optional
            The dimension to color the polygons by
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`hvplot.converter.HoloViewsConverter`.
        Returns
        -------
        obj : HoloViews object
            The HoloViews representation of the plot.
        """
        return self(x, y, c=c, kind='polygons', **kwds)

    def paths(self, x=None, y=None, c=None, **kwds):
        """
        LineString and LineRing plot for geopandas dataframes.

        Parameters
        ----------
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`hvplot.converter.HoloViewsConverter`.
        Returns
        -------
        obj : HoloViews object
            The HoloViews representation of the plot.
        """
        return self(x, y, c=c, kind='paths', **kwds)

    def labels(self, x=None, y=None, text=None, **kwds):
        """
        Labels plot.

        Parameters
        ----------
        x, y : string, optional
            The coordinate variable along the x- and y-axis
        text : string, optional
            The column to draw the text labels from
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`hvplot.converter.HoloViewsConverter`.
        Returns
        -------
        obj : HoloViews object
            The HoloViews representation of the plot.
        """
        return self(x, y, text=text, kind='labels', **kwds)

class hvPlot(hvPlotTabular):
    __all__ = [
        'line',
        'step',
        'scatter',
        'area',
        'errorbars',
        'heatmap',
        'hexbin',
        'bivariate',
        'bar',
        'barh',
        'box',
        'violin',
        'hist',
        'kde',
        'density',
        'table',
        'dataset',
        'points',
        'vectorfield',
        'polygons',
        'paths',
        'labels',
        'image',
        'rgb',
        'quadmesh',
        'contour',
        'contourf',
    ]

    def image(self, x=None, y=None, z=None, colorbar=True, **kwds):
        """
        Image plot

        Parameters
        ----------
        x, y : string, optional
            The coordinate variable along the x- and y-axis
        z : string, optional
            The data variable to plot
        colorbar: boolean
            Whether to display a colorbar
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`hvplot.converter.HoloViewsConverter`.
        Returns
        -------
        obj : HoloViews object
            The HoloViews representation of the plot.
        """
        return self(x, y, z=z, kind='image', colorbar=colorbar, **kwds)

    def rgb(self, x=None, y=None, z=None, bands=None, **kwds):
        """
        RGB plot

        Parameters
        ----------
        x, y : string, optional
            The coordinate variable along the x- and y-axis
        bands : string, optional
            The coordinate variable to draw the RGB channels from
        z : string, optional
            The data variable to plot
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`hvplot.converter.HoloViewsConverter`.
        Returns
        -------
        obj : HoloViews object
            The HoloViews representation of the plot.
        """
        if bands is not None:
            kwds['bands'] = bands
        return self(x, y, z=z, kind='rgb', **kwds)

    def quadmesh(self, x=None, y=None, z=None, colorbar=True, **kwds):
        """
        QuadMesh plot

        Parameters
        ----------
        x, y : string, optional
            The coordinate variable along the x- and y-axis
        z : string, optional
            The data variable to plot
        colorbar: boolean
            Whether to display a colorbar
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`hvplot.converter.HoloViewsConverter`.
        Returns
        -------
        obj : HoloViews object
            The HoloViews representation of the plot.
        """
        return self(x, y, z=z, kind='quadmesh', colorbar=colorbar, **kwds)

    def contour(self, x=None, y=None, z=None, colorbar=True, **kwds):
        """
        Line contour plot

        Parameters
        ----------
        x, y : string, optional
            The coordinate variable along the x- and y-axis
        z : string, optional
            The data variable to plot
        levels: int, optional
            The number of contour levels
        colorbar: boolean
            Whether to display a colorbar
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`hvplot.converter.HoloViewsConverter`.
        Returns
        -------
        obj : HoloViews object
            The HoloViews representation of the plot.
        """
        return self(x, y, z=z, kind='contour', colorbar=colorbar, **kwds)

    def contourf(self, x=None, y=None, z=None, colorbar=True, **kwds):
        """
        Filled contour plot

        Parameters
        ----------
        x, y : string, optional
            The coordinate variable along the x- and y-axis
        z : string, optional
            The data variable to plot
        levels: int, optional
            The number of contour levels
        colorbar: boolean
            Whether to display a colorbar
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`hvplot.converter.HoloViewsConverter`.
        Returns
        -------
        obj : HoloViews object
            The HoloViews representation of the plot.
        """
        return self(x, y, z=z, kind='contourf', colorbar=colorbar, **kwds)
