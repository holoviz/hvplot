"""
interactive API
"""

import abc
import operator
import sys

import holoviews as hv
import panel as pn
import param

from panel.layout import Column, Row, VSpacer, HSpacer
from panel.widgets.base import Widget


class Interactive():
    """
    Interactive is a wrapper around and object that lets users create
    interactive pipelines by calling existing APIs on an object with
    dynamic parameters or widgets.
    """

    __metaclass__ = abc.ABCMeta

    _fig = None

    def __init__(self, obj, transform=None, plot=False, depth=0,
                 loc='top_left', center=False, dmap=False, **kwargs):
        self._obj = obj
        self._method = None
        if transform is None:
            self._transform = hv.dim('*')
        else:
            self._transform = transform
        self._plot = plot
        self._depth = depth
        self._loc = loc
        self._center = center
        self._dmap = dmap
        self._kwargs = kwargs
        ds = hv.Dataset(self._obj)
        self._current = self._transform.apply(ds, keep_index=True, compute=False)

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
        kwargs = dict(self._kwargs, **kwargs)
        return type(self)(self._obj, transform, plot, depth,
                           loc, center, dmap, **kwargs)

    def _repr_mimebundle_(self, include=[], exclude=[]):
        return self.layout._repr_mimebundle_()

    def __dir__(self):
        return [d for d in dir(self._current) if d[0] != '_']

    def __getattr__(self, name):
        if name in dir(self):
            self._method = name
            self.__doc__ = getattr(self._obj, name).__doc__
            return self
        raise AttributeError(name)

    def __call__(self, *args, **kwargs):
        if self._method is None:
            if self._depth == 0:
                return self._clone(*args, **kwargs)
            raise AttributeError
        method = type(self._transform)(self._transform, self._method, accessor=True)
        return self._clone(method(*args, **kwargs))

    #----------------------------------------------------------------
    # Interactive pipeline APIs
    #----------------------------------------------------------------

    # Builtin functions
    def __abs__(self):
        transform = type(self._transform)(self._transform, abs)
        return self._clone(transform)
    def __round__(self, ndigits=None):
        args = () if ndigits is None else (ndigits,)
        transform = type(self._transform)(self._transform, round_, *args)
        return self._clone(transform)

    # Unary operators
    def __neg__(self):
        transform = type(self._transform)(self._transform, operator.neg)
        return self._clone(transform)
    def __not__(self):
        transform = type(self._transform)(self._transform, operator.not_)
        return self._clone(transform)
    def __invert__(self):
        transform = type(self._transform)(self._transform, operator.inv)
        return self._clone(transform)
    def __pos__(self):
        transform = type(self._transform)(self._transform, operator.pos)
        return self._clone(transform)

    # Binary operators
    def __add__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        transform = type(self._transform)(self._transform, operator.add, other)
        return self._clone(transform)
    def __and__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        transform = type(self._transform)(self._transform, operator.and_, other)
        return self._clone(transform)
    def __div__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        transform = type(self._transform)(self._transform, operator.div, other)
        return self._clone(transform)
    def __eq__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        transform = type(self._transform)(self._transform, operator.eq, other)
        return self._clone(transform)
    def __floordiv__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        transform = type(self._transform)(self._transform, operator.floordiv, other)
        return self._clone(transform)
    def __ge__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        transform = type(self._transform)(self._transform, operator.ge, other)
        return self._clone(transform)
    def __gt__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        transform = type(self._transform)(self._transform, operator.gt, other)
        return self._clone(transform)
    def __le__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        transform = type(self._transform)(self._transform, operator.le, other)
        return self._clone(transform)
    def __lt__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        transform = type(self._transform)(self._transform, operator.lt, other)
        return self._clone(transform)
    def __lshift__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        transform = type(self._transform)(self._transform, operator.lshift, other)
        return self._clone(transform)
    def __mod__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        transform = type(self._transform)(self._transform, operator.mod, other)
        return self._clone(transform)
    def __mul__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        transform = type(self._transform)(self._transform, operator.mul, other)
        return self._clone(transform)
    def __ne__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        transform = type(self._transform)(self._transform, operator.ne, other)
        return self._clone(transform)
    def __or__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        transform = type(self._transform)(self._transform, operator.or_, other)
        return self._clone(transform)
    def __rshift__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        transform = type(self._transform)(self._transform, operator.rshift, other)
        return self._clone(transform)
    def __pow__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        transform = type(self._transform)(self._transform, operator.pow, other)
        return self._clone(transform)
    def __sub__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        transform = type(self._transform)(self._transform, operator.sub, other)
        return self._clone(transform)
    def __truediv__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        transform = type(self._transform)(self._transform, operator.truediv, other)
        return self._clone(transform)

    # Reverse binary operators
    def __radd__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        transform = type(self._transform)(self._transform, operator.add, other, reverse=True)
        return self._clone(transform)
    def __rand__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        transform = type(self._transform)(self._transform, operator.and_, other)
        return self._clone(transform)
    def __rdiv__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        transform = type(self._transform)(self._transform, operator.div, other, reverse=True)
        return self._clone(transform)
    def __rfloordiv__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        transform = type(self._transform)(self._transform, operator.floordiv, other, reverse=True)
        return self._clone(transform)
    def __rlshift__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        transform = type(self._transform)(self._transform, operator.rlshift, other)
        return self._clone(transform)
    def __rmod__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        transform = type(self._transform)(self._transform, operator.mod, other, reverse=True)
        return self._clone(transform)
    def __rmul__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        transform = type(self._transform)(self._transform, operator.mul, other, reverse=True)
        return self._clone(transform)
    def __ror__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        transform = type(self._transform)(self._transform, operator.or_, other, reverse=True)
        return self._clone(transform)
    def __rpow__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        transform = type(self._transform)(self._transform, operator.pow, other, reverse=True)
        return self._clone(transform)
    def __rrshift__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        transform = type(self._transform)(self._transform, operator.rrshift, other)
        return self._clone(transform)
    def __rsub__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        transform = type(self._transform)(self._transform, operator.sub, other, reverse=True)
        return self._clone(transform)
    def __rtruediv__(self, other):
        other = other._transform if isinstance(other, Interactive) else other
        transform = type(self._transform)(self._transform, operator.truediv, other, reverse=True)
        return self._clone(transform)

    def plot(self, *args, **kwargs):
        @pn.depends()
        def get_ax():
            from matplotlib.backends.backend_agg import FigureCanvas
            from matplotlib.pyplot import Figure
            Interactive._fig = fig = Figure()
            FigureCanvas(fig)
            return fig.subplots()
        kwargs['ax'] = get_ax
        transform = hv.dim(self._transform, 'plot', accessor=True)
        return self._clone(transform(*args, **kwargs), plot=True)

    def hvplot(self, *args, **kwargs):
        transform = type(self._transform)(self._transform, 'hvplot', accessor=True)
        dmap = 'kind' not in kwargs
        return self._clone(transform(*args, **kwargs), dmap=dmap)

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    @property
    def layout(self):
        """
        Returns a layout of the widgets and output arranged according
        to the center and and widget location specified in the
        interactive call.
        """
        widget_box = self.widgets
        panel = self.output
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
        return Row(*components)

    @property
    def output(self):
        """
        Returns the output of the interactive pipeline, which is
        either a HoloViews DynamicMap or a Panel object.

        Returns
        -------
        DynamicMap or Panel object wrapping the interactive output.
        """
        return self.dmap() if self._dmap else self.panel(**self._kwargs)

    @property
    def widgets(self):
        """
        Returns a Column of widgets which control the interactive output.

        Returns
        -------
        A Column of widgets
        """
        widgets = []
        for op in self._transform.ops:
            op_args = list(op['args'])+list(op['kwargs'].values())
            for op_arg in op_args:
                if 'panel' in sys.modules:
                    if isinstance(op_arg, Widget):
                        widgets.append(op_arg)
                if 'ipywidgets' in sys.modules:
                    from ipywidgets import Widget as IPyWidget
                    if isinstance(op_arg, IPyWidget):
                        widgets.append(op_arg)
                if (isinstance(op_arg, param.Parameter) and
                    isinstance(op_arg.owner, Widget)):
                    widget.append(op_arg.owner)
        return pn.Column(*widgets)

    def dmap(self):
        """
        Wraps the output in a DynamicMap. Only valid if the output
        is a HoloViews object.
        """
        return hv.DynamicMap(self._callback)

    def panel(self, **kwargs):
        """
        Wraps the output in a Panel component.
        """
        return pn.panel(self._callback, **kwargs)
