"""Tests for hvplot.xugrid trimesh support."""

from unittest import TestCase, SkipTest

import numpy as np
import pandas as pd

try:
    import xarray as xr
    import xugrid as xu
    import holoviews as hv
    import hvplot.xugrid  # noqa: F401 - patches .hvplot onto xu types
except ImportError as e:
    raise SkipTest(f'xugrid or required dependency not available: {e}')

from holoviews.element import TriMesh


def _make_simple_node_uda():
    """4-node, 2-face mesh; nodes at corners of a unit square, data on nodes."""
    node_x = np.array([0.0, 1.0, 1.0, 0.0])
    node_y = np.array([0.0, 0.0, 1.0, 1.0])
    faces = np.array([[0, 1, 2], [0, 2, 3]])

    grid = xu.Ugrid2d(
        node_x=node_x,
        node_y=node_y,
        face_node_connectivity=faces,
        fill_value=-1,
    )
    node_dim = grid.node_dimension
    da = xr.DataArray([1.0, 2.0, 3.0, 4.0], dims=[node_dim])
    return xu.UgridDataArray(da, grid)


def _make_simple_face_uda():
    """Same mesh but data on faces (2 values)."""
    node_x = np.array([0.0, 1.0, 1.0, 0.0])
    node_y = np.array([0.0, 0.0, 1.0, 1.0])
    faces = np.array([[0, 1, 2], [0, 2, 3]])

    grid = xu.Ugrid2d(
        node_x=node_x,
        node_y=node_y,
        face_node_connectivity=faces,
        fill_value=-1,
    )
    face_dim = grid.face_dimension
    da = xr.DataArray([10.0, 20.0], dims=[face_dim])
    return xu.UgridDataArray(da, grid)


def _make_time_node_uda():
    """4-node, 2-face mesh with a time dimension (node data)."""
    node_x = np.array([0.0, 1.0, 1.0, 0.0])
    node_y = np.array([0.0, 0.0, 1.0, 1.0])
    faces = np.array([[0, 1, 2], [0, 2, 3]])

    grid = xu.Ugrid2d(
        node_x=node_x,
        node_y=node_y,
        face_node_connectivity=faces,
        fill_value=-1,
    )
    times = pd.date_range('2000-01-01', periods=3)
    node_dim = grid.node_dimension
    da = xr.DataArray(
        np.arange(12, dtype=float).reshape(3, 4),
        dims=['time', node_dim],
        coords={'time': times},
    )
    return xu.UgridDataArray(da, grid)


def _make_time_face_uda():
    """4-node, 2-face mesh with a time dimension (face data)."""
    node_x = np.array([0.0, 1.0, 1.0, 0.0])
    node_y = np.array([0.0, 0.0, 1.0, 1.0])
    faces = np.array([[0, 1, 2], [0, 2, 3]])

    grid = xu.Ugrid2d(
        node_x=node_x,
        node_y=node_y,
        face_node_connectivity=faces,
        fill_value=-1,
    )
    times = pd.date_range('2000-01-01', periods=3)
    face_dim = grid.face_dimension
    da = xr.DataArray(
        np.arange(6, dtype=float).reshape(3, 2),
        dims=['time', face_dim],
        coords={'time': times},
    )
    return xu.UgridDataArray(da, grid)


class TestTrimeshNodeData(TestCase):
    """Tests for trimesh plots when data lives on mesh nodes."""

    def setUp(self):
        self.uda = _make_simple_node_uda()

    def test_returns_trimesh_element(self):
        plot = self.uda.hvplot.trimesh()
        assert isinstance(plot.last if hasattr(plot, 'last') else plot, TriMesh)

    def test_trimesh_shortcut_same_as_kind(self):
        plot_a = self.uda.hvplot.trimesh()
        plot_b = self.uda.hvplot(kind='trimesh')
        assert type(plot_a) is type(plot_b)

    def test_node_count(self):
        plot = self.uda.hvplot.trimesh()
        tm = plot.last if hasattr(plot, 'last') else plot
        assert len(tm.nodes) == 4

    def test_face_count(self):
        plot = self.uda.hvplot.trimesh()
        tm = plot.last if hasattr(plot, 'last') else plot
        assert len(tm) == 2

    def test_colorbar_default_true(self):
        plot = self.uda.hvplot.trimesh()
        opts = plot.opts.get()
        assert opts.kwargs.get('colorbar', True) is True

    def test_colorbar_can_be_disabled(self):
        plot = self.uda.hvplot.trimesh(colorbar=False)
        opts = plot.opts.get()
        assert opts.kwargs.get('colorbar', True) is False


