********
HoloPlot
********

**A high-level plotting API for the PyData ecosystem built on HoloViews.**

The PyData ecosystem has a number of core data containers that allow
users to work with most types of data, including:

* pandas: DataFrame, Series
* streamz: DataFrame(s), Series(s)
* dask: DataFrame, Series
* xarray: DataArray
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

The API is currently under heavy development and should not be
considered stable but if you want to start playing with it have a look
at the `Getting Started Guide <getting_started/index.html>`_ and check
out the current functionality in the `User Guide
<user_guide/index.html>`_.

Quickstart
==========

Installation
------------

HoloPlot supports Python 2.7-3.7 on Linux, Windows, or Mac and can be installed with conda::

  conda install -c pyviz holoplot

or with pip::

  pip install holoplot

For JupyterLab support the jupyterlab_holoviews extension is also required::

  jupyter labextension install @pyviz/jupyterlab_holoviews


Overview
--------

.. notebook:: holoplot ./homepage.ipynb

.. toctree::
   :hidden:
   :maxdepth: 2

   Introduction <self>
   Getting Started <getting_started/index>
   User Guide <user_guide/index>
   About <about>
