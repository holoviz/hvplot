[![linux/mac build status](https://travis-ci.org/pyviz/holoplot.svg?branch=master)](https://travis-ci.org/pyviz/holoplot)

<h1>
HoloPlot <img src="/doc/_static/holoplot-logo.png" width="50" height="50">
</h1>

**A high-level plotting API for the PyData ecosystem built on HoloViews.**

The PyData ecosystem has a number of core Python data containers that allow users to work with a wide array of datatypes, including:

* [Pandas](http://pandas.pydata.org): DataFrame, Series (columnar/tabular data)
* [XArray](http://xarray.pydata.org): Dataset, DataArray (multidimensional arrays)
* [Dask](http://dask.pydata.org): DataFrame, Series, Array (distributed/out of core arrays and columnar data)
* [Streamz](http://streamz.readthedocs.io): DataFrame(s), Series(s) (streaming columnar data)
* [Intake](http://github.com/ContinuumIO/intake): DataSource (data catalogues)

Many of these libraries have the concept of a high-level plotting API that lets a user generate common plot types very easily. The native plotting APIs are generally built on [Matplotlib](http://matplotlib.org), which provides a solid foundation, but means that users miss out the benefits of modern, interactive plotting libraries for the web like [Bokeh](http://bokeh.pydata.org) and [HoloViews](http://holoviews.org).

HoloPlot provides a high-level plotting API built on HoloViews that provides a general and consistent API for plotting data in all the abovementioned formats. HoloPlot can integrate neatly with the individual libraries if an extension mechanism for the native plot APIs is offered, or it can be used as a standalone component.

The API is currently under heavy development and is not yet ready to be considered stable. That said, the Pandas API that it mirrors is quite stable, so if you want to start playing with it anyway, have a look at the [Getting Started Guide](getting_started/index.html) and check out the current functionality in the [User Guide.](user_guide/index.html)
