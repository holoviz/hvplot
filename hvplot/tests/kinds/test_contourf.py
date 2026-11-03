import numpy as np
import pytest
import xarray as xr
from holoviews import Store
from holoviews.element import Polygons

# Polygons is not supported by the plotly backend.
backends = pytest.mark.parametrize('backend', ['bokeh', 'matplotlib'], indirect=True)


@pytest.fixture(scope='module')
def ds():
    v1 = xr.DataArray(
        np.arange(1.0, 13.0).reshape(3, 4), coords={'y': [0, 1, 2], 'x': [0, 1, 2, 3]}
    )
    return xr.Dataset({'v1': v1, 'v2': v1 * 2})


def test_x(ds, hvplot_xarray):
    plot = ds.hvplot.contourf(x='y', z='v1')
    assert isinstance(plot, Polygons)
    assert plot.kdims == ['y', 'x']


def test_y(ds, hvplot_xarray):
    plot = ds.hvplot.contourf(y='x', z='v1')
    assert plot.kdims == ['y', 'x']


def test_z(ds, gridded_lib):
    plot = gridded_lib(ds).hvplot.contourf(z='v2')
    assert isinstance(plot, Polygons)
    assert plot.kdims == ['x', 'y']
    assert plot.vdims == ['v2']


def test_levels(ds, hvplot_xarray):
    plot = ds.hvplot.contourf(z='v1', levels=[2, 5, 8])
    # Each filled polygon is valued with the middle of its two levels.
    np.testing.assert_array_equal(plot.dimension_values('v1', expanded=False), [3.5, 6.5])


@backends
def test_logz(ds, hvplot_xarray, backend):
    # The default levels start at 0, which a log scale cannot render.
    plot = ds.hvplot.contourf(z='v1', levels=[2, 5, 8], logz=True)
    assert Store.lookup_options(backend, plot, 'plot').kwargs['logz'] is True


def test_clim(ds, hvplot_xarray):
    # Contouring adapts the value range to the levels, clim sets it back.
    plot = ds.hvplot.contourf(z='v1', levels=[2, 5, 8], clim=(0, 20))
    assert plot.vdims[0].range == (0, 20)
