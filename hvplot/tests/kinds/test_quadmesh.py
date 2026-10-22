import numpy as np
import xarray as xr


def test_unindexed_quadmesh(hvplot_xarray):
    xs = np.linspace(0, 10, 5)
    lon = xs * xs[np.newaxis, :].T
    lat = xs + xs[:, np.newaxis]
    coords = {
        'lon': (('ny', 'nx'), lon),
        'lat': (('ny', 'nx'), lat),
        'time': [1, 2, 3],
        'samples': ('nsamples', [0, 1, 2, 3]),
    }
    ds_unindexed = xr.DataArray(
        np.random.rand(5, 5, 3, 4), coords=coords, dims=('nx', 'ny', 'time', 'nsamples')
    )
    plot = ds_unindexed.hvplot.quadmesh(x='lon', y='lat')
    assert len(plot.kdims) == 2
    assert plot.kdims[0].name == 'time'
    assert plot.kdims[1].name == 'nsamples'
    p = plot[1, 0]
    assert len(p.kdims) == 2
    assert p.kdims[0].name == 'lon'
    assert p.kdims[1].name == 'lat'
