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
    """
    The plotting method: `df.hvplot(...)` creates a plot similarly to the familiar Pandas
    `df.plot` method.

    For more detailed options use a specific ploting method, e.g. `df.hvplot.line`.

    Reference: https://hvplot.holoviz.org/reference/index.html

    Parameters
    ----------
    x : string, optional
        Field name(s) to draw x-positions from. If not specified, the index is
        used.
    y : string or list, optional
        Field name(s) to draw y-positions from. If not specified, all numerical
        fields are used.
    kind : string, optional
        The kind of plot to generate, e.g. 'area', 'bar', 'line', 'scatter' etc. To see the
        available plots run `print(df.hvplot.__all__)`.
    **kwds : optional
        Additional keywords arguments are documented in `hvplot.help('scatter')` or similar
        depending on the kind of plot.

    Returns
    -------
    A Holoviews object. You can `print` the object to study its composition and run `hv.help` on
    the object to learn more about its parameters and options.

    Examples
    --------

    >>> import hvplot.pandas
    >>> from bokeh.sampledata.degrees import data as deg

    >>> line = deg.hvplot(
    ...     x="Year",
    ...     y=["Art and Performance", "Business", "Biology", "Education", "Computer Science"],
    ...     value_label="% of Degrees Earned by Women",
    ...     legend="top",
    ...     height=500,
    ...     width=620,
    ...     kind="line",
    ... )
    >>> line

    You can can add *markers* to a `line` plot by overlaying with a `scatter` plot.

    >>> scatter = deg.hvplot.scatter(
    ...     x="Year",
    ...     y=["Art and Performance", "Business", "Biology", "Education", "Computer Science"],
    ...     value_label="% of Degrees Earned by Women",
    ...     legend="top",
    ...     height=500,
    ...     width=620,
    ... )
    >>> line * scatter

    Please note that you can pass widgets or reactive functions as arguments instead of
    literal values, c.f. https://hvplot.holoviz.org/user_guide/Widgets.html.
    """

    __all__ = []

    def __init__(self, data, custom_plots={}, **metadata):
        if "query" in metadata:
            data = data.query(metadata.pop("query"))
        if "sel" in metadata:
            data = data.sel(**metadata.pop("sel"))
        if "isel" in metadata:
            data = data.isel(**metadata.pop("isel"))
        self._data = data
        self._plots = custom_plots
        self._metadata = metadata

    def __call__(self, x=None, y=None, kind=None, **kwds):
        # Convert an array-like to a list
        x = list(x) if is_list_like(x) else x
        y = list(y) if is_list_like(y) else y

        if isinstance(kind, str) and kind not in self.__all__:
            raise NotImplementedError(
                "kind='{kind}' for data of type {type}".format(kind=kind, type=type(self._data))
            )

        if panel_available:
            panel_args = ["widgets", "widget_location", "widget_layout", "widget_type"]
            panel_dict = {}
            for k in panel_args:
                if k in kwds:
                    panel_dict[k] = kwds.pop(k)
            dynamic, arg_deps, arg_names = process_dynamic_args(x, y, kind, **kwds)
            if dynamic or arg_deps:

                @pn.depends(*arg_deps, **dynamic)
                def callback(*args, **dyn_kwds):
                    xd = dyn_kwds.pop("x", x)
                    yd = dyn_kwds.pop("y", y)
                    kindd = dyn_kwds.pop("kind", kind)

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
        x = x or params.pop("x", None)
        y = y or params.pop("y", None)
        kind = kind or params.pop("kind", None)
        return HoloViewsConverter(self._data, x, y, kind=kind, **params)

    def __dir__(self):
        """
        List default attributes and custom defined plots.
        """
        dirs = super().__dir__()
        return sorted(list(dirs) + list(self._plots))

    def __getattribute__(self, name):
        """
        Custom getattribute to expose user defined subplots.
        """
        plots = object.__getattribute__(self, "_plots")
        if name in plots:
            plot_opts = plots[name]
            if "kind" in plot_opts and name in HoloViewsConverter._kind_mapping:
                param.main.warning(
                    "Custom options for existing plot types should not "
                    "declare the 'kind' argument. The .%s plot method "
                    "was unexpectedly customized with kind=%r." % (plot_opts["kind"], name)
                )
                plot_opts["kind"] = name
            return hvPlotBase(self._data, **dict(self._metadata, **plot_opts))
        return super().__getattribute__(name)


