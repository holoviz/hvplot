import numpy as np
import pandas as pd
import pytest
from holoviews import Store
from holoviews.element import Rectangles, Segments

pytestmark = pytest.mark.usefixtures('hvplot_pandas')

df = pd.DataFrame(
    {
        'Open': [100.00, 101.25, 102.75],
        'High': [104.10, 105.50, 110.00],
        'Low': [94.00, 97.10, 99.20],
        'Close': [101.15, 99.70, 109.50],
        'Volume': [10012, 5000, 18000],
    },
    index=[pd.Timestamp('2022-08-01'), pd.Timestamp('2022-08-03'), pd.Timestamp('2022-08-04')],
)

ohlc_cols = ['Open', 'High', 'Low', 'Close']


def test_x():
    plot = df.reset_index(names='Date').hvplot.ohlc(x='Date', y=ohlc_cols)
    assert plot.Segments.I.kdims == ['Date', 'Low', 'Date', 'High']
    assert plot.Rectangles.I.kdims == ['lbound', 'Open', 'ubound', 'Close']


def test_x_default_index():
    plot = df.hvplot.ohlc(y=ohlc_cols)
    assert plot.Segments.I.kdims == ['index', 'Low', 'index', 'High']


@pytest.mark.parametrize(
    'tabular_lib',
    [
        'pandas',
        'dask',
        'polars',
        'duckdb',
        pytest.param(
            'ibis',
            marks=pytest.mark.xfail(
                strict=True, reason='BUG: ohlc reads the dtype of an ibis column'
            ),
        ),
    ],
    indirect=True,
)
def test_y(tabular_lib):
    data = tabular_lib(df.reset_index(names='Date'))
    plot = data.hvplot.ohlc(x='Date', y=ohlc_cols)
    rects, segments = plot.Rectangles.I, plot.Segments.I
    assert isinstance(rects, Rectangles)
    assert isinstance(segments, Segments)
    # The boxes go from open to close, the whiskers from low to high.
    assert rects.kdims == ['lbound', 'Open', 'ubound', 'Close']
    assert segments.kdims == ['Date', 'Low', 'Date', 'High']
    assert list(segments.dimension_values('Low')) == list(df['Low'])


def test_y_default():
    plot = df.hvplot.ohlc()
    assert plot.Rectangles.I.kdims == ['lbound', 'Open', 'ubound', 'Close']
    assert plot.Segments.I.kdims == ['index', 'Low', 'index', 'High']


def test_bar_width():
    data = df.reset_index(drop=True)
    plot = data.hvplot.ohlc(y=ohlc_cols, bar_width=0.2)
    rects = plot.Rectangles.I
    widths = rects.dimension_values('ubound') - rects.dimension_values('lbound')
    np.testing.assert_allclose(widths, 0.2)


def test_pos_color():
    plot = df.hvplot.ohlc(y=ohlc_cols, pos_color='blue')
    rects = plot.Rectangles.I
    color = Store.lookup_options('bokeh', rects, 'style').kwargs['color']
    # Open < Close for the first and last bars.
    assert list(color.apply(rects)) == ['blue', 'red', 'blue']


def test_neg_color():
    plot = df.hvplot.ohlc(y=ohlc_cols, neg_color='orange')
    rects = plot.Rectangles.I
    color = Store.lookup_options('bokeh', rects, 'style').kwargs['color']
    assert list(color.apply(rects)) == ['green', 'orange', 'green']


def test_line_color():
    plot = df.hvplot.ohlc(y=ohlc_cols, line_color='grey')
    assert Store.lookup_options('bokeh', plot.Segments.I, 'style').kwargs['color'] == 'grey'


def test_ohlc_hover_cols():
    plot = df.hvplot.ohlc(y=ohlc_cols, hover_cols=['Volume'])
    segments = plot.Segments.I
    assert 'Volume' in segments
    tooltips = Store.lookup_options('bokeh', segments, 'plot').kwargs['tools'][0].tooltips
    assert len(tooltips) == len(df.columns) + 1
    assert tooltips[-1] == ('Volume', '@Volume')


def test_ohlc_hover_cols_all():
    plot = df.hvplot.ohlc(y=ohlc_cols, hover_cols='all')
    segments = plot.Segments.I
    assert 'Volume' in segments
    tooltips = Store.lookup_options('bokeh', segments, 'plot').kwargs['tools'][0].tooltips
    assert len(tooltips) == len(df.columns) + 1
    assert tooltips[-1] == ('Volume', '@Volume')


def test_ohlc_date_tooltip_format():
    plot = df.hvplot.ohlc(y=ohlc_cols)
    segments = plot.Segments.I
    hover_tool = Store.lookup_options('bokeh', segments, 'plot').kwargs['tools'][0]
    tooltips = hover_tool.tooltips
    x_label, x_tooltip = tooltips[0]
    assert '{%F %T}' in x_tooltip
    formatter_key = '@' + x_label
    formatter = hover_tool.formatters
    assert formatter[formatter_key] == 'datetime'


def test_ohlc_non_datetime_x_axis():
    df = pd.DataFrame(
        {
            'Open': [100.00, 101.25, 102.75],
            'High': [104.10, 105.50, 110.00],
            'Low': [94.00, 97.10, 99.20],
            'Close': [101.15, 99.70, 109.50],
            'Volume': [10012, 5000, 18000],
        },
        index=[1, 2, 3],
    )
    plot = df.hvplot.ohlc(y=ohlc_cols)
    segments = plot.Segments.I
    hover_tool = Store.lookup_options('bokeh', segments, 'plot').kwargs['tools'][0]
    tooltips = hover_tool.tooltips
    x_label, x_tooltip = tooltips[0]
    assert '{%F}' not in x_tooltip
    formatter_key = '@' + x_label
    assert formatter_key not in hover_tool.formatters


def test_ohlc_non_index_date_col():
    df = pd.DataFrame(
        {
            'Date': [
                pd.Timestamp('2022-08-01'),
                pd.Timestamp('2022-08-03'),
                pd.Timestamp('2022-08-04'),
            ],
            'Open': [100.00, 101.25, 102.75],
            'High': [104.10, 105.50, 110.00],
            'Low': [94.00, 97.10, 99.20],
            'Close': [101.15, 99.70, 109.50],
            'Volume': [10012, 5000, 18000],
        },
    )
    plot = df.hvplot.ohlc(hover_cols='all', use_index=False)
    segments = plot.Segments.I
    hover_tool = Store.lookup_options('bokeh', segments, 'plot').kwargs['tools'][0]
    tooltips = hover_tool.tooltips
    assert len(tooltips) == len(df.columns)
    assert tooltips[0] == ('Date', '@Date{%F %T}')
