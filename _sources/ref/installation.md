# Installation

This page lists the primary sources from which hvPlot can be installed.

## From PyPI

hvPlot is distributed on [PyPI](https://pypi.org/project/hvplot/) as a wheel and as a source distribution (sdist).

::::{tab-set}

:::{tab-item} pip

```
pip install hvplot
```

:::

:::{tab-item} uv

```
uv pip install hvplot
```

::::

Pre-releases (alpha, beta, release candidate) can also be installed from PyPI.

::::{tab-set}

:::{tab-item} pip

```
pip install hvplot --pre
```

:::

:::{tab-item} uv

```
uv pip install hvplot --prerelease allow
```

::::

## From anaconda.org

hvPlot is distributed on 3 channels on [anaconda.org](https://anaconda.org/):

- [`conda-forge`](https://github.com/conda-forge/hvplot-feedstock): Community maintained channel
- [`defaults`](https://github.com/AnacondaRecipes/hvplot-feedstock/): Anaconda maintained channel (free under certain conditions only, check Anaconda's Terms of Services)
- `pyviz`: HoloViz' custom channel

We recommend installing final releases either from `conda-forge` or `defaults`. Pre-releases are only available from the `pyviz/label/dev` subchannel.

hvPlot can be installed from these channels using [conda](https://docs.conda.io), [pixi](https://pixi.sh), [mamba/micromamba](https://mamba.readthedocs.io), etc.

::::{tab-set}

:::{tab-item} `conda-forge`

```
conda install conda-forge::hvplot
```

:::

:::{tab-item} `defaults`

```
conda install defaults::hvplot
```

:::

:::{tab-item} Pre-releases from `pyviz/label/dev`

```
conda install pyviz/label/dev::hvplot
```

:::

::::

## From Anaconda Distribution

If you just started with Python and programming in general, an easy way to install hvPlot on your computer is to download and install the [Anaconda Distribution](https://www.anaconda.com/download) that includes most of the HoloViz packages. Note it is subject to Anaconda's Terms of Services.

## From source

hvPlot can be installed from source by cloning its [GitHub repository](https://github.com/holoviz/hvplot) and running this command:

```
pip install -e .
```
