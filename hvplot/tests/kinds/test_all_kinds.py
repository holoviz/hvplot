"""Sweeps over every kind of hvPlot, with each tabular library and with each backend.

A new kind is picked up automatically. If it fails with some libraries or backends, add it
to the known failures below: the dicts are keyed by (kind, library) or (kind, backend).
"""

import holoviews as hv
import numpy as np
import pandas as pd
import pytest
from holoviews.core.options import AbbreviatedException

from hvplot import hvPlotTabular
from hvplot.converter import HoloViewsConverter
from hvplot.tests._data import makeDataFrame
from hvplot.tests._deps import TABULAR_LIBS

BACKENDS = ['bokeh', 'matplotlib', 'plotly']

KINDS = sorted(t for t in dir(hvPlotTabular) if not t.startswith('_') and t != 'explorer')
# These kinds need other columns than the ones selected by y.
FRAME_KINDS = sorted(set(KINDS) - {'bivariate', 'heatmap', 'hexbin', 'labels', 'vectorfield'})
SERIES_KINDS = sorted(set(FRAME_KINDS) - {'points', 'polygons', 'ohlc', 'paths'})

# A subset of the columns, so that the test fails if y is ignored.
Y = ['B', 'D']
# ohlc takes 4 columns: open, high, low, close. Reversed so that the order is checked too.
OHLC_Y = ['D', 'C', 'B', 'A']
# Kinds that melt y into a `Variable` column rather than make one element per column.
MELTED_KINDS = {'bar', 'barh', 'box', 'violin'}

# The kinds that do not plot the columns Y, with a backend.
BACKEND_KWARGS = {
    'bivariate': {'x': 'A', 'y': 'B'},
    'heatmap': {'x': 'A', 'y': 'B', 'C': 'C'},
    'ohlc': {'y': OHLC_Y},
    'hexbin': {'x': 'A', 'y': 'B'},
    'labels': {'x': 'A', 'y': 'B', 'text': 'C'},
    'vectorfield': {'x': 'A', 'y': 'B', 'angle': 'C', 'mag': 'D'},
}

# The default x is the index, which ibis tables don't have, and which step cannot render
# when it is the string index of the test data.
X = {(kind, 'ibis'): 'A' for kind in ['area', 'bar', 'barh', 'errorbars', 'line', 'scatter']}
X |= {('step', lib): 'A' for lib in TABULAR_LIBS}

# The kinds with no hvPlot element for the backend raise an error when called.
NOT_SUPPORTED = [('hexbin', 'plotly'), ('polygons', 'plotly'), ('vectorfield', 'plotly')]

# Known failures, as marks: `xfail` when the plot cannot be built, `render_xfail` when it cannot
# be rendered. They are not strict when the reason names another library instead of `BUG:`.
errorbars_bug = pytest.mark.render_xfail(
    reason='BUG: errorbars without yerr1 builds an ErrorBars with no error dimension'
)
dask_bars_bug = pytest.mark.render_xfail(
    reason='HoloViews: Bars of a dask DataFrame with two key dimensions fail to render',
    strict=False,
)
ibis_narwhals_bug = pytest.mark.render_xfail(
    reason='HoloViews: the Narwhals interface fails to render this element with an ibis table',
    strict=False,
)
LIB_FAILURES = {
    ('bar', 'ibis'): pytest.mark.xfail(reason='BUG: bar fails to melt an ibis table'),
    ('barh', 'ibis'): pytest.mark.xfail(reason='BUG: barh fails to melt an ibis table'),
    ('box', 'ibis'): pytest.mark.xfail(reason='BUG: box fails to melt an ibis table'),
    ('density', 'ibis'): pytest.mark.xfail(
        reason='BUG: density on ibis requires x, which it does not use'
    ),
    ('kde', 'ibis'): pytest.mark.xfail(
        reason='BUG: kde on ibis requires x, which it does not use'
    ),
    ('ohlc', 'ibis'): pytest.mark.xfail(reason='BUG: ohlc reads the dtype of an ibis column'),
    ('table', 'ibis'): pytest.mark.xfail(reason='BUG: table reads the index of an ibis table'),
    ('violin', 'ibis'): pytest.mark.xfail(reason='BUG: violin fails to melt an ibis table'),
    ('bar', 'dask'): dask_bars_bug,
    ('barh', 'dask'): dask_bars_bug,
    ('polygons', 'ibis'): ibis_narwhals_bug,
    ('step', 'ibis'): ibis_narwhals_bug,
    **{('errorbars', lib): errorbars_bug for lib in TABULAR_LIBS},
}
# Known failures with a series, by kind.
SERIES_FAILURES = {
    'box': pytest.mark.render_xfail(
        reason='HoloViews: BoxWhisker without kdims fails to render with the hover tool',
        strict=False,
    ),
    'errorbars': errorbars_bug,
}
dataset_bug = pytest.mark.xfail(
    reason='BUG: dataset fails with a KeyError, the options of Dataset are not found',
    raises=KeyError,
)
# Known failures with each backend, as marks.
BACKEND_FAILURES = {
    ('bivariate', 'plotly'): pytest.mark.render_xfail(
        reason='BUG: bivariate on plotly fails to render with a KeyError, not NotImplementedError',
        raises=KeyError,
    ),
    ('dataset', 'matplotlib'): dataset_bug,
    ('dataset', 'plotly'): dataset_bug,
    ('labels', 'matplotlib'): pytest.mark.render_xfail(
        reason='BUG: labels fail to render on matplotlib, Axes.text() gets s twice (converter.py)',
        raises=AbbreviatedException,
    ),
    **{('errorbars', backend): errorbars_bug for backend in BACKENDS},
}

