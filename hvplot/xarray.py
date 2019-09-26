def patch(name='hvplot', extension='bokeh', logo=False):
    from . import plotting
    from . import post_patch

    try:
        import xarray as xr
    except:
        raise ImportError('Could not patch plotting API onto xarray. '
                            'xarray could not be imported.')
    _patch_plot = lambda self: plotting.hvPlotGridded(self)
    _patch_plot.__doc__ = plotting.hvPlotGridded.__call__.__doc__
    patch_property = property(_patch_plot)

    xr.register_dataset_accessor(name)(cls)
    xr.register_dataarray_accessor(name)(cls)

    post_patch(extension, logo)

patch()
