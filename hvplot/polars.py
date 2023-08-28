import itertools

from hvplot import hvPlotTabular, post_patch
from hvplot.converter import HoloViewsConverter

try:
    import polars as pl
except:
    raise ImportError(
        "Could not patch plotting API onto Polars. Polars could not be imported."
    )


@pl.api.register_dataframe_namespace("hvplot")
@pl.api.register_series_namespace("hvplot")
@pl.api.register_lazyframe_namespace("hvplot")
class hvPlotTabularPolars(hvPlotTabular):
    def _get_converter(self, x=None, y=None, kind=None, **kwds):
        params = dict(self._metadata, **kwds)
        x = x or params.pop("x", None)
        y = y or params.pop("y", None)
        kind = kind or params.pop("kind", None)

        # Find columns which should be converted for LazyDataFrame and DataFrame
        if isinstance(self._data, (pl.LazyFrame, pl.DataFrame)):
            possible_columns = [
                [v] if isinstance(v, str) else v
                for v in params.values()
                if isinstance(v, (str, list))
            ]
            columns = (
                set(self._data.columns) & set(itertools.chain(*possible_columns))
            ) or {self._data.columns[0]}
            columns |= {x, y}
            columns.discard(None)

        if isinstance(self._data, pl.DataFrame):
            data = self._data.select(columns).to_pandas()
        elif isinstance(self._data, pl.Series):
            data = self._data.to_pandas()
        elif isinstance(self._data, pl.LazyFrame):
            data = self._data.select(columns).collect().to_pandas()
        else:
            raise ValueError(
                "Only Polars DataFrame, Series, and LazyFrame are supported"
            )

        return HoloViewsConverter(data, x, y, kind=kind, **params)


def patch(name="hvplot", extension="bokeh", logo=False):
    import hvplot.pandas  # noqa

    post_patch(extension, logo)


patch()
