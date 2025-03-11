"""
Tests pandas.options.backend setting
"""

from unittest.mock import patch

import pytest
import pandas as pd
import holoviews as hv
from hvplot.converter import HoloViewsConverter
from hvplot.plotting import plot
from hvplot.tests.util import makeDataFrame


no_args = ['line', 'area', 'hist', 'box', 'kde', 'density', 'bar', 'barh']
x_y = ['scatter', 'hexbin']
frame_specials = [
    # delegates to boxplot_frame
    ('boxplot', hv.BoxWhisker),
    # delegates to hist_frame
    ('hist', hv.Histogram),
]
series_specials = [
    # delegates to hist_series
    ('hist', hv.Histogram),
]
no_args_mapping = [
    (kind, el) for kind, el in HoloViewsConverter._kind_mapping.items() if kind in no_args
]
x_y_mapping = [(kind, el) for kind, el in HoloViewsConverter._kind_mapping.items() if kind in x_y]


@pytest.fixture(params=['holoviews', 'hvplot'])
def plotting_backend(request):
    initial_backend = pd.options.plotting.backend
    pd.options.plotting.backend = request.param
    try:
        yield request.param
    finally:
        pd.options.plotting.backend = initial_backend


@pytest.mark.parametrize('kind,el', no_args_mapping)
def test_pandas_series_plot_returns_holoviews_object(plotting_backend, kind, el):
    series = pd.Series([0, 1, 2])
    plot = getattr(series.plot, kind)()
    assert isinstance(plot, el)


@pytest.mark.parametrize('kind,el', no_args_mapping)
def test_pandas_dataframe_plot_returns_holoviews_object(plotting_backend, kind, el):
    df = pd.DataFrame([0, 1, 2])
    plot = getattr(df.plot, kind)()
    assert isinstance(plot, el)


@pytest.mark.parametrize('kind,el', x_y_mapping)
def test_pandas_dataframe_plot_returns_holoviews_object_when_x_and_y_set(
    plotting_backend, kind, el
):
    df = pd.DataFrame({'a': [0, 1, 2], 'b': [5, 7, 2]})
    plot = getattr(df.plot, kind)(x='a', y='b')
    assert isinstance(plot, el)


def test_pandas_dataframe_plot_does_not_implement_pie(plotting_backend):
    df = pd.DataFrame({'a': [0, 1, 2], 'b': [5, 7, 2]})
    with pytest.raises(NotImplementedError, match='pie'):
        df.plot.pie(y='a')


@pytest.mark.parametrize('kind,el', series_specials)
def test_pandas_series_specials_plot_return_holoviews_object(plotting_backend, kind, el):
    series = pd.Series([0, 1, 2])
    plot = getattr(series, kind)()
    assert isinstance(plot, el)


@pytest.mark.parametrize('kind,el', frame_specials)
def test_pandas_frame_specials_plot_return_holoviews_object(plotting_backend, kind, el):
    df = pd.DataFrame([0, 1, 2])
    plot = getattr(df, kind)()
    assert isinstance(plot, el)


@pytest.mark.parametrize('backend', ['holoviews', 'hvplot'])
@pytest.mark.parametrize('kind,el', no_args_mapping)
def test_pandas_series_plot_explicit_returns_holoviews_object(backend, kind, el):
    series = pd.Series([0, 1, 2])
    plot = getattr(series.plot, kind)(backend=backend)
    assert isinstance(plot, el)


@pytest.mark.parametrize('backend', ['holoviews', 'hvplot'])
@pytest.mark.parametrize('kind,el', no_args_mapping)
def test_pandas_dataframe_plot_explicit_returns_holoviews_object(backend, kind, el):
    df = pd.DataFrame([0, 1, 2])
    plot = getattr(df.plot, kind)(backend=backend)
    assert isinstance(plot, el)


