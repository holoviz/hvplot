def patch(name='hvplot', extension='bokeh', logo=False):
    from . import hvPlotTabular, post_patch, _module_extensions

    try:
        import streamz.dataframe as sdf
    except ImportError:
        raise ImportError(
            'Could not patch plotting API onto streamz. Streamz could not be imported.'
        )
    if 'hvplot.streamz' not in _module_extensions:
        _patch_plot = lambda self: hvPlotTabular(self)  # noqa: E731
        _patch_plot.__doc__ = hvPlotTabular.__call__.__doc__
        patch_property = property(_patch_plot)
        setattr(sdf.DataFrame, name, patch_property)
        setattr(sdf.DataFrames, name, patch_property)
        setattr(sdf.Series, name, patch_property)
        setattr(sdf.Seriess, name, patch_property)

        _module_extensions.add('hvplot.streamz')

    post_patch(extension, logo)


patch()
