from __future__ import absolute_import

import numpy as np
import pandas as pd

from ..util import with_hv_extension
from .core import hvPlotTabular


@with_hv_extension
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
    lags = pd.DataFrame({y1: values[:-lag].T.ravel(),
                         y2: values[lag:].T.ravel()})
    if isinstance(data, pd.DataFrame):
        lags['variable'] = np.repeat(data.columns, lags.shape[0] / data.shape[1])
        kwds['c'] = 'variable'
    return hvPlotTabular(lags)(y1, y2, kind='scatter', **kwds)
