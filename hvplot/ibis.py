from __future__ import absolute_import

def patch(name='hvplot', extension='bokeh', logo=False):
    from . import hvPlotTabular, post_patch

    try:
        import ibis
    except:
        raise ImportError('Could not patch plotting API onto dask. '
                          'Dask could not be imported.')
    _patch_plot = lambda self: hvPlotTabular(self)
    _patch_plot.__doc__ = hvPlotTabular.__call__.__doc__
    patch_property = property(_patch_plot)
    setattr(ibis.Expr, name, patch_property)
    
    post_patch(extension, logo)

patch()
