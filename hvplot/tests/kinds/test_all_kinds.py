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
IBIS_NEEDS_X_KINDS = {'area', 'bar', 'barh', 'errorbars', 'line', 'scatter', 'step'}
TABULAR_BUGS = {
    ('bar', 'ibis'): 'BUG: bar fails to melt an ibis table',
    ('barh', 'ibis'): 'BUG: barh fails to melt an ibis table',
    ('box', 'ibis'): 'BUG: box fails to melt an ibis table',
    ('density', 'ibis'): 'BUG: density on ibis requires x, which it does not use',
    ('kde', 'ibis'): 'BUG: kde on ibis requires x, which it does not use',
    ('ohlc', 'ibis'): 'BUG: ohlc reads the dtype of an ibis column',
    ('table', 'ibis'): 'BUG: table reads the index of an ibis table',
    ('violin', 'ibis'): 'BUG: violin fails to melt an ibis table',
}

# A subset of the columns, so that the test fails if y is ignored.
Y = ['B', 'D']
# ohlc takes 4 columns: open, high, low, close. Reversed so that the order is checked too.
OHLC_Y = ['D', 'C', 'B', 'A']
# Kinds that melt y into a `Variable` column rather than make one element per column.
MELTED_KINDS = {'bar', 'barh', 'box', 'violin'}


def kind_and_lib_params(kinds):
    params = []
    for kind in sorted(kinds):
        for lib in TABULAR_LIBS:
            marks = []
            x = None
            if lib == 'ibis' and kind in IBIS_NEEDS_X_KINDS:
                x = 'A'
            if (kind, lib) in TABULAR_BUGS:
                marks = pytest.mark.xfail(strict=True, reason=TABULAR_BUGS[kind, lib])
            params.append(pytest.param(kind, lib, x, marks=marks))
    return params


frame_kinds = pytest.mark.parametrize(
    ('kind', 'tabular_lib', 'x'), kind_and_lib_params(FRAME_TYPES), indirect=['tabular_lib']
)


def assert_kind_element(plot, kind):
    """Assert the plot is made of the element the kind maps to."""
    element = plot
    if isinstance(plot, hv.NdOverlay):  # one element per column
        element = plot.last
    elif kind == 'ohlc':  # Rectangles for the boxes, overlaid with Segments for the whiskers
        element = plot.Rectangles.I
    assert isinstance(element, HoloViewsConverter._kind_mapping[kind])


def assert_dataframe_plot(plot, kind, y):
    """Assert the plot is made of the element of the kind and of the columns selected by y."""
    assert_kind_element(plot, kind)
    if isinstance(plot, hv.NdOverlay):
        # Compared as a set as the order of y given as a set is arbitrary.
        assert set(plot.keys()) == set(y)
    elif kind in MELTED_KINDS:
        assert set(plot.dimension_values('Variable')) == set(y)
    elif kind == 'ohlc':
        # Only the y dimensions (open, close), as the x ones depend on the library.
        assert [d.name for d in plot.Rectangles.I.kdims][1::2] == [y[0], y[3]]


@frame_kinds
def test_dataframe(kind, tabular_lib, x):
    y = OHLC_Y if kind == 'ohlc' else Y
    df = tabular_lib(makeDataFrame())
    plot = df.hvplot(x=x, y=y, kind=kind)
    assert_dataframe_plot(plot, kind, y)


@pytest.mark.parametrize('tabular_lib', ['polars'], indirect=True)
@pytest.mark.parametrize('kind', sorted(FRAME_TYPES))
def test_lazyframe_polars(kind, tabular_lib):
    y = OHLC_Y if kind == 'ohlc' else Y
    df = tabular_lib(makeDataFrame()).lazy()
    plot = df.hvplot(y=y, kind=kind)
    assert_dataframe_plot(plot, kind, y)


# y is normalized the same way whatever the library, and these kinds consume it differently
# (one element per column, melted into a Variable column, binned per column).
@pytest.mark.parametrize('kind', ['line', 'bar', 'hist'])
@pytest.mark.parametrize(
    'y',
    (list(Y), tuple(Y), set(Y), np.array(Y), pd.Index(Y), pd.Series(Y)),
    ids=lambda y: type(y).__name__,
)
def test_y_container_types(kind, y, hvplot_pandas):
    plot = makeDataFrame().hvplot(y=y, kind=kind)
    assert_dataframe_plot(plot, kind, Y)


@pytest.mark.parametrize('tabular_lib', ['ibis'], indirect=True)
def test_ibis_requires_x(tabular_lib):
    # Ibis tables have no index to use as the default x.
    df = tabular_lib(makeDataFrame())
    with pytest.raises(ValueError, match='Set x explicitly'):
        df.hvplot.line(y=Y)


# DuckDB and Ibis have no Series object.
@pytest.mark.parametrize('tabular_lib', ['pandas', 'dask', 'polars'], indirect=True)
@pytest.mark.parametrize('kind', sorted(SERIES_TYPES))
def test_series(kind, tabular_lib):
    ser = tabular_lib(pd.Series(np.random.rand(10), name='A'))
    plot = ser.hvplot(kind=kind)
    assert_kind_element(plot, kind)
