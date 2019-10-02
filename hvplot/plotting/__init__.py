import holoviews as hv
from ..util import with_hv_extension

from .core import hvPlot, hvPlotTabular   # noqa

from .andrews_curves import andrews_curves   # noqa
from .parallel_coordinates import parallel_coordinates   # noqa
from .lag_plot import lag_plot   # noqa
from .scatter_matrix import scatter_matrix   # noqa


@with_hv_extension
def plot(data, kind, **kwargs):
    # drop reuse_plot
    kwargs.pop('reuse_plot', None)

    # replace with shared_axes
    sharex = kwargs.pop('sharex', None)
    sharey = kwargs.pop('sharey', None)
    if sharex is not None and sharey is not None:
        kwargs['shared_axes'] = sharex or sharey
    elif sharex is not None:
        kwargs['shared_axes'] = sharex
    elif sharey is not None:
        kwargs['shared_axes'] = sharey

    # drop all kwargs that are set to None
    no_none_kwargs = {}
    for k, v in kwargs.items():
        if v is not None:
            no_none_kwargs[k] = v

    return hvPlotTabular(data)(kind=kind, **no_none_kwargs)


def boxplot_series(*args, **kwargs):
    return plot(*args, kind='box', **kwargs)


def boxplot_frame(*args, **kwargs):
    return plot(*args, kind='box', **kwargs)


def boxplot_frame_groupby(grouped, **kwargs):
    width = kwargs.pop('width', 300)
    subplots = kwargs.pop('subplots', True)
    layout = hv.Layout if subplots else hv.Overlay
    plots = [plot(data=data, kind='box', title=name, width=width, **kwargs)
             for name, data in grouped]
    return layout(plots)


def hist_series(*args, **kwargs):
    return plot(*args, kind='hist', **kwargs)


def hist_frame(*args, **kwargs):
    return plot(*args, kind='hist', **kwargs)
