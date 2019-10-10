.. _devguide_testing:

Testing
=======

This chapter describes how to run various tests locally in a
development environment, guidelines for writing tests, and information
regarding the continuous testing infrastructure.

.. contents::
    :local:
    :depth: 2

Running Tests Locally
---------------------

Before attempting to run hvPlot tests, make sure you have successfully
run through all of the instructions in the :ref:`devguide_setup`
section of the Developer's Guide.

Test Selection
~~~~~~~~~~~~~~

Currently hvPlot uses linting and two types of tests: regular unit tests
which are run with nose and notebook example tests run with nbsmoke:

To run flake checking use:

.. code-block:: sh

    doit test_flakes

To run unit tests use:

.. code-block:: sh

    doit test_unit

To run example smoke tests use:

.. code-block:: sh

    doit test_examples

Integration tests
~~~~~~~~~~~~~~~~~

Writing Tests
-------------

In order to help keep hvPlot maintainable, all Pull Requests that touch
code should normally be accompanied by relevant tests. While
exceptions may be made for specific circumstances, the default
assumption should be that a Pull Request without tests may not be
merged.

Python Unit Tests
~~~~~~~~~~~~~~~~~

Python unit tests maintain the basic functionality of the Python
portion of the hvPlot library. A few general guidelines will help you
write Python unit tests:

absolute imports
    In order to ensure that hvPlot's unit tests as relocatable and unambiguous
    as possible, always prefer absolute imports in test files. When convenient,
    import and use the entire module under test:

    * **GOOD**: ``import hvplot.pandas``
    * **GOOD**: ``from hvplot.plotting import HvPlotTabular``
    * **BAD**: ``from ..plotting import HvPlotTabular``


Continuous Integration
----------------------

Every push to the `master` branch or any Pull Request branch on GitHub
automatically triggers a full test build on the `TravisCI`_ continuous
integration service. This is most often useful for running the full hvPlot
test suite continuously, but also triggers automated scripts for publishing
releases when a tagged branch is pushed.

You can see the list of all current and previous builds at this URL:
https://travis-ci.org/pyviz/hvplot

Configuration
~~~~~~~~~~~~~

There are a number of files that affect the build configuration:

* `.travis.yml`
    Defines the build matrix and global configurations for the stages
    described below.

* `conda.recipe/meta.yaml`
    Instructions for building a conda noarch package for hvPlot.

* `setup.py`
    Used to build sdist packages and "dev" installs. This file is the
    single source of truth of all dependencies.

* `tox.ini`
    Contains the configuration for the doit commands .

Etiquette
~~~~~~~~~

TravisCI provides five free build workers to Open Source projects. A few
considerations will help you be considerate of others needing these limited
resources:

* Group commits into meaningful chunks of work before pushing to GitHub (i.e.
  don't push on every commit).

* If you must make multiple commits in succession, navigate to TravisCI and
  cancel all but the last build, in order to free up build workers.

* If expensive ``examples`` tests are not needed (e.g. for a docs-only Pull
  Request), they may be disabled by adding the text

  .. code-block:: none

    [ci disable examples]

  to your commit message.

.. _contact the developers: https://gitter.im/pyviz/pyviz
.. _pytest: https://docs.pytest.org
.. _TravisCI: https://travis-ci.org/
