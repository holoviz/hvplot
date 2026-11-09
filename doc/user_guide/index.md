# User Guide

The user guide provides a detailed introduction to the API and
features of hvPlot. If you are new to hvPlot, start with the
[Getting started tutorial](../tutorials/getting_started.ipynb). Then get
an overview of the [types of plots](Plotting.ipynb) you can generate for
tabular data, including how to customize interactivity using
[widgets](Widgets.ipynb). Task-oriented instructions on displaying and
saving plots, creating subplots or switching the plotting extension live in
the [How-To guides](../how_to/index.md).

Once the basics are covered you can learn how to use the plotting API
for specific types of data including [gridded data](Gridded_Data.ipynb),
[network graphs](NetworkX.ipynb), [geographic data](Geographic_Data.ipynb),
and [timeseries data](Timeseries_Data.ipynb). These sections are not meant
to be read in a particular order; you should take a look at any that seem
relevant to your data.

The [interactive](Interactive.ipynb) user guide introduces you to the
ability to use the APIs of your favorite data analysis libraries
interactively by allowing you to pass in widgets in place of constant
arguments. This will provide you with an invaluable tool to perform
exploratory analyses quickly but also build powerful and complex data
analysis pipelines using APIs you are already familiar with.

**Overview**:

- [Plotting with Bokeh](Plotting)
  Overview of plotting your data with hvPlot and Bokeh.
- [Plotting with Matplotlib](Plotting_with_Matplotlib)
  Overview of plotting your data with hvPlot and Matplotlib.
- [Plotting with Plotly](Plotting_with_Plotly)
  Overview of plotting your data with hvPlot and Plotly.
- [Interactive](Interactive)
  Interactive APIs for data exploration.
- [Widgets](Widgets)
  Adding and customizing interactivity using Panel widgets.
- [Gridded Data](Gridded_Data)
  How to use hvPlot for plotting Xarray-based gridded data.
- [Network Graphs](NetworkX)
  How to use hvPlot for plotting NetworkX graphs.
- [Geographic Data](Geographic_Data)
  Using GeoViews, Cartopy, GeoPandas and spatialpandas to plot data in geographic coordinate systems.
- [Timeseries Data](Timeseries_Data)
  Using hvPlot when working with timeseries data.
- [Large Timeseries Data](Large_Timeseries)
  Using hvPlot when working with large timeseries data.

```{toctree}
:hidden: true
:maxdepth: 2
:titlesonly: true

Plotting with Bokeh <Plotting>
Plotting with Matplotlib <Plotting_with_Matplotlib>
Plotting with Plotly <Plotting_with_Plotly>
Interactive <Interactive>
Widgets <Widgets>
Gridded Data <Gridded_Data>
Network Graphs <NetworkX>
Geographic Data <Geographic_Data>
Timeseries Data <Timeseries_Data>
Large Timeseries <Large_Timeseries>
```
