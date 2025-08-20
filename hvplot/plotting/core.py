import itertools
from collections import defaultdict

import param

try:
    import panel as pn

    panel_available = True
except ImportError:
    panel_available = False

from ..converter import HoloViewsConverter
from ..util import is_list_like, process_dynamic_args

# Color palette for examples: https://www.color-hex.com/color-palette/1018056
# light green: #55a194
# Dark green: #3b7067
# Blue: #1e85f7
# Orange: #f8b014
# Red: #f16a6f


class hvPlotBase:
    """
    Internal base class.

    Concrete subclasses must implement plotting methods (e.g. `line`, `scatter`, `image`).
    A plotting method must call `self` which will effectively create a HoloViewsConverter
    and call it to return a HoloViews object.

    Concrete subclasses are meant to be mounted onto a datastructure property, e.g.:

    ```
    _patch_plot = lambda self: hvPlotTabular(self)
    _patch_plot.__doc__ = hvPlotTabular.__call__.__doc__
    plot_prop = property(_patch_plot)
    setattr(pd.DataFrame, 'hvplot', plot_prop)
    ```
    """

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
        # Convert an array-like to a list
        x = list(x) if is_list_like(x) else x
        y = list(y) if is_list_like(y) else y

        if isinstance(kind, str) and kind not in self.__all__:
            raise NotImplementedError(f"kind='{kind}' for data of type {type(self._data)}")

        if isinstance(kind, str) and kind == 'explorer':
            return self.explorer(x=x, y=y, **kwds)

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
        plots = object.__getattribute__(self, '_plots')
        if name in plots:
            plot_opts = plots[name]
            if 'kind' in plot_opts and name in HoloViewsConverter._kind_mapping:
                param.main.param.warning(
                    'Custom options for existing plot types should not '
                    "declare the 'kind' argument. The .{} plot method "
                    'was unexpectedly customized with kind={!r}.'.format(plot_opts['kind'], name)
                )
                plot_opts['kind'] = name
            return hvPlotBase(self._data, **dict(self._metadata, **plot_opts))
        return super().__getattribute__(name)

    def explorer(self, x=None, y=None, **kwds):
        """
        The `explorer` plot allows you to interactively explore your data.

        Reference: https://hvplot.holoviz.org/user_guide/Explorer.html

        Parameters
        ----------
        x : string, optional
            The coordinate variable along the x-axis
        y : string, optional
            The coordinate variable along the y-axis
        **kwds : optional
            Additional keywords arguments typically passed to hvplot's call.

        Returns
        -------
        The corresponding explorer type based on data, e.g. hvplot.ui.hvDataFrameExplorer.
        """
        from ..ui import explorer as ui_explorer

        return ui_explorer(self._data, x=x, y=y, **kwds)


