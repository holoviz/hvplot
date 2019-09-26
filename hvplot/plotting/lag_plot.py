from __future__ import absolute_import

import numpy as _np
import pandas as _pd

from  ._core import hvPlot


def lag_plot(data, lag=1, **kwds):
    """Lag plot for time series.

    Parameters:
    -----------
    data: Time series
    lag: lag of the scatter plot, default 1
    kwds: hvplot.scatter options, optional

    Returns:
    --------
    obj : HoloViews object
        The HoloViews representation of the plot.
    """
    if lag != int(lag) or int(lag) <= 0:
        raise ValueError("lag must be a positive integer")
    lag = int(lag)

    values = data.values
    y1 = 'y(t)'
    y2 = 'y(t + {0})'.format(lag)
    lags = _pd.DataFrame({y1: values[:-lag].T.ravel(),
                          y2: values[lag:].T.ravel()})
    if isinstance(data, _pd.DataFrame):
        lags['variable'] = _np.repeat(data.columns, lags.shape[0] / data.shape[1])
        kwds['c'] = 'variable'
    return hvPlot(lags)(y1, y2, kind='scatter', **kwds)
