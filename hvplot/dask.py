from __future__ import absolute_import

from .interactive import Interactive

def patch(name='hvplot', extension='bokeh', logo=False):
    from . import hvPlotTabular, post_patch

    try:
        import dask.dataframe as dd
    except:
        raise ImportError('Could not patch plotting API onto dask. '
                          'Dask could not be imported.')
    _patch_plot = lambda self: hvPlotTabular(self)
    _patch_plot.__doc__ = hvPlotTabular.__call__.__doc__
    plot_prop = property(_patch_plot)
    setattr(dd.DataFrame, name, plot_prop)
    setattr(dd.Series, name, plot_prop)

    _patch_interactive = lambda self: Interactive(self)
    _patch_interactive.__doc__ = Interactive.__call__.__doc__
    interactive_prop = property(_patch_plot)
    setattr(dd.DataFrame, name, interactive_prop)
    setattr(dd.Series, name, interactive_prop)

    post_patch(extension, logo)

patch()
