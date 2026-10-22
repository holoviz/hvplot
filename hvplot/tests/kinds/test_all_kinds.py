import holoviews as hv
import numpy as np
import pandas as pd
import pytest

from hvplot import hvPlotTabular
from hvplot.converter import HoloViewsConverter
from hvplot.tests._data import makeDataFrame

TYPES = {t for t in dir(hvPlotTabular) if not t.startswith('_') and t != 'explorer'}
FRAME_TYPES = TYPES - {'bivariate', 'heatmap', 'hexbin', 'labels', 'vectorfield'}
SERIES_TYPES = FRAME_TYPES - {'points', 'polygons', 'ohlc', 'paths'}
frame_kinds = pytest.mark.parametrize('kind', sorted(FRAME_TYPES))
series_kinds = pytest.mark.parametrize('kind', sorted(SERIES_TYPES))

COLUMNS = ['A', 'B', 'C', 'D']
y_combinations = pytest.mark.parametrize(
    'y',
    (
        list(COLUMNS),
        tuple(COLUMNS),
        set(COLUMNS),
        np.array(COLUMNS),
        pd.Index(COLUMNS),
        pd.Series(COLUMNS),
    ),
    ids=lambda x: type(x).__name__,
)
tabular_libs = pytest.mark.parametrize('tabular_lib', ['pandas', 'dask', 'polars'], indirect=True)


def assert_kind_element(plot, kind):
    """Assert the plot is made of the element the kind maps to."""
    element = plot
    if isinstance(plot, hv.NdOverlay):  # one element per column
        element = plot.last
    elif kind == 'ohlc':  # Rectangles for the boxes, overlaid with Segments for the whiskers
        element = plot.Rectangles.I
    assert isinstance(element, HoloViewsConverter._kind_mapping[kind])


def assert_dataframe_plot(plot, kind):
    assert_kind_element(plot, kind)
    if isinstance(plot, hv.NdOverlay):
        # Compared as a set as the order of y given as a set is arbitrary.
        assert set(plot.keys()) == set(COLUMNS)


@tabular_libs
@frame_kinds
@y_combinations
def test_dataframe(kind, y, tabular_lib):
    df = tabular_lib(makeDataFrame())
    plot = df.hvplot(y=y, kind=kind)
    assert_dataframe_plot(plot, kind)


@pytest.mark.parametrize('tabular_lib', ['polars'], indirect=True)
@frame_kinds
@y_combinations
def test_lazyframe_polars(kind, y, tabular_lib):
    df = tabular_lib(makeDataFrame()).lazy()
    plot = df.hvplot(y=y, kind=kind)
    assert_dataframe_plot(plot, kind)


@tabular_libs
@series_kinds
def test_series(kind, tabular_lib):
    ser = tabular_lib(pd.Series(np.random.rand(10), name='A'))
    plot = ser.hvplot(kind=kind)
    assert_kind_element(plot, kind)
