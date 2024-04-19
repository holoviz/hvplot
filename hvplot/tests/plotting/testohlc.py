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
