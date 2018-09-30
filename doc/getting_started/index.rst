***************
Getting started
***************

Installation
------------

hvPlot supports Python 2.7, 3.5, 3.6 and 3.7 on Linux, Windows, or Mac and can be installed with conda::

    conda install -c pyviz hvplot

or with pip::

    pip install hvplot

Usage
-----

Once you've installed hvPlot as above and have fetched the examples
shown on the website you can run them using `Jupyter
<http://jupyter.org>`_::

    jupyter notebook

To work with JupyterLab you will also need the PyViz JupyterLab
extension::

    conda install -c conda-forge jupyterlab
    jupyter labextension install @pyviz/jupyterlab_pyviz

Once you have installed JupyterLab and the extension launch it with::

    jupyter lab

If you have any questions, please refer to http://holoviews.org/FAQ.html
and if that doesn't help, feel free to post an issue on GitHub, question on
stackoverflow, or discuss on Gitter.


Developer Instructions
----------------------

1. Install Python 3 `miniconda <http://conda.pydata.org/miniconda.html>`_ or `anaconda <http://docs.continuum.io/anaconda/install>`_, if you don't already have it on your system.

2. Clone the hvplot git repository if you do not already have it::

    git clone git://github.com/pyviz/hvplot.git

3. Set up an environment with all of the dependencies needed to run the examples::

    cd hvplot
    conda env create --quiet --force -n hvplot -f ./environment.yml
    source activate hvplot

4. Put the `hvplot` directory into the Python path in this environment::

    pip install -e .
