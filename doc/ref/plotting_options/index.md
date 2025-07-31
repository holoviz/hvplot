(plot-options)=

# Plotting Options

hvPlot offers many ways to control the appearance and behavior of your plots. This page documents all of the **generic options** that can be applied to most plots ({meth}`hvplot.hvPlot.scatter`, {meth}`hvplot.hvPlot.line`, etc.) regardless of which plotting backend you are using (Bokeh, Matplotlib, etc.). Most plot types also offer additional options beyond the generic ones documented here. Those additional options depend on the specific type of plot (e.g. `marker` for {meth}`hvplot.hvPlot.scatter`) and the specific plotting backend (e.g. `line_width` for {meth}`hvplot.hvPlot.line` with Bokeh). The latter group of options is often styling related. These additional options are documented in the reference page for the plot type (e.g. {meth}`hvplot.hvPlot.scatter` for a scatter plot).

The plotting options can be displayed interactively for a plot type and the active plotting backend using {func}`hvplot.help`, e.g. `hvplot.help('scatter')`. The function prints all the options by default. Its output can be reduced by setting to `False` the keywords `generic` (to exclude the generic options), `docstring` (to exclude the plot type docstring), and `style` (to exclude the backend-specific styling options).

The sections below cover the generic options available for all plots, grouped into categories depending on what the options control.

## [Data Options](./data)

For organizing, grouping, and transforming the dataset before visualization, including labels, sorting, and indexing:

```{eval-rst}
.. plotting-options-table:: Data Options
```

See [this page](./data) for more information on these options.

## [Size And Layout Options](./size_layout)

Customization options for plot sizes and overall layout, including responsive mode and widget location:

```{eval-rst}
.. plotting-options-table:: Size And Layout Options
```

See [this page](./size_layout) for more information on these options.

## [Axis Options](./axis)

Customization options for axis appearance and behavior, including labels, limits, tick formatting, and axis scaling:

```{eval-rst}
.. plotting-options-table:: Axis Options
```

See [this page](./axis) for more information on these options.

## [Color And Colormap Options](./color_colormap)

Visual styling options to adjust colors and colormapping:

```{eval-rst}
.. plotting-options-table:: Color And Colormap Options
```

See [this page](./color_colormap) for more information on these options.

## [Styling Options](./styling)

:::{note}
These are the styling options shared by all the supported plotting backends. Backend-specific options can be found on the reference page of each plotting method (e.g. {meth}`hvplot.hvPlot.scatter`) or by executing `hvplot.help('scatter', docstring=False, generic=False, style=True)`.
:::

Visual styling options to adjust colors, fonts, and other aesthetic elements of the plot:

```{eval-rst}
.. plotting-options-table:: Styling Options
```

See [this page](./styling) for more information on these options.

## [Legend Options](./legend)

Options for setting the grid or legend of plots as well as colorbar options:

```{eval-rst}
.. plotting-options-table:: Legend Options
```

See [this page](./legend) for more information on these options.

## [Interactivity Options](./interactivity)

::: {note}
These options only apply to the interactive plotting backends (e.g. [Bokeh](plot-ext-bokeh)), not to the static backend [Matplotlib](plot-ext-matplotlib).
:::

Bokeh specific options for adding hover tools as well as other interactive tools like tap tool and box select tool:

```{eval-rst}
.. plotting-options-table:: Interactivity Options
```

See [this page](./interactivity) for more information on these options.

## [Resampling Options](./resampling)

Performance related options for handling large datasets, including downsampling, rasterization, and dynamic plot updates (most of these options require [Datashader](https://datashader.org/) to be installed):

```{eval-rst}
.. plotting-options-table:: Resampling Options
```

See [this page](./resampling) for more information on these options.

## [Geographic Options](./geographic)

Options for geographic plots, including map projections, tile overlays, and geographic features like coastlines and borders (most of these options require [GeoViews](https://geoviews.org) to be installed):

```{eval-rst}
.. plotting-options-table:: Geographic Options
```

See [this page](./geographic) for more information on these options.

## [Streaming Options](./streaming)

Options for handling live data streams:

```{eval-rst}
.. plotting-options-table:: Streaming Options
```

See [this page](./streaming) for more information on these options.

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

All Options <self>
Data Options <data>
Size And Layout Options <size_layout>
Axis Options <axis>
Color And Colormap Options <color_colormap>
Styling Options <styling>
Legend Options <legend>
Interactivity Options <interactivity>
Resampling Options <resampling>
Geographic Options <geographic>
Streaming Options <streaming>
```