class hvPlotTabular(hvPlotBase):
    """
    The plotting method: `df.hvplot(...)` creates a plot similarly to the familiar Pandas
    `df.plot` method.

    For more detailed options use a specific plotting method, e.g. `df.hvplot.line`.

    Reference: https://hvplot.holoviz.org/ref/api/index.html

    Plotting options: https://hvplot.holoviz.org/ref/plotting_options/index.html

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
        Additional keywords arguments are documented in :ref:`plot-options`.


    Returns
    -------
    A Holoviews object. You can `print` the object to study its composition and run

    .. code-block::

        import holoviews as hv
        hv.help(the_holoviews_object)

    to learn more about its parameters and options.

    Examples
    --------

    .. code-block::

        import pandas as pd
        import hvplot.pandas

        df = pd.DataFrame(
            {
                "actual": [100, 150, 125, 140, 145, 135, 123],
                "forecast": [90, 160, 125, 150, 141, 141, 120],
                "numerical": [1.1, 1.9, 3.2, 3.8, 4.3, 5.0, 5.5],
                "date": pd.date_range("2022-01-03", "2022-01-09"),
                "string": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            },
        )
        line = df.hvplot.line(
            x="numerical",
            y=["actual", "forecast"],
            ylabel="value",
            legend="bottom",
            height=500,
            color=["steelblue", "teal"],
            alpha=0.7,
            line_width=5,
        )
        line

    You can can add *markers* to a `line` plot by overlaying with a `scatter` plot.

    .. code-block::

        markers = df.hvplot.scatter(
            x="numerical", y=["actual", "forecast"], color=["#f16a6f", "#1e85f7"], size=50
        )
        line * markers

    Please note that you can pass widgets or reactive functions as arguments instead of
    literal values, c.f. https://hvplot.holoviz.org/user_guide/Widgets.html.
    """

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
        'labels',
        'explorer',
    ]

    def line(self, x=None, y=None, **kwds):
        """
        The `line` plot connects the points with a continuous curve.

        Reference: https://hvplot.holoviz.org/ref/api/manual/hvplot.hvPlot.line.html

        Plotting options: https://hvplot.holoviz.org/ref/plotting_options/index.html

        Parameters
        ----------
        x : string, optional
            Field name(s) to draw x-positions from. If not specified, the index is
            used. Can refer to continuous and categorical data.
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
            Additional keywords arguments are documented in :ref:`plot-options`.
            Run ``hvplot.help('line')`` for the full method documentation.

        Returns
        -------
        :class:`holoviews:holoviews.element.Curve` / Panel object
            You can `print` the object to study its composition and run:

            .. code-block::

                import holoviews as hv
                hv.help(the_holoviews_object)

            to learn more about its parameters and options.

        References
        ----------

        - Bokeh: https://docs.bokeh.org/en/latest/docs/reference/models/glyphs/line.html
        - HoloViews: https://holoviews.org/reference/elements/bokeh/Curve.html
        - Pandas: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.line.html
        - Plotly: https://plotly.com/python/line-charts/
        - Matplotlib: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html
        - Seaborn: https://seaborn.pydata.org/generated/seaborn.lineplot.html
        - Wiki: https://en.wikipedia.org/wiki/Line_chart
        """
        return self(x, y, kind='line', **kwds)

    def step(self, x=None, y=None, where='mid', **kwds):
        """
        The `step` plot connects the points with piece-wise constant curves.

        The `step` plot can be used pretty much anytime the `line` plot might be used, and has many
        of the same options available.

        Reference: https://hvplot.holoviz.org/ref/api/manual/hvplot.hvPlot.step.html

        Plotting options: https://hvplot.holoviz.org/ref/plotting_options/index.html

        Parameters
        ----------
        x : string, optional
            Field name(s) to draw x-positions from. If not specified, the index is
            used. Must refer to continuous data. Not categorical data.
        y : string or list, optional
            Field name(s) to draw y-positions from. If not specified, all numerical
            fields are used.
        by : string, optional
            A single field or list of fields to group by. All the subgroups are visualized.
        groupby: string, list, optional
            A single field or list of fields to group and filter by. Adds one or more widgets to
            select the subgroup(s) to visualize.
        where: string, optional
            Controls the transition point of the step along the x-axis. One of
            ``'mid'``, ``'pre'``, ``'post'``. Default is ``'mid'``.
        color : str or array-like, optional.
            The color for each of the series. Possible values are:

            A single color string referred to by name, RGB or RGBA code, for instance 'red' or
            '#a98d19.

            A sequence of color strings referred to by name, RGB or RGBA code, which will be used
            for each series recursively. For instance ['green','yellow'] each field's line will be
            filled in green or yellow, alternatively. If there is only a single series to be
            plotted, then only the first color from the color list will be used.
        **kwds : optional
            Additional keywords arguments are documented in :ref:`plot-options`.
            Run ``hvplot.help('step')`` for the full method documentation.

        Returns
        -------
        :class:`holoviews:holoviews.element.Curve` / Panel object
            You can `print` the object to study its composition and run:

            .. code-block::

                import holoviews as hv
                hv.help(the_holoviews_object)

            to learn more about its parameters and options.

        References
        ----------

        - Bokeh: https://docs.bokeh.org/en/latest/docs/reference/models/glyphs/step.html
        - HoloViews: https://holoviews.org/gallery/demos/bokeh/step_chart.html
        - Pandas: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.line.html (use `draw_style='step'`)
        - Plotly: https://plotly.com/python/line-charts/ (See the Interpolation Section)
        - Matplotlib: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.step.html
        """
        return self(x, y, kind='step', where=where, **kwds)

    def scatter(self, x=None, y=None, **kwds):
        """
        The `scatter` plot visualizes your points as markers in 2D space. You can visualize
        one more dimension by using colors.

        The `scatter` plot is a good first way to plot data with non continuous axes.

        Reference: https://hvplot.holoviz.org/ref/api/manual/hvplot.hvPlot.scatter.html

        Plotting options: https://hvplot.holoviz.org/ref/plotting_options/index.html

        Parameters
        ----------
        x : string, optional
            Field name(s) to draw x-positions from. If not specified, the index is
            used. Can refer to continuous and categorical data.
        y : string or list, optional
            Field name(s) to draw y-positions from. If not specified, all numerical
            fields are used.
        marker : string, optional
            The marker shape depends on the activated plotting backend:

            - Bokeh: Bokeh marker styles and a subset of Matplotlib styles, e.g.
              ``'circle'`` (default), ``'dot'``, ``'cross'``, ``'x'``, ``'square'``
              for Bokeh markers and ``'+'``, ``'x'``, ``'s'`` for Matplotlib-
              compatible markers.
              See https://docs.bokeh.org/en/latest/docs/examples/basic/scatters/markertypes.html
              for the list of Bokeh markers.
            - Matplotlib: Any supported marker, e.g. ``'s'`` (square), ``'x'``
              (cross), ``'+'``, etc.
              See https://matplotlib.org/stable/api/markers_api.html for the list
              of Matplotlib markers.
        c : string, optional
            A color or a field name to draw the color of the marker from. Alias of
            ``color``.
        s : int, optional, also available as 'size'
            The size of the marker.
        scale: number, optional
            Scaling factor to apply to point scaling. Default is 1.
        logz : bool
            Whether to apply log scaling to the z-axis. Default is False.
        **kwds : optional
            Additional keywords arguments are documented in :ref:`plot-options`.
            Run ``hvplot.help('scatter')`` for the full method documentation.

        Returns
        -------
        :class:`holoviews:holoviews.element.Scatter` / Panel object
            You can `print` the object to study its composition and run:

            .. code-block::

                import holoviews as hv
                hv.help(the_holoviews_object)

            to learn more about its parameters and options.

        References
        ----------

        - Bokeh: https://docs.bokeh.org/en/latest/docs/examples/basic/scatters/color_scatter.html
        - HoloViews: https://holoviews.org/reference/elements/matplotlib/Scatter.html
        - Pandas: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.scatter.html
        - Plotly: https://plotly.com/python/line-and-scatter/
        - Matplotlib:  https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.scatter.html
        - Seaborn: https://seaborn.pydata.org/generated/seaborn.scatterplot.html
        - Wiki: https://en.wikipedia.org/wiki/Scatter_plot
        """
        return self(x, y, kind='scatter', **kwds)

    def area(self, x=None, y=None, y2=None, stacked=True, **kwds):
        """
        The `area` plot can be used to color the area under a line or to color the space between two
        lines.

        Reference: https://hvplot.holoviz.org/ref/api/manual/hvplot.hvPlot.area.html

        Plotting options: https://hvplot.holoviz.org/ref/plotting_options/index.html

        Parameters
        ----------
        x : string, optional
            Field name(s) to draw x-positions from. If not specified, the index is
            used. Can refer to continuous and categorical data.
        y : string, optional
            Field name to draw the first y-position from
        y2 : string, optional
            Field name to draw the second y-position from
        stacked : boolean, optional
            Whether to stack multiple areas. Default is True.
        **kwds : optional
            Additional keywords arguments are documented in :ref:`plot-options`.
            Run ``hvplot.help('area')`` for the full method documentation.

        Returns
        -------
        :class:`holoviews:holoviews.element.Area` / Panel object
            You can `print` the object to study its composition and run:

            .. code-block::

                import holoviews as hv
                hv.help(the_holoviews_object)

            to learn more about its parameters and options.

        References
        ----------

        - Bokeh: https://docs.bokeh.org/en/latest/docs/user_guide/basic/areas.html#directed-areas
        - HoloViews: https://holoviews.org/reference/elements/matplotlib/Area.html
        - Pandas: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.area.html
        - Plotly: https://plotly.com/python/filled-area-plots/
        - Matplotlib:  https://matplotlib.org/stable/gallery/lines_bars_and_markers/fill_between_demo.html
        - Wiki: https://en.wikipedia.org/wiki/Area_chart
        """
        if 'alpha' not in kwds and not stacked:
            kwds['alpha'] = 0.5
        return self(x, y, y2=y2, kind='area', stacked=stacked, **kwds)

    def errorbars(self, x=None, y=None, yerr1=None, yerr2=None, **kwds):
        """
        `errorbars` provide a visual indicator for the variability of the plotted data on a graph.
        They are usually overlaid with other plots such as `scatter` , `line` or `bar` plots to
        indicate the variability.

        Reference: https://hvplot.holoviz.org/ref/api/manual/hvplot.hvPlot.errorbars.html

        Plotting options: https://hvplot.holoviz.org/ref/plotting_options/index.html

        Parameters
        ----------
        x : string, optional
            Field name to draw the x-position from. If not specified, the index is
            used. Can refer to continuous and categorical data.
        y : string, optional
            Field name to draw the y-position from
        yerr1 : string, optional
            Field name to draw symmetric / negative errors from
        yerr2 : string, optional
            Field name to draw positive errors from
        **kwds : optional
            Additional keywords arguments are documented in :ref:`plot-options`.
            Run ``hvplot.help('errorbars')`` for the full method documentation.

        Returns
        -------
        :class:`holoviews:holoviews.element.ErrorBars` / Panel object
            You can `print` the object to study its composition and run:

            .. code-block::

                import holoviews as hv
                hv.help(the_holoviews_object)

            to learn more about its parameters and options.

        References
        ----------

        - Bokeh: https://docs.bokeh.org/en/latest/docs/examples/basic/annotations/whisker.html
        - HoloViews: https://holoviews.org/reference/elements/bokeh/ErrorBars.html
        - Matplotlib: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.errorbar.html
        - Pandas: https://pandas.pydata.org/docs/user_guide/visualization.html#visualization-errorbars
        - Plotly: https://plotly.com/python/error-bars/
        - Wikipedia: https://en.wikipedia.org/wiki/Error_bar
        """
        return self(x, y, kind='errorbars', yerr1=yerr1, yerr2=yerr2, **kwds)

    def ohlc(self, x=None, y=None, **kwds):
        """
        The `ohlc` plot visualizes the open, high, low and close prices of stocks and other assets.

        Reference: https://hvplot.holoviz.org/ref/api/manual/hvplot.hvPlot.ohlc.html

        Plotting options: https://hvplot.holoviz.org/ref/plotting_options/index.html

        Parameters
        ----------
        x : string, optional
            Field name to draw x coordinates from. If not specified, the index is used. Normally
            refers to date values.
        y : list or tuple, optional
            Field names of the OHLC fields. Default is ["open", "high", "low", "close"]
        bar_width: number, optional
            Bar width. Default is 0.5.
        line_color : string, optional
            The line color. Default is black
        pos_color : string, optional
            The color indicating a positive change. Default is green.
        neg_color : string, optional
            The color indicating a negative change. Default is red.
        **kwds : optional
            Additional keywords arguments are documented in :ref:`plot-options`.
            Run ``hvplot.help('ohlc')`` for the full method documentation.

        Returns
        -------
        :class:`holoviews:holoviews.element.Rectangles` / Panel object
            You can `print` the object to study its composition and run:

            .. code-block::

                import holoviews as hv
                hv.help(the_holoviews_object)

            to learn more about its parameters and options.

        References
        ----------

        - Bokeh: https://docs.bokeh.org/en/latest/docs/examples/topics/timeseries/candlestick.html
        - Matplotlib: https://www.statology.org/matplotlib-python-candlestick-chart/
        - Plotly: https://plotly.com/python/ohlc-charts/
        - Wikipedia: https://en.wikipedia.org/wiki/Candlestick_chart
        """
        return self(kind='ohlc', x=x, y=y, **kwds)

    def heatmap(self, x=None, y=None, C=None, colorbar=True, logz=False, **kwds):
        """
        `heatmap` visualises tabular data indexed by two key dimensions as a grid of colored values.
        This allows spotting correlations in multivariate data and provides a high-level overview
        of how the two variables are plotted. The data can either be shaped as a 2-D array
        (in which case no aggregate will be computed) or as a set of two axis variables and one
        aggregation variable (on which an aggregation is computed).

        Reference: https://hvplot.holoviz.org/ref/api/manual/hvplot.hvPlot.heatmap.html

        Plotting options: https://hvplot.holoviz.org/ref/plotting_options/index.html

        Parameters
        ----------
        x : string, optional
            Field name to draw x-positions from. In the data as an array
            case, setting x to None assumes drawing x labels from the column names,
            which can be explicitly declared by setting x to ``'columns'``.
            Can refer to continuous and categorical data.
        y : string, optional
            Field name to draw y-positions from. In the data as an array
            case, setting y to None assumes drawing y labels from the index,
            which can be explicitly declared by setting y to ``'index'`` or
            to the index name. Can refer to continuous and categorical data.
        C : string, optional
            Field to draw heatmap color from. If not specified a simple count will be used.
        colorbar: boolean, optional
            Whether to display a colorbar. Default is True.
        logz : bool
            Whether to apply log scaling to the z-axis. Default is False.
        reduce_function : function, optional
            Function to compute statistics for heatmap, for example ``np.mean``.
            If omitted, no aggregation is applied and duplicate values are dropped.
        **kwds : optional
            Additional keywords arguments are documented in :ref:`plot-options`.
            Run ``hvplot.help('heatmap')`` for the full method documentation.

        Returns
        -------
        :class:`holoviews:holoviews.element.HeatMap` / Panel object
            You can `print` the object to study its composition and run:

            .. code-block::

                import holoviews as hv
                hv.help(the_holoviews_object)

            to learn more about its parameters and options.

        References
        ----------

        - Bokeh: https://docs.bokeh.org/en/latest/docs/examples/topics/categorical/heatmap_unemployment.html
        - HoloViews: https://holoviews.org/reference/elements/bokeh/HeatMap.html
        - Matplotlib: https://matplotlib.org/stable/gallery/images_contours_and_fields/image_annotated_heatmap.html
        - Plotly: https://plotly.com/python/heatmaps/
        - Wiki: https://en.wikipedia.org/wiki/Heat_map
        """
        return self(x, y, kind='heatmap', C=C, colorbar=colorbar, logz=logz, **kwds)

    def hexbin(
        self,
        x=None,
        y=None,
        C=None,
        colorbar=True,
        gridsize=50,
        logz=False,
        min_count=None,
        **kwds,
    ):
        """
        The `hexbin` plot uses hexagons to split the area into several parts and attribute a color
        to it.

        `hexbin` offers a straightforward method for plotting dense data.

        Reference: https://hvplot.holoviz.org/ref/api/manual/hvplot.hvPlot.hexbin.html

        Plotting options: https://hvplot.holoviz.org/ref/plotting_options/index.html

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
            Function to compute statistics for hexbins, for example ``np.mean``.
            Default aggregation is a count of the values in the area.
        gridsize: int or tuple, optional
            Number of hexagonal bins along x- and y-axes. Defaults to uniform
            sampling along both axes when setting and integer but independent
            bin sampling can be specified a tuple of integers corresponding to
            the number of bins along each axis. Default is 50.
        logz : bool
            Whether to apply log scaling to the z-axis. Default is False.
        min_count : number, optional
            The display threshold before a bin is shown, by default bins with
            a count of less than 1 are hidden
        **kwds : optional
            Additional keywords arguments are documented in :ref:`plot-options`.
            Run ``hvplot.help('hexbin')`` for the full method documentation.

        Returns
        -------
        :class:`holoviews:holoviews.element.HexTiles` / Panel object
            You can `print` the object to study its composition and run:

            .. code-block::

                import holoviews as hv
                hv.help(the_holoviews_object)

            to learn more about its parameters and options.

        References
        ----------

        - Bokeh: https://docs.bokeh.org/en/latest/docs/gallery/hexbin.html
        - HoloViews: https://holoviews.org/reference/elements/bokeh/HexTiles.html
        - Plotly: https://plotly.com/python/hexbin-mapbox/
        - Wiki: https://think.design/services/data-visualization-data-design/hexbin/
        """
        return self(
            x,
            y,
            kind='hexbin',
            C=C,
            colorbar=colorbar,
            gridsize=gridsize,
            logz=logz,
            min_count=min_count,
            **kwds,
        )

    def bivariate(
        self, x=None, y=None, colorbar=True, bandwidth=None, cut=3, filled=False, levels=10, **kwds
    ):
        """
        A bivariate plot uses nested contours (or contours combined with color)
        to indicate regions of higher local density.

        Bivariate plots provide a convenient way to visualize a 2D distribution
        of values as a Kernel Density Estimate (KDE) and therefore provide a 2D
        extension to :py:meth:`~.kde`. KDE is a non-parametric way to estimate
        the probability density function of a random variable.

        The KDE works by placing a Gaussian kernel at each sample with the supplied
        bandwidth, which are then summed to produce the density estimate. By default
        the bandwidth is determined using the Scott's method, which usually produces
        good results, but it may be overridden by an explicit value.

        Bivariate plots can be a useful alternative to scatter plots, if the data
        are too dense to plot each point individually.

        Reference: https://hvplot.holoviz.org/ref/api/manual/hvplot.hvPlot.bivariate.html

        Plotting options: https://hvplot.holoviz.org/ref/plotting_options/index.html

        Parameters
        ----------
        x : string, optional
            Field name to draw x-positions from. If not specified, the index is used.
        y : string, optional
            Field name to draw y-positions from
        colorbar : boolean
            Whether to display a colorbar
        bandwidth : float, optional
            Allows supplying explicit bandwidth value of the kernel for the
            density estimate, rather than relying on Scott. Higher value
            yields smoother contours. Default is None.
        cut : float, optional
            Draw the estimate to cut * bw from the extreme data points. Default is 3.
        filled : bool, optional
            If True the contours will be filled. Default is False.
        levels : int or list, optional
            The number of contour lines to draw or a list of scalar values used
            to specify the contour levels. Default is 10.

        **kwds : optional
            Additional keywords arguments are documented in :ref:`plot-options`.
            Run ``hvplot.help('bivariate')`` for the full method documentation.

        Returns
        -------
        :class:`holoviews:holoviews.element.Bivariate` / Panel object
            You can `print` the object to study its composition and run:

            .. code-block::

                import holoviews as hv
                hv.help(the_holoviews_object)

            to learn more about its parameters and options.

        References
        ----------

        - ggplot: https://bio304-class.github.io/bio304-fall2017/ggplot-bivariate.html
        - HoloViews: https://holoviews.org/reference/elements/bokeh/Bivariate.html
        - Plotly: https://plotly.com/python/2d-histogram-contour/
        - Matplotlib: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.contour.html
        - Seaborn: https://seaborn.pydata.org/generated/seaborn.kdeplot.html
        - Wiki: https://en.wikipedia.org/wiki/Kernel_density_estimation

        Notes
        -----
        This function requires `scipy` to be installed.
        """
        return self(
            x,
            y,
            kind='bivariate',
            colorbar=colorbar,
            bandwidth=bandwidth,
            cut=cut,
            filled=filled,
            levels=levels,
            **kwds,
        )

    def bar(self, x=None, y=None, stacked=False, **kwds):
        """
        A vertical bar plot

        A `bar` plot represents categorical data with rectangular bars
        with heights proportional to the values that they represent. The x-axis
        represents the categories and the y axis represents the value scale.
        The bars are of equal width which allows for instant comparison of data.

        Reference: https://hvplot.holoviz.org/ref/api/manual/hvplot.hvPlot.bar.html

        Plotting options: https://hvplot.holoviz.org/ref/plotting_options/index.html

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

            The name of the field to draw the colors from. The field can contain numerical values or strings
            representing colors.

            A single color string referred to by name, RGB or RGBA code, for instance 'red' or
            '#a98d19'.

            A sequence of color strings referred to by name, RGB or RGBA code, which will be used
            for each series recursively. For instance ['red', 'green','blue'].
        **kwds : optional
            Additional keywords arguments are documented in :ref:`plot-options`.
            Run ``hvplot.help('bar')`` for the full method documentation.

        Returns
        -------
        :class:`holoviews:holoviews.element.Bars` / Panel object
            You can `print` the object to study its composition and run:

            .. code-block::

                import holoviews as hv
                hv.help(the_holoviews_object)

            to learn more about its parameters and options.

        References
        ----------

        - Bokeh: https://docs.bokeh.org/en/latest/docs/reference/models/glyphs/vbar.html
        - HoloViews: https://holoviews.org/reference/elements/bokeh/Bars.html
        - Matplotlib: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.bar.html
        - Pandas: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.bar.html
        - Plotly: https://plotly.com/python/bar-charts/
        - Wiki: https://en.wikipedia.org/wiki/Bar_chart
        """
        return self(x, y, kind='bar', stacked=stacked, **kwds)

    def barh(self, x=None, y=None, stacked=False, **kwds):
        """
        A horizontal bar plot

        A `barh` plot represents categorical data with rectangular bars
        with heights proportional to the values that they represent. The y-axis of the chart
        plots categories and the x-axis represents the value scale.
        The bars are of equal width which allows for instant comparison of data.

        `barh` can be used on dataframes with regular Index or MultiIndex.

        Reference: https://hvplot.holoviz.org/ref/api/manual/hvplot.hvPlot.barh.html

        Plotting options: https://hvplot.holoviz.org/ref/plotting_options/index.html

        Parameters
        ----------
        stacked : bool, optional
            If True, creates a stacked horizontal bar plot. Default is False.
        **kwds : optional
            Additional keywords arguments are documented in :ref:`plot-options`.
            Run ``hvplot.help('barh')`` for the full method documentation.

        Returns
        -------
        :class:`holoviews:holoviews.element.Bars` / Panel object
            You can `print` the object to study its composition and run:

            .. code-block::

                import holoviews as hv
                hv.help(the_holoviews_object)

            to learn more about its parameters and options.

        References
        ----------

        - Bokeh: https://docs.bokeh.org/en/latest/docs/reference/models/glyphs/hbar.html
        - HoloViews: https://holoviews.org/reference/elements/bokeh/Bars.html
        - Matplotlib: https://matplotlib.org/stable/gallery/lines_bars_and_markers/barh.html
        - Pandas: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.barh.html
        - Plotly: https://plotly.com/python/horizontal-bar-charts/
        - Wiki: https://en.wikipedia.org/wiki/Bar_chart
        """
        return self(x, y, kind='barh', stacked=stacked, **kwds)

    def box(self, y=None, by=None, **kwds):
        """
        The `box` plot gives you a visual idea about the *locality*, *spread* and *skewness* of
        numerical data through their quartiles. It is also known as *box and whiskers plot*.

        `box` plots are most useful when grouped by additional dimensions.

        Reference: https://hvplot.holoviz.org/ref/api/manual/hvplot.hvPlot.box.html

        Plotting options: https://hvplot.holoviz.org/ref/plotting_options/index.html

        Parameters
        ----------
        y : string or sequence
            Field(s) in the *wide* data to compute distribution from. If none is provided all
            numerical fields will be used.
        by : string or sequence
            Field in the *long* data to group by.
        kwds : optional
            Additional keywords arguments are documented in :ref:`plot-options`.
            Run ``hvplot.help('box')`` for the full method documentation.

        Returns
        -------
        :class:`holoviews:holoviews.element.BoxWhisker` / Panel object
            You can `print` the object to study its composition and run:

            .. code-block::

                import holoviews as hv
                hv.help(the_holoviews_object)

            to learn more about its parameters and options.

        References
        ----------
        - Bokeh: https://docs.bokeh.org/en/latest/docs/examples/topics/stats/boxplot.html
        - HoloViews: https://holoviews.org/reference/elements/bokeh/BoxWhisker.html
        - Matplotlib: https://matplotlib.org/stable/plot_types/stats/boxplot_plot.html#sphx-glr-plot-types-stats-boxplot-plot-py
        - Pandas: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.boxplot.html
        - Plotly: https://plotly.com/python/box-plots/
        - Wiki: https://en.wikipedia.org/wiki/Box_plot
        """
        return self(kind='box', x=None, y=y, by=by, **dict(kwds, hover=False))

    def violin(self, y=None, by=None, **kwds):
        """
        `violin`  plots are similar to `box` plots, but they provide a better sense of the
        distribution of data.

        Note that `violin` plots depend on the `scipy` library.

        Reference: https://hvplot.holoviz.org/ref/api/manual/hvplot.hvPlot.violin.html

        Plotting options: https://hvplot.holoviz.org/ref/plotting_options/index.html

        Parameters
        ----------
        y : string or sequence
            Field(s) in the *wide* data to compute distribution from. If none is provided all
            numerical fields will be used.
        by : string or sequence
            Field in the *long* data to group by.
        kwds : optional
            Additional keywords arguments are documented in :ref:`plot-options`.
            Run ``hvplot.help('violin')`` for the full method documentation.

        Returns
        -------
        :class:`holoviews:holoviews.element.Violin` / Panel object
            You can `print` the object to study its composition and run:

            .. code-block::

                import holoviews as hv
                hv.help(the_holoviews_object)

            to learn more about its parameters and options.

        References
        ----------

        - Seaborn: https://seaborn.pydata.org/generated/seaborn.violinplot.html
        - HoloViews: https://holoviews.org/reference/elements/bokeh/Violin.html
        - Matplotlib: https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.violinplot.html
        - Plotly: https://plotly.com/python/violin/
        - Wiki: https://en.wikipedia.org/wiki/Violin_plot
        """
        return self(kind='violin', x=None, y=y, by=by, **dict(kwds, hover=False))

    def hist(
        self, y=None, by=None, bins=20, bin_range=None, normed=False, cumulative=False, **kwds
    ):
        """
        A `histogram` displays an approximate representation of the distribution of continuous data.

        Reference: https://hvplot.holoviz.org/ref/api/manual/hvplot.hvPlot.hist.html

        Plotting options: https://hvplot.holoviz.org/ref/plotting_options/index.html

        Parameters
        ----------
        y : string or sequence
            Field(s) in the *wide* data to compute the distribution(s) from.
            Please note the fields should contain continuous data. Not categorical.
        by : string or sequence
            Field(s) in the *long* data to group by.
        bins : int or string or np.ndarray or list or tuple, optional
            The number of bins in the histogram, or an explicit set of bin edges
            or a method to find the optimal set of bin edges, e.g. 'auto', 'fd',
            'scott' etc. For more documentation on these approaches see the
            :func:`numpy.histogram_bin_edges` documentation. Default is 20.
        bin_range: tuple, optional
            The lower and upper range of the bins.
            Default is the minimum and maximum values of the continuous data.
        normed : str or bool, optional
            Controls normalization behavior.  If ``True`` or ``'integral'``, then
            ``density=True`` is passed to np.histogram, and the distribution
            is normalized such that the integral is unity.  If ``False``,
            then the frequencies will be raw counts. If ``'height'``, then the
            frequencies are normalized such that the max bin height is unity.
            Default is False.
        cumulative: bool, optional
            If True, then a histogram is computed where each bin gives the counts
            in that bin plus all bins for smaller values. The last bin gives the
            total number of data points. Default is False.
        kwds : optional
            Additional keywords arguments are documented in :ref:`plot-options`.
            Run ``hvplot.help('hist')`` for the full method documentation.

        Returns
        -------
        :class:`holoviews:holoviews.element.Histogram` / Panel object
            You can `print` the object to study its composition and run:

            .. code-block::

                import holoviews as hv
                hv.help(the_holoviews_object)

            to learn more about its parameters and options.

        See Also
        --------
        kde : Kernel Density Estimate plot.
        bivariate : 2D KDE plot.
        contour : Isolines plot for gridded data.

        References
        ----------

        - Bokeh: https://docs.bokeh.org/en/latest/docs/examples/topics/stats/histogram.html
        - HoloViews: https://holoviews.org/reference/elements/bokeh/Histogram.html
        - Pandas: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.plot.hist.html
        - Plotly: https://plotly.com/python/histograms/
        - Matplotlib: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.hist.html
        - Seaborn: https://seaborn.pydata.org/generated/seaborn.histplot.html
        - Wiki: https://en.wikipedia.org/wiki/Histogram
        """
        return self(
            kind='hist',
            x=None,
            y=y,
            by=by,
            bins=bins,
            bin_range=bin_range,
            normed=normed,
            cumulative=cumulative,
            **kwds,
        )

    def kde(self, y=None, by=None, **kwds):
        """
        The Kernel density estimate (`kde`) plot shows the distribution of the data.

        The KDE works by placing a Gaussian kernel at each sample with the supplied
        bandwidth, which are then summed to produce the density estimate. By default
        the bandwidth is determined using the Scott's method, which usually produces
        good results, but it may be overridden by an explicit value.

        ``density`` is an alias of ``kde``.

        Reference: https://hvplot.holoviz.org/ref/api/manual/hvplot.hvPlot.kde.html

        Plotting options: https://hvplot.holoviz.org/ref/plotting_options/index.html

        Parameters
        ----------
        y : string or sequence
            Field(s) in the data to compute distribution on. If not specified all numerical fields
            are used.
        by : string or sequence
            Field(s) in the data to group by.
        bandwidth : float, optional
            Allows supplying explicit bandwidth value of the kernel for the
            density estimate, rather than relying on Scott. Higher value
            yields smoother contours. Default is None.
        cut : float, optional
            Draw the estimate to cut * bw from the extreme data points. Default is 3.
        filled :
            Whether the bivariate contours should be filled. Default is True.
        bw_method : optional
            Not supported.
        ind : optional
            Not supported.
        kwds : optional
            Additional keywords arguments are documented in :ref:`plot-options`.
            Run ``hvplot.help('kde')`` for the full method documentation.

        Returns
        -------
        :class:`holoviews:holoviews.element.Distribution` / Panel object
            You can `print` the object to study its composition and run:

            .. code-block::

                import holoviews as hv
                hv.help(the_holoviews_object)

            to learn more about its parameters and options.

        See Also
        --------
        hist : Histogram plot.
        bivariate : 2D KDE plot.
        contour : Isolines plot for gridded data.

        References
        ----------

        - HoloViews: https://holoviews.org/reference/elements/bokeh/Distribution.html
        - Pandas: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.kde.html
        - Plotly: https://plotly.com/python/distplot/
        - Seaborn: https://seaborn.pydata.org/generated/seaborn.kdeplot.html
        - Wiki: https://en.wikipedia.org/wiki/Kernel_density_estimation

        Notes
        -----
        This function requires ``scipy`` to be installed.
        """

        return self(kind='kde', x=None, y=y, by=by, **kwds)

    def density(self, y=None, by=None, **kwds):
        """
        Alias of :meth:`hvplot.hvPlot.kde`.
        """
        return self(kind='kde', x=None, y=y, by=by, **kwds)

    def table(self, columns=None, **kwds):
        """
        Displays a 'table'.

        Reference: https://hvplot.holoviz.org/ref/api/manual/hvplot.hvPlot.table.html

        Plotting options: https://hvplot.holoviz.org/ref/plotting_options/index.html

        Parameters
        ----------
        columns : string or sequence
            The field(s) to display as columns.
        **kwds : optional
            Additional keywords arguments are documented in :ref:`plot-options`.
            Run ``hvplot.help('table')`` for the full method documentation.

        Returns
        -------
        :class:`holoviews:holoviews.element.Table` / Panel object
            You can `print` the object to study its composition and run:

            .. code-block::

                import holoviews as hv
                hv.help(the_holoviews_object)

            to learn more about its parameters and options.

        References
        ----------

        - HoloViews: https://holoviews.org/reference/elements/bokeh/Table.html
        - Plotly: https://plotly.com/python/table/
        - Matplotlib: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.table.html
        """
        return self(kind='table', **dict(kwds, columns=columns))

    def dataset(self, columns=None, **kwds):
        """
        Wraps the dataset in a :class:`holoviews:holoviews.element.Dataset`
        object, for further processing with HoloViews.

        Parameters
        ----------
        **kwds : optional
            Additional keywords arguments are documented in :ref:`plot-options`.
            Run ``hvplot.help('dataset')`` for the full method documentation.

        Returns
        -------
        :class:`holoviews:holoviews.element.Dataset` / Panel object
            You can `print` the object to study its composition and run:

            .. code-block::

                import holoviews as hv
                hv.help(the_holoviews_object)

            to learn more about its parameters and options.

        References
        ----------

        - HoloViews Tabular: https://holoviews.org/getting_started/Tabular_Datasets.html
        - HoloViews Gridded: https://holoviews.org/getting_started/Gridded_Datasets.html
        """
        return self(kind='dataset', **dict(kwds, columns=columns))

    def points(self, x=None, y=None, **kwds):
        """
        A `points` plot visualizes positions in a 2D space. This is useful for example for
        geographic plots.

        Although the :meth:`hvplot.hvPlot.scatter` plot is superficially
        similar to the ``points`` plot (they can generate plots that look
        identical), the two plot types are semantically quite different.
        The fundamental difference is that ``scatter`` is used to visualize
        data where the y variable is dependent, unlike ``points``.

        This difference means that ``points`` plots can most naturally
        overlay with other plots that express independent variables in
        two-dimensional space, such as raster types like
        :meth:`hvplot.hvPlot.image`. Conversely, ``scatter`` expresses a
        dependent relationship between x and y and thus most naturally
        overlay with chart types such as :meth:`hvplot.hvPlot.line`.

        Reference: https://hvplot.holoviz.org/ref/api/manual/hvplot.hvPlot.points.html

        Plotting options: https://hvplot.holoviz.org/ref/plotting_options/index.html

        Parameters
        ----------
        x : string, optional
            The coordinate variable along the x-axis. Default is the first numeric field.
        y : string, optional
            The coordinate variable along the y-axis. Default is the second numeric field.
        c : string, optional
            The dimension to color the points by
        s : int, optional, also available as 'size'
            The size of the marker
        marker : string, optional
            The marker shape specified above can be any supported by matplotlib, e.g. s, d, o etc.
            See https://matplotlib.org/stable/api/markers_api.html.
        scale: number, optional
            Scaling factor to apply to point scaling. Default is 1.
        logz : bool
            Whether to apply log scaling to the z-axis. Default is False.
        **kwds : optional
            Additional keywords arguments are documented in :ref:`plot-options`.
            Run ``hvplot.help('points')`` for the full method documentation.

        Returns
        -------
        :class:`holoviews:holoviews.element.Points` / Panel object
            You can `print` the object to study its composition and run:

            .. code-block::

                import holoviews as hv
                hv.help(the_holoviews_object)

            to learn more about its parameters and options.

        References
        ----------

        - HoloViews: https://holoviews.org/reference/elements/bokeh/Points.html
        """
        return self(x, y, kind='points', **kwds)

    def vectorfield(self, x=None, y=None, angle=None, mag=None, **kwds):
        """
        vectorfield visualizes vectors given by the (``x``, ``y``) starting point,
        a magnitude (``mag``) and an `angle`. A ``vectorfield`` plot is also known
        as a ``quiver`` plot.

        Reference: https://hvplot.holoviz.org/ref/api/manual/hvplot.hvPlot.vectorfield.html

        Plotting options: https://hvplot.holoviz.org/ref/plotting_options/index.html

        Parameters
        ----------
        x : string
            Field name to draw x-positions from
        y : string
            Field name to draw y-positions from
        mag : string
            Magnitude.
        angle : string
            Angle in radians.
        **kwds : optional
            Additional keywords arguments are documented in :ref:`plot-options`.
            Run ``hvplot.help('vectorfield')`` for the full method documentation.

        Returns
        -------
        :class:`holoviews:holoviews.element.VectorField` / Panel object
            You can `print` the object to study its composition and run:

            .. code-block::

                import holoviews as hv
                hv.help(the_holoviews_object)

            to learn more about its parameters and options.

        References
        ----------

        - HoloViews: https://holoviews.org/reference/elements/bokeh/VectorField.html
        - Matplotlib: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.quiver.html
        - Plotly: https://plotly.com/python/quiver-plots/
        - Wiki: https://simple.wikipedia.org/wiki/Vector_field
        """
        return self(x, y, angle=angle, mag=mag, kind='vectorfield', **kwds)

    def polygons(self, x=None, y=None, c=None, **kwds):
        """
        Polygon plot for geopandas dataframes.

        Reference: https://hvplot.holoviz.org/ref/api/manual/hvplot.hvPlot.polygons.html

        Plotting options: https://hvplot.holoviz.org/ref/plotting_options/index.html

        Parameters
        ----------
        c : string, optional
            The dimension to color the polygons by
        logz : bool
            Enables logarithmic colormapping. Default is False.
        **kwds : optional
            Additional keywords arguments are documented in :ref:`plot-options`.
            Run ``hvplot.help('polygons')`` for the full method documentation.

        Returns
        -------
        :class:`holoviews:holoviews.element.Polygons` / Panel object
            You can `print` the object to study its composition and run:

            .. code-block::

                import holoviews as hv
                hv.help(the_holoviews_object)

            to learn more about its parameters and options.
        """
        return self(x, y, c=c, kind='polygons', **kwds)

    def paths(self, x=None, y=None, c=None, **kwds):
        """
        Plot one or more collection of lines.

        Each path is a collection of independent x and y coordinates,
        represented from:

        - tabular data: 1 path
        - gridded data: 1 path
        - GeoPandas GeoDataFrame: as many paths as LineString/MultiLineString
          as geometries contained in the dtaset

        Options like ``color`` or ``line_width`` are vectorized, i.e. each
        sub-line of a path can be displayed separately based on another dimension.
        For example, each sub-line of a hurricane path can be plotted with
        a color based on the wind speed.

        Parameters
        ----------
        **kwds : optional
            Additional keywords arguments are documented in :ref:`plot-options`.
            Run ``hvplot.help('paths')`` for the full method documentation.

        Returns
        -------
        :class:`holoviews:holoviews.element.Path` / Panel object
            You can `print` the object to study its composition and run:

            .. code-block::

                import holoviews as hv
                hv.help(the_holoviews_object)

            to learn more about its parameters and options.

        References
        ----------

        - HoloViews: https://holoviews.org/reference/elements/bokeh/Path.html
        """
        return self(x, y, c=c, kind='paths', **kwds)

    def labels(self, x=None, y=None, text=None, **kwds):
        """
        Labels plot.

        `labels` are mostly useful when overlaid on top of other plots using the `*`
        operator.

        Reference: https://hvplot.holoviz.org/ref/api/manual/hvplot.hvPlot.labels.html

        Plotting options: https://hvplot.holoviz.org/ref/plotting_options/index.html

        Parameters
        ----------
        x : string, optional
            The coordinate variable along the x-axis
        y : string, optional
            The coordinate variable along the y-axis
        text : string, optional
            The column to draw the text labels from; it's also possible to
            provide a template string containing the column names to
            automatically format the text, e.g. "{col1}, {col2}".
        **kwds : optional
            Additional keywords arguments are documented in :ref:`plot-options`.
            Run ``hvplot.help('labels')`` for the full method documentation.

        Returns
        -------
        :class:`holoviews:holoviews.element.Labels` / Panel object
            You can `print` the object to study its composition and run:

            .. code-block::

                import holoviews as hv
                hv.help(the_holoviews_object)

            to learn more about its parameters and options.

        References
        ----------

        - Bokeh: https://docs.bokeh.org/en/latest/docs/reference/models/glyphs/text.html
        - HoloViews: https://holoviews.org/reference/elements/bokeh/Labels.html
        - Matplotlib: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.text.html#matplotlib.pyplot.text
        - Plotly: https://plotly.com/python/text-and-annotations/
        """
        return self(x, y, text=text, kind='labels', **kwds)


