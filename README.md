# hvPlot makes data analysis and visualization simple <img src="https://github.com/holoviz/hvplot/blob/main/doc/_static/logo.png?raw=true" style="width:2em;margin-bottom:-15px">

|    |    |
| --- | --- |
| Downloads | ![https://pypistats.org/packages/hvplot](https://img.shields.io/pypi/dm/hvplot?label=pypi) ![https://anaconda.org/pyviz/hvplot](https://pyviz.org/_static/cache/hvplot_conda_downloads_badge.svg)
| Build Status | [![Build Status](https://github.com/holoviz/hvplot/workflows/tests/badge.svg?query=branch%3Amain)](https://github.com/holoviz/hvplot/actions?query=workflow%3Atests+branch%3Amain) |
| Coverage | [![codecov](https://codecov.io/gh/holoviz/hvplot/branch/main/graph/badge.svg)](https://codecov.io/gh/holoviz/hvplot) |
| Latest dev release | [![Github tag](https://img.shields.io/github/tag/holoviz/hvplot.svg?label=tag&colorB=11ccbb)](https://github.com/holoviz/hvplot/tags) [![dev-site](https://img.shields.io/website-up-down-green-red/https/holoviz-dev.github.io/hvplot.svg?label=dev%20website)](https://holoviz-dev.github.io/hvplot/) |
| Latest release | [![Github release](https://img.shields.io/github/release/holoviz/hvplot.svg?label=tag&colorB=11ccbb)](https://github.com/holoviz/hvplot/releases) [![PyPI version](https://img.shields.io/pypi/v/hvplot.svg?colorB=cc77dd)](https://pypi.python.org/pypi/hvplot) [![hvplot version](https://img.shields.io/conda/v/pyviz/hvplot.svg?colorB=4488ff&style=flat)](https://anaconda.org/pyviz/hvplot) [![conda-forge version](https://img.shields.io/conda/v/conda-forge/hvplot.svg?label=conda%7Cconda-forge&colorB=4488ff)](https://anaconda.org/conda-forge/hvplot) [![defaults version](https://img.shields.io/conda/v/anaconda/hvplot.svg?label=conda%7Cdefaults&style=flat&colorB=4488ff)](https://anaconda.org/anaconda/hvplot) |
| Python | [![Python support](https://img.shields.io/pypi/pyversions/hvplot.svg)](https://pypi.org/project/hvplot/) |
| Docs | [![gh-pages](https://img.shields.io/github/last-commit/holoviz/hvplot/gh-pages.svg)](https://github.com/holoviz/hvplot/tree/gh-pages) [![site](https://img.shields.io/website-up-down-green-red/http/hvplot.holoviz.org.svg)](https://hvplot.holoviz.org) |
| Binder | [![Binder](https://img.shields.io/badge/launch%20v0.8.1-binder-579aca.svg?logo=data:image/png;base64,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)](https://mybinder.org/v2/gh/holoviz/hvplot/v0.8.1?urlpath=lab/tree) |
| Support | [![Discourse](https://img.shields.io/discourse/status?server=https%3A%2F%2Fdiscourse.holoviz.org)](https://discourse.holoviz.org/c/hvplot/8) |

[Home](https://hvplot.holoviz.org/) | [Installation instructions](#installation-instructions) | [Getting Started Guide](https://hvplot.holoviz.org/getting_started/index.html) | [Reference Guides](https://hvplot.holoviz.org/reference/index.html) | [Examples](#examples) | [License](#license) | [Support](#support--feedback)

## hvPlot provides a familiar, high-level API for visualization

The API is based on the familiar Pandas `.plot` API and the innovative `.interactive` API.

<img src="https://github.com/MarcSkovMadsen/awesome-panel-assets/blob/master/images/hvPlot/hvplot-total-intro.gif?raw=true" style="max-height:600px;border-radius:2%;">

## hvPlot works with the tools you know and love

hvPlot

- supports a wide range of data sources including [Pandas](http://pandas.pydata.org), [Polars](https://docs.pola.rs/), [XArray](http://xarray.pydata.org), [Dask](http://dask.pydata.org), [Streamz](http://streamz.readthedocs.io), [Intake](http://github.com/ContinuumIO/intake), [GeoPandas](http://geopandas.org) and [NetworkX](https://networkx.github.io/documentation/stable/).
- supports the plotting backends [Bokeh](https://docs.bokeh.org/en/latest/), [Matplotlib](https://matplotlib.org/) and [Plotly](https://plotly.com/python/).
- exposes the powerful tools from the [HoloViz](https://holoviz.org/) ecosystem in a familiar and convenient API.

[<img src="https://hvplot.holoviz.org/assets/diagram.svg" style="max-height:400px;border-radius:2%;"/>](https://holoviz.org/)

hvPlot is **the simplest way to benefit from the [HoloViz](https://holoviz.org/) ecosystem for data exploration**.

## hvPlot can be used for exploration, reporting and data apps

Check out [this blog post](https://towardsdatascience.com/the-easiest-way-to-create-an-interactive-dashboard-in-python-77440f2511d1) to see how easy it is to create an interactive dashboard with hvPlot and Panel.

<a href="https://towardsdatascience.com/the-easiest-way-to-create-an-interactive-dashboard-in-python-77440f2511d1"><img src="https://miro.medium.com/max/700/1*bZjPtucT8O1esjQaGQenHw.gif" style="max-height:600px;border-radius:2%;"></a>

## Mini getting-started

Head over to the [getting started guide](https://hvplot.holoviz.org/getting_started/index.html) for more!

### Install

hvPlot can be installed on Linux, Windows, or Mac with ``conda``:

```bash
conda install hvplot
```

or with ``pip``:

```bash
pip install hvplot
```

Please note that for versions of `jupyterlab<3.0`, you must install the JupyterLab extension manually with:

```bash
jupyter labextension install @pyviz/jupyterlab_pyviz
```

### Plotting data

Work with your data source:

```python
import numpy as np
import pandas as pd

idx = pd.date_range('1/1/2000', periods=1000)
df  = pd.DataFrame(np.random.randn(1000, 4), index=idx, columns=list('ABCD')).cumsum()
```

Import the hvPlot extension for your data source and optionally set the plotting backend:

```python
import hvplot.pandas
# Optional: hvplot.extension('matplotlib') or hvplot.extension('plotly')
```

Use the `.hvplot` API as you would use the Pandas or Xarray `.plot` API:

```python
df.hvplot()
```

[<img src="https://github.com/MarcSkovMadsen/awesome-panel-assets/blob/master/images/hvPlot/hvplot-intro-plot.gif?raw=true" style="max-height:300px;border-radius:2%;">](https://hvplot.holoviz.org/user_guide/index.html)


### Interactive data apps

Just add `.interactive` and replace your normal arguments with [Panel widgets](https://panel.holoviz.org/reference/index.html#widgets) or [Ipywidgets](https://ipywidgets.readthedocs.io/en/stable/examples/Widget%20List.html).

```python
import panel as pn
pn.extension()

df.interactive(width=600).head(n=pn.widgets.IntSlider(start=1, end=5, value=3))
```

[<img src="https://github.com/MarcSkovMadsen/awesome-panel-assets/blob/master/images/hvPlot/hvplot-intro-interactive.gif?raw=true" style="max-height:300px;border-radius:2%;">](https://hvplot.holoviz.org/user_guide/Interactive.html)

### How to find documentation from your notebook or editor

To see the available arguments for a specific `kind` of plot run

```python
hvplot.help(kind='scatter')
```

In a notebook or ipython environment the usual

- `help` and `?` will provide you with documentation.
- `TAB` and `SHIFT+TAB` completion will help you navigate.

## License

hvPlot is completely free and open-source. It is licensed under the [BSD 3-Clause License](https://opensource.org/licenses/BSD-3-Clause).

## Support & Feedback

- Usage questions and showcases -> [HoloViz Community](https://holoviz.org/community.html)
- Bug reports and feature requests -> [Github](https://github.com/holoviz/hvplot)
- Developer discussions -> [Discord](https://discord.gg/rb6gPXbdAr)

For more detail check out the [HoloViz Community Guide](https://holoviz.org/community.html).

## Contributions

We would love to work with you no matter whether you want to contribute to issue management, PRs, documentation, blog posts, community support or social media communication.

To get started with the code or docs check out the [Developer Guide](https://hvplot.holoviz.org/developer_guide/index.html).