@pytest.mark.parametrize('backend', ['holoviews', 'hvplot'])
@pytest.mark.parametrize('kind,el', x_y_mapping)
def test_pandas_dataframe_plot_explicit_returns_holoviews_object_when_x_and_y_set(
    backend, kind, el
):
    df = pd.DataFrame({'a': [0, 1, 2], 'b': [5, 7, 2]})
    plot = getattr(df.plot, kind)(x='a', y='b', backend=backend)
    assert isinstance(plot, el)


@pytest.mark.parametrize('backend', ['holoviews', 'hvplot'])
def test_pandas_dataframe_plot_explicit_does_not_implement_pie(backend):
    df = pd.DataFrame({'a': [0, 1, 2], 'b': [5, 7, 2]})
    with pytest.raises(NotImplementedError, match='pie'):
        df.plot.pie(y='a', backend=backend)


@pytest.mark.parametrize('backend', ['holoviews', 'hvplot'])
@pytest.mark.parametrize('kind,el', series_specials)
def test_pandas_series_specials_plot_explicit_return_holoviews_object(backend, kind, el):
    series = pd.Series([0, 1, 2])
    plot = getattr(series, kind)(backend=backend)
    assert isinstance(plot, el)


@pytest.mark.parametrize('backend', ['holoviews', 'hvplot'])
@pytest.mark.parametrize('kind,el', frame_specials)
def test_pandas_frame_specials_plot_explicit_return_holoviews_object(backend, kind, el):
    df = pd.DataFrame([0, 1, 2])
    plot = getattr(df, kind)(backend=backend)
    assert isinstance(plot, el)


def test_pandas_plot_reuse_plot_dropped(plotting_backend):
    df = pd.DataFrame([0, 1, 2])
    with patch('hvplot.plotting.hvPlotTabular.__call__') as hvcall:
        df.plot.line(reuse_plot=True)
    hvcall.assert_called_with(kind='line')


def test_pandas_plot_sharexy_handled(plotting_backend):
    df = pd.DataFrame([0, 1, 2])
    with patch('hvplot.plotting.hvPlotTabular.__call__') as hvcall:
        df.plot.line(sharex=True, sharey=True)
        hvcall.assert_called_with(kind='line', shared_axes=True)
        df.plot.line(sharex=False, sharey=True)
        hvcall.assert_called_with(kind='line', shared_axes=True)
        df.plot.line(sharex=True, sharey=False)
        hvcall.assert_called_with(kind='line', shared_axes=True)
        df.plot.line(sharex=False, sharey=False)
        hvcall.assert_called_with(kind='line', shared_axes=False)
        df.plot.line(sharex=True)
        hvcall.assert_called_with(kind='line', shared_axes=True)
        df.plot.line(sharex=False)
        hvcall.assert_called_with(kind='line', shared_axes=False)
        df.plot.line(sharey=True)
        hvcall.assert_called_with(kind='line', shared_axes=True)
        df.plot.line(sharey=False)
        hvcall.assert_called_with(kind='line', shared_axes=False)


def test_pandas_plot_extension_loaded(plotting_backend):
    df = pd.DataFrame([0, 1, 2])
    with patch('hvplot.hvplot_extension') as mock_hvplot_ext:
        df.plot.line()
        mock_hvplot_ext.assert_called_once_with('bokeh', logo=False)


def test_plot_supports_duckdb_relation():
    duckdb = pytest.importorskip('duckdb')
    connection = duckdb.connect(':memory:')
    relation = duckdb.from_df(makeDataFrame(), connection=connection)
    out = plot(relation, 'line')
    assert isinstance(out, hv.NdOverlay)


def test_plot_supports_duckdb_connection():
    duckdb = pytest.importorskip('duckdb')
    connection = duckdb.connect(':memory:')
    relation = duckdb.from_df(makeDataFrame(), connection=connection)
    relation.to_view('test')
    out = plot(connection.execute('SELECT * FROM test'), 'line')
    assert isinstance(out, hv.NdOverlay)
