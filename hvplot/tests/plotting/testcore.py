import numpy as np
import pandas as pd
import hvplot.pandas  # noqa

import pytest

try:
    import polars as pl
    import hvplot.polars  # noqa
    skip_polar = False
except ImportError:
    class pl:
        DataFrame = None
        LazyFrame = None
        Series = None
    skip_polar = True


FRAME_IGNORE_TYPES = {"bivariate", "heatmap", "hexbin", "labels", "vectorfield"}
SERIES_IGNORE_TYPES = {*FRAME_IGNORE_TYPES, "points", "polygons", "ohlc", "paths"}

y_combinations = pytest.mark.parametrize("y", (
    ["A", "B", "C", "D"],
    ("A", "B", "C", "D"),
    {"A", "B", "C", "D"},
    np.array(["A", "B", "C", "D"]),
    pd.Index(["A", "B", "C", "D"]),
    pd.Series(["A", "B", "C", "D"]),
    ),
    ids=lambda x: type(x).__name__
)

@y_combinations
def test_diffent_input_types_pandas(y):
    df = pd._testing.makeDataFrame()
    types = {t for t in dir(df.hvplot) if not t.startswith("_")}

    for t in types - FRAME_IGNORE_TYPES:
        df.hvplot(y=y, kind=t)


def test_series_pandas():
    ser = pd.Series(np.random.rand(10), name="A")
    assert isinstance(ser, pd.Series)

    types = {t for t in dir(ser.hvplot) if not t.startswith("_")}
    for t in types - SERIES_IGNORE_TYPES:
        ser.hvplot(kind=t)



@pytest.mark.skipif(skip_polar, reason="polars not installed")
@pytest.mark.parametrize("cast", (pl.DataFrame, pl.LazyFrame))
@y_combinations
def test_diffent_input_types_polars(y, cast):
    df = cast(pd._testing.makeDataFrame())
    assert isinstance(df, cast)

    types = {t for t in dir(df.hvplot) if not t.startswith("_")}
    for t in types - FRAME_IGNORE_TYPES:
        df.hvplot(y=y, kind=t)


@pytest.mark.skipif(skip_polar, reason="polars not installed")
def test_series_polars():
    ser = pl.Series(values=np.random.rand(10), name="A")
    assert isinstance(ser, pl.Series)

    types = {t for t in dir(ser.hvplot) if not t.startswith("_")}
    for t in types - SERIES_IGNORE_TYPES:
        ser.hvplot(kind=t)
