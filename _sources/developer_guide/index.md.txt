(devguide-setup)=

# Developer Guide

```{contents}
:depth: 3
:local: true
```

## Set up

The hvPlot library is a complex project which provides a wide range
of data interfaces and an extensible set of plotting backends, which
means the development and testing process involves a wide set of
libraries.

If you have any problems with the steps here, please contact the developers on [Discord](https://discord.gg/AXRHnJU6sP).

### Preliminaries

#### Git

The hvPlot source code is stored in a [Git](https://git-scm.com) source control repository.
The first step to working on hvPlot is to install Git on to your system.
There are different ways to do this depending on whether, you are using
Windows, OSX, or Linux.

To install Git on any platform, refer to the [Installing Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) section of
the [Pro Git Book](https://git-scm.com/book/en/v2).

#### Conda (optional)

Developing hvPlot requires a wide range of dependencies that can all be installed with
the [conda package manager](https://conda.io). Using `conda` is sometimes the easiest way to install
a dependency (e.g. `graphviz`, Firefox drivers). However, these days most of the dependencies
required to develop hvPlot can be installed with `pip`.

Follow [these instructions](https://conda.io/projects/conda/user-guide/install/index.html) to download conda.

### Cloning the Repository

The source code for the hvPlot project is hosted on GitHub. To clone the
source repository, issue the following command:

```sh
git clone https://github.com/holoviz/hvplot.git
```

This will create a `hvplot` directory at your file system
location. This `hvplot` directory is referred to as the *source
checkout* for the remainder of this document.

(dev-guide-installing-dependencies)=

### Installing Dependencies

hvPlot requires many additional packages for development and
testing.

::::{tab-set}

:::{tab-item} pip

Start by creating a virtual environment with `venv`:

```
python -m venv .venv
```

Activate it:

```
# Linux/MacOs
source .venv/bin/activate
# Windows
.venv\Scripts\activate
```

Install the test dependencies:

``` bash
pip install --prefer-binary -e '.[tests, examples-tests, geo, hvdev, hvdev-geo, dev-extras]'
```

:::

:::{tab-item} conda

Create a development conda environment using one of the environment files present
in the `./envs` folder, and activate it:

``` bash
conda env create --file envs/py3.10-tests.yaml
conda activate hvplottests
```

:::

::::


### Setting up pre-commit

hvPlot uses `pre-commit` to automatically apply linting to hvPlot code.
If you intend to contribute to hvPlot we recommend you enable it with:

```sh
pre-commit install
```

This will ensure that every time you make a commit linting will automatically be applied.


## Testing

This chapter describes how to run various tests locally in a
development environment, guidelines for writing tests, and information
regarding the continuous testing infrastructure.

### Running Tests Locally

Before attempting to run hvPlot tests, make sure you have successfully
run through all of the instructions in the {ref}`devguide-setup`
section of the Developer's Guide.

Currently hvPlot uses linting two types of tests: regular unit tests
which are run with `pytest` and notebook example tests run with `pytest` and `nbval`:

Run the unit tests with:

```bash
pytest hvplot
pytest -v hvplot --geo  # include the test that require geo dependencies
```

Run the example tests with:

```sh
pytest -n auto --dist loadscope --nbval-lax -p no:python
```

### Writing Tests

In order to help keep hvPlot maintainable, all Pull Requests that touch
code should normally be accompanied by relevant tests. While
exceptions may be made for specific circumstances, the default
assumption should be that a Pull Request without tests may not be
merged.

Python unit tests maintain the basic functionality of the Python
portion of the hvPlot library. A few general guidelines will help you
write Python unit tests:

In order to ensure that hvPlot's unit tests as relocatable and unambiguous
as possible, always prefer absolute imports in test files. When convenient,
import and use the entire module under test:

- **Good**: `import hvplot.pandas`
- **Good**: `from hvplot.plotting import HvPlotTabular`
- **Bad**: `from ..plotting import HvPlotTabular`

### Continuous Integration (CI)

Every push to the `main` branch or any Pull Request branch on GitHub
automatically triggers a full test build on the [Github Action](https://github.com/holoviz/hvplot/actions) continuous
integration service. This is most often useful for running the full hvPlot
test suite continuously, but also triggers automated scripts for publishing
releases when a tagged branch is pushed.

When in doubt about what command to run, you can always inspect the Github
workflow files in the `./github/workflows` folder so see what commands
are running on the CI.

Github Action provides a limited number free build workers to Open Source projects.
Please be considerate of others and group commits into meaningful chunks of
work before pushing to GitHub (i.e. don't push on every commit).
