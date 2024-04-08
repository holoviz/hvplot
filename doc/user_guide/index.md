# User Guide

The user guide provides a detailed introduction to the API and
features of hvPlot. In the [Introduction](Introduction.ipynb) you
will learn how to activate the plotting API and start using it. Next
you will learn to use the API for tabular data and get an overview of
the [types of plots](Plotting.ipynb) you can generate and how to
[customize](Customization.ipynb) them; including how to customize
interactivity using [widgets](Widgets.ipynb). Next is an overview on how to
[display and save plots](Viewing.ipynb)  in the notebook, on the
commandline, and from a script. Another section will introduce you to
generating [subplots](Subplots.ipynb) from your data.

Once the basics are covered you can learn how to use the plotting API
for specific types of data including [streaming data](Streaming.ipynb), [gridded data](Gridded_Data.ipynb)
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

Lastly the [statistical plots](Statistical_Plots.ipynb) section will
take you through a number of specialized plot types modelled on the
pandas.plotting module and the [pandas API](Pandas_API.ipynb) section mimics
the [pandas visualization docs](https://pandas.pydata.org/pandas-docs/stable/user_guide/visualization.ipynb)
but using pandas.options.plotting.backend to do the plotting in HoloViews
rather than Matplotlib.

**Overview**:

- [Introduction](Introduction)
  Introduction to hvPlot and how to start using it.
- [Integrations](Integrations)
  How hvPlot integrates with the Python ecosystem.
- [Plotting with Bokeh](Plotting)
  Overview of plotting your data with hvPlot and Bokeh.
- [Plotting with Matplotlib](Plotting_with_Matplotlib)
  Overview of plotting your data with hvPlot and Matplotib.
- [Plotting with Plotly](Plotting_with_Plotly)
  Overview of plotting your data with hvPlot and Plotly.
- [Customization](Customization)
  Listing of available options to customize plots.
- [Interactive](Interactive)
  Interactive APIs for data exploration.
- [Widgets](Widgets)
  Adding and customizing interactivity using Panel widgets.
- [Plotting Extensions](Plotting_Extensions)
  Changing the plotting extension.
- [Exploring data](Explorer)
  Exploring data with user interface.
- [Viewing](Viewing)
  Displaying and saving plots in the notebook, at the command prompt, or in scripts.
- [Subplots](Subplots)
  How to generate subplots and grids.
- [Streaming](Streaming)
  How to use hvPlot for streaming plots with the streamz library.
- [Gridded Data](Gridded_Data)
  How to use hvPlot for plotting XArray-based gridded data.
- [Network Graphs](NetworkX)
  How to use hvPlot for plotting NetworkX graphs.
- [Geographic Data](Geographic_Data)
  Using GeoViews, Cartopy, GeoPandas and spatialpandas to plot data in geographic coordinate systems.
- [Timeseries Data](Timeseries_Data)
  Using hvPlot when working with timeseries data.
- [Large Timeseries Data](Large_Timeseries)
  Using hvPlot when working with large timeseries data.
- [Statistical Plots](Statistical_Plots)
  A number of statistical plot types modeled on the pandas.plotting module.
- [Pandas API](Pandas_API)
  How to use pandas.plot directly by switching out the plotting backend.

```{toctree}
:hidden: true
:maxdepth: 2
:titlesonly: true

Introduction <Introduction>
Integrations <Integrations>
Plotting with Bokeh <Plotting>
Plotting with Matplotlib <Plotting_with_Matplotlib>
Plotting with Plotly <Plotting_with_Plotly>
Customization <Customization>
Interactive <Interactive>
Widgets <Widgets>
Plotting Extensions <Plotting_Extensions>
Exploring data <Explorer>
Viewing <Viewing>
Subplots <Subplots>
Streaming <Streaming>
Gridded Data <Gridded_Data>
Network Graphs <NetworkX>
Geographic Data <Geographic_Data>
Timeseries Data <Timeseries_Data>
Large Timeseries <Large_Timeseries>
Statistical Plots <Statistical_Plots>
Pandas API <Pandas_API>
```
