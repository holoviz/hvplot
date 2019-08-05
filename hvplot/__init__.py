from __future__ import absolute_import

import sys
import inspect
import textwrap

import param
import numpy as _np
import pandas as _pd
import holoviews as _hv

from holoviews import Store

from .converter import HoloViewsConverter
from .util import get_ipy
from .utilities import save, show # noqa

__version__ = str(param.version.Version(fpath=__file__, archive_commit="$Format:%h$",
                                        reponame="hvplot"))

# Register plotting interfaces
def _patch_plot(self):
    return hvPlot(self)

_METHOD_DOCS = {}

def _get_doc(kind, completions=False, docstring=True, generic=True, style=True):
    converter = HoloViewsConverter
    method = getattr(hvPlot, kind)
    kind_opts = converter._kind_options.get(kind, [])
    eltype = converter._kind_mapping[kind]

    formatter = ''
    if completions:
        formatter = "hvplot.{kind}({completions})"
    if docstring:
        if formatter:
            formatter += '\n'
        formatter += "{docstring}"
    if generic:
        if formatter:
            formatter += '\n'
        formatter += "{options}"

    if eltype in Store.registry['bokeh']:
        valid_opts = Store.registry['bokeh'][eltype].style_opts
        if style:
            formatter += '\n{style}'
    else:
        valid_opts = []

    style_opts = 'Style options\n-------------\n\n' + '\n'.join(sorted(valid_opts))

    parameters = []
    if sys.version_info.major < 3:
        argspec = inspect.getargspec(method)
        args = argspec.args[1:]
        defaults = argspec.defaults or [None]*len(args)
        for arg, dflt in zip(args, defaults):
            parameters.append((arg, dflt))
    else:
        sig = inspect.signature(method)
        for name, p in list(sig.parameters.items())[1:]:
            if p.kind == 1:
                parameters.append((name, p.default))
    parameters += [(o, None) for o in
                   valid_opts+kind_opts+converter._axis_options+converter._op_options]

    completions = ', '.join(['%s=%s' % (n, v) for n, v in parameters])
    options = textwrap.dedent(converter.__doc__)
    method_doc = _METHOD_DOCS.get(kind, method.__doc__)
    _METHOD_DOCS[kind] = method_doc
    return formatter.format(
        kind=kind, completions=completions, docstring=textwrap.dedent(method_doc),
        options=options, style=style_opts)


def _patch_doc(kind):
    method = getattr(hvPlot, kind)
    docstring = _get_doc(kind, get_ipy())
    if sys.version_info.major == 2:
        method.__func__.__doc__ = docstring
    else:
        method.__doc__ = docstring


def help(kind=None, docstring=True, generic=True, style=True):
    """
    Provide a docstring with all valid options which apply to the plot
    type.

    Parameters
    ----------
    kind: str
        The kind of plot to provide help for
    docstring: boolean (default=True)
        Whether to display the docstring
    generic: boolean (default=True)
        Whether to provide list of generic options
    style: boolean (default=True)
        Whether to provide list of style options
    """
    print(_get_doc(kind, docstring=docstring, generic=generic, style=style))


