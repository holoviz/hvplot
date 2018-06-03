import xarray as xr

from . import HoloPlot, _hv

if _hv.extension._loaded:
    _hv.extension('bokeh', logo=False)

@xr.register_dataset_accessor('holoplot')
@xr.register_dataarray_accessor('holoplot')
class XArrayHoloPlot(HoloPlot):
    """
    HoloPlot implementation for xarray
    """
