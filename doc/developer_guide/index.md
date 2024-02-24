(devguide-setup)=

# Getting Set Up

The hvPlot library is a complex project which provides a wide range
of data interfaces and an extensible set of plotting backends, which
means the development and testing process involves a wide set of
libraries.

```{contents}
:depth: 2
:local: true
```

% dev_guide_preliminaries:

## Preliminaries

### Git

The hvPlot source code is stored in a [Git] source control repository.
The first step to working on hvPlot is to install Git on to your system.
There are different ways to do this depending on whether, you are using
Windows, OSX, or Linux.

To install Git on any platform, refer to the [Installing Git] section of
the [Pro Git Book].

### Conda

Developing hvPlot requires a wide range of packages that are not
easily and quickly available using pip. To make this more manageable,
core developers rely heavily on the [conda package manager] for the
free [Anaconda] Python distribution. However, `conda` can also
install non-Python package dependencies, which helps streamline hvPlot
development greatly. It is *strongly* recommended that anyone
developing hvPlot also use `conda`, and the remainder of the
instructions will assume that `conda` is available.

To install Conda on any platform, see the [Download conda] section of the
[conda documentation].

## Cloning the Repository

The source code for the hvPlot project is hosted on [GitHub]. To clone the
source repository, issue the following command:

```sh
git clone https://github.com/holoviz/hvplot.git
```

This will create a `hvplot` directory at your file system
location. This `hvplot` directory is referred to as the *source
checkout* for the remainder of this document.

(dev-guide-installing-dependencies)=

## Installing Dependencies

hvPlot requires many additional packages for development and
testing.

### Conda Environments

Create an empty conda environment with the name that you prefer, here we've
chosen hvplot_dev. Activate and configure its channels to only use
`pyviz/label/dev` and `conda-forge`. The former is used to install the
development versions of the other HoloViz packages, such as HoloViews or Panel.

```sh
conda create -n hvplot_dev
conda activate hvplot_dev
conda config --env --append channels pyviz/label/dev --append channels conda-forge
conda config --env --remove channels defaults
```

Since hvPlot interfaces with a large range of different libraries the
full test suite requires a wide range of dependencies. To make it
easier to install and run different parts of the test suite across
different platforms hvPlot uses a library called `pyctdev` to make things
more consistent and general. Specify also the desired Python version you want
to base your environment on.

You will need to pick a Python version. The best practice is to choose the minimum version
currently supported by hvPlot on the main development branch. If you cannot get the minimum
version installed, then try with a more recent version of Python.

```sh
conda install python=3.x pyctdev
```

Finally to install the dependencies required to run the full unit test
suite and all the examples:

```sh
doit develop_install -o examples_tests -o tests -o examples_conda
```

Add `-o doc` if you want to install the dependencies required to build
the website.

### Setting up pre-commit

hvPlot uses `pre-commit` to automatically apply linting to hvPlot code.
If you intend to contribute to hvPlot we recommend you enable it with:

```sh
pre-commit install
```

This will ensure that every time you make a commit linting will automatically be applied.

(devguide-python-setup)=

## Commands

You can list the available `doit` commands with `doit list`.

## Next Steps

If you have any problems with the steps here, please [contact the developers].

```{toctree}
:hidden: true
:maxdepth: 2
:titlesonly: true

Getting Set up <self>
Testing <testing>
```

[anaconda]: https://anaconda.com/downloads
[conda documentation]: https://conda.io/docs/index.html
[conda package manager]: https://conda.io/docs/intro.html
[contact the developers]: https://gitter.im/pyviz/pyviz
[doit]: https://pydoit.org/
[download conda]: https://conda.io/docs/download.html
[git]: https://git-scm.com
[github]: https://github.com
[installing git]: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git
[pro git book]: https://git-scm.com/book/en/v2
