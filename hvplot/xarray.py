from __future__ import absolute_import

import xarray as xr

from panel.widgets import Widget

from .interactive import Interactive


class XArrayInteractive(Interactive):

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
