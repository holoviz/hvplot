import sys
import time

import bokeh
from packaging.version import Version


def retry(func, *args, **kwargs):
    for i in range(5):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            wait = 10 * 2**i
            print(f'Attempt {i + 1} failed: {e}. Retrying in {wait}s...', file=sys.stderr)
            time.sleep(wait)
    return func(*args, **kwargs)


if Version(bokeh.__version__).release < (3, 5, 0):
    import bokeh.sampledata

    retry(bokeh.sampledata.download)
    print('bokeh data downloaded.')

try:
    import pooch  # noqa: F401
    import scipy  # noqa: F401
    import xarray as xr

    retry(xr.tutorial.open_dataset, 'air_temperature')
    retry(xr.tutorial.open_dataset, 'rasm', decode_times=False)
    print('xarray data downloaded.')
except ModuleNotFoundError as e:
    print(f'ModuleNotFoundError when attempting to download xarray datasets : {e}')
