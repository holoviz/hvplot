**********
User Guide
**********

The user guide provides a detailed introduction to the API and
features of hvPlot. In the `Introduction <Introduction.html>`_ you
will learn how to activate the plotting API and start using it. Next
you will learn to use the API for tabular data and get an overview of
the `types of plots <Plotting.html>`_ you can generate and how to
`customize <Customization.html>`_ them; including how to customize
interactivity using `widgets <Widgets.html>`_. Next is an overview on how to
`display and save plots <Viewing.html>`_  in the notebook, on the
commandline, and from a script. Another section will introduce you to
generating `subplots <Subplots.html>`_ from your data.

Once the basics are covered you can learn how to use the plotting API
for specific types of data including `streaming data
<Streaming.html>`_, `gridded data <Gridded_Data.html>`_
`network graphs <NetworkX.html>`_, `geographic data <Geographic_Data.html>`_,
and `timeseries data <Timeseries_Data.html>`_. These sections are not meant
to be read in a particular order; you should take a look at any that seem
relevant to your data.

The `interactive <Interactive.html>`_ user guide introduces you to the
ability to use the APIs of your favorite data analysis libraries
interactively by allowing you to pass in widgets in place of constant
arguments. This will provide you with an invaluable tool to perform
exploratory analyses quickly but also build powerful and complex data
analysis pipelines using APIs you are already familiar with.

Lastly the `statistical plots <Statistical_Plots.html>`_ section will
take you through a number of specialized plot types modelled on the
pandas.plotting module and the `pandas API <Pandas_API.html>`_ section mimics
the `pandas visualization docs
<https://pandas.pydata.org/pandas-docs/stable/user_guide/visualization.html>`_
but using pandas.options.plotting.backend to do the plotting in HoloViews
rather than Matplotlib.

**Overview**:

* `Introduction <Introduction.html>`_
  Introduction to hvPlot and how to start using it.

* `Plotting with Bokeh <Plotting.html>`_
  Overview of plotting your data with hvPlot and Bokeh.

* `Plotting with Matplotlib <Plotting_with_Matplotlib.html>`_
  Overview of plotting your data with hvPlot and Matplotib.

* `Plotting with Plotly <Plotting_with_Plotly.html>`_
  Overview of plotting your data with hvPlot and Plotly.

* `Customization <Customization.html>`_
  Listing of available options to customize plots.

* `Interactive <Interactive.html>`_
  Interactive APIs for data exploration.

* `Widgets <Widgets.html>`_
  Adding and customizing interactivity using Panel widgets.

* `Plotting Extensions <Plotting_Extensions.html>`_
  Changing the plotting extension.

* `Exploring data <Explorer.html>`_
  Exploring data with user interface.

* `Viewing <Viewing.html>`_
  Displaying and saving plots in the notebook, at the command prompt, or in scripts.

* `Subplots <Subplots.html>`_
  How to generate subplots and grids.

* `Streaming <Streaming.html>`_
  How to use hvPlot for streaming plots with the streamz library.

* `Gridded Data <Gridded_Data.html>`_
  How to use hvPlot for plotting XArray-based gridded data.

* `Network Graphs <NetworkX.html>`_
  How to use hvPlot for plotting NetworkX graphs.

* `Geographic Data <Geographic_Data.html>`_
  Using GeoViews, Cartopy, GeoPandas and spatialpandas to plot data in geographic coordinate systems.

* `Timeseries Data <Timeseries_Data.html>`_
  Using hvPlot when working with timeseries data.

* `Statistical Plots <Statistical_Plots.html>`_
  A number of statistical plot types modeled on the pandas.plotting module.

* `Pandas API <Pandas_API.html>`_
  How to use pandas.plot directly by switching out the plotting backend.

.. toctree::
    :titlesonly:
    :hidden:
    :maxdepth: 2

    Introduction <Introduction>
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
    Statistical Plots <Statistical_Plots>
    Pandas API <Pandas_API>
