"""
Experimental support for ibis.
"""


def patch(name='hvplot', extension='bokeh', logo=False):
    from . import hvPlotTabular, post_patch, _module_extensions

    try:
        import ibis
    except ImportError:
        raise ImportError('Could not patch plotting API onto ibis. Ibis could not be imported.')

    if 'hvplot.ibis' not in _module_extensions:
        _patch_plot = lambda self: hvPlotTabular(self)  # noqa: E731
        _patch_plot.__doc__ = hvPlotTabular.__call__.__doc__
        patch_property = property(_patch_plot)
        setattr(ibis.Expr, name, patch_property)

        _module_extensions.add('hvplot.ibis')

    post_patch(extension, logo)


patch()
