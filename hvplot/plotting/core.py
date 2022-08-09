from collections import defaultdict

import param
try:
    import panel as pn
    panel_available = True
except:
    panel_available = False

from ..converter import HoloViewsConverter
from ..util import is_list_like, process_dynamic_args


class hvPlotBase:

    __all__ = []

    def __init__(self, data, custom_plots={}, **metadata):
        if 'query' in metadata:
            data = data.query(metadata.pop('query'))
        if 'sel' in metadata:
            data = data.sel(**metadata.pop('sel'))
        if 'isel' in metadata:
            data = data.isel(**metadata.pop('isel'))
        self._data = data
        self._plots = custom_plots
        self._metadata = metadata

    def __call__(self, x=None, y=None, kind=None, **kwds):
        """
        Default plot method (for more detailed options use specific
        plot method, e.g. df.hvplot.line)

        Parameters
        ----------
        x : string, list, or array-like, optional
            Field name(s) to draw x-positions from
        y : string, list, or array-like, optional
            Field name(s) to draw y-positions from
        kind : string, optional
            The kind of plot to generate, e.g. 'line', 'scatter', etc.
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('scatter')` or similar
            depending on the type of plot.
        
        Returns
        -------
        HoloViews object: Object representing the requested visualization
        """
        # Convert an array-like to a list
        x = list(x) if is_list_like(x) else x
        y = list(y) if is_list_like(y) else y

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
        dirs = super().__dir__()
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
        return super().__getattribute__(name)


