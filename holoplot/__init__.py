import numpy as _np
import pandas as _pd
import holoviews as _hv
from holoviews.ipython import display # noqa

from bokeh.io import export_png as _export_png, show as _show, save as _save
from bokeh.resources import CDN as _CDN

from .converter import HoloViewsConverter

renderer = _hv.renderer('bokeh')

# Register plotting interfaces
def _patch_plot(self):
    return HoloPlot(self)


def patch(library, extension=None, logo=False):
    """
    Patch library to support HoloViews based plotting API.
    """
    if not isinstance(library, list): library = [library]
    if 'streamz' in library:
        try:
            import streamz.dataframe as sdf
        except ImportError:
            raise ImportError('Could not patch plotting API onto streamz. '
                              'Streamz could not be imported.')
        sdf.DataFrame.plot = property(_patch_plot)
        sdf.DataFrames.plot = property(_patch_plot)
        sdf.Series.plot = property(_patch_plot)
        sdf.Seriess.plot = property(_patch_plot)
    if 'pandas' in library:
        try:
            import pandas as pd
        except:
            raise ImportError('Could not patch plotting API onto pandas. '
                              'Pandas could not be imported.')
        pd.DataFrame.plot = property(_patch_plot)
        pd.Series.plot = property(_patch_plot)
    if 'dask' in library:
        try:
            import dask.dataframe as dd
        except:
            raise ImportError('Could not patch plotting API onto dask. '
                              'Dask could not be imported.')
        dd.DataFrame.plot = property(_patch_plot)
        dd.Series.plot = property(_patch_plot)
    if 'intake' in library:
        try:
            from intake.source.base import DataSource
        except ImportError:
            raise ImportError('Could not patch plotting API onto intake. '
                              'Intake could not be imported.')
        DataSource.plot = property(_patch_plot)
    if 'xarray' in library:
        try:
            from xarray import DataArray
        except ImportError:
            raise ImportError('Could not patch plotting API onto xarray. '
                              'Xarray could not be imported.')
        DataArray.plot = property(_patch_plot)
    if extension and not _hv.extension._loaded:
        _hv.extension(extension, logo=logo)


class HoloPlot(object):

    def __init__(self, data, **metadata):
        self._data = data
        self._metadata = metadata

    def __call__(self, x=None, y=None, kind=None, **kwds):
        params = dict(self._metadata, **kwds)
        converter = HoloViewsConverter(
            self._data, x, y, kind=kind, **params
        )
        return converter(kind, x, y)

    def line(self, x=None, y=None, **kwds):
        """
        Line plot

        Parameters
        ----------
        x, y : string, optional
            Field name to draw x- and y-positions from
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`holoplot.converter.HoloViewsConverter`.
        Returns
        -------
        HoloViews object: Object representing the requested visualization
        """
        return self(x, y, kind='line', **kwds)

    def scatter(self, x=None, y=None, **kwds):
        """
        Scatter plot

        Parameters
        ----------
        x, y : string, optional
            Field name to draw x- and y-positions from
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`holoplot.converter.HoloViewsConverter`.
        Returns
        -------
        obj : HoloViews object
            The HoloViews representation of the plot.
        """
        return self(x, y, kind='scatter', **kwds)

    def area(self, x=None, y=None, stacked=True, **kwds):
        """
        Area plot

        Parameters
        ----------
        x, y : string, optional
            Field name to draw x- and y-positions from
        stacked : boolean
            Whether to stack multiple areas
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`holoplot.converter.HoloViewsConverter`.
        Returns
        -------
        obj : HoloViews object
            The HoloViews representation of the plot.
        """
        if 'alpha' not in kwds and not stacked:
            kwds['alpha'] = 0.5
        return self(x, y, kind='area', stacked=stacked, **kwds)

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
            :py:meth:`holoplot.converter.HoloViewsConverter`.
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
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`holoplot.converter.HoloViewsConverter`.
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
            :py:meth:`holoplot.converter.HoloViewsConverter`.
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
            :py:meth:`holoplot.converter.HoloViewsConverter`.
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
            :py:meth:`holoplot.converter.HoloViewsConverter`.
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
            :py:meth:`holoplot.converter.HoloViewsConverter`.
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
            :py:meth:`holoplot.converter.HoloViewsConverter`.
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
            :py:meth:`holoplot.converter.HoloViewsConverter`.
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
            :py:meth:`holoplot.converter.HoloViewsConverter`.
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
            :py:meth:`holoplot.converter.HoloViewsConverter`.
        Returns
        -------
        obj : HoloViews object
            The HoloViews representation of the plot.
        """
        return self(kind='table', **dict(kwds, columns=columns))

    def image(self, x=None, y=None, colorbar=True, **kwds):
        """
        Image plot

        Parameters
        ----------
        x, y : label or position, optional
            Field name to draw x- and y-positions from
        colorbar: boolean
            Whether to display a colorbar
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`holoplot.converter.HoloViewsConverter`.
        Returns
        -------
        obj : HoloViews object
            The HoloViews representation of the plot.
        """
        return self(x, y, kind='image', colorbar=True, **kwds)

    def quadmesh(self, x=None, y=None, **kwds):
        """
        QuadMesh plot

        Parameters
        ----------
        x, y : label or position, optional
            Field name to draw x- and y-positions from
        colorbar: boolean
            Whether to display a colorbar
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`holoplot.converter.HoloViewsConverter`.
        Returns
        -------
        obj : HoloViews object
            The HoloViews representation of the plot.
        """
        return self(x, y, kind='quadmesh', colorbar=True, **kwds)



def save(obj, filename, title=None, resources=None):
    """
    Saves HoloViews objects and bokeh plots to file.

    Parameters
    ----------
    obj : HoloViews object
       HoloViews object to export
    filename : string
       Filename to save the plot to
    title : string
       Optional title for the plot
    resources: bokeh resources
       One of the valid bokeh.resources (e.g. CDN or INLINE)
    """
    if isinstance(obj, _hv.Dimensioned):
        plot = renderer.get_plot(obj).state
    else:
        raise ValueError('%s type object not recognized and cannot be saved.' %
                         type(obj).__name__)

    if filename.endswith('png'):
        _export_png(plot, filename=filename)
        return
    if not filename.endswith('.html'):
        filename = filename + '.html'

    if title is None:
        title = 'HoloPlot Plot'
    if resources is None:
        resources = _CDN

    if obj.traverse(lambda x: x, [_hv.HoloMap]):
        renderer.save(plot, filename)
    else:
        _save(plot, filename, title=title, resources=resources)


def show(obj):
    """
    Displays HoloViews objects in and outside the notebook

    Parameters
    ----------
    obj : HoloViews object
       HoloViews object to export
    """
    if not isinstance(obj, _hv.Dimensioned):
        raise ValueError('%s type object not recognized and cannot be shown.' %
                         type(obj).__name__)

    if obj.traverse(lambda x: x, [_hv.HoloMap]):
        renderer.app(obj, show=True, new_window=True)
    else:
        _show(renderer.get_plot(obj).state)


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
    kwds: HoloPlot.scatter options, optional

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
    kwds: HoloPlot.scatter options, optional

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
    return HoloPlot(lags).scatter(y1, y2, **kwds)


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
