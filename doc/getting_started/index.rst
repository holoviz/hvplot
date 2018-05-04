***************
Getting started
***************

Installation
------------

HoloPlot supports Python 2.7, 3.5, 3.6 and 3.7 on Linux, Windows, or Mac and can be installed with conda::

    conda install -c pyviz holoplot

or with pip::

    pip install holoplot

For JupyterLab support, the jupyterlab_holoviews extension is also required::

    jupyter labextension install @pyviz/jupyterlab_holoviews

Usage
-----

Once you've installed HoloPlot as above and have fetched the examples
shown on the website you can run them using `Jupyter
<http://jupyter.org>`_::

    jupyter notebook

To work with JupyterLab you will also need the HoloViews JupyterLab
extension::

    conda install -c conda-forge jupyterlab
    jupyter labextension install @pyviz/jupyterlab_holoviews

Once you have installed JupyterLab and the extension launch it with::

    jupyter lab


Developer Instructions
----------------------

1. Install Python 3 `miniconda <http://conda.pydata.org/miniconda.html>`_ or
`anaconda <http://docs.continuum.io/anaconda/install>`_, if you don't already have it on your system.

2. Clone the holoplot git repository if you do not already have it::

    git clone git://github.com/pyviz/holoplot.git

3. Set up an environment with all of the dependencies needed to run the examples::

    cd holoplot
    conda env create --quiet --force -n holoplot -f ./environment.yml
    source activate holoplot

4. Put the `holoplot` directory into the Python path in this environment::

    pip install -e .
