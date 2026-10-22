import numpy as np
import pytest
import xarray as xr
from holoviews import Store
from holoviews.element import Contours

# Contours is not supported by the plotly backend.
backends = pytest.mark.parametrize('backend', ['bokeh', 'matplotlib'], indirect=True)


@pytest.fixture(scope='module')
def ds():
    v1 = xr.DataArray(
        np.arange(1.0, 13.0).reshape(3, 4), coords={'y': [0, 1, 2], 'x': [0, 1, 2, 3]}
    )
    return xr.Dataset({'v1': v1, 'v2': v1 * 2})


def test_x(ds, hvplot_xarray):
    plot = ds.hvplot.contour(x='y', z='v1')
    assert isinstance(plot, Contours)
    assert plot.kdims == ['y', 'x']


def test_y(ds, hvplot_xarray):
    plot = ds.hvplot.contour(y='x', z='v1')
    assert plot.kdims == ['y', 'x']


def test_z(ds, gridded_lib):
    plot = gridded_lib(ds).hvplot.contour(z='v2')
    assert isinstance(plot, Contours)
    assert plot.kdims == ['x', 'y']
    assert plot.vdims == ['v2']


def test_levels(ds, hvplot_xarray):
    plot = ds.hvplot.contour(z='v1', levels=3)
    assert len(plot.dimension_values('v1', expanded=False)) == 3


def test_levels_list(ds, hvplot_xarray):
    plot = ds.hvplot.contour(z='v1', levels=[2, 5, 8])
    np.testing.assert_array_equal(plot.dimension_values('v1', expanded=False), [2, 5, 8])


@backends
def test_logz(ds, hvplot_xarray, backend):
    plot = ds.hvplot.contour(z='v1', logz=True)
    assert Store.lookup_options(backend, plot, 'plot').kwargs['logz'] is True
