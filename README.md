# hvPlot makes data analysis and visualization simple <img src="https://github.com/holoviz/hvplot/blob/master/doc/_static/logo.png?raw=true" style="width:2em;margin-bottom:-15px">

[Home](https://hvplot.holoviz.org/) | [Installation instructions](#installation-instructions) | [Getting Started Guide](https://hvplot.holoviz.org/user_guide/index.html) | [Reference Guides](https://hvplot.holoviz.org/reference/index.html) | [Examples](https://hvplot.holoviz.org/topics.html) | [Download Notebooks](https://downgit.github.io/#/home?url=https://github.com/holoviz/hvplot/tree/master/examples)| [Run Notebooks on Binder](https://mybinder.org/v2/gh/holoviz/hvplot/v0.8.0?urlpath=lab/tree/examples) | [License](#license) | [Support](#support--feedback)

## hvPlot provides a familiar, high-level API for visualization

The API is based on the familiar 🐼 Pandas `.plot()` API and the innovative `.interactive` API.

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

To get started check out the [installation instructions](#installation-instructions), [user guide](https://hvplot.holoviz.org/user_guide/index.html) or the [live user guide on Binder](https://mybinder.org/v2/gh/holoviz/hvplot/v0.8.0?urlpath=lab/tree/examples/user_guide/Introduction.ipynb).

## How to make your data pipeline  `.interactive`

Just add `.interactive()` and replace your normal arguments with [Panel](https://panel.holoviz.org) widgets.

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
import hvplot
hvplot.help(kind='scatter')
```

In a notebook or ipython environment the usual

- `help` and `?` will provide you with documentation.
- `TAB` and `SHIFT+TAB` completion will help you navigate.

## Examples

[<img src="http://blog.holoviz.org/images/hvplot_collage.png" style="max-height:400px;border-radius:2%;">](https://hvplot.holoviz.org/topics.html)

## License

hvPlot is completely free and open-source and licensed under the [BSD 3-Clause License](https://opensource.org/licenses/BSD-3-Clause).

## Support & Feedback

| Type                     | Channel                                              |
| ------------------------ | ------------------------------------------------------ |
| 🐛&nbsp; **Bug Reports**       | <a href="https://github.com/holoviz/hvplot/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+label%3Abug+sort%3Areactions-%2B1-desc+" title="Open Bug Report"><img src="https://img.shields.io/github/issues/holoviz/hvplot/bug.svg?label=bug"></a>                                 |
| 🎁&nbsp; **Feature Requests**  | <a href="https://github.com/holoviz/hvplot/issues?q=is%3Aopen+is%3Aissue+label%3Afeature+sort%3Areactions-%2B1-desc" title="Open Feature Request"><img src="https://img.shields.io/github/issues/holoviz/hvplot/feature.svg?label=feature%20request"></a>                                 |
| 👩&nbsp; **Usage Questions**   |  <a href="https://discourse.holoviz.org/" title="Open Support Request"> <img src="https://img.shields.io/discourse/status?server=https%3A%2F%2Fdiscourse.holoviz.org"></a> |
| 👩‍💻&nbsp; **Developer Questions**   |  <a href="https://gitter.im/pyviz/pyviz" title="Discuss with developers"> <img src="https://img.shields.io/gitter/room/TechnologyAdvice/Stardust.svg"></a> |
| 📢&nbsp; **Announcements**  | <a href="https://twitter.com/HoloViz_org" title="Follow hvPlot on Twitter"><img src="https://img.shields.io/twitter/follow/HoloViz_org.svg?style=social&label=Follow"> |

Reach out on [Gitter](https://gitter.im/pyviz/pyviz) if you would like to join the weekly triaging or bi-weekly HoloViz call.

## Project Status

|    |    |
| --- | --- |
| Build Status | [![Build Status](https://github.com/holoviz/hvplot/workflows/tests/badge.svg?query=branch%3Amaster)](https://github.com/holoviz/hvplot/actions?query=workflow%3Atests+branch%3Amaster) |
| Coverage | [![codecov](https://codecov.io/gh/holoviz/hvplot/branch/master/graph/badge.svg)](https://codecov.io/gh/holoviz/hvplot) |
| Latest dev release | [![Github tag](https://img.shields.io/github/tag/holoviz/hvplot.svg?label=tag&colorB=11ccbb)](https://github.com/holoviz/hvplot/tags) [![dev-site](https://img.shields.io/website-up-down-green-red/https/pyviz-dev.github.io/hvplot.svg?label=dev%20website)](https://pyviz-dev.github.io/hvplot/) |
| Latest release | [![Github release](https://img.shields.io/github/release/holoviz/hvplot.svg?label=tag&colorB=11ccbb)](https://github.com/holoviz/hvplot/releases) [![PyPI version](https://img.shields.io/pypi/v/hvplot.svg?colorB=cc77dd)](https://pypi.python.org/pypi/hvplot) [![hvplot version](https://img.shields.io/conda/v/pyviz/hvplot.svg?colorB=4488ff&style=flat)](https://anaconda.org/pyviz/hvplot) [![conda-forge version](https://img.shields.io/conda/v/conda-forge/hvplot.svg?label=conda%7Cconda-forge&colorB=4488ff)](https://anaconda.org/conda-forge/hvplot) [![defaults version](https://img.shields.io/conda/v/anaconda/hvplot.svg?label=conda%7Cdefaults&style=flat&colorB=4488ff)](https://anaconda.org/anaconda/hvplot) |
| Python | [![Python support](https://img.shields.io/pypi/pyversions/hvplot.svg)](https://pypi.org/project/hvplot/) |
| Docs | [![gh-pages](https://img.shields.io/github/last-commit/holoviz/hvplot/gh-pages.svg)](https://github.com/holoviz/hvplot/tree/gh-pages) [![site](https://img.shields.io/website-up-down-green-red/http/hvplot.holoviz.org.svg)](http://hvplot.holoviz.org) |