from packaging.version import Version

from . import hvPlot, post_patch


def patch(name='hvplot', extension='bokeh', logo=False):
    try:
        import intake
    except:
        raise ImportError('Could not patch plotting API onto intake. '
                          'intake could not be imported.')

    _patch_plot = lambda self: hvPlot(self)
    _patch_plot.__doc__ = hvPlot.__call__.__doc__
    patch_property = property(_patch_plot)
    setattr(intake.source.base.DataSource, name, patch_property)
    post_patch(extension, logo)

try:
    import intake.plotting # noqa
    patch()
except:
    import intake
    if Version(intake.__version__) <= Version('0.1.5'):
        patch()
        patch(name='plot')
    else:
        post_patch(extension='bokeh', logo=False)