KIND_AND_LIB = [
    pytest.param(kind, lib, X.get((kind, lib)), marks=LIB_FAILURES.get((kind, lib), []))
    for kind in FRAME_KINDS
    for lib in TABULAR_LIBS
]
KIND_AND_BACKEND = [
    pytest.param(kind, backend, marks=BACKEND_FAILURES.get((kind, backend), []))
    for kind in KINDS
    for backend in BACKENDS
    if (kind, backend) not in NOT_SUPPORTED
]


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


@pytest.mark.parametrize(('kind', 'tabular_lib', 'x'), KIND_AND_LIB, indirect=['tabular_lib'])
def test_dataframe(kind, tabular_lib, x):
    y = OHLC_Y if kind == 'ohlc' else Y
    df = tabular_lib(makeDataFrame())
    plot = df.hvplot(x=x, y=y, kind=kind)
    assert_dataframe_plot(plot, kind, y)


@pytest.mark.parametrize('tabular_lib', ['polars'], indirect=True)
@pytest.mark.parametrize(
    'kind',
    [pytest.param(kind, marks=LIB_FAILURES.get((kind, 'polars'), [])) for kind in FRAME_KINDS],
)
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


@pytest.mark.lib_skip('duckdb', 'ibis', reason='DuckDB and Ibis have no Series object.')
@pytest.mark.parametrize(
    'kind', [pytest.param(kind, marks=SERIES_FAILURES.get(kind, [])) for kind in SERIES_KINDS]
)
def test_series(kind, tabular_lib):
    ser = tabular_lib(pd.Series(np.random.rand(10), name='A'))
    plot = ser.hvplot(kind=kind)
    assert_kind_element(plot, kind)


# A numeric index, as the string index of makeDataFrame cannot be rendered by every kind.
@pytest.fixture
def numeric_index_df():
    return makeDataFrame().reset_index(drop=True)


@pytest.mark.parametrize(('kind', 'backend'), KIND_AND_BACKEND, indirect=['backend'])
def test_kind_with_backend(hvplot_pandas, backend, numeric_index_df, kind):
    plot = numeric_index_df.hvplot(kind=kind, **BACKEND_KWARGS.get(kind, {'y': Y}))
    assert_kind_element(plot, kind)


@pytest.mark.parametrize(('kind', 'backend'), NOT_SUPPORTED, indirect=['backend'])
def test_kind_not_supported(hvplot_pandas, backend, numeric_index_df, kind):
    with pytest.raises(
        NotImplementedError, match=f"'{kind}' plot not supported by the '{backend}'"
    ):
        numeric_index_df.hvplot(kind=kind, **BACKEND_KWARGS.get(kind, {'y': Y}))
