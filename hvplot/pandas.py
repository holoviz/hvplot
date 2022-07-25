"""
hvPlot makes data analysis and visualization simple
===================================================

hvPlot provides an easy to use, high-level, extended 🐼 Pandas .plot like API
that works across a wide range of data sources and plotting backends.

hvPlot

- supports a wide range of data sources including Pandas, Dask, XArray
Rapids cuDF, Streamz, Intake, Geopandas, NetworkX and Ibis.
- supports the plotting backends Bokeh (default), Matplotlib and Plotly.
- is built on top of HoloViews and allows you to drop into the rest of the
HoloViz ecosystem when more power or flexibility is needed.

To learn more check out https://hvplot.holoviz.org/. To report issues or contribute go to
https://github.com/holoviz/hvplot. To join the community go to
https://discourse.holoviz.org/.

How to use hvPlot in 3 simple steps
-----------------------------------

Work with the data source you already know and ❤️

>>> import pandas as pd, numpy as np
>>> idx = pd.date_range('1/1/2000', periods=1000)
>>> df  = pd.DataFrame(np.random.randn(1000, 4), index=idx, columns=list('ABCD')).cumsum()

Import the hvplot extension for your data source

>>> import hvplot.pandas

Use the `.hvplot` API as you would use the Pandas `.plot` API.

>>> curves = df.hvplot()
>>> curves

In a Jupyter Notebook, this will display a line plot of the
A, B, C and D time series.

For more check out the user guide https://hvplot.holoviz.org/user_guide/index.html

How to get help
---------------

To see the available arguments for a specific `kind` of plot run

>>> import hvplot
>>> hvplot.help(kind='scatter')

In a notebook or ipython environment the usual

- `help` and `?` will provide you with documentation.
- `TAB` and `SHIFT+TAB` completion will help you navigate.
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
