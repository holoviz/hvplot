"""Tests for hvplot.xugrid trimesh support."""

from unittest import TestCase, SkipTest

import numpy as np
import pytest

try:
    import xarray as xr
    import xugrid as xu
    import holoviews as hv
    import hvplot.xugrid  # noqa: F401 - patches .hvplot onto xu types
except ImportError as e:
    raise SkipTest(f'xugrid or required dependency not available: {e}')

from holoviews.element import TriMesh


def _make_simple_node_uda():
    """
    Tiny 4-node, 2-triangle mesh with data on nodes.

    Nodes layout (x, y):
      2 (0,1)
      |\\
      | \\
      0  1   (0,0) (1,0)
      |\\
      | \\
      (not a 4th real node - just using 3 nodes for 2 triangles)

    Actually use 4 nodes, 2 faces:
      3 (0,1) --- 2 (1,1)
      |         /
      |       /
      0 (0,0) - 1 (1,0)

    faces: [0,1,2] and [0,2,3]
    """
    node_x = np.array([0.0, 1.0, 1.0, 0.0])
    node_y = np.array([0.0, 0.0, 1.0, 1.0])
    faces = np.array([[0, 1, 2], [0, 2, 3]])

    grid = xu.Ugrid2d(
        node_x=node_x,
        node_y=node_y,
        face_node_connectivity=faces,
        fill_value=-1,
    )
    # Node-centered data
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
    import pandas as pd

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
    import pandas as pd

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
        # trimesh() returns a HoloViews element (possibly wrapped)
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

    def test_explicit_time_selection_node(self):
        """Passing time= as a scalar should collapse the time dimension."""
        import pandas as pd

        t0 = pd.Timestamp('2000-01-01')
        plot = self.uda_node.hvplot.trimesh(time=t0)
        tm = plot.last if hasattr(plot, 'last') else plot
        assert isinstance(tm, TriMesh)

    def test_explicit_time_selection_face(self):
        import pandas as pd

        t0 = pd.Timestamp('2000-01-01')
        plot = self.uda_face.hvplot.trimesh(time=t0)
        tm = plot.last if hasattr(plot, 'last') else plot
        assert isinstance(tm, TriMesh)


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
        # UgridDataset can be built from a UgridDataArray via .to_dataset()
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
