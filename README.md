[![linux mac build Status](https://travis-ci.org/pyviz/holoplot.svg?branch=master)](https://travis-ci.org/pyviz/holoplot)

# HoloPlot

**A high-level plotting API for the PyData ecosystem built on HoloViews.**

The PyData ecosystem has a number of core data containers that allow
users to work with most types of data, including:

* pandas: DataFrame, Series
* streamz: DataFrame(s), Series(s)
* dask: DataFrame, Series, Array
* xarray: Dataset, DataArray
* geopandas: DataFrame
* intake: DataSource

Many of these libraries have the concept of a high-level plotting API
that lets a user generate common plot types very easily. The native
plotting APIs are generally built on matplotlib, which provides a
solid foundation, but means that users miss out the benefits of
modern, interactive plotting libraries like bokeh and holoviews.

HoloPlot provides a high-level plotting API built on HoloViews which
will provide a general and consistent API for plotting data in all the
abovementioned formats. HoloPlot will integrate neatly with the
individual libraries if an extension mechanism for the native plot
APIs is offered or can be used as a standalone component.
