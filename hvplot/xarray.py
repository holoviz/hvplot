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

>>> import xarray as xr
>>> air_ds = xr.tutorial.open_dataset('air_temperature').load()
>>> air = air_ds.air
>>> air1d = air.sel(lat=40, lon=285)

Import the hvplot extension for your data source

>>> import hvplot.xarray  # noqa

Use the `.hvplot` api as you would use the Pandas `.plot` api.

>>> curve=air1d.hvplot()
>>> curve

In a Jupyter Notebook, this will provide you with a plot of the
air temperature time series.

For more check out the user guide https://hvplot.holoviz.org/user_guide/index.html and the
introduction to working with gridded data https://hvplot.holoviz.org/user_guide/Gridded_Data.html.

How to select the kind of plot
------------------------------

You can add the `kind` argument

>>> air1d.hvplot(kind="scatter")

or use the specific kind of plot method

>>> air1d.hvplot.scatter()

For the available kinds of plots check out the reference gallery
https://hvplot.holoviz.org/reference/index.html

How to get help
---------------

To see the available arguments for a specific kind of plot run

>>> hvplot.help(kind='scatter')

In a notebook or ipython environment TAB and SHIFT+TAB completion will help you
navigate and learn.

How to export
-------------

>>> hvplot.save(curve, filename="curve.html")

For more check out https://hvplot.holoviz.org/user_guide/Viewing.html#saving-plots

How to drop into HoloViews
--------------------------

You don't have to do anything special as a hvPlot object is already a HoloViews
object.

You can understand the structure of your objects as usual by printing them

>>> print(curve)
:Curve   [time]   (air)

and list the available options using `hv.help´.

>>> import holoviews as hv
>>> hv.extension("bokeh")
>>> hv.help(curve)

# Todo: fix https://github.com/holoviz/holoviews/issues/5364

How to create data apps
-----------------------

You can create powerful data apps by combining with Panel.

>>> import panel as pn
>>> pn.pane.HoloViews(curve, sizing_mode="stretch_both").servable()

Then run `panel serve script.py --autoreload --show`. This will open the plot in your browser. When
you save the script, the browser will reload. This speeds up your development process.

For more check out https://panel.holoviz.org/reference/panes/HoloViews.html
"""
import xarray as xr

from panel.widgets import Widget

from .interactive import Interactive


class XArrayInteractive(Interactive):

    @classmethod
    def applies(cls, obj):
        return isinstance(obj, (xr.DataArray, xr.Dataset))

    def sel(self, **kwargs):
        processed = {}
        for k, v in kwargs.items():
            if isinstance(v, type) and issubclass(v, Widget):
                if hasattr(v, 'end'):
                    values = self._current[k].values
                    v = v(name=k, start=values.min(), end=values.max())
                if hasattr(v, 'options'):
                    v = v(name=k, options={str(v): v for v in self._current[k].values})
            processed[k] = v
        self._method = 'sel'
        return self.__call__(**processed)

    sel.__doc__ = xr.DataArray.sel.__doc__

    def isel(self, **kwargs):
        processed = {}
        for k, v in kwargs.items():
            if isinstance(v, type) and issubclass(v, Widget):
                if hasattr(v, 'end'):
                    v = v(name=k, end=len(self._current[k]))
            processed[k] = v
        self._method = 'isel'
        return self.__call__(**processed)

    isel.__doc__ = xr.DataArray.isel.__doc__


def patch(name='hvplot', interactive='interactive', extension='bokeh', logo=False):
    from . import hvPlot, post_patch

    try:
        import xarray as xr
    except:
        raise ImportError('Could not patch plotting API onto xarray. '
                          'xarray could not be imported.')

    xr.register_dataset_accessor(name)(hvPlot)
    xr.register_dataarray_accessor(name)(hvPlot)
    xr.register_dataset_accessor(interactive)(XArrayInteractive)
    xr.register_dataarray_accessor(interactive)(XArrayInteractive)

    post_patch(extension, logo)

patch()
