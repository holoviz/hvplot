<h1>
hvPlot <img src="/doc/_static/hvplot-logo.png" width="50" height="50">
</h1>

**A high-level plotting API for the PyData ecosystem built on HoloViews.**

|    |    |
| --- | --- |
| Build Status | [![Linux/MacOS Build Status](https://travis-ci.org/pyviz/hvplot.svg?branch=master&logo=travis)](https://travis-ci.org/pyviz/hvplot) [![Windows Build status](https://img.shields.io/appveyor/ci/pyviz/hvplot/master.svg?logo=appveyor)](https://ci.appveyor.com/project/pyviz/hvplot/branch/master) |
| Coverage | [![codecov](https://codecov.io/gh/pyviz/hvplot/branch/master/graph/badge.svg)](https://codecov.io/gh/pyviz/hvplot) |
| Latest dev release | [![Github tag](https://img.shields.io/github/tag/pyviz/hvplot.svg?label=tag&colorB=11ccbb)](https://github.com/pyviz/hvplot/tags) |
| Latest release | [![Github release](https://img.shields.io/github/release/pyviz/hvplot.svg?label=tag&colorB=11ccbb)](https://github.com/pyviz/hvplot/releases) [![PyPI version](https://img.shields.io/pypi/v/hvplot.svg?colorB=cc77dd)](https://pypi.python.org/pypi/hvplot) [![hvplot version](https://img.shields.io/conda/v/pyviz/hvplot.svg?colorB=4488ff&style=flat)](https://anaconda.org/pyviz/hvplot) [![conda-forge version](https://img.shields.io/conda/v/conda-forge/hvplot.svg?label=conda%7Cconda-forge&colorB=4488ff)](https://anaconda.org/conda-forge/hvplot) [![defaults version](https://img.shields.io/conda/v/anaconda/hvplot.svg?label=conda%7Cdefaults&style=flat&colorB=4488ff)](https://anaconda.org/anaconda/hvplot) |
| Docs | [![gh-pages](https://img.shields.io/github/last-commit/pyviz/hvplot/gh-pages.svg)](https://github.com/pyviz/hvplot/tree/gh-pages) [![site](https://img.shields.io/website-up-down-green-red/http/hvplot.pyviz.org.svg)](http://hvplot.pyviz.org) |



## What is it?

The PyData ecosystem has a number of core Python data containers that allow users to work with a wide array of datatypes, including:

* [Pandas](http://pandas.pydata.org): DataFrame, Series (columnar/tabular data)
* [XArray](http://xarray.pydata.org): Dataset, DataArray (multidimensional arrays)
* [Dask](http://dask.pydata.org): DataFrame, Series, Array (distributed/out of core arrays and columnar data)
* [Streamz](http://streamz.readthedocs.io): DataFrame(s), Series(s) (streaming columnar data)
* [Intake](http://github.com/ContinuumIO/intake): DataSource (data catalogues)
* [GeoPandas](http://geopandas.org): GeoDataFrame (geometry data)
* [NetworkX](https://networkx.github.io/documentation/stable/): Graph (network graphs)

Several of these libraries have the concept of a high-level plotting API that lets a user generate common plot types very easily. The native plotting APIs are generally built on [Matplotlib](http://matplotlib.org), which provides a solid foundation, but means that users miss out the benefits of modern, interactive plotting libraries for the web like [Bokeh](http://bokeh.pydata.org) and [HoloViews](http://holoviews.org).

hvPlot provides a high-level plotting API built on HoloViews that provides a general and consistent API for plotting data in all the abovementioned formats. hvPlot can integrate neatly with the individual libraries if an extension mechanism for the native plot APIs is offered, or it can be used as a standalone component.

To start using hvplot have a look at the [Getting Started Guide](https://pyviz.github.io/hvplot/getting_started/index.html) and check out the current functionality in the [User Guide.](https://pyviz.github.io/hvplot/user_guide/index.html)

<img src="http://blog.pyviz.org/images/hvplot_collage.png">

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


## About PyViz

hvPlot is part of the PyViz initiative for making Python-based visualization tools work well together.
See [pyviz.org](http://pyviz.org) for related packages that you can use with hvPlot and
[status.pyviz.org](http://status.pyviz.org) for the current status of each PyViz project.
