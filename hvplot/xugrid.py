"""Adds the `.hvplot` method to xu.UgridDataArray and xu.UgridDataset"""


def patch(name='hvplot', extension='bokeh', logo=False):
    from . import post_patch, _module_extensions
    from .plotting.core import hvPlotXugrid

    try:
        import xugrid as xu
    except ImportError:
        raise ImportError(
            'Could not patch plotting API onto xugrid. xugrid could not be imported.'
        )

    if 'hvplot.xugrid' not in _module_extensions:
        _patch_plot = lambda self: hvPlotXugrid(self)  # noqa: E731
        _patch_plot.__doc__ = hvPlotXugrid.__call__.__doc__
        plot_prop = property(_patch_plot)
        setattr(xu.UgridDataArray, name, plot_prop)
        setattr(xu.UgridDataset, name, plot_prop)
        _module_extensions.add('hvplot.xugrid')

    post_patch(extension, logo)


patch()
