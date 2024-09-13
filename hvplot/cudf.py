from .interactive import Interactive


def patch(name='hvplot', interactive='interactive', extension='bokeh', logo=False):
    from . import hvPlotTabular, post_patch, _module_extensions

    try:
        import cudf
    except ImportError:
        raise ImportError('Could not patch plotting API onto cuDF. cuDF could not be imported.')

    if 'hvplot.cudf' not in _module_extensions:
        _patch_plot = lambda self: hvPlotTabular(self)  # noqa: E731
        _patch_plot.__doc__ = hvPlotTabular.__call__.__doc__
        plot_prop = property(_patch_plot)
        setattr(cudf.DataFrame, name, plot_prop)
        setattr(cudf.Series, name, plot_prop)

        _patch_interactive = lambda self: Interactive(self)  # noqa: E731
        _patch_interactive.__doc__ = Interactive.__call__.__doc__
        interactive_prop = property(_patch_interactive)
        setattr(cudf.DataFrame, interactive, interactive_prop)
        setattr(cudf.Series, interactive, interactive_prop)

        _module_extensions.add('hvplot.cudf')

    post_patch(extension, logo)


patch()
