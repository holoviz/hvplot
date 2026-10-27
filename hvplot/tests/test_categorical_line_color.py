"""Categorical color mapping for line-like plots (issue #1759)."""

import holoviews as hv
import pandas as pd
import pytest
from holoviews.core.overlay import NdOverlay

import hvplot.pandas  # noqa: F401


@pytest.fixture
def series_data():
    return {
        'x': [0, 1, 2, 0, 1, 2],
        'y': [1, 2, 3, 3, 2, 1],
        'cat': ['A'] * 3 + ['B'] * 3,
    }


@pytest.mark.parametrize('kind', ['line', 'step', 'area'])
@pytest.mark.parametrize('frontend', ['pandas', 'polars', 'polars_lazy'])
def test_categorical_color_matches_by_and_renders(series_data, kind, frontend):
    if frontend == 'pandas':
        data = pd.DataFrame(series_data)
    else:
        pl = pytest.importorskip('polars')
        pytest.importorskip('pyarrow')
        import hvplot.polars  # noqa: F401

        data = pl.DataFrame(series_data)
        if frontend == 'polars_lazy':
            data = data.lazy()

    actual = getattr(data.hvplot, kind)(x='x', y='y', color='cat')
    expected = getattr(data.hvplot, kind)(x='x', y='y', by='cat')
    assert isinstance(actual, NdOverlay)
    assert list(actual.keys()) == list(expected.keys()) == ['A', 'B']
    assert len(actual) == 2
    hv.renderer('bokeh').get_plot(actual)


@pytest.mark.parametrize('kind', ['line', 'step', 'area'])
def test_literal_color_and_explicit_by_unchanged(series_data, kind):
    df = pd.DataFrame(series_data)
    literal = getattr(df.hvplot, kind)(x='x', y='y', color='red')
    assert not isinstance(literal, NdOverlay)
    hv.renderer('bokeh').get_plot(literal)

    grouped = getattr(df.hvplot, kind)(x='x', y='y', color='red', by='cat')
    assert isinstance(grouped, NdOverlay)
    assert list(grouped.keys()) == ['A', 'B']
    hv.renderer('bokeh').get_plot(grouped)


@pytest.mark.parametrize('kind', ['line', 'step', 'area'])
def test_direct_kind_dispatches_categorical_color(series_data, kind):
    df = pd.DataFrame(series_data)
    plot = df.hvplot(x='x', y='y', kind=kind, color='cat')
    assert isinstance(plot, NdOverlay)
    assert list(plot.keys()) == ['A', 'B']
