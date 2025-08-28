import difflib
import sys
import warnings
from functools import partial

import param
import holoviews as hv
import pandas as pd
import numpy as np
import colorcet as cc

from bokeh.models import HoverTool
from holoviews.core.dimension import Dimension
from holoviews.core.spaces import DynamicMap, HoloMap, Callable
from holoviews.core.overlay import NdOverlay
from holoviews.core.options import Store, Cycle, Palette
from holoviews.core.layout import NdLayout
from holoviews.core.util import max_range
from holoviews.element import (
    Curve,
    Scatter,
    Area,
    Bars,
    BoxWhisker,
    Dataset,
    Distribution,
    Table,
    HeatMap,
    Image,
    HexTiles,
    QuadMesh,
    Bivariate,
    Histogram,
    Violin,
    Contours,
    Polygons,
    Points,
    Path,
    Labels,
    RGB,
    ErrorBars,
    VectorField,
    Rectangles,
    Segments,
)
from holoviews.plotting.bokeh import OverlayPlot, colormap_generator
from holoviews.plotting.util import process_cmap
from holoviews.operation import histogram, apply_when
from holoviews.streams import Buffer, Pipe
from holoviews.util.transform import dim, lon_lat_to_easting_northing
from pandas import DatetimeIndex, MultiIndex

from .backend_transforms import _transfer_opts_cur_backend
from .util import (
    _HV_GE_1_21_0,
    _Undefined,
    filter_opts,
    is_tabular,
    is_series,
    is_dask,
    is_duckdb,
    is_intake,
    is_cudf,
    is_streamz,
    is_ibis,
    is_lazy_data,
    is_xarray,
    is_xarray_dataarray,
    process_crs,
    process_intake,
    process_xarray,
    relabel,
    relabel_redim,
    redim_,
    support_index,
    check_library,
    is_geodataframe,
    process_derived_datetime_xarray,
    process_derived_datetime_pandas,
    _convert_col_names_to_str,
    import_datashader,
    import_geoviews,
    is_mpl_cmap,
    _find_stack_level,
)
from .utilities import hvplot_extension

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
        old = {k: v for k, v in self.param.values().items() if k not in ['callable', 'name']}
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


