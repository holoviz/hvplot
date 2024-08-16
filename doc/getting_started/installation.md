# Installation

|    |    |
| --- | --- |
| Latest release | [![Github release](https://img.shields.io/github/release/holoviz/hvplot.svg?label=tag&colorB=11ccbb)](https://github.com/holoviz/hvplot/releases) [![PyPI version](https://img.shields.io/pypi/v/hvplot.svg?colorB=cc77dd)](https://pypi.python.org/pypi/hvplot) [![hvplot version](https://img.shields.io/conda/v/pyviz/hvplot.svg?colorB=4488ff&style=flat)](https://anaconda.org/pyviz/hvplot) [![conda-forge version](https://img.shields.io/conda/v/conda-forge/hvplot.svg?label=conda%7Cconda-forge&colorB=4488ff)](https://anaconda.org/conda-forge/hvplot) [![defaults version](https://img.shields.io/conda/v/anaconda/hvplot.svg?label=conda%7Cdefaults&style=flat&colorB=4488ff)](https://anaconda.org/anaconda/hvplot) |
| Python | [![Python support](https://img.shields.io/pypi/pyversions/hvplot.svg)](https://pypi.org/project/hvplot/) |

hvPlot supports Python 3.9 and above on Linux, Windows, or Mac. hvPlot can be installed with [conda](https://conda.io/en/latest/):

    conda install hvplot

or with `pip`:

    pip install hvplot

Note that `hvplot` needs to run in a Jupyter environment to automatically show output plots. However, if you are using a raw Python or IPython console, it is still possible to [show the plots](https://hvplot.holoviz.org/user_guide/Viewing.html#python-command-prompt-scripts) with `hvplot.show()` or [save the plots](https://hvplot.holoviz.org/user_guide/Viewing.html#saving-plots) even if you cannot view them interactively. For versions of `jupyterlab>=3.0` the necessary extension is automatically bundled in the `pyviz_comms` package, which must be >=2.0. However note that for version of `jupyterlab<3.0` you must also manually install the JupyterLab extension with:

    conda install jupyterlab
    jupyter labextension install @pyviz/jupyterlab_pyviz

To run the guides in this site create an environment with the required dependencies:

    conda create -n hvplot-env -c conda-forge -c nodefaults hvplot geoviews datashader xarray pandas geopandas dask streamz networkx intake intake-xarray intake-parquet s3fs scipy spatialpandas pooch rasterio fiona plotly matplotlib jupyterlab
