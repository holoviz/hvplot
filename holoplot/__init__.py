from .converter import HoloViewsConverter

# Register plotting interfaces
def _patch_plot(self):
    return HoloPlot(self)


def patch(library):
    """
    Patch library to support HoloViews based plotting API.
    """
    if library == 'streamz':
        try:
            import streamz.dataframe as sdf
        except ImportError:
            raise ImportError('Could not patch plotting API onto streamz. '
                              'Streamz could not be imported.')
        sdf.DataFrame.plot = property(_patch_plot)
        sdf.DataFrames.plot = property(_patch_plot)
        sdf.Series.plot = property(_patch_plot)
        sdf.Seriess.plot = property(_patch_plot)
    elif library == 'pandas':
        try:
            import pandas as pd
        except:
            raise ImportError('Could not patch plotting API onto pandas. '
                              'Pandas could not be imported.')
        pd.DataFrame.plot = property(_patch_plot)
        pd.Series.plot = property(_patch_plot)
    elif library == 'dask':
        try:
            import dask.dataframe as dd
        except:
            raise ImportError('Could not patch plotting API onto dask. '
                              'Dask could not be imported.')
        dd.DataFrame.plot = property(_patch_plot)
        dd.Series.plot = property(_patch_plot)
    elif library == 'intake':
        
        try:
            from intake.source.base import DataSource
        except ImportError:
            raise ImportError('Could not patch plotting API onto intake. '
                              'Intake could not be imported.')
        DataSource.plot = property(_patch_plot)


class HoloPlot(object):

    def __init__(self, data):
        self._data = data

    def __call__(self, x=None, y=None, kind='line', backlog=1000,
             width=700, height=300, title=None, grid=False,
             legend=True, logx=False, logy=False, loglog=False,
             xticks=None, yticks=None, xlim=None, ylim=None, rot=None,
             fontsize=None, colormap=None, hover=True, **kwds):
        converter = HoloViewsConverter(
            self._data, width=width, height=height, backlog=backlog,
            title=title, grid=grid, legend=legend, logx=logx,
            logy=logy, loglog=loglog, xticks=xticks, yticks=yticks,
            xlim=xlim, ylim=ylim, rot=rot, fontsize=fontsize,
            colormap=colormap, hover=hover, **kwds
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