class hvPlotTabularDuckDB(hvPlotTabular):
    def _get_converter(self, x=None, y=None, kind=None, **kwds):
        import duckdb
        from duckdb.typing import (
            BIGINT,
            FLOAT,
            DOUBLE,
            INTEGER,
            SMALLINT,
            TINYINT,
            UBIGINT,
            UINTEGER,
            USMALLINT,
            UTINYINT,
            HUGEINT,
        )

        params = dict(self._metadata, **kwds)
        x = x or params.pop('x', None)
        y = y or params.pop('y', None)
        kind = kind or params.pop('kind', None)

        # Handle DuckDB Relation and Connection objects
        if isinstance(self._data, (duckdb.DuckDBPyConnection, duckdb.DuckDBPyRelation)):
            if isinstance(self._data, duckdb.DuckDBPyConnection):
                data = self._data.df()
            else:
                data = self._data

            if params.get('hover_cols') != 'all':
                data_columns = data.columns
                possible_columns = [
                    [v] if isinstance(v, str) else v
                    for v in params.values()
                    if isinstance(v, (str, list))
                ]

                columns = (set(data_columns) & set(itertools.chain(*possible_columns))) or {
                    data_columns[0]
                }
                if y is None:
                    # When y is not specified HoloViewsConverter finds all the numeric
                    # columns and use them as y values (see _process_chart_y). We need
                    # to include these columns too.

                    if isinstance(data, duckdb.DuckDBPyRelation):
                        numeric_columns = data.select_types(
                            [
                                BIGINT,
                                FLOAT,
                                DOUBLE,
                                INTEGER,
                                SMALLINT,
                                TINYINT,
                                UBIGINT,
                                UINTEGER,
                                USMALLINT,
                                UTINYINT,
                                HUGEINT,
                            ]
                        ).columns
                    else:
                        numeric_columns = data.select_dtypes(include='number').columns
                    columns |= set(numeric_columns)
                xs = x if is_list_like(x) else (x,)
                ys = y if is_list_like(y) else (y,)
                columns |= {*xs, *ys}
                columns.discard(None)

            if isinstance(data, duckdb.DuckDBPyRelation):
                columns = sorted(columns, key=lambda c: data_columns.index(c))
                data = data.select(*columns).to_df()
            else:
                columns = sorted(columns, key=lambda c: data.columns.get_loc(c))
                data = data[list(columns)]
        else:
            raise ValueError(
                'Only duckdb.DuckDBPyConnection and duckdb.DuckDBPyRelation are supported'
            )

        return HoloViewsConverter(data, x, y, kind=kind, **params)


