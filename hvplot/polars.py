"""Adds the `.hvplot` method to pl.DataFrame, pl.LazyFrame and pl.Series"""

from hvplot import post_patch
from hvplot.plotting.core import hvPlotTabularPolars


def patch(name='hvplot', extension='bokeh', logo=False):
    try:
        import polars as pl
    except ImportError:
        raise ImportError(
            'Could not patch plotting API onto Polars. Polars could not be imported.'
        )
    pl.api.register_dataframe_namespace(name)(hvPlotTabularPolars)
    pl.api.register_series_namespace(name)(hvPlotTabularPolars)
    pl.api.register_lazyframe_namespace(name)(hvPlotTabularPolars)

    post_patch(extension, logo)


patch()
