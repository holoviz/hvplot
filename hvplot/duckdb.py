"""Adds the `.hvplot` method to duckdb.DuckDBPyRelation and duckdb.DuckDBPyConnection"""


def patch(name='hvplot', interactive='interactive', extension='bokeh', logo=False):
    from hvplot.plotting.core import hvPlotTabularDuckDB
    from . import post_patch

    try:
        import duckdb
    except ImportError:
        raise ImportError(
            'Could not patch plotting API onto DuckDB. DuckDB could not be imported.'
        )

    # Patching for DuckDBPyRelation and DuckDBPyConnection
    _patch_duckdb_plot = lambda self: hvPlotTabularDuckDB(self)  # noqa: E731
    _patch_duckdb_plot.__doc__ = hvPlotTabularDuckDB.__call__.__doc__
    plot_prop_duckdb = property(_patch_duckdb_plot)
    setattr(duckdb.DuckDBPyRelation, name, plot_prop_duckdb)
    setattr(duckdb.DuckDBPyConnection, name, plot_prop_duckdb)

    post_patch(extension, logo)


patch()
