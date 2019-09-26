import holoviews as _hv

from ._core import hvPlot, hvPlotTab, hvPlotGridded

from .andrews_curves import andrews_curves
from .parallel_coordinates import parallel_coordinates
from .lag_plot import lag_plot
from .scatter_matrix import scatter_matrix


def plot(data, kind, **kwargs):
    extension = 'bokeh'
    logo = False
    kwargs.pop('reuse_plot', False)  # drop this kwarg is present
    if extension and not getattr(_hv.extension, '_loaded', False):
        _hv.extension(extension, logo=logo)
    return hvPlotTab(data)(kind=kind, **kwargs)
