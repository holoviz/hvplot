import sys
import time

import bokeh
from packaging.version import Version


def download(label, func, *args, **kwargs):
    for i in range(5):
        try:
            func(*args, **kwargs)
            print(f'{label} data downloaded.')
            return
        except Exception as e:
            wait = 10 * 2**i
            print(f'Attempt {i + 1} failed: {e}. Retrying in {wait}s...', file=sys.stderr)
            time.sleep(wait)
    print(f'Failed to download {label} dataset after 5 attempts.')


if Version(bokeh.__version__).release < (3, 5, 0):
    import bokeh.sampledata

    download('bokeh', bokeh.sampledata.download)

try:
    import pooch  # noqa: F401
    import scipy  # noqa: F401
    import xarray as xr

    download('xarray air_temperature', xr.tutorial.open_dataset, 'air_temperature')
    download('xarray rasm', xr.tutorial.open_dataset, 'rasm', decode_times=False)
except ModuleNotFoundError as e:
    print(f'ModuleNotFoundError when attempting to download xarray datasets : {e}')

try:
    from hvplot.sampledata import download as _hvs_download

    download('nyc_taxi', _hvs_download, 'nyc_taxi_remote')
except ImportError:
    print('hvsampledata is not available in this environment, skipping nyc_taxi download.')

try:
    from cartopy.io import shapereader

    # Natural Earth features rendered by the geo unit tests, which can't access the network.
    for category, name, scale in [
        ('physical', 'coastline', '110m'),
        ('physical', 'coastline', '10m'),
        ('physical', 'land', '110m'),
        ('physical', 'land', '50m'),
        ('cultural', 'admin_0_boundary_lines_land', '110m'),
    ]:
        download(
            f'Natural Earth {name} {scale}',
            shapereader.natural_earth,
            resolution=scale,
            category=category,
            name=name,
        )
except ModuleNotFoundError as e:
    print(f'ModuleNotFoundError when attempting to download Natural Earth data : {e}')
