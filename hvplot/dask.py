import sys

from .interactive import Interactive


class DaskInteractive(Interactive):
    @classmethod
    def applies(cls, obj):
        if 'dask.dataframe' in sys.modules:
            import dask.dataframe as dd

            return isinstance(obj, (dd.Series, dd.DataFrame))
        return False

    def compute(self):
        self._method = 'compute'
        return self.__call__()


def patch(name='hvplot', interactive='interactive', extension='bokeh', logo=False):
    from . import hvPlotTabular, post_patch, _module_extensions

    try:
        import dask.dataframe as dd
    except ImportError:
        raise ImportError('Could not patch plotting API onto dask. Dask could not be imported.')

    if 'hvplot.dask' not in _module_extensions:
        _patch_plot = lambda self: hvPlotTabular(self)  # noqa: E731
        _patch_plot.__doc__ = hvPlotTabular.__call__.__doc__
        plot_prop = property(_patch_plot)
        setattr(dd.DataFrame, name, plot_prop)
        setattr(dd.Series, name, plot_prop)

        _patch_interactive = lambda self: DaskInteractive(self)  # noqa: E731
        _patch_interactive.__doc__ = DaskInteractive.__call__.__doc__
        interactive_prop = property(_patch_interactive)
        setattr(dd.DataFrame, interactive, interactive_prop)
        setattr(dd.Series, interactive, interactive_prop)

        _module_extensions.add('hvplot.dask')

    post_patch(extension, logo)


patch()
