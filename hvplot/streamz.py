def patch(name='hvplot', extension='bokeh', logo=False):
    from . import plotting
    from . import post_patch

    try:
        import streamz.dataframe as sdf
    except ImportError:
        raise ImportError('Could not patch plotting API onto streamz. '
                            'Streamz could not be imported.')
    _patch_plot = lambda self: plotting.hvPlotTab(self)
    _patch_plot.__doc__ = plotting.hvPlotTab.__call__.__doc__
    patch_property = property(_patch_plot)
    setattr(sdf.DataFrame, name, patch_property)
    setattr(sdf.DataFrames, name, patch_property)
    setattr(sdf.Series, name, patch_property)
    setattr(sdf.Seriess, name, patch_property)

    post_patch(extension, logo)

patch()
