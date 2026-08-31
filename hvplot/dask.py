"""Patch the hvPlot plotting API onto Dask objects."""

import sys

from .interactive import Interactive


class DaskInteractive(Interactive):
    """Interactive pipeline wrapper for Dask objects."""

    @classmethod
    def applies(cls, obj):
        """Return whether the object is a Dask Series or DataFrame."""
        if 'dask.dataframe' in sys.modules:
            import dask.dataframe as dd

            return isinstance(obj, (dd.Series, dd.DataFrame))
        return False

    def compute(self):
        """Trigger computation of the underlying Dask object."""
        self._method = 'compute'
        return self.__call__()


def patch(name='hvplot', interactive='interactive', extension='bokeh', logo=False):
    """Patch the hvPlot plotting API onto Dask DataFrame and Series."""
    from . import _module_extensions, hvPlotTabular, post_patch

    try:
        import dask.dataframe as dd
    except ImportError as e:
        raise ImportError(
            'Could not patch plotting API onto dask. Dask could not be imported.'
        ) from e

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
