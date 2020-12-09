from __future__ import absolute_import

from .interactive import Interactive

def patch(name='hvplot', interactive='interactive', extension='bokeh', logo=False):
    from . import hvPlotTabular, post_patch

    try:
        import cudf
    except:
        raise ImportError('Could not patch plotting API onto cuDF. '
                          'cuDF could not be imported.')
    _patch_plot = lambda self: hvPlotTabular(self)
    _patch_plot.__doc__ = hvPlotTabular.__call__.__doc__
    plot_prop = property(_patch_plot)
    setattr(cudf.DataFrame, name, plot_prop)
    setattr(cudf.Series, name, plot_prop)

    _patch_interactive = lambda self: Interactive(self)
    _patch_interactive.__doc__ = Interactive.__call__.__doc__
    interactive_prop = property(_patch_interactive)
    setattr(cudf.DataFrame, interactive, interactive_prop)
    setattr(cudf.Series, interactive, interactive_prop)

    post_patch(extension, logo)

patch()
