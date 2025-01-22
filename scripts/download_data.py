import bokeh
from packaging.version import Version

if Version(bokeh.__version__).release < (3, 5, 0):
    import bokeh.sampledata

    bokeh.sampledata.download()
    print('bokeh data downloaded.')

try:
    import pooch  # noqa: F401
    import scipy  # noqa: F401
    import xarray as xr

    xr.tutorial.open_dataset('air_temperature')
    xr.tutorial.open_dataset('rasm')
    print('xarray data downloaded.')
except ModuleNotFoundError as e:
    print(f'ModuleNotFoundError when attempting to download xarray datasets : {e}')
