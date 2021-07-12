"""
interactive API
"""

import abc
import operator
import sys

import holoviews as hv
import pandas as pd
import panel as pn
import param

from panel.layout import Column, Row, VSpacer, HSpacer
from panel.widgets.base import Widget

from .util import is_tabular, is_xarray, is_xarray_dataarray


def _find_widgets(op):
    widgets = []
    op_args = list(op['args'])+list(op['kwargs'].values())
    for op_arg in op_args:
        if 'panel' in sys.modules:
            if isinstance(op_arg, Widget) and op_arg not in widgets:
                widgets.append(op_arg)
        if isinstance(op_arg, hv.dim):
            for nested_op in op_arg.ops:
                for widget in _find_widgets(nested_op):
                    if widget not in widgets:
                        widgets.append(widget)
        if 'ipywidgets' in sys.modules:
            from ipywidgets import Widget as IPyWidget
            if isinstance(op_arg, IPyWidget) and op_arg not in widgets:
                widgets.append(op_arg)
        if (isinstance(op_arg, param.Parameter) and
            isinstance(op_arg.owner, pn.widgets.Widget) and
            op_arg.owner not in widgets):
            widgets.append(op_arg.owner)
    return widgets


class Interactive():
    """
    Interactive is a wrapper around a Python object that lets users create
    interactive pipelines by calling existing APIs on an object with
    dynamic parameters or widgets.
    """

    __metaclass__ = abc.ABCMeta

    _fig = None

    def __init__(self, obj, transform=None, plot=False, depth=0,
                 loc='top_left', center=False, dmap=False, inherit_kwargs={},
                 max_rows=100, **kwargs):
        self._init = False
        self._obj = obj
        self._method = None
        if transform is None:
            dim = '*'
            transform = hv.util.transform.dim
            if is_xarray(obj):
                transform = hv.util.transform.xr_dim
                if is_xarray_dataarray(obj):
                    dim = obj.name
                if dim is None:
                    raise ValueError(
                        "Cannot use interactive API on DataArray without name."
                        "Assign a name to the DataArray and try again."
                    )
            elif is_tabular(obj):
                transform = hv.util.transform.df_dim
            self._transform = transform(dim)
        else:
            self._transform = transform
        self._plot = plot
        self._depth = depth
        self._loc = loc
        self._center = center
        self._dmap = dmap
        self._inherit_kwargs = inherit_kwargs
        self._max_rows = max_rows
        self._kwargs = kwargs
        ds = hv.Dataset(self._obj)
        self._current = self._transform.apply(ds, keep_index=True, compute=False)
        self._init = True

    @property
    def _params(self):
        return [v for k, v in self._transform.params.items() if k != 'ax']

    @property
    def _callback(self):
        @pn.depends(*self._params)
        def evaluate(*args, **kwargs):
            ds = hv.Dataset(self._obj)
            obj = self._transform.apply(ds, keep_index=True, compute=False)
            if self._plot:
                return Interactive._fig
            elif isinstance(obj, pd.DataFrame):
                return pn.pane.DataFrame(obj, max_rows=self._max_rows)
            else:
                return obj
        return evaluate

    def _clone(self, transform=None, plot=None, loc=None, center=None,
               dmap=None, **kwargs):
        plot = self._plot or plot
        transform = transform or self._transform
        loc = self._loc if loc is None else loc
        center = self._center if center is None else center
        dmap = self._dmap if dmap is None else dmap
        depth = self._depth+1
        kwargs = dict(self._inherit_kwargs, **dict(self._kwargs, **kwargs))
        return type(self)(self._obj, transform, plot, depth,
                          loc, center, dmap, **kwargs)

    def _repr_mimebundle_(self, include=[], exclude=[]):
        return self.layout()._repr_mimebundle_()

    def __dir__(self):
        current = self._current
        if self._method:
            current = getattr(current, self._method)
        extras = {attr for attr in dir(current) if not attr.startswith('_')}
        if is_tabular(current) and hasattr(current, 'columns'):
            extras |= set(current.columns)
        try:
            return sorted(set(super(Interactive, self).__dir__()) | extras)
        except Exception:
            return sorted(set(dir(type(self))) | set(self.__dict__) | extras)

    def __getattribute__(self, name):
        self_dict = super(Interactive, self).__getattribute__('__dict__')
        if not self_dict.get('_init'):
            return super(Interactive, self).__getattribute__(name)

        current = self_dict['_current']
        method = self_dict['_method']
        if method:
            current = getattr(current, method)
        extras = [d for d in dir(current) if not d.startswith('_')]
        if name in extras and name not in super(Interactive, self).__dir__():
            if self._method:
                transform = type(self._transform)(self._transform, self._method, accessor=True)
                transform._ns = self._current
                inherit_kwargs = {}
                if self._method == 'plot':
                    inherit_kwargs['ax'] = self._get_ax_fn()
                try:
                    new = self._clone(transform, inherit_kwargs=inherit_kwargs)
                finally:
                    self._method = None
            else:
                new = self
            new._method = name
            try:
                new.__doc__ = getattr(new, name).__doc__
            except Exception:
                pass
            return new
        return super(Interactive, self).__getattribute__(name)

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
        if self._method is None:
            if self._depth == 0:
                return self._clone(*args, **kwargs)
            raise AttributeError
        elif self._method == 'plot':
            kwargs['ax'] = self._get_ax_fn()
        try:
            method = type(self._transform)(self._transform, self._method,
                                       accessor=True)
            kwargs = dict(self._inherit_kwargs, **kwargs)
            clone = self._clone(method(*args, **kwargs), plot=self._method == 'plot')
        finally:
            self._method = None
        return clone

    #----------------------------------------------------------------
    # Interactive pipeline APIs
    #----------------------------------------------------------------

    def __array_ufunc__(self, *args, **kwargs):
        transform = self._transform
        if self._method:
            transform = type(transform)(transform, self._method, accessor=True)
            transform._ns = self._current
            self._method = None
        transform = args[0](transform, *args[3:], **kwargs)
        return self._clone(transform)

    def _apply_operator(self, operator, *args, **kwargs):
        transform = self._transform
        if self._method:
            transform = type(transform)(transform, self._method, accessor=True)
            transform._ns = self._current
            self._method = None
        transform = type(transform)(transform, operator, *args)
        return self._clone(transform)

    # Builtin functions
    def __abs__(self):
        return self._apply_operator(abs)

    def __round__(self, ndigits=None):
        args = () if ndigits is None else (ndigits,)
        return self._apply_operator(round, *args)

    # Unary operators
    def __neg__(self):
        return self._apply_operator(operator.neg)
    def __not__(self):
        return self._apply_operator(operator.not_)
    def __invert__(self):
        return self._apply_operator(operator.inv)
    def __pos__(self):
        return self._apply_operator(operator.pos)

    # Binary operators
    def __add__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        return self._apply_operator(operator.add, other)
    def __and__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        return self._apply_operator(operator.and_, other)
    def __div__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        return self._apply_operator(operator.div, other)
    def __eq__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        return self._apply_operator(operator.eq, other)
    def __floordiv__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        return self._apply_operator(operator.floordiv, other)
    def __ge__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        return self._apply_operator(operator.ge, other)
    def __gt__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        return self._apply_operator(operator.gt, other)
    def __le__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        return self._apply_operator(operator.le, other)
    def __lt__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        return self._apply_operator(operator.lt, other)
    def __lshift__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        return self._apply_operator(operator.lshift, other)
    def __mod__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        return self._apply_operator(operator.mod, other)
    def __mul__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        return self._apply_operator(operator.mul, other)
    def __ne__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        return self._apply_operator(operator.ne, other)
    def __or__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        return self._apply_operator(operator.or_, other)
    def __rshift__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        return self._apply_operator(operator.rshift, other)
    def __pow__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        return self._apply_operator(operator.pow, other)
    def __sub__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        return self._apply_operator(operator.sub, other)
    def __truediv__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        return self._apply_operator(operator.truediv, other)

    # Reverse binary operators
    def __radd__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        return self._apply_operator(operator.div, other, reverse=True)
    def __rand__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        return self._apply_operator(operator.and_, other, reverse=True)
    def __rdiv__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        return self._apply_operator(operator.div, other, reverse=True)
    def __rfloordiv__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        return self._apply_operator(operator.floordiv, other, reverse=True)
    def __rlshift__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        return self._apply_operator(operator.rlshift, other)
    def __rmod__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        return self._apply_operator(operator.mod, other, reverse=True)
    def __rmul__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        return self._apply_operator(operator.mul, other, reverse=True)
    def __ror__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        return self._apply_operator(operator.or_, other, reverse=True)
    def __rpow__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        return self._apply_operator(operator.pow, other, reverse=True)
    def __rrshift__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        return self._apply_operator(operator.rrshift, other)
    def __rsub__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        return self._apply_operator(operator.sub, other, reverse=True)
    def __rtruediv__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        return self._apply_operator(operator.truediv, other, reverse=True)

    def __getitem__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        return self._apply_operator(operator.getitem, other)

    def _plot(self, *args, **kwargs):
        @pn.depends()
        def get_ax():
            from matplotlib.backends.backend_agg import FigureCanvas
            from matplotlib.pyplot import Figure
            Interactive._fig = fig = Figure()
            FigureCanvas(fig)
            return fig.subplots()
        kwargs['ax'] = get_ax
        transform = self._transform
        if self._method:
            transform = type(transform)(transform, self._method, accessor=True)
            transform._ns = self._current
            self._method = None
        transform = type(transform)(transform, 'plot', accessor=True)
        return self._clone(transform(*args, **kwargs), plot=True)

    def hvplot(self, *args, **kwargs):
        transform = self._transform
        if self._method:
            transform = type(transform)(transform, self._method, accessor=True)
            transform._ns = self._current
            self._method = None
        transform = type(transform)(transform, 'hvplot', accessor=True)
        dmap = 'kind' not in kwargs
        return self._clone(transform(*args, **kwargs), dmap=dmap)

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    def layout(self, **kwargs):
        """
        Returns a layout of the widgets and output arranged according
        to the center and widget location specified in the
        interactive call.
        """
        widget_box = self.widgets()
        panel = self.output()
        loc = self._loc
        if loc in ('left', 'right'):
            widgets = Column(VSpacer(), widget_box, VSpacer())
        elif loc in ('top', 'bottom'):
            widgets = Row(HSpacer(), widget_box, HSpacer())
        elif loc in ('top_left', 'bottom_left'):
            widgets = Row(widget_box, HSpacer())
        elif loc in ('top_right', 'bottom_right'):
            widgets = Row(HSpacer(), widget_box)
        elif loc in ('left_top', 'right_top'):
            widgets = Column(widget_box, VSpacer())
        elif loc in ('left_bottom', 'right_bottom'):
            widgets = Column(VSpacer(), widget_box)
        center = self._center
        if not widgets:
            if center:
                components = [HSpacer(), panel, HSpacer()]
            else:
                components = [panel]
        elif center:
            if loc.startswith('left'):
                components = [widgets, HSpacer(), panel, HSpacer()]
            elif loc.startswith('right'):
                components = [HSpacer(), panel, HSpacer(), widgets]
            elif loc.startswith('top'):
                components = [HSpacer(), Column(widgets, Row(HSpacer(), panel, HSpacer())), HSpacer()]
            elif loc.startswith('bottom'):
                components = [HSpacer(), Column(Row(HSpacer(), panel, HSpacer()), widgets), HSpacer()]
        else:
            if loc.startswith('left'):
                components = [widgets, panel]
            elif loc.startswith('right'):
                components = [panel, widgets]
            elif loc.startswith('top'):
                components = [Column(widgets, panel)]
            elif loc.startswith('bottom'):
                components = [Column(panel, widgets)]
        return Row(*components, **kwargs)

    def output(self):
        """
        Returns the output of the interactive pipeline, which is
        either a HoloViews DynamicMap or a Panel object.

        Returns
        -------
        DynamicMap or Panel object wrapping the interactive output.
        """
        return self.holoviews() if self._dmap else self.panel(**self._kwargs)

    def widgets(self):
        """
        Returns a Column of widgets which control the interactive output.

        Returns
        -------
        A Column of widgets
        """
        widgets = []
        for op in self._transform.ops:
            for w in _find_widgets(op):
                if w not in widgets:
                    widgets.append(w)
        return pn.Column(*widgets)

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

    def panel(self, **kwargs):
        """
        Wraps the output in a Panel component.
        """
        return pn.panel(self._callback, **kwargs)