def patch(library, name='hvplot', extension=None, logo=False):
    """
    Patch library to support HoloViews based plotting API.
    """
    if not isinstance(library, list): library = [library]
    _patch_plot.__doc__ = hvPlot.__call__.__doc__
    patch_property = property(_patch_plot)
    if 'streamz' in library:
        try:
            import streamz.dataframe as sdf
        except ImportError:
            raise ImportError('Could not patch plotting API onto streamz. '
                              'Streamz could not be imported.')
        setattr(sdf.DataFrame, name, patch_property)
        setattr(sdf.DataFrames, name, patch_property)
        setattr(sdf.Series, name, patch_property)
        setattr(sdf.Seriess, name, patch_property)
    if 'pandas' in library:
        try:
            import pandas as pd
        except:
            raise ImportError('Could not patch plotting API onto pandas. '
                              'Pandas could not be imported.')
        setattr(pd.DataFrame, name, patch_property)
        setattr(pd.Series, name, patch_property)
    if 'dask' in library:
        try:
            import dask.dataframe as dd
        except:
            raise ImportError('Could not patch plotting API onto dask. '
                              'Dask could not be imported.')
        setattr(dd.DataFrame, name, patch_property)
        setattr(dd.Series, name, patch_property)
    if 'xarray' in library:
        try:
            import xarray as xr
        except:
            raise ImportError('Could not patch plotting API onto xarray. '
                              'xarray could not be imported.')
        xr.register_dataset_accessor(name)(hvPlot)
        xr.register_dataarray_accessor(name)(hvPlot)
    if 'intake' in library:
        try:
            import intake
        except:
            raise ImportError('Could not patch plotting API onto intake. '
                              'intake could not be imported.')
        setattr(intake.source.base.DataSource, name, patch_property)
    if extension and not getattr(_hv.extension, '_loaded', False):
        _hv.extension(extension, logo=logo)


class hvPlot(object):

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
        dirs = super(hvPlot, self).__dir__()
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
            return hvPlot(self._data, **dict(self._metadata, **plot_opts))
        return super(hvPlot, self).__getattribute__(name)

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

    def paths(self, **kwds):
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
        return self(x=None, y=None, kind='paths', **kwds)

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


def scatter_matrix(data, c=None, chart='scatter', diagonal='hist', alpha=0.5, **kwds):
    """
    Scatter matrix of numeric columns.

    Parameters:
    -----------
    data: DataFrame
    c: str, optional
        Column to color by
    chart: str, optional
        Chart type (one of 'scatter', 'bivariate', 'hexbin')
    diagonal: str, optional
        Chart type for the diagonal (one of 'hist', 'kde')
    kwds: hvplot.scatter options, optional

    Returns:
    --------
    obj : HoloViews object
        The HoloViews representation of the plot.
    """
    data = _hv.Dataset(data)
    supported = list(HoloViewsConverter._kind_mapping)
    if diagonal not in supported:
        raise ValueError('diagonal type must be one of: %s, found %s' %
                         (supported, diagonal))
    if chart not in supported:
        raise ValueError('Chart type must be one of: %s, found %s' %
                         (supported, chart))
    diagonal = HoloViewsConverter._kind_mapping[diagonal]
    chart = HoloViewsConverter._kind_mapping[chart]

    colors = _hv.plotting.util.process_cmap('Category10', categorical=True)
    chart_opts = dict(alpha=alpha, cmap=colors, tools=['box_select', 'lasso_select'],
                      nonselection_alpha=0.1, **kwds)

    grid = _hv.operation.gridmatrix(data, diagonal_type=diagonal, chart_type=chart)
    if c:
        chart_opts['color_index'] = c
        grid = grid.map(lambda x: x.clone(vdims=x.vdims+[c]), 'Scatter')
        groups = _hv.operation.gridmatrix(data.groupby(c).overlay(),
                                          chart_type=chart,
                                          diagonal_type=diagonal)
        grid = (grid * groups).map(lambda x: x.get(0) if isinstance(x.get(0), chart) else x.get(1),
                                   _hv.Overlay)

    diagonal_opts = {'fill_color': _hv.Cycle(values=colors)}
    return grid.options({chart.__name__: chart_opts, diagonal.__name__: diagonal_opts})


def lag_plot(data, lag=1, **kwds):
    """Lag plot for time series.

    Parameters:
    -----------
    data: Time series
    lag: lag of the scatter plot, default 1
    kwds: hvplot.scatter options, optional

    Returns:
    --------
    obj : HoloViews object
        The HoloViews representation of the plot.
    """
    if lag != int(lag) or int(lag) <= 0:
        raise ValueError("lag must be a positive integer")
    lag = int(lag)

    values = data.values
    y1 = 'y(t)'
    y2 = 'y(t + {0})'.format(lag)
    lags = _pd.DataFrame({y1: values[:-lag].T.ravel(),
                          y2: values[lag:].T.ravel()})
    if isinstance(data, _pd.DataFrame):
        lags['variable'] = _np.repeat(data.columns, lags.shape[0] / data.shape[1])
        kwds['c'] = 'variable'
    return hvPlot(lags).scatter(y1, y2, **kwds)


