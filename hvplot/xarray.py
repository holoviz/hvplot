def patch(name='hvplot', extension='bokeh', logo=False):
    from . import plotting
    from . import post_patch

    try:
        import xarray as xr
    except:
        raise ImportError('Could not patch plotting API onto xarray. '
                            'xarray could not be imported.')

    xr.register_dataset_accessor(name)(plotting.hvPlotGridded)
    xr.register_dataarray_accessor(name)(plotting.hvPlotGridded)

    post_patch(extension, logo)

patch()
