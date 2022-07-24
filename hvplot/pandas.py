"""
hvPlot makes data analysis and visualization simple
===================================================

hvPlot provides an easy to use, high-level, extended 🐼 Pandas .plot like API
that works across a wide range of data sources and plotting backends.

hvPlot

- supports a wide range of data sources including Pandas, Dask, XArray
Rapids cuDF, Streamz, Intake, Geopandas, NetworkX and Ibis.
- supports the plotting backends Bokeh (default), Matplotlib and Plotly.
- is build on top of HoloViews and allows you to drop into HoloViews when
more flexibility and power is needed.

To learn more check out https://hvplot.holoviz.org/. To report issues or contribute check out
https://github.com/holoviz/hvplot. To join the community check out
https://discourse.holoviz.org/.

How to use hvPlot in 3 simple steps
-----------------------------------

Work with the data source you already know and ❤️

>>> import pandas as pd, numpy as np
>>> idx = pd.date_range('1/1/2000', periods=1000)
>>> df  = pd.DataFrame(np.random.randn(1000, 4), index=idx, columns=list('ABCD')).cumsum()

Import the hvplot extension for your data source

>>> import hvplot.pandas

Use the `.hvplot` api as you would use the Pandas `.plot` api.

>>> curves=df.hvplot()
>>> curves

In a Jupyter Notebook, this will provide you with a plot of the
A, B, C and D time series.

For more check out the user guide https://hvplot.holoviz.org/user_guide/index.html

How to select the kind of plot
------------------------------

You can add the `kind` argument

>>> df.hvplot(kind="scatter")

or use the specific kind of plot method

>>> df.hvplot.scatter()

For the available kinds of plots check out the reference gallery
https://hvplot.holoviz.org/reference/index.html

How to get help
---------------

To see the available arguments for a specific kind of plot run

>>> hvplot.help(kind='scatter')

In a notebook or ipython environment tab completion will also be able to
provide you with the list of available arguments for your data source and
plotting backend.

How to export
-------------

>>> hvplot.save(curves, filename="curves.html")

For more check out https://hvplot.holoviz.org/user_guide/Viewing.html#saving-plots

How to drop into HoloViews
--------------------------

You don't have to do anything special as a hvPlot object is already a HoloViews
object.

You can understand the structure of your objects as usual by printing them

>>> print(curves)
:NdOverlay   [Variable]
   :Curve   [index]   (value)

and list the available options using `hv.help´.

>>> import holoviews as hv
>>> hv.extension("bokeh")
>>> hv.help(curves)

# Todo: fix https://github.com/holoviz/holoviews/issues/5364

How to create data apps
-----------------------

You can create powerful data apps by combining with Panel.

>>> import panel as pn
>>> pn.pane.HoloViews(curves, sizing_mode="stretch_both").servable()

Then run `panel serve script.py --autoreload --show`. This will open the plot in your browser. When
you save the script, the browser will reload. This speeds up your development process.

For more check out https://panel.holoviz.org/reference/panes/HoloViews.html
"""
from .interactive  import Interactive

def patch(name='hvplot', interactive='interactive', extension='bokeh', logo=False):
    from . import hvPlotTabular, post_patch

    try:
        import pandas as pd
    except:
        raise ImportError('Could not patch plotting API onto pandas. '
                          'Pandas could not be imported.')
    _patch_plot = lambda self: hvPlotTabular(self)
    _patch_plot.__doc__ = hvPlotTabular.__call__.__doc__
    plot_prop = property(_patch_plot)
    setattr(pd.DataFrame, name, plot_prop)
    setattr(pd.Series, name, plot_prop)

    _patch_interactive = lambda self: Interactive(self)
    _patch_interactive.__doc__ = Interactive.__call__.__doc__
    interactive_prop = property(_patch_interactive)
    setattr(pd.DataFrame, interactive, interactive_prop)
    setattr(pd.Series, interactive, interactive_prop)

    post_patch(extension, logo)

patch()