class TestTrimeshFaceData(TestCase):
    """Tests for trimesh plots when data lives on mesh faces."""

    def setUp(self):
        self.uda = _make_simple_face_uda()

    def test_returns_trimesh_element(self):
        plot = self.uda.hvplot.trimesh()
        tm = plot.last if hasattr(plot, 'last') else plot
        assert isinstance(tm, TriMesh)

    def test_node_count_after_face_to_node(self):
        """Face data is interpolated to nodes; all 4 nodes must be present."""
        plot = self.uda.hvplot.trimesh()
        tm = plot.last if hasattr(plot, 'last') else plot
        assert len(tm.nodes) == 4

    def test_face_count(self):
        plot = self.uda.hvplot.trimesh()
        tm = plot.last if hasattr(plot, 'last') else plot
        assert len(tm) == 2


class TestTrimeshExtraDimCoords(TestCase):
    """Tests for extra dimensions with 2D or missing coordinates."""

    def _make_grid(self):
        node_x = np.array([0.0, 1.0, 1.0, 0.0])
        node_y = np.array([0.0, 0.0, 1.0, 1.0])
        faces = np.array([[0, 1, 2], [0, 2, 3]])
        return xu.Ugrid2d(
            node_x=node_x,
            node_y=node_y,
            face_node_connectivity=faces,
            fill_value=-1,
        )

    def test_2d_coord_produces_dynamic_map(self):
        """A 2D coordinate (like FVCOM's siglay) should be filtered out
        and replaced with integer indices for the groupby slider."""
        grid = self._make_grid()
        node_dim = grid.node_dimension
        da = xr.DataArray(
            np.arange(12, dtype=float).reshape(3, 4),
            dims=['siglay', node_dim],
            coords={'siglay': (['siglay', node_dim], np.random.rand(3, 4))},
        )
        uda = xu.UgridDataArray(da, grid)
        plot = uda.hvplot.trimesh()
        assert isinstance(plot, hv.DynamicMap)

    def test_dim_without_coord_produces_dynamic_map(self):
        """A dimension with no coordinate at all should get integer indices
        and still produce a working groupby slider."""
        grid = self._make_grid()
        node_dim = grid.node_dimension
        da = xr.DataArray(
            np.arange(12, dtype=float).reshape(3, 4),
            dims=['layer', node_dim],
        )
        uda = xu.UgridDataArray(da, grid)
        plot = uda.hvplot.trimesh()
        assert isinstance(plot, hv.DynamicMap)


class TestTrimeshTimeDimension(TestCase):
    """Tests for trimesh plots with an extra time dimension (groupby slider)."""

    def setUp(self):
        self.uda_node = _make_time_node_uda()
        self.uda_face = _make_time_face_uda()

    def test_time_dim_creates_dynamic_map(self):
        plot = self.uda_node.hvplot.trimesh()
        assert isinstance(plot, hv.DynamicMap)

    def test_dynamic_map_face_data(self):
        plot = self.uda_face.hvplot.trimesh()
        assert isinstance(plot, hv.DynamicMap)


class TestTrimeshUgridDataset(TestCase):
    """Tests for trimesh when the input is a UgridDataset."""

    def _make_dataset(self):
        node_x = np.array([0.0, 1.0, 1.0, 0.0])
        node_y = np.array([0.0, 0.0, 1.0, 1.0])
        faces = np.array([[0, 1, 2], [0, 2, 3]])
        grid = xu.Ugrid2d(
            node_x=node_x,
            node_y=node_y,
            face_node_connectivity=faces,
            fill_value=-1,
        )
        node_dim = grid.node_dimension
        da = xr.DataArray([1.0, 2.0, 3.0, 4.0], dims=[node_dim], name='temp')
        uda = xu.UgridDataArray(da, grid)
        return uda.to_dataset()

    def test_dataset_returns_trimesh(self):
        ds = self._make_dataset()
        plot = ds.hvplot.trimesh()
        tm = plot.last if hasattr(plot, 'last') else plot
        assert isinstance(tm, TriMesh)

    def test_dataset_explicit_z(self):
        ds = self._make_dataset()
        plot = ds.hvplot.trimesh(z='temp')
        tm = plot.last if hasattr(plot, 'last') else plot
        assert isinstance(tm, TriMesh)


