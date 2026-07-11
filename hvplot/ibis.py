"""
Experimental support for ibis.
"""


def patch(name='hvplot', extension='bokeh', logo=False):
    from . import _module_extensions, hvPlotTabular, post_patch

    try:
        import ibis
    except ImportError as e:
        raise ImportError(
            'Could not patch plotting API onto ibis. Ibis could not be imported.'
        ) from e

    if 'hvplot.ibis' not in _module_extensions:
        _patch_plot = lambda self: hvPlotTabular(self)  # noqa: E731
        _patch_plot.__doc__ = hvPlotTabular.__call__.__doc__
        patch_property = property(_patch_plot)
        setattr(ibis.Expr, name, patch_property)

        _module_extensions.add('hvplot.ibis')

    post_patch(extension, logo)


patch()
