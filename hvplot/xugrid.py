"""Adds the `.hvplot` method to xu.UgridDataArray and xu.UgridDataset."""


def patch(name='hvplot', extension='bokeh', logo=False):
    """Patch xugrid objects with the hvplot accessors."""
    from . import _module_extensions, post_patch
    from .plotting.core import hvPlotXugrid

    try:
        import xugrid as xu
    except ImportError as e:
        raise ImportError(
            'Could not patch plotting API onto xugrid. xugrid could not be imported.'
        ) from e

    if 'hvplot.xugrid' not in _module_extensions:
        _patch_plot = lambda self: hvPlotXugrid(self)  # noqa: E731
        _patch_plot.__doc__ = hvPlotXugrid.__call__.__doc__
        plot_prop = property(_patch_plot)
        setattr(xu.UgridDataArray, name, plot_prop)
        setattr(xu.UgridDataset, name, plot_prop)
        _module_extensions.add('hvplot.xugrid')

    post_patch(extension, logo)


def _unpatch(name='hvplot'):
    """Undo `patch()`. Private, used by the test suite."""
    import xugrid as xu

    from . import _module_extensions

    for cls in (xu.UgridDataArray, xu.UgridDataset):
        if name in vars(cls):
            delattr(cls, name)
    _module_extensions.discard('hvplot.xugrid')


patch()
