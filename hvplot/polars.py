"""Adds the `.hvplot` method to pl.DataFrame, pl.LazyFrame and pl.Series."""

from hvplot import _module_extensions, post_patch
from hvplot.plotting.core import hvPlotTabularPolars


def patch(name='hvplot', extension='bokeh', logo=False):
    """Patch the hvPlot plotting API onto polars DataFrame, LazyFrame and Series."""
    try:
        import polars as pl
    except ImportError as e:
        raise ImportError(
            'Could not patch plotting API onto Polars. Polars could not be imported.'
        ) from e
    if 'hvplot.polars' not in _module_extensions:
        pl.api.register_dataframe_namespace(name)(hvPlotTabularPolars)
        pl.api.register_series_namespace(name)(hvPlotTabularPolars)
        pl.api.register_lazyframe_namespace(name)(hvPlotTabularPolars)
        _module_extensions.add('hvplot.polars')

    post_patch(extension, logo)


def _unpatch(name='hvplot'):
    """Undo `patch()`. Private, used by the test suite."""
    import polars as pl

    for cls in (pl.DataFrame, pl.Series, pl.LazyFrame):
        if name in vars(cls):
            delattr(cls, name)
        # Polars' namespace registration also records the name here.
        cls._accessors.discard(name)
    _module_extensions.discard('hvplot.polars')


patch()
