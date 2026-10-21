import string
from datetime import datetime

import numpy as np
import pandas as pd
import xarray as xr

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


def air_temperature():
    """Small synthetic version of `xr.tutorial.open_dataset('air_temperature')`.

    Same variable, coords, dtypes and main attrs, without the download.
    """
    lat = np.linspace(75, 15, 10, dtype='float32')  # descending, like the original
    lon = np.linspace(200, 330, 12, dtype='float32')
    # ns like the original, recent pandas versions default to us.
    time = pd.date_range('2013-01-01', periods=6, freq='6h').astype('datetime64[ns]')
    air = np.random.default_rng(1).uniform(240, 300, size=(len(time), len(lat), len(lon)))
    return xr.Dataset(
        {
            'air': (
                ('time', 'lat', 'lon'),
                air,
                {'long_name': '4xDaily Air temperature at sigma level 995', 'units': 'degK'},
            )
        },
        coords={
            'time': ('time', time, {'standard_name': 'time', 'long_name': 'Time'}),
            'lat': (
                'lat',
                lat,
                {
                    'standard_name': 'latitude',
                    'long_name': 'Latitude',
                    'units': 'degrees_north',
                    'axis': 'Y',
                },
            ),
            'lon': (
                'lon',
                lon,
                {
                    'standard_name': 'longitude',
                    'long_name': 'Longitude',
                    'units': 'degrees_east',
                    'axis': 'X',
                },
            ),
        },
        attrs={'Conventions': 'COARDS', 'title': '4x daily NMC reanalysis (1948)'},
    )
