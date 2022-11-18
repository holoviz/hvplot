.. _devguide_setup:

Getting Set Up
==============

The hvPlot library is a complex project which provides a wide range
of data interfaces and an extensible set of plotting backends, which
means the development and testing process involves a wide set of
libraries.

.. contents::
    :local:
    :depth: 2

.. dev_guide_preliminaries:

Preliminaries
-------------

Git
~~~

The hvPlot source code is stored in a `Git`_ source control repository.
The first step to working on hvPlot is to install Git on to your system.
There are different ways to do this depending on whether, you are using
Windows, OSX, or Linux.

To install Git on any platform, refer to the `Installing Git`_ section of
the `Pro Git Book`_.

Conda
~~~~~

Developing hvPlot requires a wide range of packages that are not
easily and quickly available using pip. To make this more manageable,
core developers rely heavily on the `conda package manager`_ for the
free `Anaconda`_ Python distribution. However, ``conda`` can also
install non-Python package dependencies, which helps streamline hvPlot
development greatly. It is *strongly* recommended that anyone
developing hvPlot also use ``conda``, and the remainder of the
instructions will assume that ``conda`` is available.

To install Conda on any platform, see the `Download conda`_ section of the
`conda documentation`_.

Cloning the Repository
----------------------

The source code for the hvPlot project is hosted on GitHub_. To clone the
source repository, issue the following command:

.. code-block:: sh

    git clone https://github.com/holoviz/hvplot.git

This will create a ``hvplot`` directory at your file system
location. This ``hvplot`` directory is referred to as the *source
checkout* for the remainder of this document.

.. _dev_guide_installing_dependencies:

Installing Dependencies
-----------------------

hvPlot requires many additional packages for development and
testing.

Conda Environments
~~~~~~~~~~~~~~~~~~

Create an empty conda environment with the name that you prefer, here we've
chosen hvplot_dev. Activate and configure its channels to only use
``pyviz/label/dev`` and ``conda-forge``. The former is used to install the
development versions of the other HoloViz packages, such as HoloViews or Panel.

.. code-block:: sh

    conda install mamba -c conda-forge
    conda create -n hvplot_dev
    conda activate hvplot_dev
    conda config --env --append channels pyviz/label/dev --append channels conda-forge
    conda config --env --remove channels defaults

Since hvPlot interfaces with a large range of different libraries the
full test suite requires a wide range of dependencies. To make it
easier to install and run different parts of the test suite across
different platforms hvPlot uses a library called ``pyctdev`` to make things
more consistent and general. Specify also the desired Python version you want
to base your environment on.

You will need to pick a Python version. The best practice is to choose the minimum version
currently supported by hvPlot on the main development branch. If you cannot get the minimum
version installed, then try with a more recent version of Python.

.. code-block:: sh

    mamba install python=3.x pyctdev

Finally to install the dependencies required to run the full unit test
suite and all the examples:

.. code-block:: sh

    doit develop_install -o tests -o examples --conda-mode mamba

Add ``-o doc`` if you want to install the dependencies required to build
the website.

Setting up pre-commit
~~~~~~~~~~~~~~~~~~~~~

hvPlot uses ``pre-commit`` to automatically apply linting to hvPlot code.
If you intend to contribute to hvPlot we recommend you enable it with:

.. code-block:: sh

    pre-commit install

This will ensure that every time you make a commit linting will automatically be applied.

.. _devguide_python_setup:

Commands
--------

You can list the available `doit` commands with `doit list`.

.. code-block:: sh

    $ doit list
    build_docs             build docs
    develop_install        python develop install, with specified optional groups of dependencies (installed by conda only).
    ecosystem_setup        Common conda setup (must be run in base env).
    env_capture            Report all information required to recreate current conda environment
    env_create             Create named environment if it doesn't already exist
    env_dependency_graph   Write out dependency graph of named environment.
    env_export             Generate a pinned environment.yaml from specified env, filtering
    env_export2
    list_envs
    miniconda_download     Download Miniconda3-latest
    miniconda_install      Install Miniconda3-latest to location if not already present
    package_build          Build and then test conda.recipe/ (or specified alternative).
    package_test           Test existing package
    package_upload         Upload package built from conda.recipe/ (or specified alternative).
    pip_on_conda           Experimental: provide pip build env via conda
    test_all               Run all tests
    test_examples          Test that default examples run
    test_flakes            Flake check python and notebooks
    test_unit              Run unit tests with coverage

You can learn more about using `doit` on the `DoIt`_ web site.

Next Steps
----------

If you have any problems with the steps here, please `contact the developers`_.

.. _Anaconda: https://anaconda.com/downloads
.. _contact the developers: https://gitter.im/pyviz/pyviz
.. _conda package manager: https://conda.io/docs/intro.html
.. _conda documentation: https://conda.io/docs/index.html
.. _Download conda: https://conda.io/docs/download.html
.. _Git: https://git-scm.com
.. _GitHub: https://github.com
.. _Installing Git: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git
.. _Pro Git Book: https://git-scm.com/book/en/v2
.. _DoIt: https://pydoit.org/


.. toctree::
    :titlesonly:
    :hidden:
    :maxdepth: 2

    Getting Set up <self>
    Testing <testing>
