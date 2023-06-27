"""
interactive API

`Interactive` is a wrapper around a Python object that lets users
create interactive pipelines by calling existing APIs on an object
with dynamic parameters or widgets. An `Interactive` instance watches
what operations are applied to the object.
"""

from functools import partial

import holoviews as hv

from panel.react import react

from .converter import HoloViewsConverter
from .util import is_tabular


class Interactive(react):
    """
    The `.interactive` API enhances the API of data analysis libraries
    like Pandas, Dask, and Xarray, by allowing to replace in a pipeline
    static values by dynamic widgets. When displayed, an interactive
    pipeline will incorporate the dynamic widgets that control it, as long
    as its normal output that will automatically be updated as soon as a
    widget value is changed.

    `Interactive` can be instantiated with an object. However the recommended
    approach is to instantiate it via the `.interactive` accessor that is
    available on a data structure when it has been patched, e.g. after
    executing `import hvplot.pandas`. The accessor can also be called which
    allows to pass down kwargs.

    A pipeline can then be created from this object, the pipeline will render
    with its widgets and its interactive output.

    Reference: https://hvplot.holoviz.org/user_guide/Interactive.html

    Parameters
    ----------
    obj: DataFrame, Series, DataArray, DataSet
        A supported data structure object
    loc : str, optional
        Widget(s) location, one of 'bottom_left', 'bottom_right', 'right'
        'top-right', 'top-left' and 'left'. By default 'top_left'
    center : bool, optional
        Whether to center to pipeline output, by default False
    max_rows : int, optional
        Maximum number of rows displayed, only used when the output is a
        dataframe, by default 100
    kwargs: optional
        Optional kwargs that are passed down to customize the displayed
        object. E.g. if the output is a DataFrame `width=200` will set
        the size of the DataFrame Pane that renders it.

    Examples
    --------
    Instantiate it from an object:
    >>> dfi = Interactive(df)

    Or with the `.interactive` accessor when the object is patched:
    >>> import hvplot.pandas
    >>> dfi = df.interactive
    >>> dfi = df.interactive(width=200)

    Create interactive pipelines from the `Interactive` object:
    >>> widget = panel.widgets.IntSlider(value=1, start=1, end=5)
    >>> dfi.head(widget)
    """

    _display_options = ('center', 'dmap', 'loc')

    def __dir__(self):
        current = self._current
        if self._method:
            current = getattr(current, self._method)
        extras = {attr for attr in dir(current) if not attr.startswith('_')}
        if is_tabular(current) and hasattr(current, 'columns'):
            extras |= set(current.columns)
        try:
            return sorted(set(super().__dir__()) | extras)
        except Exception:
            return sorted(set(dir(type(self))) | set(self.__dict__) | extras)

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    def dmap(self):
        """
        Wraps the output in a DynamicMap. Only valid if the output
        is a HoloViews object.
        """
        return hv.DynamicMap(self._callback)

    def holoviews(self):
        """
        Returns a HoloViews object to render the output of this
        pipeline. Only works if the output of this pipeline is a
        HoloViews object, e.g. from an .hvplot call.
        """
        return hv.DynamicMap(self._callback)

    def output(self):
        """
        Returns the output of the interactive pipeline, which is
        either a HoloViews DynamicMap or a Panel object.

        Returns
        -------
        DynamicMap or Panel object wrapping the interactive output.
        """
        return self.holoviews() if self._display_opts.get('dmap') else self.panel(**self._kwargs)


class _hvplot:

    _kinds = tuple(HoloViewsConverter._kind_mapping)

    __slots__ = ["_interactive"]

    def __init__(self, _interactive):
        self._interactive = _interactive

    def __call__(self, *args, _kind=None, **kwargs):
        # The underscore in _kind is to not overwrite it
        # if 'kind' is in kwargs and the function
        # is used with partial.
        if _kind and "kind" in kwargs:
            raise TypeError(f"{_kind}() got an unexpected keyword argument 'kind'")
        if _kind:
            kwargs["kind"] = _kind

        new = self._interactive._resolve_accessor()
        operation = {
            'fn': 'hvplot',
            'args': args,
            'kwargs': kwargs,
        }
        dmap = 'kind' not in kwargs or isinstance(kwargs['kind'], str)
        return new._clone(operation, dmap=dmap)

    def __getattr__(self, attr):
        if attr in self._kinds:
            return partial(self, _kind=attr)
        else:
            raise AttributeError(f"'hvplot' object has no attribute '{attr}'")

    def __dir__(self):
        # This function is for autocompletion
        return self._interactive._obj.hvplot.__all__


react.register_accessor('hvplot', _hvplot)