class hvPlotTabular(hvPlotBase):
    """
    The plotting method: `df.hvplot(...)` creates a plot similarly to the familiar Pandas
    `df.plot` method.

    For more detailed options use a specific ploting method, e.g. `df.hvplot.line`.

    Reference: https://hvplot.holoviz.org/reference/index.html

    Parameters
    ----------
    x : string, optional
        Field name(s) to draw x-positions from. If not specified, the index is
        used.
    y : string or list, optional
        Field name(s) to draw y-positions from. If not specified, all numerical
        fields are used.
    kind : string, optional
        The kind of plot to generate, e.g. 'area', 'bar', 'line', 'scatter' etc. To see the
        available plots run `print(df.hvplot.__all__)`.
    **kwds : optional
        Additional keywords arguments are documented in `hvplot.help('scatter')` or similar
        depending on the kind of plot.

    Returns
    -------
    A Holoviews object. You can `print` the object to study its composition and run

    >>> import holoviews as hv
    >>> hv.help(the_holoviews_object)

    to learn more about its parameters and options.

    Examples
    --------

    >>> import hvplot.pandas
    >>> from bokeh.sampledata.degrees import data as deg

    >>> line = deg.hvplot(
    ...     x="Year",
    ...     y=["Art and Performance", "Business", "Biology", "Education", "Computer Science"],
    ...     value_label="% of Degrees Earned by Women",
    ...     legend="top",
    ...     height=500,
    ...     width=620,
    ...     kind="line",
    ... )
    >>> line

    You can can add *markers* to a `line` plot by overlaying with a `scatter` plot.

    >>> scatter = deg.hvplot.scatter(
    ...     x="Year",
    ...     y=["Art and Performance", "Business", "Biology", "Education", "Computer Science"],
    ...     value_label="% of Degrees Earned by Women",
    ...     legend="top",
    ...     height=500,
    ...     width=620,
    ... )
    >>> line * scatter

    Please note that you can pass widgets or reactive functions as arguments instead of
    literal values, c.f. https://hvplot.holoviz.org/user_guide/Widgets.html.
    """

    __all__ = [
        "line",
        "step",
        "scatter",
        "area",
        "errorbars",
        "ohlc",
        "heatmap",
        "hexbin",
        "bivariate",
        "bar",
        "barh",
        "box",
        "violin",
        "hist",
        "kde",
        "density",
        "table",
        "dataset",
        "points",
        "vectorfield",
        "polygons",
        "paths",
        "labels",
    ]

    def line(self, x=None, y=None, **kwds):
        """
        The `line` plot connects the points with a continous curve.

        A `line` plot is useful when data is continuous and has a continuous axis.

        Reference: https://hvplot.holoviz.org/reference/pandas/line.html

        Parameters
        ----------
        x : string, optional
            Field name(s) to draw x-positions from. If not specified, the index is
            used.
        y : string or list, optional
            Field name(s) to draw y-positions from. If not specified, all numerical
            fields are used.
        by : string, optional
            A single column or list of columns to group by. All the subgroups are visualized.
        groupby: string, list, optional
            A single field or list of fields to group and filter by. Adds one or more widgets to
            select the subgroup(s) to visualize.
        color : str or array-like, optional.
            The color for each of the series. Possible values are:

            A single color string referred to by name, RGB or RGBA code, for instance 'red' or
            '#a98d19.

            A sequence of color strings referred to by name, RGB or RGBA code, which will be used
            for each series recursively. For instance ['green','yellow'] each field’s line will be
            filled in green or yellow, alternatively. If there is only a single series to be
            plotted, then only the first color from the color list will be used.
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('line')`.

        Returns
        -------
        A Holoviews object. You can `print` the object to study its composition and run

        >>> import holoviews as hv
        >>> hv.help(the_holoviews_object)

        to learn more about its parameters and options.

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

        Please note that you can pass widgets or reactive functions as arguments instead of
        literal values, c.f. https://hvplot.holoviz.org/user_guide/Widgets.html.

        References
        ----------

        - Bokeh: https://docs.bokeh.org/en/latest/docs/reference/models/glyphs/line.html
        - HoloViews: https://holoviews.org/reference/elements/bokeh/Curve.html
        - Pandas: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.line.html
        - Plotly: https://plotly.com/python/line-charts/
        - Matplotlib: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html
        - Wiki: https://en.wikipedia.org/wiki/Line_chart
        """
        return self(x, y, kind="line", **kwds)

    def step(self, x=None, y=None, where="mid", **kwds):
        """
        The `step` plot connects the points with piece-wise constant curves.

        The `step` plot can be used pretty much anytime the `line` plot might be used, and has many
        of the same options available.

        Reference: https://hvplot.holoviz.org/reference/pandas/step.html

        Parameters
        ----------
        x : string, optional
            Field name(s) to draw x-positions from. If not specified, the index is
            used.
        y : string or list, optional
            Field name(s) to draw y-positions from. If not specified, all numerical
            fields are used.
        by : string, optional
            A single field or list of fields to group by. All the subgroups are visualized.
        groupby: string, list, optional
            A single field or list of fields to group and filter by. Adds one or more widgets to
            select the subgroup(s) to visualize.
        where: string, optional
            The interpolation method. One of 'mid', 'pre', 'post'. Default is 'mid'.
        color : str or array-like, optional.
            The color for each of the series. Possible values are:

            A single color string referred to by name, RGB or RGBA code, for instance 'red' or
            '#a98d19.

            A sequence of color strings referred to by name, RGB or RGBA code, which will be used
            for each series recursively. For instance ['green','yellow'] each field’s line will be
            filled in green or yellow, alternatively. If there is only a single series to be
            plotted, then only the first color from the color list will be used.
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('step')`.

        Returns
        -------
        A Holoviews object. You can `print` the object to study its composition and run

        >>> import holoviews as hv
        >>> hv.help(the_holoviews_object)

        to learn more about its parameters and options.

        Examples
        --------

        >>> import hvplot.pandas
        >>> from bokeh.sampledata.degrees import data as deg
        >>> plot = deg.hvplot.step(
        ...     x='Year',
        ...     y=['Art and Performance', 'Business', 'Biology', 'Education', 'Computer Science'],
        ...     value_label='% of Degrees Earned by Women', legend='top', height=500, width=1000
        ... )
        >>> plot

        You can can add *markers* to a `step` plot by overlaying with a `scatter` plot.

        >>> markers = deg.hvplot.scatter(
        ...     x='Year',
        ...     y=['Art and Performance', 'Business', 'Biology', 'Education', 'Computer Science'],
        ...     value_label='% of Degrees Earned by Women', legend='top', height=500, width=1000
        ... )
        >>> plot*markers

        Please note that you can pass widgets or reactive functions as arguments instead of
        literal values, c.f. https://hvplot.holoviz.org/user_guide/Widgets.html.

        References
        ----------

        - Bokeh: https://docs.bokeh.org/en/latest/docs/reference/models/glyphs/step.html
        - HoloViews: https://holoviews.org/gallery/demos/bokeh/step_chart.html
        - Pandas: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.line.html (use `draw_style='step')
        - Plotly: https://plotly.com/python/line-charts/ (See the Interpolation Section)
        - Matplotlib: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.step.html
        """
        return self(x, y, kind="step", where=where, **kwds)

    def scatter(self, x=None, y=None, **kwds):
        """
        The `scatter` plot visualizes your points as markers in 2D space. You can visualize
        one more dimension by using colors.

        The `scatter` plot is a good first way to plot data with non continuous axes.

        Reference: https://hvplot.holoviz.org/reference/pandas/scatter.html

        Parameters
        ----------
        x : string, optional
            Field name(s) to draw x-positions from. If not specified, the index is
            used.
        y : string or list, optional
            Field name(s) to draw y-positions from. If not specified, all numerical
            fields are used.
        marker : string, optional
            The marker shape specified above can be any supported by matplotlib, e.g. s, d, o etc.
            See https://matplotlib.org/stable/api/markers_api.html.
        c : string, optional
            A color or a Field name to draw the color of the marker from
        s : int, optional, also available as 'size'
            The size of the marker
        by : string, optional
            A single field or list of fields to group by. All the subgroups are visualized.
        groupby: string, list, optional
            A single field or list of fields to group and filter by. Adds one or more widgets to
            select the subgroup(s) to visualize.
        scale: number, optional, abbreviation `s`.
            Scaling factor to apply to point scaling.
        logz : bool
            Whether to apply log scaling to the z-axis. Default is False.
        color : str or array-like, optional.
            The color for each of the series. Possible values are:

            A single color string referred to by name, RGB or RGBA code, for instance 'red' or
            '#a98d19.

            A sequence of color strings referred to by name, RGB or RGBA code, which will be used
            for each series recursively. For instance ['green','yellow'] each field’s line will be
            filled in green or yellow, alternatively. If there is only a single series to be
            plotted, then only the first color from the color list will be used.
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('scatter')`.

        Returns
        -------
        A Holoviews object. You can `print` the object to study its composition and run

        >>> import holoviews as hv
        >>> hv.help(the_holoviews_object)

        to learn more about its parameters and options.

        Example
        -------

        >>> import hvplot.pandas
        >>> from bokeh.sampledata.iris import flowers as df
        >>> df.hvplot.scatter(
        ...     x='sepal_length', y='sepal_width', by='species',
        ...     legend='top', height=400, width=400
        ... )

        The points will be grouped and color coded `by` the categorical values in the 'species'
        column.

        References
        ----------

        - Bokeh: http://docs.bokeh.org/en/latest/docs/user_guide/plotting.html#scatter-markers
        - HoloViews: http://holoviews.org/reference/elements/matplotlib/Scatter.html
        - Pandas: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.scatter.html
        - Plotly: https://plotly.com/python/line-and-scatter/
        - Matplotlib:  https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.scatter.html
        - Wiki: https://en.wikipedia.org/wiki/Scatter_plot
        """
        return self(x, y, kind="scatter", **kwds)

    def area(self, x=None, y=None, y2=None, stacked=True, **kwds):
        """
        The `area` plot can be used to color the area under a line or to color the space between two
        lines.

        Reference: https://hvplot.holoviz.org/reference/pandas/area.html

        Parameters
        ----------
        x : string, optional
            Field name(s) to draw x-positions from. If not specified, the index is
            used.
        y : string, optional
            Field name to draw the first y-position from
        y2 : string, optional
            Field name to draw the second y-position from
        stacked : boolean, optional
            Whether to stack multiple areas. Default is False.
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('area')`.

        Returns
        -------
        A Holoviews object. You can `print` the object to study its composition and run

        >>> import holoviews as hv
        >>> hv.help(the_holoviews_object)

        to learn more about its parameters and options.

        Example
        -------

        >>> import hvplot.pandas
        >>> from bokeh.sampledata.degrees import data
        >>> data.hvplot.area(x='Year', y='Computer Science',
        ...     label='% of Computer Science Degrees Earned by Women',
        ...     ylim=(0, 100), width=500, height=400, color='pink'
        ... )

        References
        ----------

        - Bokeh: http://docs.bokeh.org/en/latest/docs/user_guide/plotting.html#directed-areas
        - HoloViews: http://holoviews.org/reference/elements/matplotlib/Area.html
        - Pandas: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.area.html
        - Plotly: https://plotly.com/python/filled-area-plots/
        - Matplotlib:  https://matplotlib.org/stable/gallery/lines_bars_and_markers/fill_between_demo.html
        - Wiki: https://en.wikipedia.org/wiki/Area_chart
        """
        if "alpha" not in kwds and not stacked:
            kwds["alpha"] = 0.5
        return self(x, y, y2=y2, kind="area", stacked=stacked, **kwds)

    def errorbars(self, x=None, y=None, yerr1=None, yerr2=None, **kwds):
        """
        `errorbars` provide a visual indicator for the variability of the plotted data on a graph.
        They are usually overlayed with other plots such as `scatter` , `line` or `bar` plots to
        indicate the variability.

        Reference: https://hvplot.holoviz.org/reference/pandas/errorbars.html

        Parameters
        ----------
        x : string, optional
            Field name to draw the x-position from. If not specified, the index is
            used.
        y : string, optional
            Field name to draw the y-position from
        yerr1 : string, optional
            Field name to draw symmetric / negative errors from
        yerr2 : string, optional
            Field name to draw positive errors from
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('errorbars')`.

        Returns
        -------
        A Holoviews object. You can `print` the object to study its composition and run

        >>> import holoviews as hv
        >>> hv.help(the_holoviews_object)

        to learn more about its parameters and options.

        Example
        -------

        >>> import pandas as pd
        >>> import hvplot.pandas
        >>> data = pd.DataFrame({
        ...     "y": [1.0, 1.2, 0.8],
        ...     "yerr1": [0.2, .4, 0.1],
        ...     "yerr2": [0.2, .2, 0.2],
        ... })
        >>> errorbars = data.hvplot.errorbars(y="y", yerr1="yerr1", yerr2="yerr2")
        >>> errorbars

        Normally you would overlay the `errorbars` on for example a `scatter` plot.

        >>> scatter = data.hvplot.scatter(y="y", color="green", size=50)
        >>> scatter * errorbars

        References
        ----------

        - Bokeh: https://docs.bokeh.org/en/latest/docs/user_guide/annotations.html#whiskers
        - HoloViews: https://holoviews.org/reference/elements/bokeh/ErrorBars.html
        - Matplotlib: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.errorbar.html
        - Pandas: https://pandas.pydata.org/docs/user_guide/visualization.html#visualization-errorbars
        - Plotly: https://plotly.com/python/error-bars/
        - Wikipedia: https://en.wikipedia.org/wiki/Error_bar
        """
        return self(x, y, kind="errorbars", yerr1=yerr1, yerr2=yerr2, **kwds)

    def ohlc(self, x=None, y=None, **kwds):
        """
        The `ohlc` plot visualizes the open, high, low and close prices of stocks and other assets.

        Reference: https://hvplot.holoviz.org/reference/pandas/ohlc.html

        Parameters
        ----------
        x : string, optional
            Field name to draw x coordinates from. If not specified, the index is used.
        y : list or tuple, optional
            Field names of the OHLC fields. Default is ["open", "high", "low", "close"]
        line_color : string, optional
            The line color. Default is black
        pos_color : string, optional
            The color indicating a positive change. Default is green.
        neg_color : string, optional
            The color indicating a negative change. Default is red.
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('ohlc')`.

        Returns
        -------
        A Holoviews object. You can `print` the object to study its composition and run

        >>> import holoviews as hv
        >>> hv.help(the_holoviews_object)

        to learn more about its parameters and options.

        Example
        -------
        >>> import hvplot.pandas
        >>> import pandas as pd
        >>> data = pd.DataFrame({
        ...     "open": [100, 101, 102],
        ...     "high": [101, 103, 104],
        ...     "low": [99, 100, 100],
        ...     "close": [101, 99, 103],
        ... }, index=[pd.Timestamp("2022-08-01"), pd.Timestamp("2022-08-02"), pd.Timestamp("2022-08-03")])
        >>> data.hvplot.ohlc()

        References
        ----------

        - Bokeh: https://docs.bokeh.org/en/latest/docs/gallery/candlestick.html
        - Matplotlib: https://www.statology.org/matplotlib-python-candlestick-chart/
        - Plotly: https://plotly.com/python/ohlc-charts/
        - Wikipedia: https://en.wikipedia.org/wiki/Candlestick_chart
        """
        return self(kind="ohlc", x=x, y=y, **kwds)

    def heatmap(self, x=None, y=None, C=None, colorbar=True, **kwds):
        """
        `heatmap` visualises tabular data indexed by two key dimensions as a grid of colored values.
        This allows spotting correlations in multivariate data and provides a high-level overview
        of how the two variables are plotted.

        Reference: https://hvplot.holoviz.org/reference/pandas/heatmap.html

        Parameters
        ----------
        x : string, optional
            Field name to draw x coordinates from. If not specified, the index is used.
        y : string
            Field name to draw y-positions from
        C : string, optional
            Field to draw heatmap color from. If not specified a simple count will be used.
        colorbar: boolean, optional
            Whether to display a colorbar. Default is True.
        logz : bool
            Whether to apply log scaling to the z-axis. Default is False.
        reduce_function : function, optional
            Function to compute statistics for heatmap, for example `np.mean`.
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('heatmap')`.

        Returns
        -------
        A Holoviews object. You can `print` the object to study its composition and run

        >>> import holoviews as hv
        >>> hv.help(the_holoviews_object)

        to learn more about its parameters and options.

        Example
        -------

        >>> import numpy as np
        >>> from bokeh.sampledata import sea_surface_temperature as sst

        >>> import hvplot.pandas

        >>> df = sst.sea_surface_temperature
        >>> df.hvplot.heatmap(
        ...     x="time.month", y="time.day", C="temperature", reduce_function=np.mean,
        ...     height=500, width=500, colorbar=False,
        >>> )

        References
        ----------

        - Bokeh: http://docs.bokeh.org/en/latest/docs/gallery/categorical_heatmap.html
        - HoloViews: https://holoviews.org/reference/elements/bokeh/HeatMap.html
        - Matplotlib: https://matplotlib.org/stable/gallery/images_contours_and_fields/image_annotated_heatmap.html
        - Plotly: https://plotly.com/python/heatmaps/
        - Wiki: https://en.wikipedia.org/wiki/Heat_map
        """
        return self(x, y, kind="heatmap", C=C, colorbar=colorbar, **kwds)

    def hexbin(self, x=None, y=None, C=None, colorbar=True, **kwds):
        """
        The `hexbin` plot uses hexagons to split the area into several parts and attribute a color
        to it.

        `hexbin` offers a straightforward method for plotting dense data.

        Reference: https://hvplot.holoviz.org/reference/pandas/hexbin.html

        Parameters
        ----------
        x : string, optional
            Field name to draw x coordinates from. If not specified, the index is used.
        y : string
            Field name to draw y-positions from
        C : string, optional
            Field to draw hexbin color from. If not specified a simple count will be used.
        colorbar: boolean, optional
            Whether to display a colorbar. Default is True.
        reduce_function : function, optional
            Function to compute statistics for hexbins, for example `np.mean`.
        gridsize: int, optional
            The number of hexagons in the x-direction
        logz : bool
            Whether to apply log scaling to the z-axis. Default is False.
        min_count : number, optional
            The display threshold before a bin is shown, by default bins with
            a count of less than 1 are hidden
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('hexbin')`.

        Returns
        -------
        A Holoviews object. You can `print` the object to study its composition and run

        >>> import holoviews as hv
        >>> hv.help(the_holoviews_object)

        to learn more about its parameters and options.

        Example
        -------

        >>> import hvplot.pandas
        >>> import pandas as pd
        >>> import numpy as np

        >>> n = 500
        >>> df = pd.DataFrame({
        ...     "x": 2 + 2 * np.random.standard_normal(n),
        ...     "y": 2 + 2 * np.random.standard_normal(n),
        ... })
        >>> df.hvplot.hexbin("x", "y", clabel="Count", height=400, width=500)

        References
        ----------

        - Bokeh: https://docs.bokeh.org/en/latest/docs/gallery/hexbin.html
        - HoloViews: https://holoviews.org/reference/elements/bokeh/HexTiles.html
        - Plotly: https://plotly.com/python/hexbin-mapbox/
        - Wiki: https://think.design/services/data-visualization-data-design/hexbin/
        """
        return self(x, y, kind="hexbin", C=C, colorbar=colorbar, **kwds)

    def bivariate(self, x=None, y=None, colorbar=True, **kwds):
        """
        A bivariate, density plot uses nested contours (or contours plus colors) to indicate
        regions of higher local density.

        `bivariate` plots can be a useful alternative to scatter plots, if your data are too dense
        to plot each point individually.

        Reference: https://hvplot.holoviz.org/reference/pandas/bivariate.html

        Parameters
        ----------
        x : string, optional
            Field name to draw x-positions from. If not specified, the index is used.
        y : string, optional
            Field name to draw y-positions from
        colorbar: boolean
            Whether to display a colorbar
        bandwidth: int, optional
            The bandwidth of the kernel for the density estimate. Default is None.
        cut: Integer, Optional
            Draw the estimate to cut * bw from the extreme data points. Default is None.
        filled : bool, optional
            If True the the contours will be filled. Default is False.
        levels: int, optional
            The number of contour lines to draw. Default is 10.

        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('bivariate')`.

        Returns
        -------
        A Holoviews object. You can `print` the object to study its composition and run

        >>> import holoviews as hv
        >>> hv.help(the_holoviews_object)

        to learn more about its parameters and options.

        Examples
        --------

        >>> import hvplot.pandas
        >>> from bokeh.sampledata.autompg import autompg_clean as df

        >>> bivariate = df.hvplot.bivariate("accel", "mpg")
        >>> bivariate

        To get a better intuitive understanding of the `bivariate` plot, you can try overlaying the
        corresponding scatter plot.

        >>> scatter = df.hvplot.scatter("accel", "mpg")
        >>> bivariate * scatter

        References
        ----------

        - ggplot: https://bio304-class.github.io/bio304-fall2017/ggplot-bivariate.html
        - HoloViews: https://holoviews.org/reference/elements/bokeh/Bivariate.html
        - Plotly: https://plotly.com/python/2d-histogram-contour/
        - Matplotlib: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.contour.html
        - Wiki: https://en.wikipedia.org/wiki/Bivariate_analysis
        """
        return self(x, y, kind="bivariate", colorbar=colorbar, **kwds)

    def bar(self, x=None, y=None, **kwds):
        """
        A vertical bar plot

        A `bar` plot represents categorical data with rectangular bars
        with heights proportional to the values that they represent. The x-axis
        plots categories and the y axis represents the value scale.
        The bars are of equal width which allows for instant comparison of data.

        `bar` can be used on dataframes with regular Index or MultiIndex.

        Reference: https://hvplot.holoviz.org/reference/pandas/bar.html

        Parameters
        ----------
        x : string, optional
            Field name to draw x-positions from. If not specified, the index is used.
        y : string, optional
            Field name to draw y-positions from. If not specified, all numerical
            fields are used.
        stacked : bool, optional
            If True, creates a stacked bar plot. Default is False.
        color : str or array-like, optional.
            The color for each of the series. Possible values are:

            A single color string referred to by name, RGB or RGBA code, for instance 'red' or
            '#a98d19.

            A sequence of color strings referred to by name, RGB or RGBA code, which will be used
            for each series recursively. For instance ['green','yellow'] each field’s line will be
            filled in green or yellow, alternatively. If there is only a single series to be
            plotted, then only the first color from the color list will be used.
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('bar')`.

        Returns
        -------
        A Holoviews object. You can `print` the object to study its composition and run

        >>> import holoviews as hv
        >>> hv.help(the_holoviews_object)

        to learn more about its parameters and options.

        Example
        -------

        >>> import hvplot.pandas
        >>> import pandas as pd

        >>> df = pd.DataFrame({
        ...     'speed': [0.1, 17.5, 40, 48, 52, 69, 88],
        ...     'lifespan': [2, 8, 70, 1.5, 25, 12, 28],
        ...     },
        ...     index= ['snail', 'pig', 'elephant', 'rabbit', 'giraffe', 'coyote', 'horse']
        ... )
        >>> df.hvplot.bar(rot=90, color=["#457278", "#615078"])

        You can stack the bars by setting `stacked=True`

        >>> df.hvplot.bar(stacked=True, rot=90, color=["#457278", "#615078"])

        References
        ----------

        - Bokeh: https://docs.bokeh.org/en/latest/docs/reference/models/glyphs/vbar.html
        - HoloViews: https://holoviews.org/reference/elements/bokeh/Bars.html
        - Matplotlib: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.bar.html
        - Pandas: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.bar.html
        - Plotly: https://plotly.com/python/bar-charts/
        - Wiki: https://en.wikipedia.org/wiki/Bar_chart
        """
        return self(x, y, kind="bar", **kwds)

    def barh(self, x=None, y=None, **kwds):
        """
        A horizontal bar plot

        A `barh` plot represents categorical data with rectangular bars
        with heights proportional to the values that they represent. The y-axis of the chart
        plots categories and the x-axis represents the value scale.
        The bars are of equal width which allows for instant comparison of data.

        `barh` can be used on dataframes with regular Index or MultiIndex.

        Reference: https://hvplot.holoviz.org/reference/pandas/barh.html

        Parameters
        ----------
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('image')`.

        Returns
        -------
        A Holoviews object. You can `print` the object to study its composition and run

        >>> import holoviews as hv
        >>> hv.help(the_holoviews_object)

        to learn more about its parameters and options.

        Examples
        --------

        >>> import hvplot.pandas
        >>> import pandas as pd

        >>> df = pd.DataFrame(
        ...     {
        ...         "speed": [0.1, 17.5, 40, 48, 52, 69, 88],
        ...         "lifespan": [2, 8, 70, 1.5, 25, 12, 28],
        ...     },
        ...     index=["snail", "pig", "elephant", "rabbit", "giraffe", "coyote", "horse"],
        ... )
        >>> df.hvplot.barh(color=["#457278", "#615078"])

        You can stack the bars by setting `stacked=True`

        >>> df.hvplot.barh(stacked=True, color=["#457278", "#615078"])

        References
        ----------

        - Bokeh: https://docs.bokeh.org/en/latest/docs/reference/models/glyphs/hbar.html
        - HoloViews: https://holoviews.org/reference/elements/bokeh/Bars.html
        - Matplotlib: https://matplotlib.org/stable/gallery/lines_bars_and_markers/barh.html
        - Pandas: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.barh.html
        - Plotly: https://plotly.com/python/horizontal-bar-charts/
        - Wiki: https://en.wikipedia.org/wiki/Bar_chart
        """
        return self(x, y, kind="barh", **kwds)

    def box(self, y=None, by=None, **kwds):
        """
        The `box` plot gives you a visual idea about 5 components in a dataset. It is also
        known as *box and whiskers plot*. It is useful for describing measures of
        central tendencies and measures of dispersion in a dataset.

        `box` plots are most useful when grouped by additional dimensions.

        Reference: https://hvplot.holoviz.org/reference/pandas/box.html

        Parameters
        ----------
        y : string or sequence
            Field in the data to compute distribution from.
        by : string or sequence
            Field in the data to group by.
        kwds : optional
            Additional keywords arguments are documented in `hvplot.help('box')`.

        Returns
        -------
        A Holoviews object. You can `print` the object to study its composition and run

        >>> import holoviews as hv
        >>> hv.help(the_holoviews_object)

        to learn more about its parameters and options.

        References
        ----------

        - Wiki: https://en.wikipedia.org/wiki/Box_plot
        """
        return self(kind="box", x=None, y=y, by=by, **dict(kwds, hover=False))

    def violin(self, y=None, by=None, **kwds):
        """
        Violin plot

        Reference: https://hvplot.holoviz.org/reference/pandas/violin.html

        Parameters
        ----------
        y : string or sequence
            Field in the data to compute distribution on.
        by : string or sequence
            Field in the data to group by.
        kwds : optional
            Additional keywords arguments are documented in `hvplot.help('violin')`.

        Returns
        -------
        A Holoviews object. You can `print` the object to study its composition and run

        >>> import holoviews as hv
        >>> hv.help(the_holoviews_object)

        to learn more about its parameters and options.

        References
        ----------

        - Wiki: https://en.wikipedia.org/wiki/Box_plot
        """
        return self(kind="violin", x=None, y=y, by=by, **dict(kwds, hover=False))

    def hist(self, y=None, by=None, **kwds):
        """
        Histogram

        Reference: https://hvplot.holoviz.org/reference/pandas/hist.html

        Parameters
        ----------
        y : string or sequence
            Field in the data to compute distribution on.
        by : string or sequence
            Field in the data to group by.
        kwds : optional
            Additional keywords arguments are documented in `hvplot.help('hist')`.

        Returns
        -------
        A Holoviews object. You can `print` the object to study its composition and run

        >>> import holoviews as hv
        >>> hv.help(the_holoviews_object)

        to learn more about its parameters and options.
        """
        return self(kind="hist", x=None, y=y, by=by, **kwds)

    def kde(self, y=None, by=None, **kwds):
        """
        KDE plot

        Reference: https://hvplot.holoviz.org/reference/pandas/kde.html

        Parameters
        ----------
        y : string or sequence
            Field in the data to compute distribution on.
        by : string or sequence
            Field in the data to group by.
        kwds : optional
            Additional keywords arguments are documented in `hvplot.help('kde')`.

        Returns
        -------
        A Holoviews object. You can `print` the object to study its composition and run

        >>> import holoviews as hv
        >>> hv.help(the_holoviews_object)

        to learn more about its parameters and options.
        """
        return self(kind="kde", x=None, y=y, by=by, **kwds)

    def density(self, y=None, by=None, **kwds):
        """
        Density plot. Same as `kde` plot

        Reference: https://hvplot.holoviz.org/reference/pandas/kde.html

        Parameters
        ----------
        y : string or sequence
            Field in the data to compute distribution on.
        by : string or sequence
            Field in the data to group by.
        kwds : optional
            Additional keywords arguments are documented in `hvplot.help('kde')`.

        Returns
        -------
        A Holoviews object. You can `print` the object to study its composition and run

        >>> import holoviews as hv
        >>> hv.help(the_holoviews_object)

        to learn more about its parameters and options.
        """
        return self(kind="kde", x=None, y=y, by=by, **kwds)

    def table(self, columns=None, **kwds):
        """
        Table

        Reference: https://hvplot.holoviz.org/reference/pandas/table.html

        Parameters
        ----------
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('table')`.

        Returns
        -------
        A Holoviews object. You can `print` the object to study its composition and run

        >>> import holoviews as hv
        >>> hv.help(the_holoviews_object)

        to learn more about its parameters and options.
        """
        return self(kind="table", **dict(kwds, columns=columns))

    def dataset(self, columns=None, **kwds):
        """
        Dataset

        Todo: Describe the reason for exposing this.

        Reference: Todo. Find link

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
        return self(kind="dataset", **dict(kwds, columns=columns))

    def points(self, x=None, y=None, **kwds):
        """
        Point plot use for 2D coordinate systems

        Reference: https://hvplot.holoviz.org/reference/geopandas/points.html

        Parameters
        ----------
        x, y : string, optional
            The coordinate variable along the x- and y-axis
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('points')`.

        Returns
        -------
        A Holoviews object. You can `print` the object to study its composition and run

        >>> import holoviews as hv
        >>> hv.help(the_holoviews_object)

        to learn more about its parameters and options.
        """
        return self(x, y, kind="points", **kwds)

    def vectorfield(self, x=None, y=None, angle=None, mag=None, **kwds):
        """
        Vectorfield plot

        Reference: https://hvplot.holoviz.org/reference/xarray/vectorfield.html

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
        A Holoviews object. You can `print` the object to study its composition and run

        >>> import holoviews as hv
        >>> hv.help(the_holoviews_object)

        to learn more about its parameters and options.
        """
        return self(x, y, angle=angle, mag=mag, kind="vectorfield", **kwds)

    def polygons(self, x=None, y=None, c=None, **kwds):
        """
        Polygon plot for geopandas dataframes

        Reference: https://hvplot.holoviz.org/reference/geopandas/polygons.html

        Parameters
        ----------
        c: string, optional
            The dimension to color the polygons by
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('polygons')`.

        Returns
        -------
        A Holoviews object. You can `print` the object to study its composition and run

        >>> import holoviews as hv
        >>> hv.help(the_holoviews_object)

        to learn more about its parameters and options.
        """
        return self(x, y, c=c, kind="polygons", **kwds)

    def paths(self, x=None, y=None, c=None, **kwds):
        """
        LineString and LineRing plot for geopandas dataframes.

        Reference: https://github.com/holoviz/hvplot/issues/828

        Parameters
        ----------
        **kwds : optional
            Additional keywords arguments are documented in `hvplot.help('paths')`.

        Returns
        -------
        A Holoviews object. You can `print` the object to study its composition and run

        >>> import holoviews as hv
        >>> hv.help(the_holoviews_object)

        to learn more about its parameters and options.
        """
        return self(x, y, c=c, kind="paths", **kwds)

    def labels(self, x=None, y=None, text=None, **kwds):
        """
        Labels plot.

        Reference: https://hvplot.holoviz.org/reference/pandas/labels.html

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
        A Holoviews object. You can `print` the object to study its composition and run

        >>> import holoviews as hv
        >>> hv.help(the_holoviews_object)

        to learn more about its parameters and options.
        """
        return self(x, y, text=text, kind="labels", **kwds)


class hvPlot(hvPlotTabular):
    """
    The plotting method: `df.hvplot(...)` creates a plot similarly to the familiar Pandas
    `df.plot` method.

    For more detailed options use a specific ploting method, e.g. `df.hvplot.line`.

    Reference: https://hvplot.holoviz.org/reference/index.html

    Parameters
    ----------
    x : string, optional
        Field name(s) to draw x-positions from. If not specified, the index is
        used.
    y : string or list, optional
        Field name(s) to draw y-positions from. If not specified, all numerical
        fields are used.
    kind : string, optional
        The kind of plot to generate, e.g. 'area', 'bar', 'line', 'scatter' etc. To see the
        available plots run `print(df.hvplot.__all__)`.
    **kwds : optional
        Additional keywords arguments are documented in `hvplot.help('scatter')` or similar
        depending on the kind of plot.

    Returns
    -------
    A Holoviews object. You can `print` the object to study its composition and run `hv.help` on
    the object to learn more about its parameters and options.

    Examples
    --------

    >>> import hvplot.pandas
    >>> from bokeh.sampledata.degrees import data as deg

    >>> line = deg.hvplot(
    ...     x="Year",
    ...     y=["Art and Performance", "Business", "Biology", "Education", "Computer Science"],
    ...     value_label="% of Degrees Earned by Women",
    ...     legend="top",
    ...     height=500,
    ...     width=620,
    ...     kind="line",
    ... )
    >>> line

    You can can add *markers* to a `line` plot by overlaying with a `scatter` plot.

    >>> scatter = deg.hvplot.scatter(
    ...     x="Year",
    ...     y=["Art and Performance", "Business", "Biology", "Education", "Computer Science"],
    ...     value_label="% of Degrees Earned by Women",
    ...     legend="top",
    ...     height=500,
    ...     width=620,
    ... )
    >>> line * scatter

    Please note that you can pass widgets or reactive functions as arguments instead of
    literal values, c.f. https://hvplot.holoviz.org/user_guide/Widgets.html.
    """

    __all__ = [
        "line",
        "step",
        "scatter",
        "area",
        "errorbars",
        "heatmap",
        "hexbin",
        "bivariate",
        "bar",
        "barh",
        "box",
        "violin",
        "hist",
        "kde",
        "density",
        "table",
        "dataset",
        "points",
        "vectorfield",
        "polygons",
        "paths",
        "labels",
        "image",
        "rgb",
        "quadmesh",
        "contour",
        "contourf",
    ]

    def image(self, x=None, y=None, z=None, colorbar=True, **kwds):
        """
        Image plot

        You can very often use `image` to display an x, y grid, like for example geographic
        data with `latitude` and `longitude` coordinates.

        Reference: https://hvplot.holoviz.org/reference/xarray/image.html

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
        A Holoviews object. You can `print` the object to study its composition and run

        >>> import holoviews as hv
        >>> hv.help(the_holoviews_object)

        to learn more about its parameters and options.

        Example
        -------

        >>> import hvplot.xarray
        >>> import xarray as xr
        >>> ds = xr.tutorial.open_dataset('air_temperature')
        >>> ds.hvplot.image(x='lon', y='lat', z='air', groupby='time', cmap='kbc_r')
        """
        return self(x, y, z=z, kind="image", colorbar=colorbar, **kwds)

    def rgb(self, x=None, y=None, z=None, bands=None, **kwds):
        """
        RGB plot

        Reference: https://hvplot.holoviz.org/reference/xarray/rgb.html

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
        A Holoviews object. You can `print` the object to study its composition and run

        >>> import holoviews as hv
        >>> hv.help(the_holoviews_object)

        to learn more about its parameters and options.
        """
        if bands is not None:
            kwds["bands"] = bands
        return self(x, y, z=z, kind="rgb", **kwds)

    def quadmesh(self, x=None, y=None, z=None, colorbar=True, **kwds):
        """
        QuadMesh plot

        Reference: https://hvplot.holoviz.org/reference/xarray/quadmesh.html

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
        A Holoviews object. You can `print` the object to study its composition and run

        >>> import holoviews as hv
        >>> hv.help(the_holoviews_object)

        to learn more about its parameters and options.
        """
        return self(x, y, z=z, kind="quadmesh", colorbar=colorbar, **kwds)

    def contour(self, x=None, y=None, z=None, colorbar=True, **kwds):
        """
        Line contour plot

        Reference: https://hvplot.holoviz.org/reference/xarray/contour.html

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
        A Holoviews object. You can `print` the object to study its composition and run

        >>> import holoviews as hv
        >>> hv.help(the_holoviews_object)

        to learn more about its parameters and options.
        """
        return self(x, y, z=z, kind="contour", colorbar=colorbar, **kwds)

    def contourf(self, x=None, y=None, z=None, colorbar=True, **kwds):
        """
        Filled contour plot

        Reference. https://hvplot.holoviz.org/reference/xarray/contourf.html

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
        A Holoviews object. You can `print` the object to study its composition and run

        >>> import holoviews as hv
        >>> hv.help(the_holoviews_object)

        to learn more about its parameters and options.
        """
        return self(x, y, z=z, kind="contourf", colorbar=colorbar, **kwds)
