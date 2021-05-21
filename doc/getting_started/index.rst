***************
Getting Started
***************

Welcome to hvPlot!

Installation
------------

|CondaPyViz|_ |CondaDefaults|_ |PyPI|_ |License|_

hvPlot works with `Python 2.7 and Python 3 <https://travis-ci.org/pyviz/hvplot>`_ on Linux, Windows, or Mac.  The recommended way to install hvPlot is using the `conda <http://conda.pydata.org/docs/>`_ command provided by `Anaconda <http://docs.continuum.io/anaconda/install>`_ or `Miniconda <http://conda.pydata.org/miniconda.html>`_::

  conda install -c pyviz hvplot

or using PyPI::

  pip install hvplot

For versions of `jupyterlab>=3.0` the necessary extension is
automatically bundled in the `pyviz_comms` package, which must be
>=2.0. However note that for version of `jupyterlab<3.0` you must also
manually install the JupyterLab extension with::

  conda install jupyterlab
  jupyter labextension install @pyviz/jupyterlab_pyviz


.. |CondaPyViz| image:: https://img.shields.io/conda/v/pyviz/hvplot.svg
.. _CondaPyViz: https://anaconda.org/pyviz/hvplot

.. |CondaDefaults| image:: https://img.shields.io/conda/v/anaconda/hvplot.svg?label=conda%7Cdefaults
.. _CondaDefaults: https://anaconda.org/anaconda/hvplot

.. |PyPI| image:: https://img.shields.io/pypi/v/hvplot.svg
.. _PyPI: https://pypi.python.org/pypi/hvplot

.. |License| image:: https://img.shields.io/pypi/l/hvplot.svg
.. _License: https://github.com/holoviz/holoviz/blob/master/LICENSE.txt


Usage
-----

For information on using hvPlot, take a look at the `User Guide <../user_guide>`_.
The `announcement blog <http://blog.pyviz.org/hvplot_announcement.html>`_ is another great
resource to learn about the features of hvPlot and get an idea of what it can do.
