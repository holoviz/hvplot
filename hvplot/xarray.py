import xarray as xr

from panel.depends import bind
from panel.react import react
from panel.widgets import Widget
from panel.widgets.slider import _RangeSliderBase

from .interactive import Interactive
from .util import is_xarray

class sel:

    def __init__(self, interactive):
        self._interactive = interactive

    def __call__(self, *args, **kwargs):
        new = self._interactive._resolve_accessor()
        processed = {}
        for k, v in kwargs.items():
            if isinstance(v, type) and issubclass(v, Widget):
                if hasattr(v, 'end'):
                    min_val = self._interactive[k].values.min()
                    max_val = self._interactive[k].values.max()
                    if issubclass(v, _RangeSliderBase):
                        value = (min_val.eval(), max_val.eval())
                    else:
                        value = min_val.eval()
                    v = v(name=k, start=min_val, end=max_val, value=value)
                    if isinstance(v, _RangeSliderBase):
                        v = bind(lambda slc: slice(*slc), v)
                if hasattr(v, 'options'):
                    options = self._interactive[k].values.pipe(lambda vs: {str(v): v for v in vs})
                    v = v(name=k, options=options)
            processed[k] = v
        operation = {
            'fn': 'sel',
            'args': args,
            'kwargs': processed,
        }
        return new._clone(operation)

sel.__call__.__doc__ = xr.Dataset.sel.__doc__

class isel:

    def __init__(self, interactive):
        self._interactive = interactive

    def __call__(self, *args, **kwargs):
        new = self._interactive._resolve_accessor()
        processed = {}
        for k, v in kwargs.items():
            if isinstance(v, type) and issubclass(v, Widget):
                if hasattr(v, 'end'):
                    if issubclass(v, _RangeSliderBase):
                        value = (0, len(self._interactive.eval()))
                    else:
                        value = 0
                    v = v(
                        name=k, end=self._interactive.len(), value=value
                    )
                    if isinstance(v, _RangeSliderBase):
                        v = bind(lambda slc: slice(*slc), v)
            processed[k] = v
        operation = {
            'fn': 'isel',
            'args': args,
            'kwargs': processed
        }
        return new._clone(operation)

isel.__call__.__doc__ = xr.Dataset.isel.__doc__

react.register_accessor('isel', isel, predicate=is_xarray)
react.register_accessor('sel',  sel,  predicate=is_xarray)

def patch(name='hvplot', interactive='interactive', extension='bokeh', logo=False):
    from . import hvPlot, post_patch

    try:
        import xarray as xr
    except:
        raise ImportError('Could not patch plotting API onto xarray. '
                          'xarray could not be imported.')

    xr.register_dataset_accessor(name)(hvPlot)
    xr.register_dataarray_accessor(name)(hvPlot)
    xr.register_dataset_accessor(interactive)(Interactive)
    xr.register_dataarray_accessor(interactive)(Interactive)

    post_patch(extension, logo)

patch()