class HoloViewsConverter:
    """
    Data Options
    ------------
    attr_labels : bool or None, default=None
        Whether to use an xarray object's attributes as labels, defaults to
        None to allow best effort without throwing a warning. Set to True
        to see warning if the attrs can't be found, set to False to disable
        the behavior.
    by : str or list of str or None, default=None
        Dimension(s) by which to group the data categories. An
        :doc:`holoviews:reference/containers/bokeh/NdOverlay` is
        returned by default unless ``subplots=True``, then an
        :doc:`holoviews:reference/containers/bokeh/NdLayout` is returned.
    dynamic : bool, default=True
        Whether to return a dynamic plot which sends updates on widget and
        zoom/pan events or whether all the data should be embedded
        (warning: for large groupby operations embedded data can become
        very large if ``dynamic=False``).
    fields : dict, default={}
        A dictionary of fields for renaming or transforming data dimensions.
    groupby : str or list or None, default=None
        Dimension(s) by which to group data, enabling widgets. Returns a
        :doc:`holoviews:reference/containers/bokeh/DynamicMap` if
        ``dynamic=True``, else returns a
        :doc:`holoviews:reference/containers/bokeh/HoloMap`. See ``dynamic``
        for more information.
    group_label : str or None, default=None
        Sets a custom label for the dimension created when plotting multiple columns.
        When multiple columns are plotted (e.g., multiple y values), hvPlot automatically reshapes the data from wide to long format.
        It creates a new grouping dimension that holds the original column names.
        By default, this grouping dimension is labeled ``'Variable'``.
        Setting ``group_label`` overrides this default label.

        .. note::
           ``group_label`` only applies when plotting multiple columns and does not control grouping with ``by``.
    kind : str, default='line'
        The type of plot to generate. Should only be set when calling
        ``hvplot()`` directly.
    label : str or None, default=None
        Label for the data, typically used in the plot title or legends.
    persist : bool, default=False
        Whether to persist the data in memory when using dask.
    row : str or None, default=None
        Column name to use for splitting the plot into separate subplots by rows.
    col : str or None, default=None
        Column name to use for splitting the plot into separate subplots by columns.
    sort_date : bool, default=True
        Whether to sort the x-axis by date before plotting
    subplots : bool, default=False
        Whether to display data in separate subplots when using the ``by`` parameter.
    transforms : dict, default={}
        A dictionary of HoloViews dim transforms to apply before plotting
    use_dask : bool, default=False
        Enables support for Dask-backed xarray datasets, allowing out-of-core computation
        and parallel processing. Only applicable when the input data is an xarray object.
        Has no effect on Pandas or other non-xarray data structures.
    use_index : bool, default=True
        Whether to use the data's index for the x-axis by default.
    value_label : str, default='value'
        Sets a custom label for the values when the data is reshaped from wide to long format (e.g., when plotting multiple columns).
        This label is typically used for the y-axis, colorbar, or in hover tooltips.

    Geographic Options
    ------------------
    coastline : bool, default=False
        Whether to display a coastline on top of the plot, setting
        coastline='10m'/'50m'/'110m' specifies a specific scale.
    crs : str or int or pyproj.CRS or pyproj.Proj or cartopy.CRS or None
        Coordinate reference system of the data (input projection) specified as a string
        or integer EPSG code, a CRS or Proj pyproj object, a Cartopy
        CRS object or class name, a WKT string, or a proj.4 string.
        Defaults to PlateCarree.
    features : dict or list or None, default=None
        A list of features or a dictionary of features and the scale
        at which to render it. Available features include 'borders',
        'coastline', 'lakes', 'land', 'ocean', 'rivers' and 'states'.
        Available scales include '10m'/'50m'/'110m'.
    geo : bool, default=False
        Whether the plot should be treated as geographic (and assume
        PlateCarree, i.e. lat/lon coordinates).
    global_extent : bool, default=False
        Whether to expand the plot extent to span the whole globe.
    project : bool, default=False
        Whether to project the data before plotting (adds initial
        overhead but avoids projecting data when plot is dynamically
        updated).
    projection : str or int or pyproj.CRS or pyproj.Proj or cartopy.CRS or bool or None
        Coordinate reference system of the plot (output projection) specified as a string
        or integer EPSG code, a CRS or Proj pyproj object, a Cartopy
        CRS object or class name, a WKT string, or a proj.4 string.
        Defaults to PlateCarree.
    tiles : bool or str or xyzservices.TileProvider or holoviews.Tiles or geoviews.WMTS or None, default=False
        Whether to overlay the plot on a tile source. If coordinate values fall within
        lat/lon bounds, auto-projects to EPSG:3857, unless ``projection=False``:

        - ``True``: OpenStreetMap layer
        - ``xyzservices.TileProvider`` instance (requires xyzservices to
          be installed)
        - a map string name based on one of the default layers made
          available by HoloViews or GeoViews.
        - a ``holoviews.Tiles`` or ``geoviews.WMTS`` instance or class
    tiles_opts : dict or None, default=None
        Options to customize the tiles layer created when ``tiles`` is set,
        e.g. ``dict(alpha=0.5)``.

    Size And Layout Options
    -----------------------
    aspect : float or {'equal', 'square'} or None, default=None
        Sets the width-to-height ratio of the plot. When None (the default),
        hvPlot chooses an appropriate aspect automatically. Use
        ``'equal'`` or ``'square'`` to modify the unit ratio between axes,
        or supply a numeric value (e.g. 2.0) for a custom ratio.
        To control the scaling of individual axis units, use the
        ``data_aspect`` option instead.
    data_aspect : float or None, default=None
        Defines the aspect of the axis scaling, i.e. the ratio of
        y-unit to x-unit.
    frame_width/frame_height : int
        The width and height of the data area of the plot
    max_width/max_height : int
        The maximum width and height of the plot for responsive modes
    min_width/min_height : int
        The minimum width and height of the plot for responsive modes
    height : int, default=300
        The height of the plot in pixels
    width : int, default=700
        The width of the plot in pixels
    padding : number or tuple
        Fraction by which to increase auto-ranged extents to make
        datapoints more visible around borders. Supports tuples to
        specify different amount of padding for x- and y-axis and
        tuples of tuples to specify different amounts of padding for
        upper and lower bounds.
    responsive : bool, default=False
        Whether the plot should responsively resize depending on the
        size of the browser. Responsive mode will only work if at
        least one dimension of the plot is left undefined, e.g. when
        width and height or width and aspect are set the plot is set
        to a fixed size, ignoring any responsive option. Only supported by the
        interactive plotting backends.
    widget_location : str, optional
        Specifies where to place widgets generated by options like ``groupby``.
        Valid values are: ``'right'`` (default), ``'left'``, ``'bottom'``,
        ``'right'``, ``'top'``, ``'top_left'``, ``'top_right'``,
        ``'bottom_left'``, ``'bottom_right'``, ``'left_top'``,
        ``'left_bottom'``, ``'right_top'``, ``'right_bottom'``.
        Only applies if the plot generates widgets (e.g. via ``groupby``).

    Axis Options
    ------------
    autorange : Literal['x', 'y'] or None, default=None
        Whether to enable auto-ranging along the x- or y-axis when
        zooming. Only supported by the Bokeh backend.

        .. versionadded:: 0.9.0
    flip_xaxis/flip_yaxis : bool or None, default=None
        Whether to flip the axis left to right or up and down respectively.
    framewise : bool, default=True
        Whether to compute the axis ranges frame-by-frame when using dynamic plots.
    invert : bool, default=False
        Swaps x- and y-axis.
    logx/logy : bool, default=False
        Enables logarithmic x- and y-axis respectively.
    loglog : bool or None, default=None
        Enables logarithmic x- and y-axis.
    rot : number or None, default=None
        Rotates the axis ticks along the x-axis by the specified
        number of degrees.
    shared_axes : bool, default=True
        Whether to link axes between plots.
    subcoordinate_y : bool or dict or None, default=None
       Whether to enable sub-coordinate y systems for this plot. Accepts also a
       dictionary of related options to pass down to HoloViews,
       e.g. ``{'subcoordinate_scale': 2}``.

       .. versionadded:: 0.11.0
    title : str or None, default=None
        Title for the plot.
    xaxis : str or bool or None
        Whether to show the x-axis and whether to place it at the top or
        bottom. A bare axis means that an axis line is still displayed but
        there are no axis ticks and labels. Valid options include:
        ``bottom`` (default), ``bottom-bare``, ``top``, ``top-bare``,
        ``None`` (no axis at all), ``True`` (same as ``bottom``), and
        ``False`` (same as ``None``).
    yaxis : str or bool or None
        Whether to show the y-axis and whether to place it at the left or
        right. A bare axis means that an axis line is still displayed but
        there are no axis ticks and labels. Valid options include:
        ``left`` (default), ``left-bare``, ``right``, ``right-bare``,
        ``None`` (no axis at all), ``True`` (same as ``left``), and
        ``False`` (same as ``None``).
    xformatter/yformatter : str or bokeh.TickFormatter or None, default=None
        Formatter for the x-axis and y-axis (accepts printf formatter,
        e.g. '%.3f', and bokeh TickFormatter).
    xlabel/ylabel/clabel : str or None, default=None
        Axis labels for the x-axis, y-axis, and colorbar.
    xlim/ylim : tuple or None, default=None
        Plot limits of the x- and y-axis. One bound can be left unset by
        using ``None`` (e.g. ``xlim=(10, None)`` means there is no upper bound).
    xticks/yticks/cticks : int or list or np.ndarray or None, default=None
        Ticks along x-axis and y-axis, as an integer, list of ticks positions,
        Numpy ndarray, or list of tuples of the tick positions and labels.
        Also accepts a Bokeh ``Ticker`` instance when the Bokeh plotting backend
        is enabled.

        .. versionadded:: 0.11.0
           ``cticks`` was added in this version and is only supported by the
           Bokeh plotting backend.

    Legend Options
    --------------
    legend : bool or str or None, default=None
        Whether to show a legend, or a legend position. A cardinal position
        (``'top'``, ``'bottom'``, ``'left'``, ``'right'`` (default)) or a
        corner placement (``'top_left'``, ``'top_right'``, ``'bottom_left'``,
        ``'bottom_right'``).
    legend_cols : int or None, default=None
        Number of columns in the legend.

        .. versionadded:: 0.12.0

    legend_opts : dict or None, default=None
        Allows setting specific styling options for the legend. They keys
        should be attributes of the ``Legend`` model for Bokeh and keyword
        arguments of the ``Axes.legen`` method for Matplotlib.

        .. versionadded:: 0.12.0

    Interactivity Options
    ---------------------
    hover : bool or str or None, default=None
        Whether to show hover tooltips, default is True unless ``datashade=True``
        in which case hover is False by default. Also accepts ``'hline'``
        and ``'vline'`` to change the hit-testing mode.
    hover_cols : list or str, default=[]
        Additional columns to add to the hover tool or 'all' which will
        include all columns (including indexes if ``use_index=True``).
    hover_formatters : dict or None, default=None
        A dict of formatting options for the hover tooltip.

        .. deprecated:: 0.12
           Use ``hover_tooltips`` instead.
    hover_tooltips : list[str] or list[tuple] or None, default=None
        A list of dimensions to be displayed in the hover tooltip.
    toolbar : str or bool or None, optional
        Whether to display a toolbar and where to place it. Displayed by
        default, disabled with ``'disable'``, ``None`` or ``False``. Location
        must be one ``'above'``, ``'below'``, ``'left'``, or ``'right'``
        (the default).

        .. versionadded:: 0.12.0

    autohide_toolbar : bool, optional
        Whether to automatically hide the toolbar until the user hovers over
        the plot. This keyword has no effect if the toolbar is disabled
        (``toolbar=None``). Default is False.

        .. versionadded:: 0.12.0
    tools : list, default=[]
        List of tool instances or strings (e.g. ['tap', 'box_select'])

    Color And Colormap Options
    --------------------------
    bgcolor : str or None, default=None
        Background color of the data area of the plot
    color : str or list or column name or None, default=None
        Defines the color(s) to use for the plot. Accepts:

        - a single color name (e.g., ``'red'``, ``'blue'``)
        - a HEX color code (e.g., ``'#ff5733'``)
        - a list of colors for multiple elements
        - a column name from the dataset to map colors based on values.

    c : str or list or column name or None, default=None
        Alias for ``color``. If both ``color`` and ``c`` are provided,
        the ``color`` keyword takes precedence.
    cmap : str or list or dict or colormap object or None, default=None
        The colormap to use for continuous or categorical color mapping.

        Accepts:

        - a predefined colormap name from Bokeh, Matplotlib, or Colorcet
          (e.g., ``'viridis'``, ``'plasma'``)
        - a list of named colors or HEX color codes.
        - a dictionary mapping categories to colors for discrete colormaps.
        - A colormap object from HoloViews or Matplotlib.

        If not specified, a default colormap is automatically chosen based on the data type:

        - Linear data: Uses the ``kbc_r`` colormap.
        - Categorical data: Uses ``glasbey_category10`` colormap from Colorcet.
        - Cyclic data: Uses ``colorwheel`` colormap.
        - Diverging data: Uses ``coolwarm`` colormap.

        You can override these defaults by explicitly setting ``cmap=<colormap_name>``.
        Only one of ``cmap``, ``colormap``, or ``color_key`` can be specified at a time.
    colorbar : bool or None, default=None
        Enables a colorbar. Enabled by default for these plots: ``bivariate``,
        ``contour``, ``contourf``, ``heatmap``, ``image``, ``hexbin``, ``quadmesh``,
        ``polygons``. Enabled by default for rasterized plots.
    colormap : str or list  or colormap object or None, default=None
        Alias for ``cmap``. Accepts the same values as ``cmap``.
        See ``cmap`` for more details.
        Only one of ``cmap``, ``colormap``, or ``color_key`` can be specified at a time.
    color_key : str or list or dict or None, default=None
        Alias for ``cmap``. Accepts the same values as ``cmap``.
        See ``cmap`` for more details.
        Only one of ``cmap``, ``colormap``, or ``color_key`` can be specified at a time.
    clim : tuple or None, default=None
        Lower and upper bound of the color scale
    cnorm : str, default='linear'
        Color scaling which must be one of ``'linear'``, ``'log'`` or ``'eq_hist'``.
    rescale_discrete_levels : bool or None, default=None
        If ``cnorm='eq_hist'`` and there are only a few discrete values,
        then ``rescale_discrete_levels=True`` (the default) decreases
        the lower limit of the autoranged span so that the values are
        rendering towards the (more visible) top of the ``cmap`` range,
        thus avoiding washout of the lower values.  Has no effect if
        ``cnorm!=`eq_hist``.
    robust : bool or None, default=None
        If this option is True and no ``clim`` was provided, the colormap range
        is computed with 2nd and 98th percentiles instead of the extreme values
        for image elements. For RGB elements, clips the "RGB", or
        raw reflectance values between 2nd and 98th percentiles.
        Follows the same logic as xarray's robust option.
    symmetric : bool or None, default=None
        Whether the data are symmetric around zero. If left unset, the data
        will be checked for symmetry as long as the size is less than
        ``check_symmetric_max``.
    check_symmetric_max : int, default=1000000
        Size above which to stop checking for symmetry by default on the data.

    Styling Options
    ---------------
    backend_opts : dict or None, optional
        A dictionary of custom options to apply to the plot or subcomponents of
        the plot. The keys in the dictionary mirror attribute access on the
        underlying plotting backend objects stored in the plot's handles, e.g.
        ``{'hover.attachment': 'vertical'}`` will index the hover in the handles
        and then set the attachment.

        .. versionadded:: 0.12.0
    fontscale : number
        Scales the size of all fonts by the same amount, e.g. fontscale=1.5
        enlarges all fonts (title, xticks, labels etc.) by 50%.
    fontsize : number or dict or None, default=None
        Set title, label and legend text to the same fontsize. Finer control
        by using a dict: ``{'title': '15pt', 'ylabel': '5px', 'ticks': 20}``.
    grid : bool or None, default=None
        Whether to show a grid.

    Resampling Options
    ------------------
    aggregator : str, datashader.Reduction, or None, default=None
        Aggregator to use when applying rasterize or datashade operation
        (valid options include ``'mean'``, ``'count'``, ``'min'``, ``'max'``
        and more, and datashader reduction objects)
    datashade : bool, default=False
        Whether to apply rasterization and shading (colormapping) using
        the Datashader library, returning an RGB object instead of
        individual points
    downsample : bool or str or None, default=None
        Controls the application of downsampling to the plotted data,
        which is particularly useful for large timeseries datasets to
        reduce the amount of data sent to browser and improve
        visualization performance.

        Acceptable values:

        - ``False``: No downsampling is applied.
        - ``True``: Applies downsampling using HoloViews' default algorithm
          (LTTB - Largest Triangle Three Buckets).
        - ``'lttb'``: Explicitly applies the Largest Triangle Three Buckets
          algorithm. Uses ``tsdownsample`` if installed.
        - ``'minmax'``: Applies the MinMax algorithm, selecting the minimum
          and maximum values in each bin. Requires ``tsdownsample``.
        - ``'m4'``: Applies the M4 algorithm, selecting the minimum, maximum,
          first, and last values in each bin. Requires ``tsdownsample``.
        - ``'minmax-lttb'``: Combines MinMax and LTTB algorithms for
          downsampling, first applying MinMax to reduce to a preliminary
          set of points, then LTTB for further reduction. Requires
          ``tsdownsample``.

        Other string values corresponding to supported algorithms in
        HoloViews may also be used.
    dynspread : bool, default=False
        For plots generated with datashade=True or rasterize=True,
        automatically increase the point size when the data is sparse
        so that individual points become more visible.
    max_px : int, default=3
        The maximum size in pixels for dynamically spreading elements in sparse data using ``dynspread``.
        This helps to increase the visibility of sparse data points.
    pixel_ratio : number or None, default=None
       Pixel ratio applied to the height and width, used when rasterizing or
       datashading. When not set explicitly, the ratio is automatically
       obtained from the browser device pixel ratio. Default is 1 when
       the browser information is not available. Useful when the browser
       information is not available (pixel_ratio=2 can give better results on
       Retina displays) or for using lower resolution for speed.
    precompute : bool, default=False
        Whether to precompute aggregations when using ``rasterize`` or ``datashade``.
    rasterize : bool, default=False
        Whether to apply rasterization using the Datashader library,
        returning an aggregated Image (to be colormapped by the
        plotting backend) instead of individual points.
    resample_when : int or None, default=None
        Applies a resampling operation (datashade, rasterize or downsample) if
        the number of individual data points present in the current viewport
        is above this threshold. The raw plot is displayed otherwise.
    selector : datashader.Reduction | str | tuple | None, default=None
        Datashader reduction to apply during a ``rasterize`` or ``datashade``
        operation, used to select additional information for inclusion in the
        hover tooltip. Supported options include:

        - string: only ``'first'`` and ``'last'``
        - tuple of two strings: ``(<reduction>, <column>)``, e.g. ``('min', 'value')``.
        - Datashader object: ``ds.first``, ``ds.last``, ``ds.min``, and ``ds.max``.

        .. versionadded:: 0.12.0
           Requires ``holoviews>=1.21``.
           Requires ``bokeh>=3.7``.
    threshold : float, default=0.5
        When using ``dynspread``, this value defines the minimum density of overlapping points
        required before the spreading operation is applied.
        Values between 0 and 1, where 1 means always spread and 0 means never spread.
    x_sampling/y_sampling : number or None, default=None:
        Specifies the smallest allowed sampling interval along the x/y axis.
        Used when rasterizing or datashading.

    Streaming Options
    -----------------
    backlog : int, default=1000
        Maximum number of rows to keep in the stream buffer when using a streaming data source.
    stream : holoviews.streams.Stream or None, default=None
        A stream object for streaming plots, allowing data updates without re-rendering the entire plot.
    """

    _gridded_types = ['image', 'contour', 'contourf', 'quadmesh', 'rgb', 'points', 'dataset']

    _geom_types = ['paths', 'polygons']

    _geo_types = sorted(
        _gridded_types + _geom_types + ['points', 'vectorfield', 'labels', 'hexbin', 'bivariate']
    )

    _stats_types = ['hist', 'kde', 'violin', 'box', 'density']

    _data_options = [
        'attr_labels',
        'by',
        'dynamic',
        'fields',
        'group_label',
        'groupby',
        'kind',
        'label',
        'persist',
        'row',
        'col',
        'sort_date',
        'subplots',
        'transforms',
        'use_dask',
        'use_index',
        'value_label',
    ]

    _geo_options = [
        'geo',
        'crs',
        'features',
        'project',
        'coastline',
        'tiles',
        'tiles_opts',
        'projection',
        'global_extent',
    ]

    _size_layout_options = [
        'aspect',
        'data_aspect',
        'frame_height',
        'frame_width',
        'height',
        'max_height',
        'max_width',
        'min_height',
        'min_width',
        'padding',
        'responsive',
        'widget_location',
        'width',
    ]

    _axis_config_options = [
        'autorange',
        'clabel',
        'flip_xaxis',
        'flip_yaxis',
        'framewise',
        'invert',
        'loglog',
        'logx',
        'logy',
        'rot',
        'shared_axes',
        'subcoordinate_y',
        'title',
        'xaxis',
        'yaxis',
        'xformatter',
        'yformatter',
        'xlabel',
        'ylabel',
        'xlim',
        'ylim',
        'xticks',
        'yticks',
        'cticks',
    ]

    _legend_options = [
        'legend',
        'legend_cols',
        'legend_opts',
    ]

    _interactivity_options = [
        'hover',
        'hover_cols',
        'hover_formatters',
        'hover_tooltips',
        'toolbar',
        'autohide_toolbar',
        'tools',
    ]

    _color_options = [
        'bgcolor',
        'clim',
        'color',
        'colorbar',
        'colormap',
        'c',
        'cmap',
        'color_key',
        'cnorm',
        'rescale_discrete_levels',
        'robust',
        'symmetric',
        'check_symmetric_max',
    ]

    _style_options = [
        'backend_opts',
        'fontscale',
        'fontsize',
        'grid',
    ]

    _resample_options = [
        'datashade',
        'rasterize',
        'pixel_ratio',
        'x_sampling',
        'y_sampling',
        'downsample',
        'aggregator',
        'resample_when',
        'dynspread',
        'max_px',
        'precompute',
        'selector',
        'threshold',
    ]

    _stream_options = [
        'backlog',
        'stream',
    ]

    _docstring_sections = {
        'data': 'Data Options',
        'geographic': 'Geographic Options',
        'size_layout': 'Size And Layout Options',
        'axis': 'Axis Options',
        'legend': 'Legend Options',
        'color': 'Color And Colormap Options',
        'interactivity': 'Interactivity Options',
        'style': 'Styling Options',
        'resampling': 'Resampling Options',
        'streaming': 'Streaming Options',
    }

    _options_groups = {
        'data': _data_options,
        'geographic': _geo_options,
        'size_layout': _size_layout_options,
        'axis': _axis_config_options,
        'legend': _legend_options,
        'interactivity': _interactivity_options,
        'color': _color_options,
        'style': _style_options,
        'resampling': _resample_options,
        'streaming': _stream_options,
    }

    # Options specific to a particular plot type
    _kind_options = {
        'area': ['x', 'y', 'y2', 'stacked'],
        'bar': ['x', 'y', 'stacked'],
        'barh': ['x', 'y', 'stacked'],
        'box': ['x', 'y'],
        'errorbars': ['x', 'y', 'yerr1', 'yerr2'],
        'bivariate': ['x', 'y', 'bandwidth', 'cut', 'filled', 'levels'],
        'contour': ['x', 'y', 'z', 'levels', 'logz'],
        'contourf': ['x', 'y', 'z', 'levels', 'logz'],
        'dataset': ['columns'],
        'density': ['y', 'bw_method', 'ind', 'bandwidth', 'cut', 'filled'],
        'heatmap': ['x', 'y', 'C', 'reduce_function', 'logz'],
        'hexbin': ['x', 'y', 'C', 'reduce_function', 'gridsize', 'logz', 'min_count'],
        'hist': ['y', 'bins', 'bin_range', 'normed', 'cumulative'],
        'image': ['x', 'y', 'z', 'logz'],
        'kde': ['y', 'bw_method', 'ind', 'bandwidth', 'cut', 'filled'],
        'labels': ['x', 'y', 'text', 'c', 'xoffset', 'yoffset', 'text_font', 'text_font_size'],
        'line': ['x', 'y'],
        'ohlc': ['x', 'y', 'bar_width', 'pos_color', 'neg_color', 'line_color'],
        'paths': ['x', 'y'],
        'points': ['x', 'y', 's', 'marker', 'c', 'scale', 'logz'],
        'polygons': ['x', 'y', 'logz', 'c'],
        'rgb': ['x', 'y', 'z', 'bands'],
        'scatter': ['x', 'y', 's', 'c', 'scale', 'logz', 'marker'],
        'step': ['x', 'y', 'where'],
        'table': ['columns'],
        'quadmesh': ['x', 'y', 'z', 'logz'],
        'vectorfield': ['x', 'y', 'angle', 'mag'],
        'violine': ['y'],
    }

    # Mapping from kind to HoloViews element type
    _kind_mapping = {
        'area': Area,
        'bar': Bars,
        'barh': Bars,
        'bivariate': Bivariate,
        'box': BoxWhisker,
        'contour': Contours,
        'contourf': Polygons,
        'dataset': Dataset,
        'density': Distribution,
        'errorbars': ErrorBars,
        'heatmap': HeatMap,
        'hexbin': HexTiles,
        'hist': Histogram,
        'image': Image,
        'kde': Distribution,
        'labels': Labels,
        'line': Curve,
        'ohlc': Rectangles,
        'paths': Path,
        'points': Points,
        'polygons': Polygons,
        'quadmesh': QuadMesh,
        'rgb': RGB,
        'scatter': Scatter,
        'step': Curve,
        'table': Table,
        'vectorfield': VectorField,
        'violin': Violin,
    }

    # Types which have a colorbar by default
    _colorbar_types = [
        'bivariate',
        'contour',
        'contourf',
        'heatmap',
        'image',
        'hexbin',
        'quadmesh',
        'polygons',
    ]

    _legend_positions = (
        'top_right',
        'top_left',
        'bottom_left',
        'bottom_right',
        'right',
        'left',
        'top',
        'bottom',
    )

    _default_plot_opts = {
        'logx': False,
        'logy': False,
        'show_legend': True,
        'legend_position': 'right',
        'show_grid': False,
        'responsive': False,
        'shared_axes': True,
    }

    _default_cmaps = {
        'linear': 'kbc_r',
        'categorical': cc.palette['glasbey_category10'],
        'cyclic': 'colorwheel',
        'diverging': 'coolwarm',
    }

    def __init__(
        self,
        data,
        x,
        y,
        kind=None,
        by=None,
        use_index=True,
        group_label=None,
        value_label='value',
        backlog=1000,
        persist=False,
        use_dask=False,
        crs=None,
        fields={},
        groupby=None,
        dynamic=True,
        grid=None,
        legend=None,
        legend_cols=None,
        legend_opts=None,
        rot=None,
        title=None,
        xlim=None,
        ylim=None,
        clim=None,
        robust=None,
        symmetric=None,
        logx=None,
        logy=None,
        loglog=None,
        hover=None,
        hover_cols=[],
        hover_formatters=None,
        hover_tooltips=None,
        subplots=False,
        label=None,
        invert=False,
        stacked=False,
        colorbar=None,
        cticks=None,
        datashade=False,
        rasterize=False,
        downsample=None,
        resample_when=None,
        row=None,
        col=None,
        debug=False,
        framewise=True,
        aggregator=None,
        selector=None,
        projection=None,
        global_extent=None,
        geo=False,
        precompute=False,
        flip_xaxis=None,
        flip_yaxis=None,
        dynspread=False,
        x_sampling=None,
        y_sampling=None,
        pixel_ratio=None,
        project=False,
        toolbar=_Undefined,
        autohide_toolbar=False,
        tools=[],
        attr_labels=None,
        coastline=False,
        tiles=False,
        tiles_opts=None,
        sort_date=True,
        check_symmetric_max=1000000,
        transforms={},
        stream=None,
        cnorm=None,
        features=None,
        rescale_discrete_levels=None,
        autorange=None,
        subcoordinate_y=None,
        backend_opts=None,
        **kwds,
    ):
        if debug:
            warnings.warn(
                '`debug` has been deprecated and will be removed in a future version.',
                FutureWarning,
                stacklevel=_find_stack_level(),
            )

        # Process data and related options
        self._redim = fields
        self.use_index = use_index
        self.value_label = value_label
        self.label = label
        self._process_data(
            kind,
            data,
            x,
            y,
            by,
            groupby,
            row,
            col,
            use_dask,
            persist,
            backlog,
            label,
            group_label,
            value_label,
            hover_cols,
            attr_labels,
            transforms,
            stream,
            robust,
            kwds,
        )

        self.dynamic = dynamic
        self.geo = any([geo, crs, global_extent, projection, project, coastline, features])
        # Try importing geoviews if geo-features requested
        if self.geo or self.datatype == 'geopandas':
            import_geoviews()

        self.crs = self._process_crs(data, crs) if self.geo else None
        self.output_projection = self.crs
        self.project = project
        self.coastline = coastline
        self.features = features
        self.tiles = tiles
        self.tiles_opts = tiles_opts or {}
        self.sort_date = sort_date

        if self.geo:
            if self.kind not in self._geo_types:
                param.main.param.warning(
                    f'geo option cannot be used with kind={self.kind!r} plot '
                    'type. Geographic plots are only supported for '
                    f'following plot types: {self._geo_types!r}'
                )
            from cartopy import crs as ccrs
            from geoviews.util import project_extents

            if projection is not None:
                projection = process_crs(projection)

            self.output_projection = projection or (ccrs.GOOGLE_MERCATOR if tiles else self.crs)
            if tiles and self.output_projection != ccrs.GOOGLE_MERCATOR:
                raise ValueError(
                    'Tiles can only be used with output projection of '
                    '`cartopy.crs.GOOGLE_MERCATOR`. To get rid of this error '
                    'remove `projection=` or `tiles=`'
                )
            if self.crs != projection and (xlim or ylim):
                px0, py0, px1, py1 = ccrs.GOOGLE_MERCATOR.boundary.bounds
                x0, x1 = xlim or (px0, px1)
                y0, y1 = ylim or (py0, py1)
                extents = (x0, y0, x1, y1)
                x0, y0, x1, y1 = project_extents(extents, self.crs, self.output_projection)
                if xlim:
                    xlim = (x0, x1)
                if ylim:
                    ylim = (y0, y1)
        elif projection is False:
            # to disable automatic projection of tiles
            self.output_projection = projection

        # Operations
        if resample_when is not None and not any([rasterize, datashade, downsample]):
            raise ValueError(
                'At least one resampling operation (rasterize, datashader, '
                'downsample) must be enabled when resample_when is set.'
            )
        if selector is not None:
            if not _HV_GE_1_21_0:
                msg = 'selector requires holoviews>=1.21.'
                raise ImportError(msg)
            if not (datashade or rasterize):
                msg = 'rasterize or datashade must be enabled when selector is set.'
                raise ValueError(msg)
        self.resample_when = resample_when
        self.datashade = datashade
        self.rasterize = rasterize
        self.downsample = downsample
        self.dynspread = dynspread
        self.aggregator = aggregator
        self.selector = selector
        self.precompute = precompute
        self.x_sampling = x_sampling
        self.y_sampling = y_sampling
        self.pixel_ratio = pixel_ratio

        # By type
        self.subplots = subplots
        self._by_type = NdLayout if subplots else NdOverlay

        self._backend = Store.current_backend
        if hvplot_extension.compatibility is None:
            self._backend_compat = self._backend
        else:
            self._backend_compat = hvplot_extension.compatibility

        self.stacked = stacked

        plot_opts = dict(self._default_plot_opts, **self._process_plot())
        if xlim is not None:
            plot_opts['xlim'] = tuple(xlim)
        if ylim is not None:
            plot_opts['ylim'] = tuple(ylim)
        if autorange is not None:
            plot_opts['autorange'] = autorange

        self.invert = invert
        if loglog is not None:
            logx = logx or loglog
            logy = logy or loglog
        if logx is not None:
            plot_opts['logx'] = logx
        if logy is not None:
            plot_opts['logy'] = logy

        if grid is not None:
            plot_opts['show_grid'] = grid

        if legend is not None:
            plot_opts['show_legend'] = bool(legend)

        if legend in self._legend_positions:
            plot_opts['legend_position'] = legend
        elif legend not in (True, False, None):
            raise ValueError(
                'The legend option should be a boolean or '
                f'a valid legend position (i.e. one of {list(self._legend_positions)}).'
            )
        if legend_cols is not None:
            plot_opts['legend_cols'] = legend_cols
        if legend_opts is not None:
            plot_opts['legend_opts'] = legend_opts

        if subcoordinate_y:
            plot_opts['subcoordinate_y'] = True
            if isinstance(subcoordinate_y, dict):
                plot_opts.update(subcoordinate_y)

        plotwds = [
            'xticks',
            'yticks',
            'xlabel',
            'ylabel',
            'clabel',
            'padding',
            'xformatter',
            'yformatter',
            'height',
            'width',
            'frame_height',
            'frame_width',
            'min_width',
            'min_height',
            'max_width',
            'max_height',
            'fontsize',
            'fontscale',
            'responsive',
            'shared_axes',
            'aspect',
            'data_aspect',
            'bgcolor',
        ]
        for plotwd in plotwds:
            if plotwd in kwds:
                plot_opts[plotwd] = kwds.pop(plotwd)

        self._style_opts, plot_opts, kwds = self._process_style(kwds, plot_opts)

        for axis_name in ['xaxis', 'yaxis']:
            if axis_name in kwds:
                axis = kwds.pop(axis_name)
                plot_opts[axis_name] = axis or None

        if flip_xaxis:
            plot_opts['invert_xaxis'] = True
        if flip_yaxis:
            plot_opts['invert_yaxis'] = True

        if self.geo and not plot_opts.get('data_aspect'):
            plot_opts['data_aspect'] = 1

        ignore_opts = ['responsive', 'aspect', 'data_aspect', 'frame_height', 'frame_width']
        if not any(plot_opts.get(opt) for opt in ignore_opts):
            plot_opts['width'] = plot_opts.get('width', 700)
            plot_opts['height'] = plot_opts.get('height', 300)

        if isinstance(colorbar, bool):
            plot_opts['colorbar'] = colorbar
        elif self.kind in self._colorbar_types:
            plot_opts['colorbar'] = True
        elif self.rasterize:
            plot_opts['colorbar'] = plot_opts.get('colorbar', True)
        if plot_opts.get('colorbar') is True and cticks is not None:
            if self._backend == 'plotly':
                raise ValueError('cticks option is not supported for plotly backend')
            key = 'cticks' if self._backend == 'bokeh' else 'cbar_ticks'
            self._style_opts[key] = cticks

        if 'logz' in kwds and 'logz' in self._kind_options.get(self.kind, {}):
            plot_opts['logz'] = kwds.pop('logz')
        if invert:
            plot_opts['invert_axes'] = self.kind != 'barh'
        if rot:
            axis = 'yrotation' if invert else 'xrotation'
            plot_opts[axis] = rot

        tools = list(tools) or list(plot_opts.get('tools', []))
        # Disable hover for errorbars plot as Bokeh annotations can't be hovered.
        if kind == 'errorbars':
            hover = False
        elif hover is None:
            hover = True if self.selector else not self.datashade
        if hover and not any(
            t for t in tools if isinstance(t, HoverTool) or t in ['hover', 'vline', 'hline']
        ):
            if hover in {'vline', 'hline'}:
                plot_opts['hover_mode'] = hover
            tools.append('hover')
        if 'hover' in tools:
            if hover_tooltips:
                plot_opts['hover_tooltips'] = hover_tooltips
            if hover_formatters:
                warnings.warn(
                    'hover_formatters has been deprecated and will be removed '
                    'in a future version. Use hover_tooltips instead.',
                    DeprecationWarning,
                    stacklevel=_find_stack_level(),
                )
                plot_opts['hover_formatters'] = hover_formatters
        if toolbar is not _Undefined:
            if toolbar is False:
                toolbar = None
            elif toolbar is True:
                toolbar = 'right'
            plot_opts['toolbar'] = toolbar
        if autohide_toolbar:
            if not _HV_GE_1_21_0:
                warnings.warn(
                    'autohide_toolbar requires holoviews>=1.21, skipped.',
                    stacklevel=_find_stack_level(),
                )
            else:
                plot_opts['autohide_toolbar'] = autohide_toolbar
        plot_opts['tools'] = tools

        if backend_opts is not None:
            plot_opts['backend_opts'] = backend_opts

        if self.crs and global_extent:
            plot_opts['global_extent'] = global_extent
        if projection:
            plot_opts['projection'] = self.output_projection
        title = title if title is not None else getattr(self, '_title', None)
        if title is not None:
            plot_opts['title'] = title
        if (
            self.kind in self._colorbar_types
            or self.rasterize
            or self.datashade
            or self._color_dim
        ):
            try:
                if not use_dask:
                    symmetric = self._process_symmetric(symmetric, clim, check_symmetric_max)
                if self._style_opts.get('cmap') is None:
                    if self._process_categorical_datashader()[0]:
                        self._style_opts['cmap'] = self._default_cmaps['categorical']
                    elif symmetric:
                        self._style_opts['cmap'] = self._default_cmaps['diverging']
                    else:
                        self._style_opts['cmap'] = self._default_cmaps['linear']
                if robust:
                    plot_opts['clim_percentile'] = True
                if symmetric is not None:
                    plot_opts['symmetric'] = symmetric
            except TypeError:
                pass
        if cnorm is not None:
            plot_opts['cnorm'] = cnorm
        if rescale_discrete_levels is not None:
            plot_opts['rescale_discrete_levels'] = rescale_discrete_levels

        self._plot_opts = plot_opts
        self._overlay_opts = {
            k: v for k, v in self._plot_opts.items() if k in OverlayPlot.param.objects()
        }

        self._norm_opts = {'framewise': framewise, 'axiswise': not plot_opts.get('shared_axes')}
        self.kwds = kwds

        # Process dimensions and labels
        self.label = label
        self._relabel = {'label': label} if label else {}
        self._dim_ranges = {'c': clim or (None, None)}

        # High-level options
        self._validate_kwds(kwds)
        if debug:
            kwds = dict(
                x=self.x,
                y=self.y,
                by=self.by,
                kind=self.kind,
                groupby=self.groupby,
                grid=self.grid,
            )
            param.main.param.warning(
                'Plotting {kind} plot with parameters x: {x}, '
                'y: {y}, by: {by}, groupby: {groupby}, row/col: {grid}'.format(**kwds)
            )

    def _process_categorical_datashader(self):
        categorical, agg = False, None
        if not (self.datashade or self.rasterize):
            return categorical, agg

        ds = import_datashader()

        categorical = False
        if self.aggregator:
            agg = self.aggregator
            if isinstance(agg, str) and self._color_dim:
                categorical = agg == 'count_cat'
                agg = getattr(ds.reductions, agg)(self._color_dim)
            else:
                categorical = isinstance(agg, (ds.count_cat, ds.by))
        elif self._color_dim:
            agg = ds.reductions.mean(self._color_dim)
        elif self.by and not self.subplots:
            agg = ds.reductions.count_cat(self.by[0])
            categorical = True
        elif (
            (isinstance(self.y, list) and len(self.y) > 1)
            or (self.y is None and len(set(self.variables) - set(self.indexes)) > 1)
        ) and self.kind in ('scatter', 'line', 'area'):
            agg = ds.reductions.count_cat(self.group_label)
            categorical = True
        return categorical, agg

    def _process_symmetric(self, symmetric, clim, check_symmetric_max):
        if symmetric is not None or clim is not None:
            return symmetric

        if is_xarray(self.data):
            # chunks mean it's lazily loaded; nanquantile will eagerly load
            data = self.data[self.z]
            if not getattr(data, '_in_memory', True) or data.chunks:
                return False
            if is_xarray_dataarray(data):
                if data.size > check_symmetric_max:
                    return False
            else:
                return False

        elif self._color_dim:
            data = (
                self.data[self._color_dim]
                if self._color_dim in self.data.columns
                else self.data.index.get_level_values(self._color_dim)
            )
        else:
            return

        if data.size == 0:
            return False

        cmin = np.nanquantile(data, 0.05)
        cmax = np.nanquantile(data, 0.95)

        return bool(cmin < 0 and cmax > 0)

    def _process_crs(self, data, crs):
        """Given crs as proj4 string, data.attr, or cartopy.crs return cartopy.crs"""
        if hasattr(data, 'rio') and data.rio.crs is not None:
            # if data is a rioxarray
            _crs = data.rio.crs.to_wkt()
        # get the proj string: either the value of data.attrs[crs] or crs itself
        elif isinstance(crs, str):
            _crs = getattr(data, 'attrs', {}).get(crs or 'crs', crs)
        else:
            _crs = crs

        try:
            return process_crs(_crs)
        except ValueError as e:
            # only raise error if crs was specified in kwargs
            if crs:
                raise ValueError(
                    f"'{crs}' must be either a valid crs or an reference to "
                    f'a `data.attr` containing a valid crs: {e}'
                )

    def _process_data(
        self,
        kind,
        data,
        x,
        y,
        by,
        groupby,
        row,
        col,
        use_dask,
        persist,
        backlog,
        label,
        group_label,
        value_label,
        hover_cols,
        attr_labels,
        transforms,
        stream,
        robust,
        kwds,
    ):
        gridded = kind in self._gridded_types
        gridded_data = False
        da = None

        # Validate DataSource
        self.data_source = data
        self.is_series = is_series(data)
        if self.is_series:
            data = data.to_frame()
        if is_intake(data):
            data = process_intake(data, use_dask or persist)
        # Pandas interface in HoloViews doesn't accept non-string columns.
        # The converter stores a reference to the source data to
        # update the `_dataset` property (of the hv object its __call__ method
        # returns) with a hv Dataset created from the source data, which
        # is done for optimizating some operations in HoloViews.
        data = _convert_col_names_to_str(data)

        self.source_data = data

        if groupby is not None and not isinstance(groupby, list):
            groupby = [groupby]
        if by is not None and not isinstance(by, list):
            by = [by]
        grid = []
        if row is not None:
            grid.append(row)
        if col is not None:
            grid.append(col)
        streaming = False
        if is_geodataframe(data):
            datatype = 'geopandas' if hasattr(data, 'geom_type') else 'spatialpandas'
            self.data = data
            if kind is None:
                if datatype == 'geopandas':
                    geom_types = {gt[5:] if gt and 'Multi' in gt else gt for gt in data.geom_type}
                    if None in geom_types:
                        geom_types.remove(None)
                else:
                    geom_types = [
                        type(data.geometry.dtype)
                        .__name__.replace('Multi', '')
                        .replace('Dtype', '')
                    ]
                if len(geom_types) > 1:
                    raise ValueError(
                        'The GeopandasInterface can only read dataframes which '
                        'share a common geometry type'
                    )
                geom_type = list(geom_types)[0]
                if geom_type == 'Point':
                    kind = 'points'
                elif geom_type == 'Polygon':
                    kind = 'polygons'
                elif geom_type in ('LineString', 'LineRing', 'Line'):
                    kind = 'paths'
            # if only one arg is provided, treat it like color
            if x is not None and y is None:
                kwds['color'] = kwds.pop('color', kwds.pop('c', x))
                x = None
        elif isinstance(data, pd.DataFrame):
            datatype = 'pandas'
            self.data = data
        elif is_dask(data):
            datatype = 'dask'
            self.data = data.persist() if persist else data
        elif is_duckdb(data):
            datatype = 'duckdb'
            self.data = data
        elif is_cudf(data):
            datatype = 'cudf'
            self.data = data
        elif is_ibis(data):
            datatype = 'ibis'
            self.data = data
        elif is_streamz(data):
            datatype = 'streamz'
            self.data = data.example
            if isinstance(self.data, pd.DataFrame):
                self.data = self.data.iloc[:0]
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

            z = kwds.get('z')
            if isinstance(data, xr.Dataset):
                if len(data.data_vars) == 0:
                    raise ValueError('Cannot plot an empty xarray.Dataset object.')
            if z is None:
                if isinstance(data, xr.Dataset):
                    z = list(data.data_vars)[0]
                else:
                    z = data.name or label or value_label
            if gridded and isinstance(data, xr.Dataset) and not isinstance(z, list):
                data = data[z]
            self.z = z

            ignore = (groupby or []) + (by or []) + grid
            coords = [c for c in data.coords if data[c].shape != () and c not in ignore]
            dims = [c for c in data.dims if data[c].shape != () and c not in ignore]

            if kind is None and (not (x or y) or all(c in data.coords for c in (x, y))):
                if list(data.coords) == ['band', 'y', 'x']:
                    kind = 'rgb'
                    gridded = True
                elif len(coords) == 1:
                    kind = 'line'
                elif len(coords) == 2 or (x and y) or len([c for c in coords if c in dims]) == 2:
                    kind = 'image'
                    gridded = True
                else:
                    kind = 'hist'

            datatype = 'dask' if use_dask else 'pandas'
            if gridded:
                datatype = 'xarray'
                gridded_data = True
            if kind == 'rgb':
                if 'bands' in kwds:
                    other_dims = [kwds['bands']]
                else:
                    other_dims = [d for d in data.coords if d not in (groupby or [])][0]
            else:
                other_dims = []
            da = data
            data, x, y, by_new, groupby_new = process_xarray(
                data,
                x,
                y,
                by,
                groupby,
                use_dask,
                persist,
                gridded,
                label,
                value_label,
                other_dims,
                kind=kind,
            )
            if kind == 'rgb' and robust:
                # adapted from xarray
                # https://github.com/pydata/xarray/blob/6af547cdd9beac3b18420ccb204f801603e11519/xarray/plot/utils.py#L729
                vmax = np.nanpercentile(data[z], 100 - 2)
                vmin = np.nanpercentile(data[z], 2)
                # Scale interval [vmin .. vmax] to [0 .. 1], with darray as 64-bit float
                # to avoid precision loss, integer over/underflow, etc with extreme inputs.
                # After scaling, downcast to 32-bit float.  This substantially reduces
                # memory usage
                data[z] = ((data[z].astype('f8') - vmin) / (vmax - vmin)).astype('f4')
                data[z] = np.minimum(np.maximum(data[z], 0), 1)

            if kind not in self._stats_types:
                if by is None:
                    by = by_new
                if groupby is None:
                    groupby = groupby_new

            if groupby:
                groupby = [g for g in groupby if g not in grid]

            # Add a title to hvplot.xarray plots that displays scalar coords values,
            # as done by xarray.plot()
            if not groupby and not grid:
                if isinstance(da, xr.DataArray):
                    self._title = da._title_for_slice()
                elif isinstance(da, xr.Dataset):
                    self._title = partial(xr.DataArray._title_for_slice, da)()

            self.data = data
        else:
            raise ValueError(f'Supplied data type {type(data).__name__} not understood')

        if stream is not None:
            if streaming:
                raise ValueError('Cannot supply streamz.DataFrame and stream argument.')
            self.stream = stream
            self.cb = None
            if isinstance(stream, Pipe):
                self.stream_type = 'updating'
            elif isinstance(stream, Buffer):
                self.stream_type = 'streaming'
            else:
                raise ValueError(f'Stream of type {type(stream)} not recognized.')
            streaming = True

        # Validate data and arguments
        if by is None:
            by = []
        if groupby is None:
            groupby = []

        if gridded_data:
            not_found = [g for g in groupby if g not in data.coords]
            post_not_found, _, _ = process_derived_datetime_xarray(data, not_found)
            data_vars = list(data.data_vars) if isinstance(data, xr.Dataset) else [data.name]
            indexes = list(data.coords.indexes)
            # Handle undeclared indexes
            if x is not None and x not in indexes:
                indexes.append(x)
            if y is not None and y not in indexes:
                indexes.append(y)
            for data_dim in data.dims:
                if not any(data_dim in data[c].dims for c in indexes):
                    for coord in data.coords:
                        if coord not in indexes and {data_dim} == set(data[coord].dims):
                            indexes.append(data_dim)
                            self.data = self.data.set_index({data_dim: coord})
                            if coord not in groupby + by:
                                groupby.append(data_dim)
            self.variables = list(data.coords) + data_vars
            self.variables.extend([item for item in not_found if item not in post_not_found])
            if groupby and post_not_found:
                raise ValueError(
                    f'The supplied groupby dimension(s) {not_found} '
                    'could not be found, expected one or '
                    f'more of: {list(data.coords)}'
                )
        else:
            if gridded and kind not in ('points', 'dataset'):
                raise ValueError(
                    f'{kind} plot type requires gridded data, '
                    'e.g. a NumPy array or xarray Dataset, '
                    f'found {type(self.data).__name__} type'
                )

            if (
                hasattr(data, 'columns')
                and hasattr(data.columns, 'name')
                and data.columns.name
                and not group_label
            ):
                group_label = data.columns.name
            elif not group_label:
                group_label = 'Variable'

            if (
                isinstance(data.columns, pd.MultiIndex)
                and x in (None, 'index')
                and y is None
                and not by
            ):
                # Broken, see https://github.com/holoviz/hvplot/issues/1364.
                # Dask reset_index doesn't accept a level, so this would need to
                # be adapted for Dask.
                self.data = data.stack().reset_index(1).rename(columns={'level_1': group_label})
                by = group_label
                x = 'index'

            # Determine valid indexes
            if isinstance(self.data, pd.DataFrame):
                if self.data.index.names == [None]:
                    indexes = [self.data.index.name or 'index']
                else:
                    indexes = list(self.data.index.names)
            elif hasattr(self.data, 'reset_index'):
                indexes = [
                    c for c in self.data.reset_index().columns if c not in self.data.columns
                ]
            else:
                indexes = [c for c in self.data.columns if c not in self.data.columns]

            if len(indexes) == 2 and not (x or y or by):
                if kind == 'heatmap':
                    x, y = indexes
                elif kind in ('bar', 'barh'):
                    x, by = indexes

            self.variables = indexes + list(self.data.columns)

            # Reset groupby dimensions
            if not support_index(self.data) and any(g for g in groupby if g in indexes):
                self.data = self.data.reset_index()

            if isinstance(by, (np.ndarray, pd.Series)):
                by_cols = []
            else:
                by_cols = by if isinstance(by, list) else [by]
            not_found = [
                g for g in groupby + by_cols if g not in list(self.data.columns) + indexes
            ]
            post_not_found, self.data = process_derived_datetime_pandas(
                self.data, not_found, indexes
            )
            if groupby and post_not_found:
                raise ValueError(
                    f'The supplied groupby dimension(s) {not_found} '
                    'could not be found, expected one or '
                    f'more of: {list(self.data.columns)}'
                )
            self.variables.extend([item for item in not_found if item not in post_not_found])

        if transforms:
            self.data = Dataset(self.data, indexes).transform(**transforms).data

        # Set data-level options
        self.x = x
        self.y = y
        self.kind = kind or 'line'
        self.datatype = datatype
        self.gridded = gridded
        self.gridded_data = gridded_data
        self.use_dask = use_dask
        self.indexes = indexes
        self.group_label = group_label or 'Variable'
        if isinstance(by, (np.ndarray, pd.Series)):
            self.data = self.data.assign(_by=by)
            self.by = ['_by']
            self.variables.append('_by')
        elif not by:
            self.by = []
        else:
            self.by = by if isinstance(by, list) else [by]
        self.groupby = groupby
        self.grid = grid
        self.streaming = streaming

        if not hover_cols:
            self.hover_cols = []
        elif isinstance(hover_cols, list):
            self.hover_cols = hover_cols
        elif hover_cols == 'all' and self.use_index:
            self.hover_cols = self.variables
        elif hover_cols == 'all' and not self.use_index:
            self.hover_cols = [v for v in self.variables if v not in self.indexes]
        elif hover_cols != 'all' and isinstance(hover_cols, str):
            self.hover_cols = [hover_cols]

        if self.datatype in ('geopandas', 'spatialpandas'):
            self.hover_cols = [c for c in self.hover_cols if c != 'geometry']

        if da is not None and attr_labels is True or attr_labels is None:
            try:
                var_tuples = [(var, da[var].attrs) for var in da.coords]
                if isinstance(da, xr.Dataset):
                    var_tuples.extend([(var, da[var].attrs) for var in da.data_vars])
                else:
                    var_tuples.append((da.name, da.attrs))
                labels = {}
                units = {}
                for var_name, var_attrs in var_tuples:
                    if var_name is None:
                        var_name = 'value'
                    if isinstance(var_attrs.get('long_name'), str):
                        labels[var_name] = var_attrs['long_name']
                    if 'units' in var_attrs:
                        units[var_name] = var_attrs['units']
                self._redim = self._merge_redim(labels, 'label')
                self._redim = self._merge_redim(units, 'unit')
            except Exception as e:
                if attr_labels is True:
                    param.main.param.warning(
                        f'Unable to auto label using xarray attrs because {e}'
                    )

    def _process_plot(self):
        kind = self.kind
        options = Store.options(backend='bokeh')
        elname = self._kind_mapping[kind].__name__
        plot_opts = options[elname].groups['plot'].options if elname in options else {}

        if kind.startswith('bar'):
            plot_opts['stacked'] = self.stacked

        if kind == 'hist':
            if self.stacked:
                param.main.param.warning(
                    'Stacking for histograms is not yet implemented in '
                    'holoviews. Use bar plots if stacking is required.'
                )

        return plot_opts

    def _process_style(self, kwds, plot_opts):
        kind = self.kind
        eltype = self._kind_mapping[kind]
        registry = Store.registry[self._backend_compat]

        if eltype in registry:
            valid_opts = registry[eltype].style_opts
        else:
            valid_opts = []

        cmap_opts = ('cmap', 'colormap', 'color_key')
        categorical_cmaps = [
            'accent',
            'category',
            'dark',
            'colorblind',
            'pastel',
            'set1',
            'set2',
            'set3',
            'paired',
            'glasbey',
        ]
        for opt in valid_opts:
            if opt not in kwds or not isinstance(kwds[opt], list) or opt in cmap_opts:
                continue
            kwds[opt] = Cycle(kwds[opt])

        # Process style options
        options = Store.options(backend=self._backend_compat)
        elname = eltype.__name__
        style = options[elname].groups['style'].kwargs if elname in options else {}
        style_opts = {
            k: v for k, v in style.items() if not isinstance(v, Cycle) and k not in cmap_opts
        }
        style_opts.update(**{k: v for k, v in kwds.items() if k in valid_opts})

        # Color
        cmap_kwds = set(cmap_opts).intersection(kwds)
        if len(cmap_kwds) > 1:
            raise TypeError('Specify at most one of `cmap`, `colormap`, or `color_key`.')

        cmap = kwds.pop(cmap_kwds.pop()) if cmap_kwds else None
        color = kwds.pop('color', kwds.pop('c', None))

        if color is not None:
            if (self.datashade or self.rasterize) and color in [self.x, self.y]:
                self.data = self.data.assign(_color=self.data[color])
                style_opts['color'] = color = '_color'
                self.variables.append('_color')
            elif isinstance(color, (np.ndarray, pd.Series)):
                self.data = self.data.assign(_color=color)
                style_opts['color'] = color = '_color'
                self.variables.append('_color')
            else:
                style_opts['color'] = color

            if (
                not isinstance(color, list)
                and color in self.variables
                and 'c' in self._kind_options.get(kind, [])
            ):
                if self.data[color].dtype.kind in 'OSU':
                    cmap = cmap or self._default_cmaps['categorical']
                else:
                    plot_opts['colorbar'] = plot_opts.get('colorbar', True)

        if isinstance(cmap, str) and cmap in self._default_cmaps:
            cmap = self._default_cmaps[cmap]

        if cmap is not None:
            style_opts['cmap'] = cmap

        if 'color' in style_opts:
            color = style_opts['color']
        elif not isinstance(cmap, dict):
            # Checks if any of the categorical cmaps matches cmap;
            # uses any() instead of `cmap in categorical_cmaps` to handle reversed colormaps (suffixed with `_r`).
            # If cmap is LinearSegmentedColormap, get the name attr, else return the str typed cmap.
            if (isinstance(cmap, str) or is_mpl_cmap(cmap)) and any(
                categorical_cmap in getattr(cmap, 'name', cmap)
                for categorical_cmap in categorical_cmaps
            ):
                color = process_cmap(cmap or self._default_cmaps['categorical'], categorical=True)
            else:
                color = cmap
        else:
            color = style_opts.get('color')

        for k, v in style.items():
            if isinstance(v, Cycle) and isinstance(v, str):
                if color == cmap:
                    if color not in Palette.colormaps and color.title() in Palette.colormaps:
                        color = color.title()
                    else:
                        Palette.colormaps[color] = colormap_generator(process_cmap(color))
                    style_opts[k] = Palette(color)
                elif isinstance(color, list):
                    style_opts[k] = Cycle(values=color)
                else:
                    style_opts[k] = color

        # Size
        size = kwds.pop('size', kwds.pop('s', None))
        if size is not None:
            scale = kwds.get('scale', 1)
            if self.datashade or self.rasterize:
                param.main.param.warning(
                    'There is no reasonable way to use size (or s) with '
                    'rasterize or datashade. To aggregate along a third '
                    'dimension, set color (or c) to the desired dimension.'
                )
            if isinstance(size, (np.ndarray, pd.Series)):
                size = np.sqrt(size) * scale
                self.data = self.data.assign(_size=size)
                style_opts['size'] = '_size'
                self.variables.append('_size')
            elif isinstance(size, str):
                style_opts['size'] = np.sqrt(dim(size)) * scale
            elif not isinstance(size, dim):
                style_opts['size'] = np.sqrt(size) * scale
        elif 'size' in valid_opts:
            style_opts['size'] = np.sqrt(30)

        # Marker
        if 'marker' in kwds and 'marker' in self._kind_options[self.kind]:
            style_opts['marker'] = kwds.pop('marker')

        return style_opts, plot_opts, kwds

    def _validate_kwds(self, kwds):
        kind_opts = self._kind_options.get(self.kind, [])
        kind = self.kind
        eltype = self._kind_mapping[kind]
        if eltype in Store.registry[self._backend_compat]:
            valid_opts = Store.registry[self._backend_compat][eltype].style_opts
        else:
            valid_opts = []
        ds_opts = ['max_px', 'threshold']
        mismatches = sorted(k for k in kwds if k not in kind_opts + ds_opts + valid_opts)
        if not mismatches:
            return

        if 'ax' in mismatches:
            mismatches.pop(mismatches.index('ax'))
            param.main.param.warning(
                'hvPlot does not have the concept of axes, '
                'and the ax keyword will be ignored. Compose '
                'plots with the * operator to overlay plots or the '
                '+ operator to lay out plots beside each other '
                'instead.'
            )
        if 'figsize' in mismatches:
            mismatches.pop(mismatches.index('figsize'))
            param.main.param.warning(
                'hvPlot does not have the concept of a figure, '
                'and the figsize keyword will be ignored. The '
                'size of each subplot in a layout is set '
                'individually using the width and height options.'
            )

        combined_opts = (
            self._data_options
            + self._size_layout_options
            + self._axis_config_options
            + self._legend_options
            + self._resample_options
            + self._geo_options
            + kind_opts
            + valid_opts
        )
        # Add the global styling options and interactivity options in the suggestions
        # for only bokeh since they may not be supported by all the backends.
        # See e.g. alpha for Area plots with plotly:
        # https://github.com/holoviz/holoviews/issues/5226
        if self._backend_compat == 'bokeh':
            combined_opts = (
                combined_opts
                + self._color_options
                + self._style_options
                + self._interactivity_options
            )
        for mismatch in mismatches:
            suggestions = difflib.get_close_matches(mismatch, combined_opts)
            param.main.param.warning(
                f'{mismatch} option not found for {self.kind} plot with '
                f'{self._backend_compat}; similar options include: {suggestions}'
            )

    def __call__(self, kind, x, y):
        kind = self.kind or kind
        method = getattr(self, kind)

        groups = self.groupby
        zs = self.kwds.get('z', [])
        if not isinstance(zs, list):
            zs = [zs]
        groups += self.grid
        if self.gridded and not kind == 'points':
            groups += self.by
        if groups or len(zs) > 1:
            if self.streaming:
                raise NotImplementedError('Streaming and groupby not yet implemented')
            data = self.data
            if (
                not support_index(data)
                and not self.gridded
                and any(g in self.indexes for g in groups)
            ):
                data = data.reset_index()

            if self.datatype in ('geopandas', 'spatialpandas'):
                columns = [c for c in data.columns if c != 'geometry']
                shape_dims = ['Longitude', 'Latitude'] if self.geo else ['x', 'y']
                dataset = Dataset(data, kdims=shape_dims + columns)
            elif self.datatype == 'xarray':
                import xarray as xr

                if isinstance(data, xr.Dataset):
                    if kind == 'image':
                        dims_with_coords = set(data.coords.keys())
                        missing_coords = set(self.indexes) - dims_with_coords
                        new_coords = {
                            coord: np.arange(data[coord].shape[0]) for coord in missing_coords
                        }
                        data = data.assign_coords(**new_coords)
                    dataset = Dataset(data, self.indexes)
                else:
                    name = data.name or self.label or self.value_label
                    dataset = Dataset(data, self.indexes, name)
            else:
                dataset = Dataset(data, self.variables)
            dataset = redim_(dataset, **self._redim)

            if groups:
                datasets = dataset.groupby(groups, dynamic=self.dynamic)
                if len(zs) > 1:
                    dimensions = [Dimension(self.group_label, values=zs)] + datasets.kdims
                    if self.dynamic:

                        def z_wrapper(**kwargs):
                            z = kwargs.pop(self.group_label)
                            ds = datasets.select(**kwargs)
                            return ds.reindex(vdims=[ds.get_dimension(z)])

                        obj = DynamicMap(z_wrapper, kdims=dimensions)

                        def method_wrapper(ds, x, y):
                            z = ds.vdims[0].name
                            el = method(x, y, z, data=ds.data)
                            el._transforms = dataset._transforms
                            el._dataset = ds
                            return el

                        obj = obj.apply(
                            method_wrapper, x=x, y=y, per_element=True, link_inputs=False
                        )
                    else:
                        obj = HoloMap(
                            {
                                (z,) + k: method(x, y, z, dataset[k])
                                for k, v in datasets.data.items()
                                for z in zs
                            },
                            kdims=dimensions,
                        )
                else:

                    def method_wrapper(ds, x, y):
                        el = method(x, y, data=ds.data)
                        el._transforms = dataset._transforms
                        el._dataset = ds
                        return el

                    obj = datasets.apply(
                        method_wrapper, x=x, y=y, per_element=True, link_inputs=False
                    )
            elif len(zs) > 1:
                dimensions = [Dimension(self.group_label, values=zs)]
                if self.dynamic:
                    obj = DynamicMap(
                        lambda z: method(x, y, z, data=dataset.data), kdims=dimensions
                    )
                else:
                    obj = HoloMap(
                        {z: method(x, y, z, data=dataset.data) for z in zs}, kdims=dimensions
                    )
            else:
                obj = method(x, y, data=dataset.data)

            if self.gridded and self.by and not kind == 'points':
                obj = obj.layout(self.by) if self.subplots else obj.overlay(self.by)
            if self.grid:
                obj = obj.grid(self.grid).opts(
                    shared_xaxis=True, shared_yaxis=True, backend='bokeh'
                )
        else:
            if self.streaming:
                cb = partial(method, x, y)
                if self.cb is None:
                    cbcallable = cb
                else:
                    cbcallable = StreamingCallable(cb, periodic=self.cb)
                obj = DynamicMap(cbcallable, streams=[self.stream])
            else:
                data = self.source_data
                if self.datatype in ('geopandas', 'spatialpandas'):
                    columns = [c for c in data.columns if c != 'geometry']
                    shape_dims = ['Longitude', 'Latitude'] if self.geo else ['x', 'y']
                    dataset = Dataset(data, kdims=shape_dims + columns)
                elif self.datatype == 'xarray':
                    import xarray as xr

                    if isinstance(data, xr.Dataset):
                        dataset = Dataset(data, self.indexes)
                    else:
                        name = data.name or self.label or self.value_label
                        dataset = Dataset(data, self.indexes, name)
                else:
                    try:
                        dataset = Dataset(data, self.indexes)
                    except Exception:
                        dataset = Dataset(data)
                    dataset = redim_(dataset, **self._redim)

                obj = method(x, y)
                obj._dataset = dataset

        if self.crs and self.project:
            # Apply projection before rasterizing
            import geoviews as gv

            obj = gv.project(obj, projection=self.output_projection)

        if not (self.datashade or self.rasterize or self.downsample):
            layers = self._apply_layers(obj)
            layers = _transfer_opts_cur_backend(layers)
            return layers

        opts = dict(dynamic=self.dynamic)
        if self._plot_opts.get('width') is not None:
            opts['width'] = self._plot_opts['width']
        if self._plot_opts.get('height') is not None:
            opts['height'] = self._plot_opts['height']

        if self.downsample:
            try:
                from holoviews.operation.downsample import downsample1d
            except ImportError:
                raise ImportError('Downsampling requires HoloViews >=1.16')

            # Let HoloViews choose the default algo if 'downsample' is True.
            # Otherwise, user-specified algorithm
            if isinstance(self.downsample, str):
                opts['algorithm'] = self.downsample

            if self.x_sampling:
                opts['x_sampling'] = self.x_sampling
            if self._plot_opts.get('xlim') is not None:
                opts['x_range'] = self._plot_opts['xlim']
            layers = self._resample_obj(downsample1d, obj, opts)
            layers = _transfer_opts_cur_backend(layers)
            return layers

        ds = import_datashader()
        from holoviews.operation.datashader import datashade, rasterize, dynspread

        categorical, agg = self._process_categorical_datashader()
        if agg:
            opts['aggregator'] = agg
        if self.selector:
            selector = self.selector
            try:
                if isinstance(selector, str):
                    selector = getattr(ds, selector)()
                elif isinstance(selector, tuple):
                    selector = getattr(ds, selector[0])(selector[1])
            except AttributeError as e:
                sel = selector[0] if isinstance(selector, tuple) else selector
                msg = f'Invalid selector value {sel!r}.'
                raise ValueError(msg) from e
            opts['selector'] = selector
        if self.precompute:
            opts['precompute'] = self.precompute
        if self.x_sampling:
            opts['x_sampling'] = self.x_sampling
        if self.y_sampling:
            opts['y_sampling'] = self.y_sampling
        if self._plot_opts.get('xlim') is not None:
            opts['x_range'] = self._plot_opts['xlim']
        if self._plot_opts.get('ylim') is not None:
            opts['y_range'] = self._plot_opts['ylim']

        if 'cmap' in self._style_opts and self.datashade:
            levels = self._plot_opts.get('color_levels')
            cmap = self._style_opts['cmap']
            if isinstance(cmap, dict):
                opts['color_key'] = cmap
            else:
                opts['cmap'] = process_cmap(cmap, levels, categorical=categorical)

        if 'line_width' in self._style_opts:
            opts['line_width'] = self._style_opts['line_width']

        style = {}

        if self.datashade:
            operation = datashade
            if 'cmap' in opts and 'color_key' not in opts:
                opts['color_key'] = opts['cmap']
            eltype = 'RGB'
            if 'cnorm' in self._plot_opts:
                opts['cnorm'] = self._plot_opts['cnorm']
            if 'rescale_discrete_levels' in self._plot_opts:
                opts['rescale_discrete_levels'] = self._plot_opts['rescale_discrete_levels']
            if self.pixel_ratio:
                opts['pixel_ratio'] = self.pixel_ratio
        elif self.rasterize:
            operation = rasterize
            eltype = 'ImageStack' if categorical else 'Image'
            if 'cmap' in self._style_opts:
                style['cmap'] = self._style_opts['cmap']
            if self._dim_ranges.get('c', (None, None)) != (None, None):
                style['clim'] = self._dim_ranges['c']
            if self.pixel_ratio:
                opts['pixel_ratio'] = self.pixel_ratio

        processed = self._resample_obj(operation, obj, opts)
        if self.dynspread:
            processed = dynspread(
                processed,
                max_px=self.kwds.get('max_px', 3),
                threshold=self.kwds.get('threshold', 0.5),
            )

        opts = filter_opts(eltype, dict(self._plot_opts, **style), backend='bokeh')
        layers = self._apply_layers(processed).opts(eltype, **opts, backend='bokeh')
        layers = _transfer_opts_cur_backend(layers)
        return layers

    def _resample_obj(self, operation, obj, opts):
        def exceeds_resample_when(plot):
            return len(plot) > self.resample_when

        if self.resample_when is not None:
            processed = apply_when(
                obj, operation=partial(operation, **opts), predicate=exceeds_resample_when
            )
        else:
            processed = operation(obj, **opts)
        return processed

    def _get_opts(self, eltype, backend='bokeh', **custom):
        opts = dict(self._plot_opts, **dict(self._style_opts, **self._norm_opts))
        opts.update(custom)
        return filter_opts(eltype, opts, backend=backend)

    def _apply_layers(self, obj):
        if self.coastline:
            import geoviews as gv

            coastline = gv.feature.coastline.clone()
            if self.coastline in ['10m', '50m', '110m']:
                coastline = coastline.opts(scale=self.coastline)
            elif self.coastline is not True:
                param.main.param.warning(
                    'coastline scale of {self.coastline} not recognized, must be one '
                    "'10m', '50m' or '110m'."
                )
            obj = obj * coastline.opts(projection=self.output_projection)

        if self.features:
            import geoviews as gv

            for feature in reversed(self.features):
                feature_obj = getattr(gv.feature, feature)
                if feature_obj is None:
                    raise ValueError(
                        f'Feature {feature!r} was not recognized, must be one of '
                        "'borders', 'coastline', 'lakes', 'land', 'ocean', "
                        "'rivers' and 'states'."
                    )
                feature_obj = feature_obj.clone()
                if isinstance(self.features, dict):
                    scale = self.features[feature]
                    if scale not in ['10m', '50m', '110m']:
                        param.main.param.warning(
                            f'Feature scale of {scale} not recognized, '
                            "must be one of '10m', '50m' or '110m'."
                        )
                    else:
                        feature_obj = feature_obj.opts(scale=scale)
                if feature_obj.group in ['Land', 'Ocean']:
                    # Underlay land/ocean
                    obj = feature_obj.opts(projection=self.output_projection) * obj
                else:
                    # overlay everything else
                    obj = obj * feature_obj.opts(projection=self.output_projection)

        if self.tiles:
            if not self.geo:
                tiles = self._get_tiles(self.tiles)
            else:
                tiles = self._get_tiles(self.tiles, lib='geoviews')
            tiles = tiles.opts(clone=True, **self.tiles_opts)
            obj = tiles * obj
        return obj

    def _get_tiles(self, source, lib='holoviews'):
        if lib == 'geoviews':
            import geoviews as gv

            sources = gv.tile_sources.tile_sources
            kls = gv.element.WMTS
            types = (kls, hv.element.tiles.Tiles)
        else:
            sources = hv.element.tile_sources
            kls = hv.element.tiles.Tiles
            types = kls

        tile_source = 'EsriImagery' if source == 'ESRI' else source
        tiles = None
        if tile_source is True:
            tiles = sources['OSM']()
        elif isinstance(tile_source, str) and tile_source in sources:
            tiles = sources[tile_source]()
        elif tile_source in sources.values():
            tiles = tile_source()
        elif isinstance(tile_source, types):
            tiles = tile_source
        elif 'xyzservices' in sys.modules:
            import xyzservices

            if isinstance(tile_source, xyzservices.TileProvider):
                tiles = kls(tile_source)
        if tiles is None:
            msg = (
                f'{tile_source} tiles not recognized. tiles must be either True, a '
                'xyzservices.TileProvider instance, a HoloViews'
                + (' or Geoviews' if lib == 'geoviews' else '')
                + ' basemap string '
                f'(one of {", ".join(sorted(sources))}), a HoloViews Tiles instance'
                + (', a Geoviews WMTS instance' if lib == 'geoviews' else '')
                + '.'
            )
            raise ValueError(msg)
        return tiles

    def _merge_redim(self, ranges, attr='range'):
        redim = dict(self._redim)
        for k, r in ranges.items():
            replace = {attr: r}
            if k in redim:
                dim = redim[k]
                if isinstance(dim, Dimension):
                    dim = dim.clone(**replace)
                elif isinstance(dim, dict) and 'range' not in dim:
                    dim = dict(dim, **replace)
                elif isinstance(dim, (tuple, str)):
                    dim = Dimension(dim, **replace)
            else:
                dim = replace
            redim[k] = dim
        return redim

    def _validate_dim(self, dimension):
        if isinstance(dimension, dim):
            dimension = dimension.dimension.name
        if isinstance(dimension, str) and dimension in self.variables:
            return dimension

    @property
    def _color_dim(self):
        return self._validate_dim(self._style_opts.get('color'))

    def _get_dimensions(self, kdims, vdims):
        for style in ('color', 'size', 'marker', 'alpha'):
            dimension = self._style_opts.get(style)
            dimensions = (kdims if kdims else []) + vdims
            dimension = self._validate_dim(dimension)
            if dimension is None:
                continue
            elif dimension not in dimensions:
                vdims.append(dimension)
                dimensions.append(dimension)
        agg_col = getattr(self.aggregator, 'column', None)
        if agg_col is not None:
            if agg_col not in dimensions:
                vdims.append(agg_col)
                dimensions.append(agg_col)
        for dimension in self.hover_cols:
            if (
                isinstance(dimension, str)
                and dimension in self.variables
                and dimension not in dimensions
            ):
                vdims.append(dimension)
        return kdims, vdims

    def _set_backends_opts(self, element, cur_opts, compat_opts):
        # Bokeh is still the main backend
        element = element.opts(**cur_opts, backend='bokeh')
        if compat_opts:
            element = element.opts(**compat_opts, backend=self._backend_compat)
        return element

    def _get_compat_opts(self, el_name, **custom):
        # Bokeh is still the main backend
        cur_opts = self._get_opts(el_name, backend='bokeh', **custom)
        if self._backend_compat != 'bokeh':
            # Don't pass custom opts to the compatibility layer
            compat_opts = self._get_opts(el_name, backend=self._backend_compat)
            compat_opts = {k: v for k, v in compat_opts.items() if k not in cur_opts}
        else:
            compat_opts = {}
        return cur_opts, compat_opts

    def _error_if_unavailable(self, kind, element=None):
        """
        Raise an error if the element is not available with the current backend.
        """
        if not element:
            element = self._kind_mapping[kind]
        if element not in Store.registry[self._backend]:
            raise NotImplementedError(
                f'{kind!r} plot not supported by the {self._backend!r} backend.'
            )

    ##########################
    #     Simple charts      #
    ##########################

    def single_chart(self, element, x, y, data=None):
        labelled = ['y' if self.invert else 'x'] if x != 'index' else []
        if not self.is_series:
            labelled.append('x' if self.invert else 'y')
        elif not self.label:
            self._relabel['label'] = y

        if 'xlabel' in self._plot_opts and 'x' not in labelled:
            labelled.append('x')
        if 'ylabel' in self._plot_opts and 'y' not in labelled:
            labelled.append('y')

        cur_el_opts = self._get_opts(element.name, labelled=labelled, backend='bokeh')
        compat_el_opts = self._get_opts(
            element.name, labelled=labelled, backend=self._backend_compat
        )
        for opts_ in [cur_el_opts, compat_el_opts]:
            if 'color' in opts_ and opts_['color'] in data.columns:
                opts_['color'] = hv.dim(opts_['color'])
        cur_opts = {
            element.name: cur_el_opts,
            'NdOverlay': filter_opts(
                'NdOverlay', dict(self._overlay_opts, batched=False), backend='bokeh'
            ),
        }
        compat_opts = {
            element.name: compat_el_opts,
            'NdOverlay': filter_opts(
                'NdOverlay', dict(self._overlay_opts), backend=self._backend_compat
            ),
        }

        ys = [y]
        if element is Area and self.kwds.get('y2'):
            ys += [self.kwds['y2']]
        if element is ErrorBars and self.kwds.get('yerr1') and self.kwds.get('yerr2'):
            ys += [self.kwds['yerr1'], self.kwds['yerr2']]
        elif element is ErrorBars and self.kwds.get('yerr1'):
            ys += [self.kwds['yerr1']]
        kdims, vdims = self._get_dimensions([x], ys)

        if self.by:
            if element is Bars and not self.subplots:
                if not support_index(data) and any(y in self.indexes for y in ys):
                    data = data.reset_index()
                return (
                    relabel_redim(
                        element(data, ([x] if x else []) + self.by, ys), self._relabel, self._redim
                    )
                    .opts(cur_opts, backend='bokeh')
                    .opts(compat_opts, backend=self._backend_compat)
                )
            chart = relabel(
                Dataset(data, self.by + kdims, vdims).to(element, kdims, vdims, self.by),
                **self._relabel,
            )
            chart = chart.layout() if self.subplots else chart.overlay(sort=False)
        else:
            chart = relabel(element(data, kdims, vdims), **self._relabel)
        return (
            redim_(chart, **self._redim)
            .opts(cur_opts, backend='bokeh')
            .opts(compat_opts, backend=self._backend_compat)
        )

    def _process_chart_x(self, data, x, y, single_y, categories=None):
        """This should happen before _process_chart_y"""
        if x is False:
            return None

        x = x or (self.x if self.x != y else None)
        if x is None:
            if self.use_index:
                xs = self.indexes
            else:
                xs = list(data.columns)
            xs = [c for c in xs if c not in self.by + self.groupby + self.grid + [y]]
            x = xs[0] if len(xs) else None

        if not x and not categories:
            raise ValueError('Could not determine what to plot. Set x explicitly')
        return x

    def _process_chart_y(self, data, x, y, single_y):
        """This should happen after _process_chart_x"""
        y = y or self.y
        if y is None:
            ys = [c for c in data.columns if c not in [x] + self.by + self.groupby + self.grid]
            if len(ys) > 1:
                # if columns have different dtypes, only include numeric columns
                from pandas.api.types import is_numeric_dtype as isnum

                num_ys = [dim for dim in ys if isnum(data[dim])]
                if len(num_ys) >= 1:
                    ys = num_ys
            y = ys[0] if len(ys) == 1 or single_y else ys
        return y

    def _process_chart_args(self, data, x, y, single_y=False, categories=None):
        if data is None:
            data = self.data
        elif not self.gridded_data:
            data = _convert_col_names_to_str(data)

        x = self._process_chart_x(data, x, y, single_y, categories=categories)
        y = self._process_chart_y(data, x, y, single_y)

        # sort by date if enabled and x is a date
        if x is not None and self.sort_date and self.datatype == 'pandas':
            from pandas.api.types import is_datetime64_any_dtype as is_datetime

            if x in self.indexes:
                if isinstance(data.index, MultiIndex):
                    idx_vals = data.index.get_level_values(x)
                    sort_kwargs = {'level': x}
                else:
                    idx_vals = data.index
                    sort_kwargs = {}
                if is_datetime(idx_vals):
                    data = data.sort_index(**sort_kwargs)
            elif x in data.columns and is_datetime(data[x]):
                data = data.sort_values(x)

        # set index to column if needed in hover_cols
        if (
            not support_index(data)
            and self.use_index
            and any(c for c in self.hover_cols if c in self.indexes and c not in data.columns)
        ):
            data = data.reset_index()

        # calculate any derived time
        dimensions = []
        for col in [x, y, self.by, self.hover_cols]:
            if col is not None:
                dimensions.extend(col if isinstance(col, list) else [col])

        not_found = [dim for dim in dimensions if dim not in self.variables]
        post_not_found, data = process_derived_datetime_pandas(data, not_found, self.indexes)
        self.variables.extend(set(post_not_found) - set(not_found))

        data, x, y = self._process_tiles_without_geo(data, x, y)
        return data, x, y

    def _process_tiles_without_geo(self, data, x, y):
        """
        Tiles without requiring geoviews/cartopy.
        """
        if self.geo or not self.tiles or self.output_projection is False:
            return data, x, y
        elif not is_geodataframe(data) and (x is None or y is None):
            return data, x, y

        if is_lazy_data(data):
            # To prevent eager evaluation: https://github.com/holoviz/hvplot/pull/1432
            pass
        elif is_geodataframe(data):
            if getattr(data, 'crs', None) is not None:
                data = data.to_crs(epsg=3857)
        else:
            min_x = np.min(data[x])
            max_x = np.max(data[x])
            min_y = np.min(data[y])
            max_y = np.max(data[y])

            x_within_bounds = -180 <= min_x <= 360 and -180 <= max_x <= 360
            y_within_bounds = -90 <= min_y <= 90 and -90 <= max_y <= 90
            if x_within_bounds and y_within_bounds:
                data = data.copy()
                lons_180 = (data[x] + 180) % 360 - 180  # ticks are better with -180 to 180
                easting, northing = lon_lat_to_easting_northing(lons_180, data[y])
                new_x = 'x' if 'x' not in data else 'x_'  # quick existing var check
                new_y = 'y' if 'y' not in data else 'y_'
                data[new_x] = easting
                data[new_y] = northing
                if is_xarray(data):
                    data = data.swap_dims({x: new_x, y: new_y})
                x = new_x
                y = new_y
        return data, x, y

    def chart(self, element, x, y, data=None):
        "Helper method for simple x vs. y charts"
        data, x, y = self._process_chart_args(data, x, y)
        if x and y and not isinstance(y, (list, tuple)):
            return self.single_chart(element, x, y, data)
        elif x and y and len(y) == 1:
            return self.single_chart(element, x, y[0], data)

        labelled = ['y' if self.invert else 'x'] if x != 'index' else []
        if self.value_label != 'value':
            labelled.append('x' if self.invert else 'y')

        if 'xlabel' in self._plot_opts and 'x' not in labelled:
            labelled.append('x')
        if 'ylabel' in self._plot_opts and 'y' not in labelled:
            labelled.append('y')

        cur_opts = {
            element.name: self._get_opts(element.name, labelled=labelled, backend='bokeh'),
            'NdOverlay': filter_opts(
                'NdOverlay', dict(self._overlay_opts, batched=False), backend='bokeh'
            ),
        }
        compat_opts = {
            element.name: self._get_opts(
                element.name, labelled=labelled, backend=self._backend_compat
            ),
            'NdOverlay': filter_opts(
                'NdOverlay', dict(self._overlay_opts), backend=self._backend_compat
            ),
        }

        charts = []
        for c in y:
            ydim = hv.Dimension(c, label=self.value_label)
            kdims, vdims = self._get_dimensions([x], [ydim])
            chart = element(data, kdims, vdims)
            chart = relabel_redim(chart, self._relabel, self._redim)
            charts.append((c, chart))
        return (
            self._by_type(charts, self.group_label, sort=False)
            .opts(cur_opts, backend='bokeh')
            .opts(compat_opts, backend=self._backend_compat)
        )

    def line(self, x=None, y=None, data=None):
        self._error_if_unavailable('line')
        return self.chart(Curve, x, y, data)

    def step(self, x=None, y=None, data=None):
        where = self.kwds.get('where', 'mid')
        return self.line(x, y, data).options('Curve', interpolation='steps-' + where)

    def scatter(self, x=None, y=None, data=None):
        self._error_if_unavailable('scatter')
        return self.chart(Scatter, x, y, data)

    def area(self, x=None, y=None, data=None):
        self._error_if_unavailable('area')
        areas = self.chart(Area, x, y, data)
        if self.stacked:
            areas = areas.map(Area.stack, NdOverlay)
        return areas

    def errorbars(self, x=None, y=None, data=None):
        self._error_if_unavailable('errorbars')
        return self.chart(ErrorBars, x, y, data)

    ##########################
    #  Categorical charts    #
    ##########################

    def _category_plot(self, element, x: str, y: list[str], data):
        """
        Helper method to generate element from indexed dataframe.
        """
        labelled = ['y' if self.invert else 'x'] if x != 'index' else []
        if self.value_label != 'value':
            labelled.append('x' if self.invert else 'y')

        if 'xlabel' in self._plot_opts and 'x' not in labelled:
            labelled.append('x')
        if 'ylabel' in self._plot_opts and 'y' not in labelled:
            labelled.append('y')

        cur_opts, compat_opts = self._get_compat_opts(element.name, labelled=labelled)

        id_vars = [x]
        if any(v in self.indexes for v in id_vars):
            # Calling reset_index() is required since id_vars from melt
            # only accepts column names, not index names.
            data = data.reset_index()
        data = data[y + [x]]

        if check_library(data, 'dask'):
            from dask.dataframe import melt
        else:
            melt = pd.melt

        df = melt(data, id_vars=[x], var_name=self.group_label, value_name=self.value_label)
        kdims = [x, self.group_label]
        vdims = [self.value_label] + self.hover_cols
        if self.subplots:
            obj = Dataset(df, kdims, vdims).to(element, x).layout()
        else:
            obj = element(df, kdims, vdims)
        return relabel_redim(obj, self._relabel, self._redim).apply(
            self._set_backends_opts, cur_opts=cur_opts, compat_opts=compat_opts
        )

    def bar(self, x=None, y=None, data=None):
        self._error_if_unavailable('bar')
        data, x, y = self._process_chart_args(data, x, y, categories=self.by)
        if (x or self.by) and y and (self.by or not isinstance(y, (list, tuple) or len(y) == 1)):
            y = y[0] if isinstance(y, (list, tuple)) else y
            return self.single_chart(Bars, x, y, data)
        return self._category_plot(Bars, x, list(y), data)

    def barh(self, x=None, y=None, data=None):
        return self.bar(x, y, data).opts('Bars', invert_axes=True)

    ##########################
    #   Statistical charts   #
    ##########################

    def _stats_plot(self, element, y, data=None):
        """
        Helper method to generate element from indexed dataframe.
        """
        data, x, y = self._process_chart_args(data, False, y)

        custom = {}
        if 'color' in self._style_opts:
            prefix = 'violin' if issubclass(element, Violin) else 'box'
            custom[prefix + '_fill_color'] = self._style_opts['color']
        cur_opts, compat_opts = self._get_compat_opts(element.name, **custom)
        ylim = self._plot_opts.get('ylim', (None, None))
        if not isinstance(y, (list, tuple)):
            ranges = {y: ylim}
            return relabel(
                element(data, self.by, y).redim.range(**ranges),
                **self._relabel,
            ).apply(self._set_backends_opts, cur_opts=cur_opts, compat_opts=compat_opts)

        labelled = ['y' if self.invert else 'x'] if self.group_label != 'Group' else []
        if self.value_label != 'value':
            labelled.append('x' if self.invert else 'y')

        if 'xlabel' in self._plot_opts and 'x' not in labelled:
            labelled.append('x')
        if 'ylabel' in self._plot_opts and 'y' not in labelled:
            labelled.append('y')

        cur_opts['labelled'] = labelled

        kdims = [self.group_label]
        data = data[list(y)]
        if check_library(data, 'dask'):
            from dask.dataframe import melt
        else:
            melt = pd.melt
        df = melt(data, var_name=self.group_label, value_name=self.value_label)
        if list(y) and df[self.value_label].dtype is not data[y[0]].dtype:
            df[self.value_label] = df[self.value_label].astype(data[y[0]].dtype)
        redim = self._merge_redim({self.value_label: ylim})
        return relabel_redim(
            element(df, kdims, self.value_label),
            self._relabel,
            redim,
        ).apply(self._set_backends_opts, cur_opts=cur_opts, compat_opts=compat_opts)

    def box(self, x=None, y=None, data=None):
        self._error_if_unavailable('box')
        return redim_(self._stats_plot(BoxWhisker, y, data), **self._redim)

    def violin(self, x=None, y=None, data=None):
        self._error_if_unavailable('violin')
        try:
            from holoviews.element import Violin
        except ImportError:
            raise ImportError('Violin plot requires HoloViews version >=1.10')
        return redim_(self._stats_plot(Violin, y, data), **self._redim)

    def hist(self, x=None, y=None, data=None):
        self._error_if_unavailable('hist')
        data, x, y = self._process_chart_args(data, False, y)

        labelled = ['y'] if self.invert else ['x']

        if 'xlabel' in self._plot_opts and 'x' not in labelled:
            labelled.append('x')
        if 'ylabel' in self._plot_opts and 'y' not in labelled:
            labelled.append('y')

        cur_opts = {
            'Histogram': self._get_opts('Histogram', labelled=labelled, backend='bokeh'),
            'NdOverlay': filter_opts('NdOverlay', self._overlay_opts, backend='bokeh'),
        }
        compat_opts = {
            'Histogram': self._get_opts('Histogram', backend=self._backend_compat),
            'NdOverlay': filter_opts(
                'NdOverlay', self._overlay_opts, backend=self._backend_compat
            ),
        }
        hist_opts = {
            'bin_range': self.kwds.get('bin_range', None),
            'normed': self.kwds.get('normed', False),
            'cumulative': self.kwds.get('cumulative', False),
            'log': self._plot_opts.get('logx', False),
        }
        if 'bins' in self.kwds:
            bins = self.kwds['bins']
            if isinstance(bins, int):
                hist_opts['num_bins'] = bins
            else:
                hist_opts['bins'] = bins

        if not isinstance(y, (list, tuple)):
            if hist_opts['bin_range'] is None:
                ys = data[y]
                ymin, ymax = (ys.min(), ys.max())
                if is_dask(ys):
                    ymin, ymax = ymin.compute(), ymax.compute()
                elif is_ibis(ys):
                    ymin, ymax = ymin.execute(), ymax.execute()
                hist_opts['bin_range'] = ymin, ymax

            ds = Dataset(data, self.by)
            if self.by:
                hist = hists = histogram(ds.groupby(self.by), dimension=y, **hist_opts)
                hist = hists.last
                hists = hists.layout() if self.subplots else hists.overlay(sort=False)
            else:
                hists = histogram(ds, dimension=y, **hist_opts)

            return (
                redim_(hists, **self._redim)
                .opts(cur_opts, backend='bokeh')
                .opts(compat_opts, backend=self._backend_compat)
            )

        if hist_opts['bin_range'] is None and not self._norm_opts.get('axiswise'):
            ranges = []
            for col in y:
                ys = data[col]
                ymin, ymax = (ys.min(), ys.max())
                if is_dask(ys):
                    ymin, ymax = ymin.compute(), ymax.compute()
                elif is_ibis(ys):
                    ymin, ymax = ymin.execute(), ymax.execute()
                ranges.append((ymin, ymax))
            if ranges:
                hist_opts['bin_range'] = max_range(ranges)

        ds = Dataset(data)
        hists = []
        for col in y:
            hist = histogram(ds, dimension=col, **hist_opts)
            hists.append((col, relabel(hist, **self._relabel)))
        return (
            redim_(
                self._by_type(hists, self.group_label, sort=False),
                **self._redim,
            )
            .opts(cur_opts, backend='bokeh')
            .opts(compat_opts, backend=self._backend_compat)
        )

    def kde(self, x=None, y=None, data=None):
        self._error_if_unavailable('kde')
        bw_method = self.kwds.pop('bw_method', None)
        ind = self.kwds.pop('ind', None)
        if bw_method is not None or ind is not None:
            raise ValueError('hvplot does not support bw_method and ind')

        dist_opts = dict(self.kwds)
        data, x, y = self._process_chart_args(data, x, y)
        cur_opts = {
            'Distribution': self._get_opts('Distribution', backend='bokeh', **dist_opts),
            'Area': self._get_opts('Distribution', backend='bokeh'),
            'NdOverlay': filter_opts(
                'NdOverlay', dict(self._overlay_opts, legend_limit=0), backend='bokeh'
            ),
        }
        compat_opts = {
            'Distribution': self._get_opts(
                'Distribution', backend=self._backend_compat, **dist_opts
            ),
            'Area': self._get_opts('Distribution', backend=self._backend_compat),
            'NdOverlay': filter_opts(
                'NdOverlay', self._overlay_opts, backend=self._backend_compat
            ),
        }

        xlim = self._plot_opts.get('xlim', (None, None))
        if not isinstance(y, (list, tuple)):
            ranges = {y: xlim}
            if self.by:
                dists = Dataset(data).to(Distribution, y, [], self.by)
                dists = dists.layout() if self.subplots else dists.overlay(sort=False)
            else:
                dists = Distribution(data, y, [])
        else:
            ranges = {self.value_label: xlim}
            data = data[y]
            df = data.melt(var_name=self.group_label, value_name=self.value_label)
            ds = Dataset(df)
            if len(df):
                dists = ds.to(Distribution, self.value_label)
                dists = dists.layout() if self.subplots else dists.overlay(sort=False)
            else:
                vdim = self.value_label + ' Density'
                dists = NdOverlay({0: Area([], self.value_label, vdim)}, [self.group_label])
        redim = self._merge_redim(ranges)
        return (
            relabel_redim(dists, self._relabel, redim)
            .opts(cur_opts, backend='bokeh')
            .opts(compat_opts, backend=self._backend_compat)
        )

    def density(self, x=None, y=None, data=None):
        return self.kde(x, y, data)

    ##########################
    #      Other charts      #
    ##########################

    def dataset(self, x=None, y=None, data=None):
        data = self.data if data is None else data
        if self.gridded:
            kdims = [self.x, self.y] if len(self.indexes) == 2 else None
            return redim_(Dataset(data, kdims=kdims), **self._redim)
        else:
            return redim_(Dataset(data, self.kwds.get('columns')), **self._redim)

    def heatmap(self, x=None, y=None, data=None):
        self._error_if_unavailable('heatmap')
        data = self.data if data is None else data
        cur_opts, compat_opts = self._get_compat_opts('HeatMap')

        if not (x or y) or (x == 'columns' and y in ('index', data.index.name)):
            cur_opts['labelled'] = []
            x, y = 'columns', 'index'
            data = (data.columns, data.index, data.values)
            z = ['value']
        else:
            z = self.kwds.get('C', [c for c in data.columns if c not in (x, y)][0])
            z = [z] + self.hover_cols
            self.use_index = False
            data, x, y = self._process_chart_args(data, x, y, single_y=True)

        redim = self._merge_redim({z[0]: self._dim_ranges['c']})
        hmap = HeatMap(data, [x, y], z, **self._relabel)
        if 'reduce_function' in self.kwds:
            hmap = hmap.aggregate(function=self.kwds['reduce_function'])
        return redim_(hmap, **redim).apply(
            self._set_backends_opts, cur_opts=cur_opts, compat_opts=compat_opts
        )

    def hexbin(self, x=None, y=None, data=None):
        self._error_if_unavailable('hexbin')
        self.use_index = False
        data, x, y = self._process_chart_args(data, x, y, single_y=True)

        z = [self.kwds['C']] if self.kwds.get('C') else []
        z += self.hover_cols

        cur_opts, compat_opts = self._get_compat_opts('HexTiles')
        if 'reduce_function' in self.kwds:
            cur_opts['aggregator'] = self.kwds['reduce_function']
        if 'gridsize' in self.kwds:
            cur_opts['gridsize'] = self.kwds['gridsize']
        if 'min_count' in self.kwds:
            cur_opts['min_count'] = self.kwds['min_count']
        redim = self._merge_redim({(z[0] if z else 'Count'): self._dim_ranges['c']})
        element = self._get_element('hexbin')
        params = dict(self._relabel)
        if self.geo:
            params['crs'] = self.crs
        return redim_(element(data, [x, y], z or [], **params), **redim).apply(
            self._set_backends_opts, cur_opts=cur_opts, compat_opts=compat_opts
        )

    def bivariate(self, x=None, y=None, data=None):
        self._error_if_unavailable('bivariate')
        self.use_index = False
        data, x, y = self._process_chart_args(data, x, y, single_y=True)

        cur_opts, compat_opts = self._get_compat_opts('Bivariate', **self.kwds)
        element = self._get_element('bivariate')
        return redim_(element(data, [x, y]), **self._redim).apply(
            self._set_backends_opts, cur_opts=cur_opts, compat_opts=compat_opts
        )

    def ohlc(self, x=None, y=None, data=None):
        self._error_if_unavailable('ohlc', Rectangles)
        self._error_if_unavailable('ohlc', Segments)
        data = self.data if data is None else data
        if x is None:
            variables = [var for var in self.variables if var not in self.indexes]
            if data[variables[0]].dtype.kind == 'M':
                x = variables[0]
            else:
                x = self.indexes[0]
        width = self.kwds.get('bar_width', 0.5)
        if y is None:
            o, h, l, c = [col for col in data.columns if col != x][:4]  # noqa: E741
        else:
            o, h, l, c = y  # noqa: E741
        neg, pos = self.kwds.get('neg_color', 'red'), self.kwds.get('pos_color', 'green')
        color_exp = (dim(o) > dim(c)).categorize({True: neg, False: pos})
        ohlc_cols = [o, h, l, c]
        if x in self.hover_cols:
            self.hover_cols.remove(x)
        vdims = list(dict.fromkeys(ohlc_cols + self.hover_cols))
        ds = Dataset(data, [x], vdims)
        if ds.dimension_values(x).dtype.kind in 'SUO':
            rects = Rectangles(ds, [x, o, x, c])
        else:
            if len(ds):
                sampling = np.min(np.diff(ds[x])) * width / 2.0
                ds = ds.transform(lbound=dim(x) - sampling, ubound=dim(x) + sampling)
            else:
                ds = ds.transform(lbound=dim(x), ubound=dim(x))
            rects = Rectangles(ds, ['lbound', o, 'ubound', c])
        segments = Segments(ds, [x, l, x, h])
        rect_cur_opts, rect_compat_opts = self._get_compat_opts('Rectangles')
        rect_cur_opts.pop('tools')
        rect_cur_opts['color'] = color_exp
        seg_cur_opts, seg_compat_opts = self._get_compat_opts('Segments')
        tools = seg_cur_opts.pop('tools', [])
        if 'hover' in tools:
            x_data = data[x] if x in data.columns else data.index
            if pd.api.types.is_datetime64_any_dtype(x_data):
                # %F %T: strftime code for %Y-%m-%d %H:%M:%S.
                # See https://man7.org/linux/man-pages/man3/strftime.3.html
                x_tooltip = f'@{x}{{%F %T}}'
                formatter = {f'@{x}': 'datetime'}
            else:
                x_tooltip = f'@{x}'
                formatter = {}
            tools[tools.index('hover')] = HoverTool(
                formatters=formatter,
                tooltips=[
                    (x, x_tooltip),
                    ('Open', f'@{o}'),
                    ('High', f'@{h}'),
                    ('Low', f'@{l}'),
                    ('Close', f'@{c}'),
                ]
                + [(hc, f'@{hc}') for hc in vdims[4:]],
            )
        seg_cur_opts['tools'] = tools
        seg_cur_opts['color'] = self.kwds.get('line_color', 'black')
        if 'xlabel' not in seg_cur_opts:
            seg_cur_opts['xlabel'] = '' if x == 'index' else x
        if 'ylabel' not in seg_cur_opts:
            seg_cur_opts['ylabel'] = ''
        segments = redim_(segments, **self._redim).apply(
            self._set_backends_opts, cur_opts=seg_cur_opts, compat_opts=seg_compat_opts
        )
        rects = redim_(rects, **self._redim).apply(
            self._set_backends_opts, cur_opts=rect_cur_opts, compat_opts=rect_compat_opts
        )
        return segments * rects

    def table(self, x=None, y=None, data=None):
        self._error_if_unavailable('table')
        data = self.data if data is None else data
        if isinstance(data.index, (DatetimeIndex, MultiIndex)):
            # To get the index displayed in the table as Bokeh doesn't show it.
            data = data.reset_index()

        cur_opts, compat_opts = self._get_compat_opts('Table')
        element = self._get_element('table')
        return redim_(
            element(data, self.kwds.get('columns'), []),
            **self._redim,
        ).apply(self._set_backends_opts, cur_opts=cur_opts, compat_opts=compat_opts)

    def labels(self, x=None, y=None, data=None):
        self._error_if_unavailable('labels')
        self.use_index = False
        data, x, y = self._process_chart_args(data, x, y, single_y=True)

        text = self.kwds.get('text')
        if not text:
            text = [c for c in data.columns if c not in (x, y)][0]
        elif text not in data.columns:
            data = data.copy()
            template_str = text  # needed for dask lazy compute
            data['label'] = data.apply(lambda row: template_str.format(**row), axis=1)
            text = 'label'

        kdims, vdims = self._get_dimensions([x, y], [text])
        cur_opts, compat_opts = self._get_compat_opts('Labels')
        element = self._get_element('labels')
        if self.by:
            labels = Dataset(data).to(element, kdims, vdims, self.by)
            labels = labels.layout() if self.subplots else labels.overlay(sort=False)
        else:
            labels = element(data, kdims, vdims)
        return redim_(labels, **self._redim).apply(
            self._set_backends_opts, cur_opts=cur_opts, compat_opts=compat_opts
        )

    ##########################
    #     Gridded plots      #
    ##########################

    def _process_gridded_args(self, data, x, y, z):
        data = self.data if data is None else data
        x = x or self.x
        y = y or self.y
        z = z or self.kwds.get('z')

        if is_xarray(data):
            import xarray as xr

            if isinstance(data, xr.DataArray):
                data = data.to_dataset(name=data.name or 'value')
        if is_tabular(data):
            if (
                not support_index(data)
                and self.use_index
                and any(c for c in self.hover_cols if c in self.indexes and c not in data.columns)
            ):
                data = data.reset_index()
            # calculate any derived time
            dimensions = []
            for dimension in [x, y, self.by, self.hover_cols]:
                if dimension is not None:
                    dimensions.extend(dimension if isinstance(dimension, list) else [dimension])

            not_found = [dim for dim in dimensions if dim not in self.variables]
            post_not_found, data = process_derived_datetime_pandas(data, not_found, self.indexes)
            self.variables.extend([item for item in not_found if item not in post_not_found])

        data, x, y = self._process_tiles_without_geo(data, x, y)
        return data, x, y, z

    def _get_element(self, kind):
        element = self._kind_mapping[kind]
        if self.geo:
            import geoviews

            element = getattr(geoviews, element.__name__)
        return element

    def image(self, x=None, y=None, z=None, data=None):
        self._error_if_unavailable('image')
        data, x, y, z = self._process_gridded_args(data, x, y, z)
        if not (x and y):
            x, y = list(data.dims)[::-1]
        if not z:
            z = list(data.data_vars)[0]
        z = [z] + self.hover_cols

        params = dict(self._relabel)
        cur_opts, compat_opts = self._get_compat_opts('Image')
        redim = self._merge_redim({z[0]: self._dim_ranges['c']})

        element = self._get_element('image')
        if self.geo:
            params['crs'] = self.crs
        return redim_(element(data, [x, y], z, **params), **redim).apply(
            self._set_backends_opts, cur_opts=cur_opts, compat_opts=compat_opts
        )

    def rgb(self, x=None, y=None, z=None, data=None):
        self._error_if_unavailable('rgb')
        data, x, y, z = self._process_gridded_args(data, x, y, z)

        coords = [c for c in data.coords if c not in self.by + self.groupby + self.grid]
        if len(coords) < 3:
            raise ValueError('Data must be 3D array to be converted to RGB.')
        x = x or coords[2]
        y = y or coords[1]
        bands = self.kwds.get('bands', coords[0])
        if z is None:
            z = list(data.data_vars)[0]
        data = data[z]
        nbands = len(data.coords[bands])
        if nbands < 3:
            raise ValueError(
                f'Selected bands coordinate ({bands}) has only {nbands:d} channels,'
                'expected at least three channels to convert to RGB.'
            )

        params = dict(self._relabel)
        xres, yres = data.attrs['res'] if 'res' in data.attrs else (1, 1)
        xs = data.coords[x][::-1] if xres < 0 else data.coords[x]
        ys = data.coords[y][::-1] if yres < 0 else data.coords[y]
        eldata = (xs, ys)
        for b in range(nbands):
            eldata += (data.isel(**{bands: b}).values,)

        element = self._get_element('rgb')
        cur_opts, compat_opts = self._get_compat_opts('RGB')
        if self.geo:
            params['crs'] = self.crs
        rgb = element(eldata, [x, y], element.vdims[:nbands], **params)
        return redim_(rgb, **self._redim).apply(
            self._set_backends_opts, cur_opts=cur_opts, compat_opts=compat_opts
        )

    def quadmesh(self, x=None, y=None, z=None, data=None):
        self._error_if_unavailable('quadmesh')
        data, x, y, z = self._process_gridded_args(data, x, y, z)

        if not (x and y):
            x, y = list(k for k, v in data.coords.items() if v.size > 1)
        if not z:
            z = list(data.data_vars)[0]
        z = [z] + self.hover_cols

        params = dict(self._relabel)
        redim = self._merge_redim({z[0]: self._dim_ranges['c']})

        element = self._get_element('quadmesh')
        cur_opts, compat_opts = self._get_compat_opts('QuadMesh')
        if self.geo:
            params['crs'] = self.crs
        return redim_(
            element(data, [x, y], z, **params),
            **redim,
        ).apply(self._set_backends_opts, cur_opts=cur_opts, compat_opts=compat_opts)

    def contour(self, x=None, y=None, z=None, data=None, filled=False):
        self._error_if_unavailable('contour')
        from holoviews.operation import contours

        if 'projection' in self._plot_opts:
            import cartopy.crs as ccrs

            t = self._plot_opts['projection']
            if isinstance(t, ccrs.CRS) and not isinstance(t, ccrs.Projection):
                raise ValueError(
                    'invalid transform:'
                    ' Spherical contouring is not supported - '
                    ' consider using PlateCarree/RotatedPole.'
                )

        cur_opts, compat_opts = self._get_compat_opts('Contours')
        qmesh = self.quadmesh(x, y, z, data)

        if self.geo:
            # Apply projection before contouring
            import cartopy.crs as ccrs
            from geoviews import project

            projection = self._plot_opts.get('projection', ccrs.GOOGLE_MERCATOR)
            qmesh = project(qmesh, projection=projection)

        if filled:
            cur_opts['line_alpha'] = 0
        if cur_opts['colorbar']:
            cur_opts['show_legend'] = False
        levels = self.kwds.get('levels', 5)
        if isinstance(levels, int):
            cur_opts['color_levels'] = levels
        return contours(qmesh, filled=filled, levels=levels).apply(
            self._set_backends_opts, cur_opts=cur_opts, compat_opts=compat_opts
        )

    def contourf(self, x=None, y=None, z=None, data=None):
        self._error_if_unavailable('contourf')
        contourf = self.contour(x, y, z, data, filled=True)
        # The holoviews contours operation used in self.contour adapts
        # the value dim range, so we need to redimension it if the user
        # has asked for it by setting `clim`. Internally an unset `clim`
        # is identified by `(None, None)`.
        if self._dim_ranges['c'] != (None, None):
            z_name = contourf.vdims[0].name
            redim = {z_name: self._dim_ranges['c']}
            return contourf.redim.range(**redim)
        else:
            return contourf

    def vectorfield(self, x=None, y=None, angle=None, mag=None, data=None):
        self._error_if_unavailable('vectorfield')
        data, x, y, _ = self._process_gridded_args(data, x, y, z=None)

        if not (x and y):
            x, y = list(k for k, v in data.coords.items() if v.size > 1)

        angle = self.kwds.get('angle')
        mag = self.kwds.get('mag')
        z = [angle, mag] + self.hover_cols
        redim = self._merge_redim({z[1]: self._dim_ranges['c']})
        params = dict(self._relabel)

        element = self._get_element('vectorfield')
        cur_opts, compat_opts = self._get_compat_opts('VectorField')
        if self.geo:
            params['crs'] = self.crs
        return redim_(
            element(data, [x, y], z, **params),
            **redim,
        ).apply(self._set_backends_opts, cur_opts=cur_opts, compat_opts=compat_opts)

    ##########################
    #    Geometry plots      #
    ##########################

    def _geom_plot(self, x=None, y=None, data=None, kind='polygons'):
        data, x, y, _ = self._process_gridded_args(data, x, y, z=None)
        params = dict(self._relabel)

        if not (x and y):
            if is_geodataframe(data):
                x, y = ('Longitude', 'Latitude') if self.geo else ('x', 'y')
            elif self.gridded_data:
                x, y = self.variables[:2:-1]
            else:
                x, y = data.columns[:2]

        redim = self._merge_redim(
            {self._color_dim: self._dim_ranges['c']} if self._color_dim else {}
        )
        kdims, vdims = self._get_dimensions([x, y], [])
        if self.gridded_data:
            vdims = Dataset(data).vdims
        element = self._get_element(kind)
        cur_opts, compat_opts = self._get_compat_opts(element.name)
        for opts_ in [cur_opts, compat_opts]:
            if 'color' in opts_ and opts_['color'] in vdims:
                opts_['color'] = hv.dim(opts_['color'])
            # if there is nothing to put in hover, turn it off
            if 'tools' in opts_ and kind in ['polygons', 'paths'] and not vdims:
                opts_['tools'] = [t for t in opts_['tools'] if t != 'hover']
        if self.geo:
            params['crs'] = self.crs
        if self.by:
            obj = Dataset(data, self.by + kdims, vdims).to(
                element, kdims, vdims, self.by, **params
            )
            if self.subplots:
                obj = obj.layout(sort=False)
            else:
                obj = obj.overlay(sort=False)
        else:
            obj = element(data, kdims, vdims, **params)

        return (
            redim_(obj, **redim)
            .opts({element.name: cur_opts}, backend='bokeh')
            .opts({element.name: compat_opts}, backend=self._backend_compat)
        )

    def polygons(self, x=None, y=None, data=None):
        self._error_if_unavailable('polygons')
        return self._geom_plot(x, y, data, kind='polygons')

    def paths(self, x=None, y=None, data=None):
        self._error_if_unavailable('paths')
        return self._geom_plot(x, y, data, kind='paths')

    def points(self, x=None, y=None, data=None):
        self._error_if_unavailable('points')
        return self._geom_plot(x, y, data, kind='points')
