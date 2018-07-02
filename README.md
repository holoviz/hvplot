[![linux/mac build status](https://travis-ci.org/pyviz/holoplot.svg?branch=master)](https://travis-ci.org/pyviz/hvplot)

<h1>
hvPlot <img src="/doc/_static/hvplot-logo.png" width="50" height="50">
</h1>

**A high-level plotting API for the PyData ecosystem built on HoloViews.**

The PyData ecosystem has a number of core Python data containers that allow users to work with a wide array of datatypes, including:

* [Pandas](http://pandas.pydata.org): DataFrame, Series (columnar/tabular data)
* [XArray](http://xarray.pydata.org): Dataset, DataArray (multidimensional arrays)
* [Dask](http://dask.pydata.org): DataFrame, Series, Array (distributed/out of core arrays and columnar data)
* [Streamz](http://streamz.readthedocs.io): DataFrame(s), Series(s) (streaming columnar data)
* [Intake](http://github.com/ContinuumIO/intake): DataSource (data catalogues)
* [GeoPandas](http://geopandas.org): GeoDataFrame (geometry data)

Several of these libraries have the concept of a high-level plotting API that lets a user generate common plot types very easily. The native plotting APIs are generally built on [Matplotlib](http://matplotlib.org), which provides a solid foundation, but means that users miss out the benefits of modern, interactive plotting libraries for the web like [Bokeh](http://bokeh.pydata.org) and [HoloViews](http://holoviews.org).

hvPlot provides a high-level plotting API built on HoloViews that provides a general and consistent API for plotting data in all the abovementioned formats. hvPlot can integrate neatly with the individual libraries if an extension mechanism for the native plot APIs is offered, or it can be used as a standalone component.

To start using hvplot have a look at the [Getting Started Guide](https://pyviz.github.io/hvplot/getting_started/index.html) and check out the current functionality in the [User Guide.](https://pyviz.github.io/hvplot/user_guide/index.html)

## Installation

hvPlot supports Python 2.7, 3.5, 3.6 and 3.7 on Linux, Windows, or Mac and can be installed with ``conda``:

```
conda install -c pyviz hvplot
```

or with ``pip``:

```
pip install hvplot
```

For JupyterLab support, the ``jupyterlab_pyviz`` extension is also required:

```
jupyter labextension install @pyviz/jupyterlab_pyviz
```
