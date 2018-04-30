import holoviews as _hv
from holoviews import (
    extension as _extension, Dimensioned as _Dimensioned, HoloMap as _HoloMap
)
from holoviews.ipython import display

from bokeh.io import export_png as _export_png, show as _show, save as _save
from bokeh.resources import CDN as _CDN

from .converter import HoloViewsConverter

renderer = _hv.renderer('bokeh')

# Register plotting interfaces
def _patch_plot(self):
    return HoloPlot(self)


def patch(library, extension=None):
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
    if extension:
        _extension(extension)


class HoloPlot(object):

    def __init__(self, data):
        self._data = data

    def __call__(self, x=None, y=None, kind=None, backlog=1000,
             width=700, height=300, title=None, grid=False,
             legend=True, logx=False, logy=False, loglog=False,
             xticks=None, yticks=None, xlim=None, ylim=None, rot=None,
             fontsize=None, colormap=None, hover=True, **kwds):
        converter = HoloViewsConverter(
            self._data, x, y, width=width, height=height, backlog=backlog,
            title=title, grid=grid, legend=legend, logx=logx,
            logy=logy, loglog=loglog, xticks=xticks, yticks=yticks,
            xlim=xlim, ylim=ylim, rot=rot, fontsize=fontsize,
            colormap=colormap, hover=hover, kind=kind, **kwds
        )
        return converter(kind, x, y)

    def line(self, x=None, y=None, **kwds):
        """
        Line plot

        Parameters
        ----------
        x, y : label or position, optional
            Coordinates for each point.
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`intake.source.base.DataSource.plot`.
        Returns
        -------
        Element : Element or NdOverlay of Elements
        """
        return self(x, y, kind='line', **kwds)

    def scatter(self, x=None, y=None, **kwds):
        """
        Scatter plot

        Parameters
        ----------
        x, y : label or position, optional
            Coordinates for each point.
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`intake.source.base.DataSource.plot`.
        Returns
        -------
        Element : Element or NdOverlay of Elements
        """
        return self(x, y, kind='scatter', **kwds)

    def area(self, x=None, y=None, **kwds):
        """
        Area plot

        Parameters
        ----------
        x, y : label or position, optional
            Coordinates for each point.
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`intake.source.base.DataSource.plot`.
        Returns
        -------
        Element : Element or NdOverlay of Elements
        """
        return self(x, y, kind='area', **kwds)

    def heatmap(self, x=None, y=None, z=None, **kwds):
        """
        HeatMap plot

        Parameters
        ----------
        x, y, z : label or position, optional
            Coordinates for each point.
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`intake.source.base.DataSource.plot`.
        Returns
        -------
        Element : Element or NdOverlay of Elements
        """
        return self(x, y, kind='heatmap', z=z, **kwds)

    def hexbin(self, x=None, y=None, z=None, **kwds):
        """
        HexBin plot

        Parameters
        ----------
        x, y : label or position, optional
            Coordinates for each point.
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`intake.source.base.DataSource.plot`.
        Returns
        -------
        Element : Element or NdOverlay of Elements
        """
        return self(x, y, kind='hexbin', **kwds)

    def bar(self, x=None, y=None, **kwds):
        """
        Bars plot

        Parameters
        ----------
        x, y : label or position, optional
            Coordinates for each point.
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`intake.source.base.DataSource.plot`.
        Returns
        -------
        Element : Element or NdOverlay of Elements
        """
        return self(x, y, kind='bar', **kwds)

    def barh(self, x=None, y=None, **kwds):
        """
        Horizontal bar plot

        Parameters
        ----------
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`intake.source.base.DataSource.plot`.
        Returns
        -------
        Element : Element or NdOverlay of Elements
        """
        return self(x, y, kind='barh', **kwds)

    def box(self, y=None, **kwds):
        """
        Boxplot

        Parameters
        ----------
        by : string or sequence
            Column in the DataFrame to group by.
        kwds : optional
            Keyword arguments to pass on to
            :py:meth:`intake.source.base.DataSource.plot`.
        Returns
        -------
        Element : Element or NdOverlay of Elements
        """
        return self(kind='box', x=None, y=y, **dict(kwds, hover=False))

    def violin(self, y=None, **kwds):
        """
        Boxplot

        Parameters
        ----------
        by : string or sequence
            Column in the DataFrame to group by.
        kwds : optional
            Keyword arguments to pass on to
            :py:meth:`intake.source.base.DataSource.plot`.
        Returns
        -------
        Element : Element or NdOverlay of Elements
        """
        return self(kind='violin', x=None, y=y, **dict(kwds, hover=False))

    def hist(self, y=None, **kwds):
        """
        Histogram

        Parameters
        ----------
        by : string or sequence
            Column in the DataFrame to group by.
        kwds : optional
            Keyword arguments to pass on to
            :py:meth:`intake.source.base.DataSource.plot`.
        Returns
        -------
        Element : Element or NdOverlay of Elements
        """
        return self(kind='hist', x=None, y=y, **kwds)

    def kde(self, y=None, **kwds):
        """
        KDE

        Parameters
        ----------
        by : string or sequence
            Column in the DataFrame to group by.
        kwds : optional
            Keyword arguments to pass on to
            :py:meth:`intake.source.base.DataSource.plot`.
        Returns
        -------
        Element : Element or NdOverlay of Elements
        """
        return self(kind='kde', x=None, y=y, **kwds)

    def table(self, columns=None, **kwds):
        """
        Table

        Parameters
        ----------
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`intake.source.base.DataSource.plot`.
        Returns
        -------
        Element : Element or NdOverlay of Elements
        """
        return self(kind='table', **dict(kwds, columns=columns))

    def image(self, x=None, y=None, z=None, **kwds):
        """
        Image plot

        Parameters
        ----------
        x, y, z : label or position, optional
            Coordinates for each point.
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`intake.source.base.DataSource.plot`.
        Returns
        -------
        Element : Element or NdOverlay of Elements
        """
        return self(x, y, kind='image', z=z, **kwds)

    def quadmesh(self, x=None, y=None, z=None, **kwds):
        """
        QuadMesh plot

        Parameters
        ----------
        x, y, z : label or position, optional
            Coordinates for each point.
        **kwds : optional
            Keyword arguments to pass on to
            :py:meth:`intake.source.base.DataSource.plot`.
        Returns
        -------
        Element : Element or NdOverlay of Elements
        """
        return self(x, y, kind='quadmesh', z=z, **kwds)



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
    if isinstance(obj, _Dimensioned):
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

    if obj.traverse(lambda x: x, [_HoloMap]):
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
    if not isinstance(obj, _Dimensioned):
        raise ValueError('%s type object not recognized and cannot be shown.' %
                         type(obj).__name__)

    if obj.traverse(lambda x: x, [_HoloMap]):
        renderer.app(obj, show=True, new_window=True)
    else:
        _show(renderer.get_plot(obj).state)