def parallel_coordinates(data, class_column, cols=None, alpha=0.5,
                         width=600, height=300, var_name='variable',
                         value_name='value', **kwds):
    """
    Parallel coordinates plotting.

    Parameters
    ----------
    frame: DataFrame
    class_column: str
        Column name containing class names
    cols: list, optional
        A list of column names to use
    alpha: float, optional
        The transparency of the lines

    Returns
    -------
    obj : HoloViews object
        The HoloViews representation of the plot.

    See Also
    --------
    pandas.plotting.parallel_coordinates : matplotlib version of this routine
    """
    # Transform the dataframe to be used in Vega-Lite
    if cols is not None:
        data = data[list(cols) + [class_column]]
    cols = data.columns
    df = data.reset_index()
    index = (set(df.columns) - set(cols)).pop()
    assert index in df.columns
    df = df.melt([index, class_column],
                 var_name=var_name, value_name=value_name)

    labelled = [] if var_name == 'variable' else ['x']
    if value_name != 'value':
        labelled.append('y')
    options = {'Curve': dict(kwds, labelled=labelled, alpha=alpha, width=width, height=height),
               'Overlay': dict(legend_limit=5000)}
    colors = _hv.plotting.util.process_cmap('Category10', categorical=True)
    dataset = _hv.Dataset(df)
    groups = dataset.to(_hv.Curve, var_name, value_name).overlay(index).items()
    return _hv.Overlay([curve.relabel(k).options('Curve', color=c)
                        for c, (k, v) in zip(colors, groups) for curve in v]).options(options)


def andrews_curves(data, class_column, samples=200, alpha=0.5,
                   width=600, height=300, **kwds):
    """
    Andrews curve plot.

    Parameters
    ----------
    frame: DataFrame
    class_column: str
        Column name containing class names
    samples: int, optional
        Number of samples to draw
    alpha: float, optional
        The transparency of the lines

    Returns
    -------
    obj : HoloViews object
        The HoloViews representation of the plot.

    See Also
    --------
    pandas.plotting.parallel_coordinates : matplotlib version of this routine
    """
    t = _np.linspace(-_np.pi, _np.pi, samples)
    vals = data.drop(class_column, axis=1).values.T

    curves = _np.outer(vals[0], _np.ones_like(t))
    for i in range(1, len(vals)):
        ft = ((i + 1) // 2) * t
        if i % 2 == 1:
            curves += _np.outer(vals[i], _np.sin(ft))
        else:
            curves += _np.outer(vals[i], _np.cos(ft))

    df = _pd.DataFrame({'t': _np.tile(_np.arange(samples), curves.shape[0]),
                       'sample': _np.repeat(_np.arange(curves.shape[0]), curves.shape[1]),
                       'value': curves.ravel(),
                       class_column: _np.repeat(data[class_column], samples)})

    labelled = ['x']
    colors = _hv.plotting.util.process_cmap('Category10', categorical=True)
    options = {'Overlay': dict(legend_limit=5000),
               'Curve': dict(kwds, labelled=labelled, alpha=alpha,
                             width=width, height=height, **kwds)}
    dataset = _hv.Dataset(df)
    groups = dataset.to(_hv.Curve, 't', 'value').overlay('sample').items()
    return _hv.Overlay([curve.relabel(k).options('Curve', color=c)
                        for c, (k, v) in zip(colors, groups) for curve in v]).options(options)

# Patch docstrings
for _kind in HoloViewsConverter._kind_mapping:
    _patch_doc(_kind)
