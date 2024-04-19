import string

from datetime import datetime

import numpy as np
import pandas as pd


# Pandas removed its make<> test utilities in version 2.2.0.

_N = 30
_K = 4


def getCols(k):
    return string.ascii_uppercase[:k]


def rands_array(nchars, size, dtype='O', replace=True):
    """
    Generate an array of byte strings.
    """
    chars = np.array(list(string.ascii_letters + string.digits), dtype=(np.str_, 1))
    retval = (
        np.random.default_rng(2)
        .choice(chars, size=nchars * np.prod(size), replace=replace)
        .view((np.str_, nchars))
        .reshape(size)
    )
    return retval.astype(dtype)


def makeStringIndex(k=10, name=None):
    return pd.Index(rands_array(nchars=10, size=k), name=name)


def makeMixedDataFrame():
    data = {
        'A': [0.0, 1.0, 2.0, 3.0, 4.0],
        'B': [0.0, 1.0, 0.0, 1.0, 0.0],
        'C': ['foo1', 'foo2', 'foo3', 'foo4', 'foo5'],
        'D': pd.bdate_range('1/1/2009', periods=5),
    }
    return pd.DataFrame(data)


def getSeriesData():
    index = makeStringIndex(_N)
    return {
        c: pd.Series(np.random.default_rng(i).standard_normal(_N), index=index)
        for i, c in enumerate(getCols(_K))
    }


def makeDataFrame():
    data = getSeriesData()
    return pd.DataFrame(data)


def makeDateIndex(k=10, freq='B', name=None, **kwargs):
    dt = datetime(2000, 1, 1)
    dr = pd.bdate_range(dt, periods=k, freq=freq, name=name)
    return pd.DatetimeIndex(dr, name=name, **kwargs)


def makeTimeSeries(nper=None, freq='B', name=None):
    if nper is None:
        nper = _N
    return pd.Series(
        np.random.default_rng(2).standard_normal(nper),
        index=makeDateIndex(nper, freq=freq),
        name=name,
    )


def getTimeSeriesData(nper=None, freq='B'):
    return {c: makeTimeSeries(nper, freq) for c in getCols(_K)}


def makeTimeDataFrame(nper=None, freq='B'):
    data = getTimeSeriesData(nper, freq)
    return pd.DataFrame(data)
