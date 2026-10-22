import numpy as np
import pytest
import xarray as xr
from holoviews import Store
from holoviews.element import QuadMesh


@pytest.fixture
def ds():
    return xr.Dataset(
        {
            'a': (('lat', 'lon'), np.arange(6.0).reshape(2, 3)),
            'b': (('lat', 'lon'), np.arange(6.0).reshape(2, 3) * 10),
        },
        coords={'lat': [10, 20], 'lon': [0, 1, 2]},
    )


def test_x(ds, gridded_lib):
    plot = gridded_lib(ds).hvplot.quadmesh(x='lat')
    assert isinstance(plot, QuadMesh)
    assert plot.kdims == ['lat', 'lon']
    assert plot.vdims == ['a']
    assert list(plot.dimension_values('lon', expanded=False)) == [0, 1, 2]


def test_y(ds, hvplot_xarray):
    plot = ds.hvplot.quadmesh(y='lon')
    assert plot.kdims == ['lat', 'lon']
    assert list(plot.dimension_values('lon', expanded=False)) == [0, 1, 2]


def test_z(ds, hvplot_xarray):
    plot = ds.hvplot.quadmesh(x='lon', y='lat', z='b')
    assert plot.vdims == ['b']
    assert plot.dimension_values('b').max() == 50


def test_logz(ds, hvplot_xarray, backend):
    # A log scale cannot render the zeros of the data.
    plot = (ds + 1).hvplot.quadmesh(x='lon', y='lat', logz=True)
    assert Store.lookup_options(backend, plot, 'plot').kwargs['logz'] is True


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
