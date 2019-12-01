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
testing. Many of these are on the main Anaconda default channel.

Conda Environments
~~~~~~~~~~~~~~~~~~

Since hvPlot interfaces with a large range of different libraries the
full test suite requires a wide range of dependencies. To make it
easier to install and run different parts of the test suite across
different platforms hvPlot uses a library called pyctdev to make things
more consistent and general.

.. code-block:: sh

    conda create -n hvplot_dev -c pyviz pyctdev python=3.6

Specify the desired Python version, currently hvPlot officially
supports Python 2.7, 3.5, 3.6 and 3.7. Once the environment has been
created you can activate it with:

.. code-block:: sh

    conda activate hvplot_dev

Finally to install the dependencies required to run the full unit test
suite and all the examples:

.. code-block:: sh

    doit develop_install -c pyviz/label/dev -o all

.. _devguide_python_setup:


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


.. toctree::
    :titlesonly:
    :hidden:
    :maxdepth: 2

    Getting Set up <index>
    Testing <testing>
