"""
interactive API

How Interactive works
---------------------

`Interactive` is a wrapper around a Python object that lets users create
interactive pipelines by calling existing APIs on an object with dynamic
parameters or widgets.

An `Interactive` instance watches what operations are applied to the object.

To do so, each operation returns a new `Interactive` instance - the creation
of a new instance being taken care of by the `_clone` method - which allows
the next operation to be recorded, and so on and so forth. E.g. `dfi.head()`
first records that the `'head'` attribute is accessed, this is achieved
by overriding `__getattribute__`. A new interactive object is returned,
which will then record that it is being called, and that new object will be
itself called as `Interactive` implements `__call__`. `__call__`  returns
another `Interactive` instance.

Note that under the hood even more `Interactive` instances may be created,
but this is the gist of it.

To be able to watch all the potential operations that may be applied to an
object, `Interactive` implements on top of `__getattribute__` and
`__call__`:

- operators such as `__gt__`, `__add__`, etc.
- the builtin functions `__abs__` and `__round__`
- `__getitem__`
- `__array_ufunc__`

The `_depth` attribute starts at 0 and is incremented by 1 everytime
a new `Interactive` instance is created part of a chain.
The root instance in an expression has a `_depth` of 0. An expression can
consist of multiple chains, such as `dfi[dfi.A > 1]`, as the `Interactive`
instance is referenced twice in the expression. As a consequence `_depth`
is not the total count of `Interactive` instance creations of a pipeline,
it is the count of instances created in the outer chain. In the example, that
would be `dfi[]`. `Interactive` instances don't have references about
the instances that created them or that they create, they just know their
current location in a chain thanks to `_depth`. However, as some parameters
need to be passed down the whole pipeline, they do have to propagate. E.g.
in `dfi.interactive(width=200)`, `width=200` will be propagated as `kwargs`.

Recording the operations applied to an object in a pipeline is done
by gradually building a so-called "dim expression", or "dim transform",
which is an expression language provided by HoloViews. dim transform
objects are a way to express transforms on `Dataset`s, a `Dataset` being
another HoloViews object that is a wrapper around common data structures
such as Pandas/Dask/... Dataframes/Series, Xarray Dataset/DataArray, etc.
For instance a Python expression such as `(series + 2).head()` can be
expressed with a dim transform whose repr will be `(dim('*').pd+2).head(2)`,
effectively showing that the dim transfom has recorded the different
operations that are meant to be applied to the data.
The `_transform` attribute stores the dim transform.

The `_obj` attribute holds the original data structure that feeds the
pipeline. All the `Interactive` instances created while parsing the
pipeline share the same `_obj` object. And they all wrap it in a `Dataset`
instance, and all apply the current dim transform they are aware of to
the original data structure to compute the intermediate state of the data,
that is stored it in the `_current_` attribute. Doing so is particularly
useful in Notebook sessions, as this allows to inspect the transformed
object at any point of the pipeline, and as such provide correct
auto-completion and docstrings. E.g. executing `dfi.A.max?` in a Notebook
will correctly return the docstring of the Pandas Series `.max()` method,
as the pipeline evaluates `dfi.A` to hold a current object `_current` that
is a Pandas Series, and no longer and DataFrame.

The `_obj` attribute is implemented as a property which gets/sets the value
from a list that contains the shared attribute. This is required for the
"function as input" to be able to update the object from a callback set up
on the root Interactive instance.

Internally interactive holds the current evaluated state on the `_current_`
attribute, when some parameter in the interactive pipeline is changed
the pipeline is marked as `_dirty`. This means that the next time `_current`
is accessed the pipeline will be re-evaluated to get the up-to-date
current value.

The `_method` attribute is a string that temporarily stores the method/attr
accessed on the object, e.g. `_method` is 'head' in `dfi.head()`, until the
Interactive instance created in the pipeline is called at which point `_method`
is reset to None. In cases such as `dfi.head` or `dfi.A`, `_method` is not
(yet) reset to None. At this stage the Interactive instance returned has
its `_current` attribute not updated, e.g. `dfi.A._current` is still the
original dataframe, not the 'A' series. Keeping `_method` is thus useful for
instance to display `dfi.A`, as the evaluation of the object will check
whether `_method` is set or not, and if it's set it will use it to compute
the object returned, e.g. the series `df.A` or the method `df.head`, and
display its repr.
"""

from functools import partial

import holoviews as hv
import panel as pn

from panel.interactive import interactive

from .converter import HoloViewsConverter
from .util import is_tabular


class Interactive(interactive):
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

    _display_options = ('loc', 'center', 'dmap')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hvplot = _hvplot(self)

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

    @staticmethod
    def _get_ax_fn():
        @pn.depends()
        def get_ax():
            from matplotlib.backends.backend_agg import FigureCanvas
            from matplotlib.pyplot import Figure
            Interactive._fig = fig = Figure()
            FigureCanvas(fig)
            return fig.subplots()
        return get_ax

    def __call__(self, *args, **kwargs):
        if self._method == 'plot':
            # This - {ax: get_ax} - is passed as kwargs to the plot method in
            # the dim expression.
            kwargs['ax'] = self._get_ax_fn()
        return super().__call__(*args, **kwargs)

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