class TestTrimeshQuadMesh(TestCase):
    """Tests for trimesh with non-triangular (quad) faces."""

    def test_quad_mesh_triangulated(self):
        """A mesh with quad faces should be fan-triangulated into triangles."""
        node_x = np.array([0.0, 1.0, 2.0, 0.0, 1.0, 2.0])
        node_y = np.array([0.0, 0.0, 0.0, 1.0, 1.0, 1.0])
        faces = np.array([[0, 1, 4, 3], [1, 2, 5, 4]])
        grid = xu.Ugrid2d(
            node_x=node_x, node_y=node_y, face_node_connectivity=faces, fill_value=-1
        )
        da = xr.DataArray(np.arange(6, dtype=float), dims=[grid.node_dimension])
        uda = xu.UgridDataArray(da, grid)
        plot = uda.hvplot.trimesh()
        tm = plot.last if hasattr(plot, 'last') else plot
        assert isinstance(tm, TriMesh)
        # 2 quads -> 4 triangles after fan triangulation
        assert len(tm) == 4


class TestTrimeshVariableName(TestCase):
    """Tests for variable name propagation."""

    def test_named_variable_in_vdim_label(self):
        """The data variable name should propagate to the TriMesh vdim label."""
        node_x = np.array([0.0, 1.0, 1.0, 0.0])
        node_y = np.array([0.0, 0.0, 1.0, 1.0])
        faces = np.array([[0, 1, 2], [0, 2, 3]])
        grid = xu.Ugrid2d(
            node_x=node_x, node_y=node_y, face_node_connectivity=faces, fill_value=-1
        )
        da = xr.DataArray([1.0, 2.0, 3.0, 4.0], dims=[grid.node_dimension], name='temperature')
        uda = xu.UgridDataArray(da, grid)
        plot = uda.hvplot.trimesh()
        tm = plot.last if hasattr(plot, 'last') else plot
        z_dim = tm.nodes.get_dimension('z')
        assert z_dim.label == 'temperature'

    def test_unnamed_variable_falls_back_to_z(self):
        """Without a name, the vdim should fall back to 'z'."""
        uda = _make_simple_node_uda()
        plot = uda.hvplot.trimesh()
        tm = plot.last if hasattr(plot, 'last') else plot
        vdim_names = [d.name for d in tm.nodes.vdims]
        assert 'z' in vdim_names


class TestTrimeshNonTrimeshKind(TestCase):
    """Tests for non-trimesh plot kinds on xugrid data."""

    def test_non_trimesh_kind_raises(self):
        uda = _make_simple_node_uda()
        with self.assertRaises(NotImplementedError):
            uda.hvplot.line()

    def test_error_message_is_helpful(self):
        uda = _make_simple_node_uda()
        with self.assertRaises(NotImplementedError) as ctx:
            uda.hvplot.scatter()
        assert 'trimesh' in str(ctx.exception)


class TestTrimeshGeo(TestCase):
    """Tests for trimesh with geo=True and CRS options."""

    def setUp(self):
        self.uda = _make_simple_node_uda()

    def test_geo_default_crs(self):
        try:
            import geoviews  # noqa: F401
        except ImportError:
            raise SkipTest('geoviews not available')

        plot = self.uda.hvplot.trimesh(geo=True)
        tm = plot.last if hasattr(plot, 'last') else plot
        assert isinstance(tm, TriMesh)

    def test_geo_non_platecarree_crs(self):
        try:
            import geoviews  # noqa: F401
            import cartopy.crs as ccrs
        except ImportError:
            raise SkipTest('geoviews or cartopy not available')

        plot = self.uda.hvplot.trimesh(geo=True, crs=ccrs.Mercator())
        tm = plot.last if hasattr(plot, 'last') else plot
        assert isinstance(tm, TriMesh)
