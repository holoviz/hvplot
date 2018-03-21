***************
Getting started
***************


Installation
------------

HvPlot supports Python 2.7-3.7 on Linux, Windows, or Mac.

Installable ``hvplot`` packages will be created at some point, but
at present, the recommended way to install hvPlot is based on conda
`conda <http://conda.pydata.org/docs>`_ environments and 
`git <https://git-scm.com>`_:

1. Install Python 3 `miniconda <http://conda.pydata.org/miniconda.html>`_ or 
`anaconda <http://docs.continuum.io/anaconda/install>`_, if you don't already have it on your system.

2. Clone the hvplot git repository if you do not already have it::

    git clone git://github.com/pyviz/hvplot.git

3. Set up an environment with all of the dependencies needed to run the examples::
    
    cd hvplot
    conda env create --quiet --force -n hvplot -f ./environment.yml
    source activate hvplot

4. Put the `hvplot` directory into the Python path in this environment::
    
    pip install -e .

Usage
-----

Once you've installed EarthSim as above and are in the EarthSim directory, you can
run the examples shown on the website using
`Jupyter <http://jupyter.org>`_::

    cd examples
    jupyter notebook --NotebookApp.iopub_data_rate_limit=1e8

(Increasing the rate limit in this way is `required for the 5.0 Jupyter version
<http://holoviews.org/user_guide/Installing_and_Configuring.html>`_,
but should not be needed in earlier or later Jupyter releases.)

To work with JupyterLab you will also need the HoloViews JupyterLab
extension::

    conda install -c conda-forge jupyterlab
    jupyter labextension install @pyviz/jupyterlab_holoviews

Once you have installed JupyterLab and the extension launch it with::

    jupyter-lab
