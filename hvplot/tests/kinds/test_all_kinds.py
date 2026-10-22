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

TABULAR_LIBS = ['pandas', 'dask', 'polars', 'duckdb', 'ibis']
# Ibis tables have no index, which these kinds use as the default x.
IBIS_NO_INDEX_KINDS = {'area', 'bar', 'barh', 'errorbars', 'line', 'scatter', 'step'}
TABULAR_BUGS = {
    ('box', 'ibis'): 'BUG: box fails to melt an ibis table',
    ('density', 'ibis'): 'BUG: density on ibis requires x, which it does not use',
    ('kde', 'ibis'): 'BUG: kde on ibis requires x, which it does not use',
    ('ohlc', 'ibis'): 'BUG: ohlc reads the dtype of an ibis column',
    ('table', 'ibis'): 'BUG: table reads the index of an ibis table',
    ('violin', 'ibis'): 'BUG: violin fails to melt an ibis table',
}


def kind_and_lib_params(kinds):
    params = []
    for kind in sorted(kinds):
        for lib in TABULAR_LIBS:
            marks = []
            if lib == 'ibis' and kind in IBIS_NO_INDEX_KINDS:
                marks = pytest.mark.skip(reason='ibis tables have no index to use as x')
            elif (kind, lib) in TABULAR_BUGS:
                marks = pytest.mark.xfail(strict=True, reason=TABULAR_BUGS[kind, lib])
            params.append(pytest.param(kind, lib, marks=marks))
    return params


frame_kinds = pytest.mark.parametrize(
    ('kind', 'tabular_lib'), kind_and_lib_params(FRAME_TYPES), indirect=['tabular_lib']
)

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


@frame_kinds
@y_combinations
def test_dataframe(kind, y, tabular_lib):
    df = tabular_lib(makeDataFrame())
    plot = df.hvplot(y=y, kind=kind)
    assert_dataframe_plot(plot, kind)


@pytest.mark.parametrize('tabular_lib', ['polars'], indirect=True)
@pytest.mark.parametrize('kind', sorted(FRAME_TYPES))
@y_combinations
def test_lazyframe_polars(kind, y, tabular_lib):
    df = tabular_lib(makeDataFrame()).lazy()
    plot = df.hvplot(y=y, kind=kind)
    assert_dataframe_plot(plot, kind)


# DuckDB and Ibis have no Series object.
@pytest.mark.parametrize('tabular_lib', ['pandas', 'dask', 'polars'], indirect=True)
@pytest.mark.parametrize('kind', sorted(SERIES_TYPES))
def test_series(kind, tabular_lib):
    ser = tabular_lib(pd.Series(np.random.rand(10), name='A'))
    plot = ser.hvplot(kind=kind)
    assert_kind_element(plot, kind)
