import pandas as pd
import hvplot.pandas  # noqa


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


def test_ohlc_hover_cols():
    plot = df.hvplot.ohlc(y=ohlc_cols, hover_cols=['Volume'])
    segments = plot.Segments.I
    assert 'Volume' in segments
    tooltips = segments.opts.get('plot').kwargs['tools'][0].tooltips
    assert len(tooltips) == len(df.columns) + 1
    assert tooltips[-1] == ('Volume', '@Volume')


def test_ohlc_hover_cols_all():
    plot = df.hvplot.ohlc(y=ohlc_cols, hover_cols='all')
    segments = plot.Segments.I
    assert 'Volume' in segments
    tooltips = segments.opts.get('plot').kwargs['tools'][0].tooltips
    assert len(tooltips) == len(df.columns) + 1
    assert tooltips[-1] == ('Volume', '@Volume')


def test_ohlc_date_tooltip_format():
    plot = df.hvplot.ohlc(y=ohlc_cols)
    segments = plot.Segments.I
    hover_tool = segments.opts.get('plot').kwargs['tools'][0]
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

    ohlc_cols = ['Open', 'High', 'Low', 'Close']

    plot = df.hvplot.ohlc(y=ohlc_cols)
    segments = plot.Segments.I
    hover_tool = segments.opts.get('plot').kwargs['tools'][0]
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
    hover_tool = segments.opts.get('plot').kwargs['tools'][0]
    tooltips = hover_tool.tooltips
    assert len(tooltips) == len(df.columns)
    assert tooltips[0] == ('Date', '@Date{%F %T}')
