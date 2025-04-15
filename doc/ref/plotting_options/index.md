(plot-options)=

# Plotting Options

hvPlot's plotting API exposes three main types of options:

- **Plot kind specific**: options specific to each plot kind; for example, `marker` is not a generic option but is specific to {meth}`hvplot.hvPlot.scatter`.
- **Generic**: options that can be passed to most of the plotting methods/kinds; these are the options displayed in the tables below, such as `width` or `title`.
- **Plotting backend and method/kind specific styling options**: in addition to the generic [Styling Options](plotting-options-styling), hvPlot exposes styling options that are specific to a particular plotting backend and plot kind. With these options, it is possible to customize each component in detail, exposing all the options a plotting backend exposes in HoloViews (they are applied to the specific HoloViews Element(s) returned by a plotting call, for example {class}`holoviews:holoviews.element.Scatter` for {meth}`hvplot.hvPlot.scatter`). These usually include options to color the line and fill color, alpha and style. These options  can be found on the reference page of each plotting method (e.g. {meth}`hvplot.hvPlot.scatter`).

The {func}`hvplot.help` function can be used to interactively display these options:

- `docstring=True` to display the method docstring, including its specific options.
- `generic=True` to display the docstring of all the generic options.
- `style=True` to display a listing of all the plotting backend specific style options.

The following tables list all the generic plotting options that can be used to customize hvPlot's plots.

## Data Options

For organizing, grouping, and transforming the dataset before visualization, including labels, sorting, and indexing:

```{eval-rst}
.. plotting-options-table:: Data Options
```

See [this page](./data) for more information on these options.

## Size And Layout Options

Customization options for plot sizes and overall layout, including responsive mode:

```{eval-rst}
.. plotting-options-table:: Size And Layout Options
```

## Axis Options

Customization options for axis appearance and behavior, including labels, limits, tick formatting, and axis scaling:

```{eval-rst}
.. plotting-options-table:: Axis Options
```

## Grid And Legend Options

Options for setting the grid or legend of plots as well as colorbar options:

```{eval-rst}
.. plotting-options-table:: Grid And Legend Options
```

(plotting-options-styling)=
## Styling Options

Visual styling options to adjust colors, fonts, and other aesthetic elements of the plot.

:::{note}
These are the styling options shared by all the supported plotting backends. Backend-specific options can be found on the
reference page of each plotting method (e.g. {meth}`hvplot.hvPlot.scatter`) or by executing `hvplot.help('scatter', docstring=False, generic=False, style=True)`.
:::

```{eval-rst}
.. plotting-options-table:: Styling Options
```

## Interactivity Options

Bokeh specific options for adding hover tools as well as other interactive tools like tap tool and box select tool:

```{eval-rst}
.. plotting-options-table:: Interactivity Options
```

## Resampling Options

Performance related options for handling large datasets, including downsampling, rasterization, and dynamic plot updates (most of these options require [Datashader](https://datashader.org/) to be installed):

```{eval-rst}
.. plotting-options-table:: Resampling Options
```

## Geographic Options

Options for geographic plots, including map projections, tile overlays, and geographic features like coastlines and borders:

```{eval-rst}
.. plotting-options-table:: Geographic Options
```

## Streaming Options

Options for handling live data streams:

```{eval-rst}
.. plotting-options-table:: Streaming Options
```

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

All Options <self>
Data Options <data>
```
