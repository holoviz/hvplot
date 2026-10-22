import numpy as np
import pytest
import xarray as xr
from holoviews import Store
from holoviews.element import TriMesh

from hvplot.tests._deps import requires

# trimesh plots are only supported for xugrid data.
pytestmark = requires('xugrid')

# HoloViews has no TriMesh plot for plotly.
bokeh_and_mpl = pytest.mark.parametrize('backend', ['bokeh', 'matplotlib'], indirect=True)


@pytest.fixture(autouse=True)
def hvplot_xugrid():
    import hvplot.xugrid  # noqa: F401


@pytest.fixture
def grid():
    """4-node, 2-face mesh; nodes at the corners of a 1x2 rectangle."""
    import xugrid as xu

    return xu.Ugrid2d(
        node_x=np.array([0.0, 1.0, 1.0, 0.0]),
        node_y=np.array([0.0, 0.0, 2.0, 2.0]),
        face_node_connectivity=np.array([[0, 1, 2], [0, 2, 3]]),
        fill_value=-1,
    )


@pytest.fixture
def uda(grid):
    """Data on the nodes."""
    import xugrid as xu

    da = xr.DataArray([1.0, 2.0, 3.0, 4.0], dims=[grid.node_dimension], name='a')
    return xu.UgridDataArray(da, grid)


def test_x_default(uda):
    plot = uda.hvplot.trimesh()
    assert isinstance(plot, TriMesh)
    assert plot.nodes.kdims[0] == 'x'
    assert list(plot.nodes.dimension_values('x')) == [0, 1, 1, 0]


@pytest.mark.xfail(strict=True, reason='BUG: trimesh ignores x and fails when it is set')
def test_x_node_coordinate(uda):
    plot = uda.hvplot.trimesh(x='mesh2d_node_x')
    assert list(plot.nodes.dimension_values(0)) == [0, 1, 1, 0]


def test_y_default(uda):
    plot = uda.hvplot.trimesh()
    assert plot.nodes.kdims[1] == 'y'
    assert list(plot.nodes.dimension_values('y')) == [0, 0, 2, 2]


@pytest.mark.xfail(strict=True, reason='BUG: trimesh ignores y and fails when it is set')
def test_y_node_coordinate(uda):
    plot = uda.hvplot.trimesh(y='mesh2d_node_y')
    assert list(plot.nodes.dimension_values(1)) == [0, 0, 2, 2]


def test_z(grid, uda):
    import xugrid as xu

    ds = xu.UgridDataset(grids=[grid])
    ds['a'] = uda
    ds['b'] = uda * 10
    plot = ds.hvplot.trimesh(z='b')
    assert plot.nodes.vdims[0].label == 'b'
    assert list(plot.nodes.dimension_values(plot.nodes.vdims[0])) == [10, 20, 30, 40]


@bokeh_and_mpl
def test_filled(uda, backend):
    plot = uda.hvplot.trimesh(filled=True)
    assert Store.lookup_options(backend, plot, 'plot').kwargs['filled'] is True
