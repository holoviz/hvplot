import numpy as np
import pandas as pd
import pytest

from hvplot import hvPlotTabular
from hvplot.tests._data import makeDataFrame

try:
    import polars as pl

    skip_polar = False
except ImportError:

    class pl:
        DataFrame = None
        LazyFrame = None
        Series = None

    skip_polar = True

try:
    import dask.dataframe as dd
except ImportError:
    dd = None


TYPES = {t for t in dir(hvPlotTabular) if not t.startswith('_') and t != 'explorer'}
FRAME_TYPES = TYPES - {'bivariate', 'heatmap', 'hexbin', 'labels', 'vectorfield'}
SERIES_TYPES = FRAME_TYPES - {'points', 'polygons', 'ohlc', 'paths'}
frame_kinds = pytest.mark.parametrize('kind', sorted(FRAME_TYPES))
series_kinds = pytest.mark.parametrize('kind', sorted(SERIES_TYPES))

y_combinations = pytest.mark.parametrize(
    'y',
    (
        ['A', 'B', 'C', 'D'],
        ('A', 'B', 'C', 'D'),
        {'A', 'B', 'C', 'D'},
        np.array(['A', 'B', 'C', 'D']),
        pd.Index(['A', 'B', 'C', 'D']),
        pd.Series(['A', 'B', 'C', 'D']),
    ),
    ids=lambda x: type(x).__name__,
)

pytestmark = pytest.mark.usefixtures('hvplot_pandas')


@pytest.fixture
def hvplot_dask():
    import hvplot.dask  # noqa: F401


@pytest.fixture
def hvplot_polars():
    import hvplot.polars  # noqa: F401


@frame_kinds
@y_combinations
def test_dataframe_pandas(kind, y):
    df = makeDataFrame()
    df.hvplot(y=y, kind=kind)


@series_kinds
def test_series_pandas(kind):
    ser = pd.Series(np.random.rand(10), name='A')
    ser.hvplot(kind=kind)


@pytest.mark.skipif(dd is None, reason='dask not installed')
@frame_kinds
@y_combinations
def test_dataframe_dask(kind, y, hvplot_dask):
    df = dd.from_pandas(makeDataFrame(), npartitions=2)
    assert isinstance(df, dd.DataFrame)
    df.hvplot(y=y, kind=kind)


@pytest.mark.skipif(dd is None, reason='dask not installed')
@series_kinds
def test_series_dask(kind, hvplot_dask):
    ser = dd.from_pandas(pd.Series(np.random.rand(10), name='A'), npartitions=2)
    assert isinstance(ser, dd.Series)
    ser.hvplot(kind=kind)


@pytest.mark.skipif(skip_polar, reason='polars not installed')
@pytest.mark.parametrize('cast', (pl.DataFrame, pl.LazyFrame))
@frame_kinds
@y_combinations
def test_dataframe_polars(kind, y, cast, hvplot_polars):
    df = cast(makeDataFrame())
    assert isinstance(df, cast)
    df.hvplot(y=y, kind=kind)


@pytest.mark.skipif(skip_polar, reason='polars not installed')
@series_kinds
def test_series_polars(kind, hvplot_polars):
    ser = pl.Series(values=np.random.rand(10), name='A')
    assert isinstance(ser, pl.Series)
    ser.hvplot(kind=kind)
