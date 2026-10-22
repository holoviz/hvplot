"""Tests for hvplot.xugrid trimesh support."""

import holoviews as hv
import numpy as np
import pandas as pd
import pytest
import xarray as xr
from holoviews.element import TriMesh

import hvplot
from hvplot.tests._deps import requires

# xugrid is optional, it is imported in the fixtures and tests.
pytestmark = requires('xugrid')


@pytest.fixture(autouse=True)
def hvplot_xugrid():
    import hvplot.xugrid  # noqa: F401


@pytest.fixture
def grid():
    """4-node, 2-face mesh; nodes at the corners of a unit square."""
    import xugrid as xu

    return xu.Ugrid2d(
        node_x=np.array([0.0, 1.0, 1.0, 0.0]),
        node_y=np.array([0.0, 0.0, 1.0, 1.0]),
        face_node_connectivity=np.array([[0, 1, 2], [0, 2, 3]]),
        fill_value=-1,
    )


@pytest.fixture
def node_uda(grid):
    """Data on the nodes."""
    import xugrid as xu

    da = xr.DataArray([1.0, 2.0, 3.0, 4.0], dims=[grid.node_dimension])
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


def test_node_data_returns_trimesh_element(node_uda):
    assert isinstance(node_uda.hvplot.trimesh(), TriMesh)


def test_node_data_trimesh_shortcut_same_as_kind(node_uda):
    plot_a = node_uda.hvplot.trimesh()
    plot_b = node_uda.hvplot(kind='trimesh')
    assert type(plot_a) is type(plot_b)


def test_node_data_node_count(node_uda):
    assert len(node_uda.hvplot.trimesh().nodes) == 4


def test_node_data_face_count(node_uda):
    assert len(node_uda.hvplot.trimesh()) == 2


def test_node_data_colorbar_default_true(node_uda):
    plot = node_uda.hvplot.trimesh()
    assert hv.Store.lookup_options('bokeh', plot, 'plot').kwargs['colorbar'] is True


def test_node_data_colorbar_can_be_disabled(node_uda):
    plot = node_uda.hvplot.trimesh(colorbar=False)
    assert hv.Store.lookup_options('bokeh', plot, 'plot').kwargs['colorbar'] is False


def test_node_data_filled_default_false(node_uda):
    plot = node_uda.hvplot.trimesh()
    assert hv.Store.lookup_options('bokeh', plot, 'plot').kwargs.get('filled') is False


def test_node_data_filled_true(node_uda):
    plot = node_uda.hvplot.trimesh(filled=True)
    assert hv.Store.lookup_options('bokeh', plot, 'plot').kwargs.get('filled') is True


def test_face_data_returns_trimesh_element(face_uda):
    assert isinstance(face_uda.hvplot.trimesh(), TriMesh)


def test_face_data_node_count_after_face_to_node(face_uda):
    """Face data is interpolated to nodes; all 4 nodes must be present."""
    assert len(face_uda.hvplot.trimesh().nodes) == 4


def test_face_data_face_count(face_uda):
    assert len(face_uda.hvplot.trimesh()) == 2


def test_2d_coord_produces_dynamic_map(grid, rng):
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


def test_dim_without_coord_produces_dynamic_map(grid):
    """A dimension with no coordinate at all should get integer indices
    and still produce a working groupby slider.
    """
    import xugrid as xu

    da = xr.DataArray(
        np.arange(12, dtype=float).reshape(3, 4), dims=['layer', grid.node_dimension]
    )
    plot = xu.UgridDataArray(da, grid).hvplot.trimesh()
    assert isinstance(plot, hv.DynamicMap)


def test_time_dim_creates_dynamic_map(time_node_uda):
    assert isinstance(time_node_uda.hvplot.trimesh(), hv.DynamicMap)


def test_time_dim_face_data_creates_dynamic_map(time_face_uda):
    assert isinstance(time_face_uda.hvplot.trimesh(), hv.DynamicMap)


@pytest.mark.parametrize('kwargs', [{}, {'z': 'temp'}], ids=['default_z', 'explicit_z'])
def test_ugrid_dataset_returns_trimesh(grid, kwargs):
    import xugrid as xu

    da = xr.DataArray([1.0, 2.0, 3.0, 4.0], dims=[grid.node_dimension], name='temp')
    ds = xu.UgridDataArray(da, grid).to_dataset()
    assert isinstance(ds.hvplot.trimesh(**kwargs), TriMesh)


def test_quad_mesh_triangulated():
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


def test_named_variable_in_vdim_label(grid):
    """The data variable name should propagate to the TriMesh vdim label."""
    import xugrid as xu

    da = xr.DataArray([1.0, 2.0, 3.0, 4.0], dims=[grid.node_dimension], name='temperature')
    plot = xu.UgridDataArray(da, grid).hvplot.trimesh()
    assert plot.nodes.get_dimension('z').label == 'temperature'


def test_unnamed_variable_falls_back_to_z(node_uda):
    """Without a name, the vdim should fall back to 'z'."""
    plot = node_uda.hvplot.trimesh()
    assert 'z' in [d.name for d in plot.nodes.vdims]


def test_non_trimesh_kind_raises(node_uda):
    with pytest.raises(NotImplementedError):
        node_uda.hvplot.line()


def test_non_trimesh_kind_error_message_is_helpful(node_uda):
    with pytest.raises(NotImplementedError, match='trimesh'):
        node_uda.hvplot.scatter()


@pytest.mark.geo
def test_geo_default_crs(node_uda):
    assert isinstance(node_uda.hvplot.trimesh(geo=True), TriMesh)


@pytest.mark.geo
def test_geo_non_platecarree_crs(node_uda):
    import cartopy.crs as ccrs

    assert isinstance(node_uda.hvplot.trimesh(geo=True, crs=ccrs.Mercator()), TriMesh)


def test_unpatch_xugrid():
    import xugrid as xu

    classes = [xu.UgridDataArray, xu.UgridDataset]

    hvplot.xugrid._unpatch()
    assert not any('hvplot' in vars(cls) for cls in classes)
    assert 'hvplot.xugrid' not in hvplot._module_extensions

    # Ends patched, the _isolate_hvplot fixture unpatches it after the test.
    hvplot.xugrid.patch()
    assert all('hvplot' in vars(cls) for cls in classes)
    assert 'hvplot.xugrid' in hvplot._module_extensions
