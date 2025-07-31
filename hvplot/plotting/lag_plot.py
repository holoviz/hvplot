import numpy as np
import pandas as pd

from ..util import with_hv_extension
from .core import hvPlotTabular


@with_hv_extension
def lag_plot(data, lag=1, **kwds):
    """Lag plot for time series.

    A lag plot is a scatter plot of a time series against a lag of itself. It helps
    in visualizing the temporal dependence between observations by plotting the values
    at time `t` on the x-axis and the values at time `t + lag` on the y-axis.

    Parameters
    ----------
    data : Series or DataFrame
        The time series to visualize.
    lag : int, optional
        Lag length of the scatter plot. Default is 1.
    **kwds : optional
        hvplot.scatter options

    Returns
    -------
    obj : HoloViews object
        The HoloViews representation of the plot.
    """
    if lag != int(lag) or int(lag) <= 0:
        raise ValueError('lag must be a positive integer')
    lag = int(lag)

    values = data.values
    y1 = 'y(t)'
    y2 = f'y(t + {lag})'
    lags = pd.DataFrame({y1: values[:-lag].T.ravel(), y2: values[lag:].T.ravel()})
    if isinstance(data, pd.DataFrame):
        lags['variable'] = np.repeat(data.columns, lags.shape[0] / data.shape[1])
        kwds['c'] = 'variable'
    return hvPlotTabular(lags)(y1, y2, kind='scatter', **kwds)