class hvPlotTabularPolars(hvPlotTabular):
    def _get_converter(self, x=None, y=None, kind=None, **kwds):
        import polars as pl

        params = dict(self._metadata, **kwds)
        x = x or params.pop('x', None)
        y = y or params.pop('y', None)
        kind = kind or params.pop('kind', None)

        # Find columns which should be converted for LazyDataFrame and DataFrame
        if isinstance(self._data, (pl.LazyFrame, pl.DataFrame)):
            try:
                column_names = self._data.collect_schema().names()
            except Exception:  # Maybe not always supported, has been there since 1.7.1
                column_names = list(self._data.columns)

            if params.get('hover_cols') == 'all':
                columns = column_names
            else:
                possible_columns = [
                    [v] if isinstance(v, str) else v
                    for v in params.values()
                    if isinstance(v, (str, list))
                ]

                columns = set(column_names) & set(itertools.chain(*possible_columns))
                columns = columns or {column_names[0]}
                if y is None:
                    # When y is not specified HoloViewsConverter finds all the numeric
                    # columns and use them as y values (see _process_chart_y). We need
                    # to include these columns too.
                    columns |= set(self._data.select(pl.col(pl.NUMERIC_DTYPES)).columns)
                xs = x if is_list_like(x) else (x,)
                ys = y if is_list_like(y) else (y,)
                columns |= {*xs, *ys}
                columns.discard(None)
                # Reorder the columns as in the data.
                columns = sorted(columns, key=lambda c: column_names.index(c))

        if isinstance(self._data, pl.DataFrame):
            data = self._data.select(columns).to_pandas()
        elif isinstance(self._data, pl.Series):
            data = self._data.to_pandas()
        elif isinstance(self._data, pl.LazyFrame):
            data = self._data.select(columns).collect().to_pandas()
        else:
            raise ValueError('Only Polars DataFrame, Series, and LazyFrame are supported')

        return HoloViewsConverter(data, x, y, kind=kind, **params)


