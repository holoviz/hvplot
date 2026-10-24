import holoviews as hv
import numpy as np
import pandas as pd
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


@pytest.fixture
def face_uda(grid):
    """Data on the faces."""
    import xugrid as xu

    da = xr.DataArray([10.0, 20.0], dims=[grid.face_dimension])
    return xu.UgridDataArray(da, grid)


@pytest.fixture
def time_node_uda(grid):
    """Data on the nodes, with a time dimension."""
    import xugrid as xu

    da = xr.DataArray(
        np.arange(12, dtype=float).reshape(3, 4),
        dims=['time', grid.node_dimension],
        coords={'time': pd.date_range('2000-01-01', periods=3)},
    )
    return xu.UgridDataArray(da, grid)


@pytest.fixture
def time_face_uda(grid):
    """Data on the faces, with a time dimension."""
    import xugrid as xu

    da = xr.DataArray(
        np.arange(6, dtype=float).reshape(3, 2),
        dims=['time', grid.face_dimension],
        coords={'time': pd.date_range('2000-01-01', periods=3)},
    )
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


def test_z_dataset_default(grid):
    import xugrid as xu

    ds = xu.UgridDataset(grids=[grid])
    ds['other'] = xu.UgridDataArray(
        xr.DataArray([5.0, 6.0, 7.0, 8.0], dims=[grid.node_dimension]), grid
    )
    ds['temp'] = xu.UgridDataArray(
        xr.DataArray([1.0, 2.0, 3.0, 4.0], dims=[grid.node_dimension]), grid
    )
    plot = ds.hvplot.trimesh()
    assert isinstance(plot, TriMesh)
    assert plot.nodes.get_dimension('z').label == 'other'


def test_z_label_from_name(grid):
    """The data variable name should propagate to the TriMesh vdim label."""
    import xugrid as xu

    da = xr.DataArray([1.0, 2.0, 3.0, 4.0], dims=[grid.node_dimension], name='temperature')
    plot = xu.UgridDataArray(da, grid).hvplot.trimesh()
    assert plot.nodes.get_dimension('z').label == 'temperature'


def test_z_unnamed_falls_back_to_z(grid):
    import xugrid as xu

    da = xr.DataArray([1.0, 2.0, 3.0, 4.0], dims=[grid.node_dimension])
    plot = xu.UgridDataArray(da, grid).hvplot.trimesh()
    assert 'z' in [d.name for d in plot.nodes.vdims]


def test_node_data_returns_trimesh_element(uda):
    assert isinstance(uda.hvplot.trimesh(), TriMesh)


def test_node_data_trimesh_shortcut_same_as_kind(uda):
    plot_a = uda.hvplot.trimesh()
    plot_b = uda.hvplot(kind='trimesh')
    assert type(plot_a) is type(plot_b)


def test_node_data_node_count(uda):
    assert len(uda.hvplot.trimesh().nodes) == 4


def test_node_data_face_count(uda):
    assert len(uda.hvplot.trimesh()) == 2


def test_face_data_returns_trimesh_element(face_uda):
    assert isinstance(face_uda.hvplot.trimesh(), TriMesh)


def test_face_data_node_count_after_face_to_node(face_uda):
    """Face data is interpolated to nodes; all 4 nodes must be present."""
    assert len(face_uda.hvplot.trimesh().nodes) == 4


def test_face_data_face_count(face_uda):
    assert len(face_uda.hvplot.trimesh()) == 2


def test_quad_faces_triangulated():
    """A mesh with quad faces should be fan-triangulated into triangles."""
    import xugrid as xu

    grid = xu.Ugrid2d(
        node_x=np.array([0.0, 1.0, 2.0, 0.0, 1.0, 2.0]),
        node_y=np.array([0.0, 0.0, 0.0, 1.0, 1.0, 1.0]),
        face_node_connectivity=np.array([[0, 1, 4, 3], [1, 2, 5, 4]]),
        fill_value=-1,
    )
    da = xr.DataArray(np.arange(6, dtype=float), dims=[grid.node_dimension])
    plot = xu.UgridDataArray(da, grid).hvplot.trimesh()
    assert isinstance(plot, TriMesh)
    # 2 quads -> 4 triangles after fan triangulation
    assert len(plot) == 4


def test_extra_dim_2d_coord_dynamic_map(grid, rng):
    """A 2D coordinate (like FVCOM's siglay) should be filtered out
    and replaced with integer indices for the groupby slider.
    """
    import xugrid as xu

    node_dim = grid.node_dimension
    da = xr.DataArray(
        np.arange(12, dtype=float).reshape(3, 4),
        dims=['siglay', node_dim],
        coords={'siglay': (['siglay', node_dim], rng.random((3, 4)))},
    )
    plot = xu.UgridDataArray(da, grid).hvplot.trimesh()
    assert isinstance(plot, hv.DynamicMap)


def test_extra_dim_without_coord_dynamic_map(grid):
    """A dimension with no coordinate at all should get integer indices
    and still produce a working groupby slider.
    """
    import xugrid as xu

    da = xr.DataArray(
        np.arange(12, dtype=float).reshape(3, 4), dims=['layer', grid.node_dimension]
    )
    plot = xu.UgridDataArray(da, grid).hvplot.trimesh()
    assert isinstance(plot, hv.DynamicMap)


def test_extra_dim_time_dynamic_map(time_node_uda):
    assert isinstance(time_node_uda.hvplot.trimesh(), hv.DynamicMap)


def test_extra_dim_time_face_data_dynamic_map(time_face_uda):
    assert isinstance(time_face_uda.hvplot.trimesh(), hv.DynamicMap)


def test_colorbar_default(uda):
    plot = uda.hvplot.trimesh()
    assert Store.lookup_options('bokeh', plot, 'plot').kwargs['colorbar'] is True


def test_colorbar_disabled(uda):
    plot = uda.hvplot.trimesh(colorbar=False)
    assert Store.lookup_options('bokeh', plot, 'plot').kwargs['colorbar'] is False


def test_kind_not_trimesh_error(uda):
    with pytest.raises(NotImplementedError):
        uda.hvplot.line()


def test_kind_not_trimesh_error_message(uda):
    with pytest.raises(NotImplementedError, match='trimesh'):
        uda.hvplot.scatter()


@pytest.mark.geo
def test_geo(uda):
    import cartopy.crs as ccrs
    import geoviews as gv

    plot = uda.hvplot.trimesh(geo=True)
    assert isinstance(plot, gv.TriMesh)
    assert plot.crs == ccrs.PlateCarree()


@pytest.mark.geo
def test_crs(uda):
    import cartopy.crs as ccrs
    import geoviews as gv

    plot = uda.hvplot.trimesh(geo=True, crs=ccrs.Mercator())
    assert isinstance(plot, gv.TriMesh)
    assert plot.crs == ccrs.Mercator()
