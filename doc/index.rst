*****
PyViz
*****

**How to solve visualization problems with Python tools**

The PyViz website and corresponding GitHub repository provide examples, demos, and training materials documenting how to solve visualization problems using interactive Python-based tools in your web browser, including `Bokeh <http://bokeh.pydata.org>`_, `HoloViews <http://holoviews.org>`_, `GeoViews <http://geo.holoviews.org>`_, `Datashader <https://github.com/bokeh/datashader>`_, and `Param <https://github.com/ioam/param>`_. 

So far, PyViz includes:

- A `Conda <https://conda.io>`_ package "pyviz" that makes it simple to install matching versions of all the libraries.
- A comprehensive `tutorial <tutorial/index>`_ showing how to use these tools together to do a wide range of different tasks.
- Sample datasets to work with.

You can view the `Tutorial <tutorial/index>`_ online, to get an idea what is covered.  If it looks relevant to you, you can then follow the steps below to get the libraries, tutorial, and sample data on your own system so you can work through the tutorial yourself. You'll then have simple-to-adapt starting points for solving your own visualization problems.



Installation
============

Step 1: Install a `Miniconda <http://conda.pydata.org/miniconda.html>`_  (or `Anaconda <https://www.continuum.io/downloads>`_) environment

-----------------------------------------------------------------

Any Linux, Mac OS X, or Windows computer with a web browser (preferably Google Chrome) should be suitable. 16GB of RAM is required for some of the examples, but most will run fine in 4GB.

If you don't already have conda on your machine, you can get it from `Anaconda.com <http://conda.pydata.org/miniconda.html>`_, and then open a terminal window.

[OPTIONAL] If you want to keep things organized, you can then create a separate Conda environment to work in for this tutorial::

   > conda create -n pyviz-tutorial python=3.6
   > source activate pyviz-tutorial

(omitting "source" if you are on Windows).


Step 2: Install `pyviz` and other required libraries
----------------------------------------------------

::

   > conda install -c pyviz pyviz


Step 3: Install the tutorials in your home directory
----------------------------------------------------

::

   > pyviz --install-examples pyviz-tutorial
   > cd pyviz-tutorial

This will create a copy of the notebooks and related files needed for the tutorial in a new subdirectory `pyviz-tutorial/`.


Step 4: Download the sample data
--------------------------------

::

   > pyviz --download-sample-data

(Small datasets come with the examples, but large ones like the NYC Taxi dataset have to be downloaded separately, which can take some time.)

Step 5: Launch Jupyter Notebook
-------------------------------

You can then launch the notebook server and client::

   > jupyter notebook

A browser window with a Jupyter Notebook instance should now open, letting you select and execute each notebook.  You can start with the ones in the "notebooks" subdirectory, as these show how to use the others in the "exercises" directory along with the applications in the "apps" directory. 

If you don't see the notebook appear (e.g. on some OS X versions), you may need to cut and paste the URL from the console output manually. 


Step 6: Test that everything is working
---------------------------------------

You can see if everything has installed correctly by selecting the ``00_Welcome.ipynb`` notebook and doing "Cell/Run All" in the menus. There may be warnings on some platforms, but you'll know it is working if you see the orange HoloViews logo after it runs ``hv.extension()``. 



.. toctree::
   :hidden:
   :maxdepth: 2

   Introduction <self>
   Tutorial <tutorial/index>
   FAQ
   About <about>
