from __future__ import absolute_import

def patch(name='hvplot', extension='bokeh', logo=False):
    from . import hvPlot, post_patch

    try:
        import xarray as xr
    except:
        raise ImportError('Could not patch plotting API onto xarray. '
                          'xarray could not be imported.')

    xr.register_dataset_accessor(name)(hvPlot)
    xr.register_dataarray_accessor(name)(hvPlot)

    post_patch(extension, logo)

patch()
