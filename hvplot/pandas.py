from __future__ import absolute_import

def patch(name='hvplot', extension='bokeh', logo=False):
    from . import hvPlotTabular, post_patch

    try:
        import pandas as pd
    except:
        raise ImportError('Could not patch plotting API onto pandas. '
                          'Pandas could not be imported.')
    _patch_plot = lambda self: hvPlotTabular(self)
    _patch_plot.__doc__ = hvPlotTabular.__call__.__doc__
    plot_prop = property(_patch_plot)
    setattr(pd.DataFrame, name, plot_prop)
    setattr(pd.Series, name, plot_prop)

    _patch_interactive = lambda self: Interactive(self)
    _patch_interactive.__doc__ = Interactive.__call__.__doc__
    interactive_prop = property(_patch_plot)
    setattr(pd.DataFrame, name, interactive_prop)
    setattr(pd.Series, name, interactive_prop)

    post_patch(extension, logo)

patch()