class hvPlot(hvPlotTabular):
    """
    The plotting method: `df.hvplot(...)` creates a plot similarly to the familiar Pandas
    `df.plot` method.

    For more detailed options use a specific plotting method, e.g. `df.hvplot.line`.

    Reference: https://hvplot.holoviz.org/ref/api/index.html

    Plotting options: https://hvplot.holoviz.org/ref/plotting_options/index.html

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
        Additional keywords arguments are documented in :ref:`plot-options`.

    Returns
    -------
    A Holoviews object. You can `print` the object to study its composition and run `hv.help` on
    the object to learn more about its parameters and options.

    Examples
    --------

    .. code-block::

        import hvplot.pandas
        import pandas as pd

        df = pd.DataFrame(
            {
                "actual": [100, 150, 125, 140, 145, 135, 123],
                "forecast": [90, 160, 125, 150, 141, 141, 120],
                "numerical": [1.1, 1.9, 3.2, 3.8, 4.3, 5.0, 5.5],
                "date": pd.date_range("2022-01-03", "2022-01-09"),
                "string": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            },
        )
        line = df.hvplot.line(
            x="numerical",
            y=["actual", "forecast"],
            ylabel="value",
            legend="bottom",
            height=500,
            color=["steelblue", "teal"],
            alpha=0.7,
            line_width=5,
        )
        line

    You can can add *markers* to a `line` plot by overlaying with a `scatter` plot.

    .. code-block::

        markers = df.hvplot.scatter(
            x="numerical", y=["actual", "forecast"], color=["#f16a6f", "#1e85f7"], size=50
        )
        line * markers

    Please note that you can pass widgets or reactive functions as arguments instead of
    literal values, c.f. https://hvplot.holoviz.org/user_guide/Widgets.html.
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
        'explorer',
    ]

    def image(self, x=None, y=None, z=None, colorbar=True, **kwds):
        """
        Image plot

        You can use `image` to display for example geographic data with independent `latitude` and
        `longitude` fields and a third dependent field.

        Reference: https://hvplot.holoviz.org/ref/api/manual/hvplot.hvPlot.image.html

        Plotting options: https://hvplot.holoviz.org/ref/plotting_options/index.html

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
        **kwds : optional
            Additional keywords arguments are documented in :ref:`plot-options`.
            Run ``hvplot.help('image')`` for the full method documentation.

        Returns
        -------
        :class:`holoviews:holoviews.element.Image` / Panel object
            You can `print` the object to study its composition and run:

            .. code-block::

                import holoviews as hv
                hv.help(the_holoviews_object)

            to learn more about its parameters and options.

        References
        ----------

        - Bokeh: https://docs.bokeh.org/en/latest/docs/examples/topics/images/image.html
        - HoloViews: https://holoviews.org/reference/elements/bokeh/Image.html
        - Matplotlib: https://matplotlib.org/stable/tutorials/introductory/images.html
        - Plotly: https://plotly.com/python/imshow/
        """
        return self(x, y, z=z, kind='image', colorbar=colorbar, **kwds)

    def rgb(self, x=None, y=None, z=None, bands=None, **kwds):
        """
        RGB plot

        `rgb`  can be used to display images that are distributed as three separate "channels" or
        "bands".

        Reference: https://hvplot.holoviz.org/ref/api/manual/hvplot.hvPlot.rgb.html

        Plotting options: https://hvplot.holoviz.org/ref/plotting_options/index.html

        Parameters
        ----------
        x : string, optional
            The coordinate variable along the x-axis. By default the third
            coordinate of the dataset.
        y : string, optional
            The coordinate variable along the y-axis. By default the second
            coordinate of the dataset.
        bands : string, optional
            The coordinate variable to draw the RGB channels from. By default
            the first coordinate of the dataset.
        z : string, optional
            The data variable to plot
        **kwds : optional
            Additional keywords arguments are documented in :ref:`plot-options`.
            Run ``hvplot.help('rgb')`` for the full method documentation.

        Returns
        -------
        :class:`holoviews:holoviews.element.RGB` / Panel object
            You can `print` the object to study its composition and run:

            .. code-block::

                import holoviews as hv
                hv.help(the_holoviews_object)

            to learn more about its parameters and options.

        References
        ----------

        - Bokeh: https://docs.bokeh.org/en/latest/docs/reference/models/glyphs/image_rgba.html
        - HoloViews: https://holoviews.org/reference/elements/bokeh/RGB.html
        - Matplotlib: https://matplotlib.org/stable/tutorials/introductory/images.html
        - Plotly: https://plotly.com/python/imshow/
        """
        if bands is not None:
            kwds['bands'] = bands
        return self(x, y, z=z, kind='rgb', **kwds)

    def quadmesh(self, x=None, y=None, z=None, colorbar=True, **kwds):
        """
        QuadMesh plot

        ``quadmesh`` allows you to plot values on an irregular grid by representing each value as a
        polygon. It is often useful for displaying projected geographic datasets.
        Note that this method can be slower than ``image``. To reduce the render
        time or the size of the saved plot, set ``rasterize=True`` to aggregate
        the values to the pixel. When rasterizing geographic plots, it is recommended
        to set ``project=True``.

        Reference: https://hvplot.holoviz.org/ref/api/manual/hvplot.hvPlot.quadmesh.html

        Plotting options: https://hvplot.holoviz.org/ref/plotting_options/index.html

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
        **kwds : optional
            Additional keywords arguments are documented in :ref:`plot-options`.
            Run ``hvplot.help('quadmesh')`` for the full method documentation.

        Returns
        -------
        :class:`holoviews:holoviews.element.QuadMesh` / Panel object
            You can `print` the object to study its composition and run:

            .. code-block::

                import holoviews as hv
                hv.help(the_holoviews_object)

            to learn more about its parameters and options.

        References
        ----------

        - HoloViews: https://holoviews.org/reference/elements/bokeh/QuadMesh.html
        """
        return self(x, y, z=z, kind='quadmesh', colorbar=colorbar, **kwds)

    def contour(self, x=None, y=None, z=None, colorbar=True, levels=5, logz=False, **kwds):
        """
        Line contour plot.

        A contour plot displays isolines representing constant values in a 2D
        scalar field over gridded data.

        Reference: https://hvplot.holoviz.org/ref/api/manual/hvplot.hvPlot.contour.html

        Plotting options: https://hvplot.holoviz.org/ref/plotting_options/index.html

        Parameters
        ----------
        x : string, optional
            The coordinate variable along the x-axis
        y : string, optional
            The coordinate variable along the y-axis
        z : string, optional
            The data variable to plot
        colorbar: boolean, optional
            Whether to display a colorbar. Default is True.
        levels: int or list, optional
            The number of contour lines to draw or a list of scalar values used
            to specify the contour levels. Default is 5.
        logz: bool, optional
            Whether to apply log scaling to the z-axis. Default is False.
        **kwds : optional
            Additional keywords arguments are documented in :ref:`plot-options`.
            Run ``hvplot.help('contour')`` for the full method documentation.

        Returns
        -------
        :class:`holoviews:holoviews.element.Contours` / Panel object
            You can `print` the object to study its composition and run:

            .. code-block::

                import holoviews as hv
                hv.help(the_holoviews_object)

            to learn more about its parameters and options.

        See Also
        --------
        contourf : Filled contour plot.

        References
        ----------

        - HoloViews: https://holoviews.org/reference/elements/bokeh/Contours.html
        - Matplotlib: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.contour.html
        - Plotly: https://plotly.com/python/contour-plots/
        """
        return self(x, y, z=z, kind='contour', colorbar=colorbar, levels=levels, logz=logz, **kwds)

    def contourf(self, x=None, y=None, z=None, colorbar=True, levels=5, logz=False, **kwds):
        """
        Filled contour plot

        Reference. https://hvplot.holoviz.org/reference/xarray/contourf.html

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
        levels: int, optional
            The number of contour lines to draw or a list of scalar values used
            to specify the contour levels. Default is 5
        logz: bool, optional
            Whether to apply log scaling to the z-axis. Default is False
        **kwds : optional
            Additional keywords arguments are documented in :ref:`plot-options`.
            Run ``hvplot.help('contourf')`` for the full method documentation.

        See Also
        --------
        contour : Line contour plot.

        Returns
        -------
        :class:`holoviews:holoviews.element.Contours` / Panel object
            You can `print` the object to study its composition and run:

            .. code-block::

                import holoviews as hv
                hv.help(the_holoviews_object)

            to learn more about its parameters and options.

        References
        ----------

        - HoloViews: https://holoviews.org/reference/elements/bokeh/Contours.html
        - Matplotlib: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.contour.html
        - Plotly: https://plotly.com/python/contour-plots/
        """
        return self(
            x, y, z=z, kind='contourf', colorbar=colorbar, levels=levels, logz=logz, **kwds
        )