class hvPlotTabular(hvPlotBase):
    __all__ = [
        'line',
        'step',
        'scatter',
        'area',
        'errorbars',
        'ohlc',
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
        The `line` plot connect the points with a continous curve.
        
        A `line` plot is useful when data is continuous and has a continuous axis.

        Reference: https://hvplot.holoviz.org/reference/pandas/line.html

        Examples
        --------

        >>> import hvplot.pandas
        >>> from bokeh.sampledata.degrees import data as deg
        >>> line = deg.hvplot.line(
        ...     x='Year', y=['Art and Performance', 'Business', 'Biology', 'Education', 'Computer Science'],
        ...     value_label='% of Degrees Earned by Women', legend='top', height=500, width=620
        ... )
        >>> line

        You can can add *markers* to a `line` plot by overlaying with a `scatter` plot.

        >>> scatter = deg.hvplot.scatter(
        ...     x='Year', y=['Art and Performance', 'Business', 'Biology', 'Education', 'Computer Science'],
        ...     value_label='% of Degrees Earned by Women', legend='top', height=500, width=620
        ... )
        >>> line * scatter

        Parameters
        ----------
        x : string, optional
            Allows plotting of one column versus another. If not specified, the index is
            used.
        y : string or list, optional
            Allows plotting of one column versus another. If not specified, all numerical
            dimensions are used.
        by : string, optional
            A single column or list of columns to group by.
        color : str, array-like, or dict, optional
            The color for each of the series. Possible values are:
            
            A single color string referred to by name, RGB or RGBA code, for instance 'red' or
            '#a98d19.

            A sequence of color strings referred to by name, RGB or RGBA code, which will be used
            for each series recursively. For instance ['green','yellow'] each column’s line will be
            filled in green or yellow, alternatively. If there is only a single series to be
            plotted, then only the first color from the color list will be used.

            A dict of the form {column namecolor}, so that each series will be colored accordingly.
            For example, if your series are called a and b, then passing {'a': 'green', 'b': 'red'}
            will color lines for series a in green and lines for series b in red.
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('line')`.
                
        Returns
        -------
        obj: Holoviews object
            You can `print` the object to study its composition and run `hv.help` on the the
            object to learn more about its parameters and options.

        References
        ----------

        - Bokeh: https://docs.bokeh.org/en/latest/docs/first_steps/first_steps_1.html#creating-a-simple-line-chart
        - Pandas: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.line.html
        - Plotly: https://plotly.com/python/line-charts/
        - Matplotlib: https://matplotlib.org/stable/plot_types/basic/plot.html
        - Wiki: https://en.wikipedia.org/wiki/Line_chart
        """
        return self(x, y, kind='line', **kwds)

    def step(self, x=None, y=None, where='mid', **kwds):
        """
        The `step` plot can be used pretty much anytime the `line` plot might be used, and has many
        of the same options available.

        Reference: https://hvplot.holoviz.org/reference/pandas/step.html

        Wiki: #Todo: Find a link
        
        Example:

        >>> import hvplot.pandas
        >>> from bokeh.sampledata.degrees import data as deg
        >>> deg.sample(n=5)
        >>> deg.hvplot.step(
        ...     x='Year',
        ...     y=['Art and Performance', 'Business', 'Biology', 'Education', 'Computer Science'], 
        ...     value_label='% of Degrees Earned by Women', legend='top', height=500, width=620
        ... )

        Parameters
        ----------
        x : string, optional
            Field name to draw x-positions from
        y : string, optional
            Field name to draw y-positions from
        where : string, optional
            Defines where the steps are placed (options: 'mid' (default), 'pre' and 'post')
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('step')`.
        
        Returns
        -------
        obj: Holoviews object
            You can `print` the object to study its composition and run `hv.help` on the the
            object to learn more about its parameters and options.
        """
        return self(x, y, kind='step', where=where, **kwds)

    def scatter(self, x=None, y=None, **kwds):
        """
        The `scatter` plot is a good first way to plot data with non continuous axes.
        
        Todo: Figure out why "non continous axes"

        Reference: https://hvplot.holoviz.org/reference/pandas/scatter.html

        Wiki: https://en.wikipedia.org/wiki/Scatter_plot

        Example:

        >>> import hvplot.pandas
        >>> from bokeh.sampledata.iris import flowers as df
        >>> df.hvplot.scatter(
        ...     x='sepal_length', y='sepal_width', by='species', 
        ...     legend='top', height=400, width=400
        ... )

        The points will be grouped and color coded `by` the categorical values in the 'species'
        column.

        Parameters

        ----------
        x : string, optional
            Field name to draw x-positions from
        y : string, optional
            Field name to draw y-positions from
        c: string, optional
            Name of the field to color points by
        s: string, optional
            Name of the field to scale point size by
        scale: number, optional
            Scaling factor to apply to point scaling
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('scatter')`.
        
        Returns
        -------
        obj: Holoviews object
            You can `print` the object to study its composition and run `hv.help` on the the
            object to learn more about its parameters and options.
        """
        return self(x, y, kind='scatter', **kwds)

    def area(self, x=None, y=None, y2=None, stacked=True, **kwds):
        """
        The `area` plot can be used to color the area under a line or to color the space between two
        lines.

        Reference: https://hvplot.holoviz.org/reference/pandas/area.html

        Wiki: https://en.wikipedia.org/wiki/Area_chart

        Example:

        Parameters
        ----------
        x, y, y2 : string, optional
            Field name to draw x- and y-positions from
        stacked : boolean
            Whether to stack multiple areas
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('area')`.
        
        Returns
        -------
        obj: Holoviews object
            You can `print` the object to study its composition and run `hv.help` on the the
            object to learn more about its parameters and options.
        """
        if 'alpha' not in kwds and not stacked:
            kwds['alpha'] = 0.5
        return self(x, y, y2=y2, kind='area', stacked=stacked, **kwds)

    def errorbars(self, x=None, y=None, yerr1=None, yerr2=None, **kwds):
        """
        The `errorbars` plot can be used for plotting the `mean` and `std`. `errorbars` is most
        helpful when overlayed with other plot types. To do this you can use the * operator.

        Reference: https://hvplot.holoviz.org/reference/pandas/errorbars.html

        Example:

        Parameters
        ----------
        x, y, y2 : string, optional
            Field name to draw x- and y-positions from
        yerr1 : string, optional
            Field name to draw symmetric / negative errors from
        yerr2 : string, optional
            Field name to draw positive errors from
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('errorbars')`.
        
        Returns
        -------
        obj: Holoviews object
            You can `print` the object to study its composition and run `hv.help` on the the
            object to learn more about its parameters and options.
        """
        return self(x, y, kind='errorbars',
                    yerr1=yerr1, yerr2=yerr2, **kwds)

    def ohlc(self, x=None, y=None, **kwds):
        """
        The `ohlc` plot visualizes the open, high, low and close prices of stocks and other assets.

        Reference: https://hvplot.holoviz.org/reference/pandas/ohlc.html

        Example:

        Parameters
        ----------
        x: string, optional
            Field name to draw x coordinates from.
        y: list or tuple, optional
            Field names of the OHLC columns
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('ohlc')`.
        
        
        Returns
        -------
        obj: Holoviews object
            You can `print` the object to study its composition and run `hv.help` on the the
            object to learn more about its parameters and options.
        """
        return self(kind='ohlc', x=x, y=y, **kwds)

    def heatmap(self, x=None, y=None, C=None, colorbar=True, **kwds):
        """
        The `heatmap` plot shows the magnitude of a phenomenon as color coded cells in a two
        dimensional matrix.

        Reference: https://hvplot.holoviz.org/reference/pandas/heatmap.html
        
        Wiki: https://en.wikipedia.org/wiki/Heat_map

        Example:

        Parameters
        ----------
        x : string, optional
            Field name to draw x-positions from
        y : string, optional
            Field name to draw y-positions from
        C : string
            Field to draw heatmap color from
        colorbar: boolean
            Whether to display a colorbar
        reduce_function : function
            Function to compute statistics for heatmap
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('heatmap')`.
        
        
        Returns
        -------
        obj : Holoviews object
            You can `print` the object to study its composition and run `hv.help` on the the
            object to learn more about its parameters and options.
        """
        return self(x, y, kind='heatmap', C=C, colorbar=colorbar, **kwds)

    def hexbin(self, x=None, y=None, C=None, colorbar=True, **kwds):
        """
        The `hexbin` plot uses hexagons to split the area into several parts and attribute a color
        to it.
        
        The graphic area is divided into a multitude of hexagons
        and the number of data points in each is counted and represented using a color gradient.
        This chart is used to visualize density, where hexagon as a shape permits to create
        contiguous areas easily while dividing the whole space into discrete units.

        `hexbin` offers a straightforward method for plotting dense data.

        Reference: https://hvplot.holoviz.org/reference/pandas/hexbin.html
        
        Wiki: https://think.design/services/data-visualization-data-design/hexbin/

        Example:

        Parameters
        ----------
        x : string, optional
            Field name to draw x-positions from
        y : string, optional
            Field name to draw y-positions from
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
            Additional keywords arguments are documented in `hvplot.help('hexbin')`.
        
        
        Returns
        -------
        obj: Holoviews object
            You can `print` the object to study its composition and run `hv.help` on the the
            object to learn more about its parameters and options.
        """
        return self(x, y, kind='hexbin', C=C, colorbar=colorbar, **kwds)

    def bivariate(self, x=None, y=None, colorbar=True, **kwds):
        """
        `bivariate` is a statistical method for creating a *2D density plot*. `bivariate`
        plots can be a useful alternative to scatter plots, if your data are too dense to plot
        each point individually.

        Reference: https://hvplot.holoviz.org/reference/pandas/bivariate.html

        Wiki: https://en.wikipedia.org/wiki/Bivariate_analysis

        Example:

        Parameters
        ----------
        x : string, optional
            Field name to draw x-positions from
        y : string, optional
            Field name to draw y-positions from
        colorbar: boolean
            Whether to display a colorbar
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('bivariate')`.
        
        Returns
        -------
        obj: Holoviews object
            You can `print` the object to study its composition and run `hv.help` on the the
            object to learn more about its parameters and options.
        """
        return self(x, y, kind='bivariate', colorbar=colorbar, **kwds)

    def bar(self, x=None, y=None, **kwds):
        """
        A vertical bar plot

        A `bar` plot represents categorical data with rectangular bars
        with heights proportional to the values that they represent. The x-axis
        plots categories and the y axis represents the value scale.
        The bars are of equal width which allows for instant comparison of data.
        
        `bar` can be used on dataframes with regular Index or MultiIndex.

        Reference: https://hvplot.holoviz.org/reference/pandas/bar.html
        
        Wiki: https://en.wikipedia.org/wiki/Bar_chart

        Example:

        Parameters
        ----------
        x : string, optional
            Field name to draw x-positions from
        y : string, optional
            Field name to draw y-positions from
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('bar')`.
        
        Returns
        -------
        obj: Holoviews object
            You can `print` the object to study its composition and run `hv.help` on the the
            object to learn more about its parameters and options.
        """
        return self(x, y, kind='bar', **kwds)

    def barh(self, x=None, y=None, **kwds):
        """
        A horizontal bar plot

        A `barh` plot represents categorical data with rectangular bars
        with heights proportional to the values that they represent. The y-axis of the chart
        plots categories and the x-axis represents the value scale.
        The bars are of equal width which allows for instant comparison of data.
        
        `barh` can be used on dataframes with regular Index or MultiIndex.

        Reference: https://hvplot.holoviz.org/reference/pandas/barh.html
        
        Wiki: https://en.wikipedia.org/wiki/Bar_chart

        Example:

        Parameters
        ----------
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('image')`.
        
        Returns
        -------
        obj: Holoviews object
            You can `print` the object to study its composition and run `hv.help` on the the
            object to learn more about its parameters and options.
        """
        return self(x, y, kind='barh', **kwds)

    def box(self, y=None, by=None, **kwds):
        """
        The `box` plot gives you a visual idea about 5 components in a dataset. It is also
        known as *box and whiskers plot*. It is useful for describing measures of
        central tendencies and measures of dispersion in a dataset.

        `box` plots are most useful when grouped by additional dimensions.

        Reference: https://hvplot.holoviz.org/reference/pandas/box.html

        Wiki: https://en.wikipedia.org/wiki/Box_plot

        Example:

        Parameters
        ----------
        y : string or sequence
            Column in the DataFrame to compute distribution on.
        by : string or sequence
            Column in the DataFrame to group by.
        kwds : optional
            Additional keywords arguments are documented in `hvplot.help('box')`.
        
        Returns
        -------
        obj: Holoviews object
            You can `print` the object to study its composition and run `hv.help` on the the
            object to learn more about its parameters and options.
        """
        return self(kind='box', x=None, y=y, by=by, **dict(kwds, hover=False))

    def violin(self, y=None, by=None, **kwds):
        """
        Violin plot

        Reference: https://hvplot.holoviz.org/reference/pandas/violin.html

        Example:

        Parameters
        ----------
        y : string or sequence
            Column in the DataFrame to compute distribution on.
        by : string or sequence
            Column in the DataFrame to group by.
        kwds : optional
            Additional keywords arguments are documented in `hvplot.help('violin')`.
        
        Returns
        -------
        obj: Holoviews object
            You can `print` the object to study its composition and run `hv.help` on the the
            object to learn more about its parameters and options.
        """
        return self(kind='violin', x=None, y=y, by=by, **dict(kwds, hover=False))

    def hist(self, y=None, by=None, **kwds):
        """
        Histogram

        Reference: https://hvplot.holoviz.org/reference/pandas/hist.html

        Example:

        Parameters
        ----------
        y : string or sequence
            Column in the DataFrame to compute distribution on.
        by : string or sequence
            Column in the DataFrame to group by.
        kwds : optional
            Additional keywords arguments are documented in `hvplot.help('hist')`.
        
        Returns
        -------
        obj: Holoviews object
            You can `print` the object to study its composition and run `hv.help` on the the
            object to learn more about its parameters and options.
        """
        return self(kind='hist', x=None, y=y, by=by, **kwds)

    def kde(self, y=None, by=None, **kwds):
        """
        KDE plot

        Reference: https://hvplot.holoviz.org/reference/pandas/kde.html

        Example:

        Parameters
        ----------
        y : string or sequence
            Column in the DataFrame to compute distribution on.
        by : string or sequence
            Column in the DataFrame to group by.
        kwds : optional
            Additional keywords arguments are documented in `hvplot.help('kde')`.
        
        Returns
        -------
        obj: Holoviews object
            You can `print` the object to study its composition and run `hv.help` on the the
            object to learn more about its parameters and options.
        """
        return self(kind='kde', x=None, y=y, by=by, **kwds)

    def density(self, y=None, by=None, **kwds):
        """
        Density plot. Same as `kde` plot

        Reference: https://hvplot.holoviz.org/reference/pandas/kde.html

        Example:

        Parameters
        ----------
        y : string or sequence
            Column in the DataFrame to compute distribution on.
        by : string or sequence
            Column in the DataFrame to group by.
        kwds : optional
            Additional keywords arguments are documented in `hvplot.help('kde')`.
        
        Returns
        -------
        obj: Holoviews object
            You can `print` the object to study its composition and run `hv.help` on the the
            object to learn more about its parameters and options.
        """
        return self(kind='kde', x=None, y=y, by=by, **kwds)

    def table(self, columns=None, **kwds):
        """
        Table

        Reference: https://hvplot.holoviz.org/reference/pandas/table.html

        Example:

        Parameters
        ----------
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('table')`.
        
        Returns
        -------
        obj: Holoviews object
            You can `print` the object to study its composition and run `hv.help` on the the
            object to learn more about its parameters and options.
        """
        return self(kind='table', **dict(kwds, columns=columns))

    def dataset(self, columns=None, **kwds):
        """
        Dataset

        Todo: Describe the reason for exposing this.

        Reference: Todo. Find link

        Example:

        Parameters
        ----------
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('dataset')`.
        
        Returns
        -------
        obj: Holoviews Dataset
            You can `print` the object to study its composition and run `hv.help` on the the
            object to learn more about its parameters and options.
        """
        return self(kind='dataset', **dict(kwds, columns=columns))

    def points(self, x=None, y=None, **kwds):
        """
        Point plot use for 2D coordinate systems

        Reference: https://hvplot.holoviz.org/reference/geopandas/points.html

        Example:

        Parameters
        ----------
        x, y : string, optional
            The coordinate variable along the x- and y-axis
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('points')`.
        
        Returns
        -------
        obj: Holoviews object
            You can `print` the object to study its composition and run `hv.help` on the the
            object to learn more about its parameters and options.
        """
        return self(x, y, kind='points', **kwds)

    def vectorfield(self, x=None, y=None, angle=None, mag=None, **kwds):
        """
        Vectorfield plot

        Reference: https://hvplot.holoviz.org/reference/xarray/vectorfield.html

        Example:

        Parameters
        ----------
        x : string, optional
            Field name to draw x-positions from
        y : string, optional
            Field name to draw y-positions from
        mag : string, optional
            Magnitude
        angle : string, optional
            Angle
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('vectorfield')`.
        
        Returns
        -------
        obj: Holoviews object
            You can `print` the object to study its composition and run `hv.help` on the the
            object to learn more about its parameters and options.
        """
        return self(x, y, angle=angle, mag=mag, kind='vectorfield', **kwds)

    def polygons(self, x=None, y=None, c=None, **kwds):
        """
        Polygon plot for geopandas dataframes

        Reference: https://hvplot.holoviz.org/reference/geopandas/polygons.html

        Example:

        Parameters
        ----------
        c: string, optional
            The dimension to color the polygons by
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('polygons')`.
        
        Returns
        -------
        obj: Holoviews object
            You can `print` the object to study its composition and run `hv.help` on the the
            object to learn more about its parameters and options.
        """
        return self(x, y, c=c, kind='polygons', **kwds)

    def paths(self, x=None, y=None, c=None, **kwds):
        """
        LineString and LineRing plot for geopandas dataframes.

        Reference: https://github.com/holoviz/hvplot/issues/828

        Example:

        Parameters
        ----------
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('paths')`.
        
        Returns
        -------
        obj: Holoviews object
            You can `print` the object to study its composition and run `hv.help` on the the
            object to learn more about its parameters and options.
        """
        return self(x, y, c=c, kind='paths', **kwds)

    def labels(self, x=None, y=None, text=None, **kwds):
        """
        Labels plot.

        Reference: https://hvplot.holoviz.org/reference/pandas/labels.html

        Example:

        Parameters
        ----------
        x, y : string, optional
            The coordinate variable along the x- and y-axis
        text : string, optional
            The column to draw the text labels from
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('labels')`.
        
        Returns
        -------
        obj: Holoviews object
            You can `print` the object to study its composition and run `hv.help` on the the
            object to learn more about its parameters and options.
        """
        return self(x, y, text=text, kind='labels', **kwds)

class hvPlot(hvPlotTabular):
    """hvPlot provides methods like `.line`, `step`, `scatter` etc. to plot your tabular
    data source. These methods works just like the familiar Pandas `.plot` function.
    
    `hvPlot` supports a wide range of data sources and plotting backends.

    `hvPlot` is available as `.hvplot` on your data source after you have imported the appropriate
    backend.
    
    Example:

    >>> import pandas as pd
    >>> import hvplot.pandas

    >>> x=y=list(range(0, 10))
    >>> df = pd.DataFrame({"observation": x, "value": y})

    >>> df.hvplot.scatter(x="observation", y="value")
    >>> # or alternatively
    >>> df.hvplot(x="observation", y="value", kind="scatter")

    Tips & Tricks:
    
    - Run `hvplot.help('scatter')` to see all the available arguments for a scatter plot.
    - Use `*` to overlay two plots and `+` to layout two plots next to each other.
    """
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

        You can very often use `image` to display an x, y grid, like for example geographic
        data with `latitude` and `longitude` coordinates.

        Reference: https://hvplot.holoviz.org/reference/xarray/image.html

        Example:

        >>> import hvplot.xarray
        >>> import xarray as xr
        >>> ds = xr.tutorial.open_dataset('air_temperature')
        >>> ds.hvplot.image(x='lon', y='lat', z='air', groupby='time', cmap='kbc_r')

        Example:

        Parameters
        ----------
        x : string, optional
            The coordinate variable along the x-axis
        y : string, optional
            The coordinate variable along the y-axis
        z : string, optional
            The data variable to plot
        colorbar: boolean
            Whether to display a colorbar
        kwds : optional
            To see all the keyword arguments available, run `hvplot.help('image')`.
        
        Returns
        -------
        obj: Holoviews object
            You can `print` the object to study its composition and run `hv.help` on the the
            object to learn more about its parameters and options.
        """
        return self(x, y, z=z, kind='image', colorbar=colorbar, **kwds)

    def rgb(self, x=None, y=None, z=None, bands=None, **kwds):
        """
        RGB plot

        Reference: https://hvplot.holoviz.org/reference/xarray/rgb.html

        Example:

        Parameters
        ----------
        x, y : string, optional
            The coordinate variable along the x- and y-axis
        bands : string, optional
            The coordinate variable to draw the RGB channels from
        z : string, optional
            The data variable to plot
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('rgb')`.
        
        Returns
        -------
        obj: Holoviews object
            You can `print` the object to study its composition and run `hv.help` on the the
            object to learn more about its parameters and options.
        """
        if bands is not None:
            kwds['bands'] = bands
        return self(x, y, z=z, kind='rgb', **kwds)

    def quadmesh(self, x=None, y=None, z=None, colorbar=True, **kwds):
        """
        QuadMesh plot

        Reference: https://hvplot.holoviz.org/reference/xarray/quadmesh.html

        Example:

        Parameters
        ----------
        x, y : string, optional
            The coordinate variable along the x- and y-axis
        z : string, optional
            The data variable to plot
        colorbar: boolean
            Whether to display a colorbar
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('quadmesh')`.
        
        Returns
        -------
        obj: Holoviews object
            You can `print` the object to study its composition and run `hv.help` on the the
            object to learn more about its parameters and options.
        """
        return self(x, y, z=z, kind='quadmesh', colorbar=colorbar, **kwds)

    def contour(self, x=None, y=None, z=None, colorbar=True, **kwds):
        """
        Line contour plot

        Reference: https://hvplot.holoviz.org/reference/xarray/contour.html

        Example:

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
            Additional keywords arguments are documented in `hvplot.help('contour')`.
        
        Returns
        -------
        obj: Holoviews object
            You can `print` the object to study its composition and run `hv.help` on the the
            object to learn more about its parameters and options.
        """
        return self(x, y, z=z, kind='contour', colorbar=colorbar, **kwds)

    def contourf(self, x=None, y=None, z=None, colorbar=True, **kwds):
        """
        Filled contour plot

        Reference. https://hvplot.holoviz.org/reference/xarray/contourf.html

        Example:

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
            Additional keywords arguments are documented in `hvplot.help('contourf')`.
        
        Returns
        -------
        obj: Holoviews object
            You can `print` the object to study its composition and run `hv.help` on the the
            object to learn more about its parameters and options.
        """
        return self(x, y, z=z, kind='contourf', colorbar=colorbar, **kwds)
