# hvPlot makes data analysis and visualization simple <img src="https://github.com/holoviz/hvplot/blob/master/doc/_static/logo.png?raw=true" style="width:2em;margin-bottom:-15px">

|    |    |
| --- | --- |
| Build Status | [![Build Status](https://github.com/holoviz/hvplot/workflows/tests/badge.svg?query=branch%3Amaster)](https://github.com/holoviz/hvplot/actions?query=workflow%3Atests+branch%3Amaster) |
| Coverage | [![codecov](https://codecov.io/gh/holoviz/hvplot/branch/master/graph/badge.svg)](https://codecov.io/gh/holoviz/hvplot) |
| Latest dev release | [![Github tag](https://img.shields.io/github/tag/holoviz/hvplot.svg?label=tag&colorB=11ccbb)](https://github.com/holoviz/hvplot/tags) [![dev-site](https://img.shields.io/website-up-down-green-red/https/pyviz-dev.github.io/hvplot.svg?label=dev%20website)](https://pyviz-dev.github.io/hvplot/) |
| Latest release | [![Github release](https://img.shields.io/github/release/holoviz/hvplot.svg?label=tag&colorB=11ccbb)](https://github.com/holoviz/hvplot/releases) [![PyPI version](https://img.shields.io/pypi/v/hvplot.svg?colorB=cc77dd)](https://pypi.python.org/pypi/hvplot) [![hvplot version](https://img.shields.io/conda/v/pyviz/hvplot.svg?colorB=4488ff&style=flat)](https://anaconda.org/pyviz/hvplot) [![conda-forge version](https://img.shields.io/conda/v/conda-forge/hvplot.svg?label=conda%7Cconda-forge&colorB=4488ff)](https://anaconda.org/conda-forge/hvplot) [![defaults version](https://img.shields.io/conda/v/anaconda/hvplot.svg?label=conda%7Cdefaults&style=flat&colorB=4488ff)](https://anaconda.org/anaconda/hvplot) |
| Python | [![Python support](https://img.shields.io/pypi/pyversions/hvplot.svg)](https://pypi.org/project/hvplot/) |
| Docs | [![gh-pages](https://img.shields.io/github/last-commit/holoviz/hvplot/gh-pages.svg)](https://github.com/holoviz/hvplot/tree/gh-pages) [![site](https://img.shields.io/website-up-down-green-red/http/hvplot.holoviz.org.svg)](https://hvplot.holoviz.org) |
| Binder | [![Binder](https://img.shields.io/badge/launch%20v0.8.0-binder-579aca.svg?logo=data:image/png;base64,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)](https://mybinder.org/v2/gh/holoviz/hvplot/v0.8.0?urlpath=lab/tree/examples) |
| Support | [![Discourse](https://img.shields.io/discourse/status?server=https%3A%2F%2Fdiscourse.holoviz.org)](https://discourse.holoviz.org/c/hvplot/8) |

[Home](https://hvplot.holoviz.org/) | [Installation instructions](#installation-instructions) | [Getting Started Guide](https://hvplot.holoviz.org/user_guide/index.html) | [Reference Guides](https://hvplot.holoviz.org/reference/index.html) | [Examples](#examples) | [License](#license) | [Support](#support--feedback)

## hvPlot provides a familiar, high-level API for visualization

The API is based on the familiar 🐼 Pandas `.plot` API and the innovative `.interactive` API.

<img src="https://github.com/MarcSkovMadsen/awesome-panel-assets/blob/master/images/hvPlot/hvplot-total-intro.gif?raw=true" style="max-height:600px;border-radius:2%;">

## hvPlot works with the tools you know and ❤️

hvPlot

- supports a wide range of data sources including [Pandas](http://pandas.pydata.org), [XArray](http://xarray.pydata.org), [Dask](http://dask.pydata.org), [Streamz](http://streamz.readthedocs.io), [Intake](http://github.com/ContinuumIO/intake), [GeoPandas](http://geopandas.org) and [NetworkX](https://networkx.github.io/documentation/stable/).
- supports the plotting backends [Bokeh](https://docs.bokeh.org/en/latest/), [Matplotlib](https://matplotlib.org/) and [Plotly](https://plotly.com/python/).
- exposes the powerful tools from the [HoloViz](https://holoviz.org/) ecosystem in a familiar and convenient API.

[<img src="https://hvplot.holoviz.org/assets/diagram.svg" style="max-height:400px;border-radius:2%;"/>](https://holoviz.org/)

hvPlot is **the recommended entrypoint to the HoloViz ecosystem**.

## hvPlot can be used for exploration, reporting and data apps

Check out [this blog post](https://towardsdatascience.com/the-easiest-way-to-create-an-interactive-dashboard-in-python-77440f2511d1) to see how easy it is to create an interactive dashboard with hvPlot and Panel.

<a href="https://towardsdatascience.com/the-easiest-way-to-create-an-interactive-dashboard-in-python-77440f2511d1"><img src="https://miro.medium.com/max/700/1*bZjPtucT8O1esjQaGQenHw.gif" style="max-height:600px;border-radius:2%;"></a>

## Installation Instructions

hvPlot supports Python 3.6, 3.7, 3.8, 3.9 and 3.10 on Linux, Windows, or Mac and can be installed with ``conda``:

```bash
conda install -c pyviz hvplot
```

or with ``pip``:

```bash
pip install hvplot
```

You can download the guides and example notebooks as a `.zip` file by clicking this
[link](https://downgit.github.io/#/home?url=https://github.com/holoviz/hvplot/tree/master/examples).

Please note that for versions of `jupyterlab<3.0`, you must install the JupyterLab extension manually with:

```bash
jupyter labextension install @pyviz/jupyterlab_pyviz
```

## How to use hvPlot in 3 simple steps

Work with the data source you already know and ❤️

```python
import pandas as pd, numpy as np
idx = pd.date_range('1/1/2000', periods=1000)
df  = pd.DataFrame(np.random.randn(1000, 4), index=idx, columns=list('ABCD')).cumsum()
```

Import the hvplot extension for your data source and optionally set the plotting backend

```python
import hvplot.pandas
# Optional: hvplot.extension('matplotlib') or hvplot.extension('plotly')
```

Use the `.hvplot` API as you would use the Pandas `.plot` API.

```python
df.hvplot()
```

[<img src="https://github.com/MarcSkovMadsen/awesome-panel-assets/blob/master/images/hvPlot/hvplot-intro-plot.gif?raw=true" style="max-height:300px;border-radius:2%;">](https://hvplot.holoviz.org/user_guide/index.html)

To get started check out the [user guide](https://hvplot.holoviz.org/user_guide/index.html) or the [live user guide on Binder](https://mybinder.org/v2/gh/holoviz/hvplot/v0.8.0?urlpath=lab/tree/examples/user_guide/Introduction.ipynb).

## How to make your data pipeline  `.interactive`

Just add `.interactive` and replace your normal arguments with [Ipywidgets](https://ipywidgets.readthedocs.io/en/stable/examples/Widget%20List.html) or [Panel widgets](https://panel.holoviz.org/reference/index.html#widgets).

```python
import panel as pn
pn.extension()

df.interactive(width=600).head(n=pn.widgets.IntSlider(start=1, end=5, value=3))
```

[<img src="https://github.com/MarcSkovMadsen/awesome-panel-assets/blob/master/images/hvPlot/hvplot-intro-interactive.gif?raw=true" style="max-height:300px;border-radius:2%;">](https://hvplot.holoviz.org/user_guide/Interactive.html)

To get started check out the [`.interactive` guide](https://hvplot.holoviz.org/user_guide/Interactive.html) or the [live `.interactive` guide on Binder](https://mybinder.org/v2/gh/holoviz/hvplot/v0.8.0?urlpath=lab/tree/examples/user_guide/Interactive.ipynb).

## How to find documentation from your notebook or editor

To see the available arguments for a specific `kind` of plot run

```python
hvplot.help(kind='scatter')
```

In a notebook or ipython environment the usual

- `help` and `?` will provide you with documentation.
- `TAB` and `SHIFT+TAB` completion will help you navigate.

## Examples

[Download](https://downgit.github.io/#/home?url=https://github.com/holoviz/hvplot/tree/master/examples) | [Run on Binder](https://mybinder.org/v2/gh/holoviz/hvplot/v0.8.0?urlpath=lab/tree/examples) | [View Gallery](https://hvplot.holoviz.org/topics.html)

[<img src="http://blog.holoviz.org/images/hvplot_collage.png" style="max-height:400px;border-radius:2%;">](https://hvplot.holoviz.org/topics.html)

## License

hvPlot is completely free and open-source. It is licensed under the [BSD 3-Clause License](https://opensource.org/licenses/BSD-3-Clause).

## Support & Feedback

| Type                     | Channel                                              |
| ------------------------ | ------------------------------------------------------ |
| 🐛&nbsp; **Bug Reports**       | <a href="https://github.com/holoviz/hvplot/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+label%3Abug+sort%3Areactions-%2B1-desc+" title="Open Bug Report"><img src="https://img.shields.io/github/issues/holoviz/hvplot/bug.svg?label=bug"></a>                                 |
| 🎁&nbsp; **Feature Requests**  | <a href="https://github.com/holoviz/hvplot/issues?q=is%3Aopen+is%3Aissue+label%3Afeature+sort%3Areactions-%2B1-desc" title="Open Feature Request"><img src="https://img.shields.io/github/issues/holoviz/hvplot/feature.svg?label=feature%20request"></a>                                 |
| 👩&nbsp; **Usage Questions**   |  <a href="https://discourse.holoviz.org/" title="Open Support Request"> <img src="https://img.shields.io/discourse/status?server=https%3A%2F%2Fdiscourse.holoviz.org"></a> |
| 👩‍💻&nbsp; **Developer Questions**   |  <a href="https://gitter.im/pyviz/pyviz" title="Discuss with developers"> <img src="https://img.shields.io/gitter/room/TechnologyAdvice/Stardust.svg"></a> |
| 📢&nbsp; **Announcements**  | <a href="https://twitter.com/HoloViz_org" title="Follow hvPlot on Twitter"><img src="https://img.shields.io/twitter/follow/HoloViz_org.svg?style=social&label=Follow"> |

## Contributions

We would ❤️ to work with you no matter whether you want to contribute to issue management, PRs, documentation, blog posts, community support or social media communication.

To get started with the code or docs check out the [Developer Guide](https://hvplot.holoviz.org/developer_guide/index.html).

Reach out on [Gitter](https://gitter.im/pyviz/pyviz) to discuss with the developers, join the weekly triaging or join the bi-weekly HoloViz call.
