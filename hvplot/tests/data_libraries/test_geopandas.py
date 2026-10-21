from unittest import TestCase

import holoviews as hv
import numpy as np
import pytest

from hvplot.tests._deps import requires


@pytest.mark.geo
@requires('geopandas', 'shapely')
class TestGeoPandas(TestCase):
    def setUp(self):
        import geopandas as gpd
        from shapely.geometry import Polygon

        import hvplot.pandas  # noqa: F401

        p_geometry = gpd.points_from_xy(
            x=[12.45339, 12.44177, 9.51667, 6.13000, 158.14997],
            y=[41.90328, 43.93610, 47.13372, 49.61166, 6.91664],
            crs='EPSG:4326',
        )
        p_names = ['Vatican City', 'San Marino', 'Vaduz', 'Luxembourg', 'Palikir']
        self.cities = gpd.GeoDataFrame({'name': p_names}, geometry=p_geometry)

        pg_geometry = [
            Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0))),
            Polygon(((2, 2), (2, 3), (3, 3), (3, 2), (2, 2))),
        ]
        pg_names = ['A', 'B']
        self.polygons = gpd.GeoDataFrame({'name': pg_names}, geometry=pg_geometry)

    def test_points_hover_cols_is_empty_by_default(self):
        points = self.cities.hvplot()
        assert points.kdims == ['x', 'y']
        assert points.vdims == []

    def test_points_hover_cols_does_not_include_geometry_when_all(self):
        points = self.cities.hvplot(x='x', y='y', hover_cols='all')
        assert points.kdims == ['x', 'y']
        assert points.vdims == ['index', 'name']

    def test_points_hover_cols_when_all_and_use_columns_is_false(self):
        points = self.cities.hvplot(x='x', hover_cols='all', use_index=False)
        assert points.kdims == ['x', 'y']
        assert points.vdims == ['name']

    def test_points_hover_cols_index_in_list(self):
        points = self.cities.hvplot(y='y', hover_cols=['index'])
        assert points.kdims == ['x', 'y']
        assert points.vdims == ['index']

    def test_points_hover_cols_positional_arg_sets_color(self):
        points = self.cities.hvplot('name')
        assert points.kdims == ['x', 'y']
        assert points.vdims == ['name']
        opts = hv.Store.lookup_options('bokeh', points, 'style').kwargs
        assert opts['color'] == 'name'

    def test_points_hover_cols_with_c_set_to_name(self):
        points = self.cities.hvplot(c='name')
        assert points.kdims == ['x', 'y']
        assert points.vdims == ['name']
        opts = hv.Store.lookup_options('bokeh', points, 'style').kwargs
        assert opts['color'] == 'name'

    def test_points_hover_cols_with_by_set_to_name(self):
        points = self.cities.hvplot(by='name')
        assert isinstance(points, hv.core.overlay.NdOverlay)
        assert points.kdims == ['name']
        assert points.vdims == []
        for element in points.values():
            assert element.kdims == ['x', 'y']
            assert element.vdims == []

    def test_points_project_xlim_and_ylim(self):
        points = self.cities.hvplot(geo=False, xlim=(-10, 10), ylim=(-20, -10))
        opts = hv.Store.lookup_options('bokeh', points, 'plot').options
        np.testing.assert_equal(opts['xlim'], (-10, 10))
        np.testing.assert_equal(opts['ylim'], (-20, -10))

    def test_points_project_xlim_and_ylim_with_geo(self):
        points = self.cities.hvplot(geo=True, xlim=(-10, 10), ylim=(-20, -10))
        opts = hv.Store.lookup_options('bokeh', points, 'plot').options
        np.testing.assert_allclose(opts['xlim'], (-10, 10))
        np.testing.assert_allclose(opts['ylim'], (-20, -10))

    def test_polygons_by_subplots(self):
        polygons = self.polygons.hvplot(geo=True, by='name', subplots=True)
        assert isinstance(polygons, hv.core.layout.NdLayout)

    def test_polygons_turns_off_hover_when_there_are_no_fields_to_include(self):
        polygons = self.polygons.hvplot(geo=True)
        opts = hv.Store.lookup_options('bokeh', polygons, 'plot').kwargs
        assert 'hover' not in opts.get('tools')

    def test_geometry_none(self):
        polygons = self.polygons.copy()
        polygons[1, 'geometry'] = None
        assert polygons.hvplot(geo=True)

    @pytest.mark.xfail(reason='Last assertion broken')
    def test_tiles_without_gv(self):
        polygons = self.polygons.copy()
        polygons_plot = polygons.hvplot(tiles=True)
        assert polygons_plot.get(1).data.crs is None

        polygons.crs = 'EPSG:4326'
        polygons_plot = self.polygons.hvplot(tiles=True)
        assert polygons_plot.get(1).data.crs == 'EPSG:3857'
