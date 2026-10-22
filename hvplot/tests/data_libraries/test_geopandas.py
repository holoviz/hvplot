import holoviews as hv
import numpy as np
import pytest

from hvplot.tests._deps import requires

# geopandas and shapely are optional, they are imported in the fixtures.
pytestmark = [
    pytest.mark.geo,
    requires('geopandas', 'shapely'),
    pytest.mark.usefixtures('hvplot_pandas'),
]


@pytest.fixture
def cities():
    import geopandas as gpd

    geometry = gpd.points_from_xy(
        x=[12.45339, 12.44177, 9.51667, 6.13000, 158.14997],
        y=[41.90328, 43.93610, 47.13372, 49.61166, 6.91664],
        crs='EPSG:4326',
    )
    names = ['Vatican City', 'San Marino', 'Vaduz', 'Luxembourg', 'Palikir']
    return gpd.GeoDataFrame({'name': names}, geometry=geometry)


@pytest.fixture
def polygons():
    import geopandas as gpd
    from shapely.geometry import Polygon

    geometry = [
        Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0))),
        Polygon(((2, 2), (2, 3), (3, 3), (3, 2), (2, 2))),
    ]
    return gpd.GeoDataFrame({'name': ['A', 'B']}, geometry=geometry)


def test_points_hover_cols_is_empty_by_default(cities):
    points = cities.hvplot()
    assert points.kdims == ['x', 'y']
    assert points.vdims == []


def test_points_hover_cols_does_not_include_geometry_when_all(cities):
    points = cities.hvplot(x='x', y='y', hover_cols='all')
    assert points.kdims == ['x', 'y']
    assert points.vdims == ['index', 'name']


def test_points_hover_cols_when_all_and_use_columns_is_false(cities):
    points = cities.hvplot(x='x', hover_cols='all', use_index=False)
    assert points.kdims == ['x', 'y']
    assert points.vdims == ['name']


def test_points_hover_cols_index_in_list(cities):
    points = cities.hvplot(y='y', hover_cols=['index'])
    assert points.kdims == ['x', 'y']
    assert points.vdims == ['index']


def test_points_hover_cols_positional_arg_sets_color(cities):
    points = cities.hvplot('name')
    assert points.kdims == ['x', 'y']
    assert points.vdims == ['name']
    opts = hv.Store.lookup_options('bokeh', points, 'style').kwargs
    assert opts['color'] == 'name'


def test_points_hover_cols_with_c_set_to_name(cities):
    points = cities.hvplot(c='name')
    assert points.kdims == ['x', 'y']
    assert points.vdims == ['name']
    opts = hv.Store.lookup_options('bokeh', points, 'style').kwargs
    assert opts['color'] == 'name'


def test_points_hover_cols_with_by_set_to_name(cities):
    points = cities.hvplot(by='name')
    assert isinstance(points, hv.NdOverlay)
    assert points.kdims == ['name']
    assert points.vdims == []
    for element in points.values():
        assert element.kdims == ['x', 'y']
        assert element.vdims == []


def test_points_project_xlim_and_ylim(cities):
    points = cities.hvplot(geo=False, xlim=(-10, 10), ylim=(-20, -10))
    opts = hv.Store.lookup_options('bokeh', points, 'plot').options
    np.testing.assert_equal(opts['xlim'], (-10, 10))
    np.testing.assert_equal(opts['ylim'], (-20, -10))


def test_points_project_xlim_and_ylim_with_geo(cities):
    points = cities.hvplot(geo=True, xlim=(-10, 10), ylim=(-20, -10))
    opts = hv.Store.lookup_options('bokeh', points, 'plot').options
    np.testing.assert_allclose(opts['xlim'], (-10, 10))
    np.testing.assert_allclose(opts['ylim'], (-20, -10))


def test_polygons_by_subplots(polygons):
    plot = polygons.hvplot(geo=True, by='name', subplots=True)
    assert isinstance(plot, hv.NdLayout)


def test_polygons_turns_off_hover_when_there_are_no_fields_to_include(polygons):
    plot = polygons.hvplot(geo=True)
    opts = hv.Store.lookup_options('bokeh', plot, 'plot').kwargs
    assert 'hover' not in opts.get('tools')


@pytest.mark.xfail(
    strict=True,
    raises=TypeError,
    reason='BUG: the geometry type of a missing geometry is NaN, not None, and is not discarded',
)
def test_geometry_none(polygons):
    polygons.loc[1, 'geometry'] = None
    assert polygons.hvplot(geo=True)


def test_tiles_without_geo(polygons):
    plot = polygons.hvplot(tiles=True)
    assert plot.get(1).data.crs is None

    polygons.crs = 'EPSG:4326'
    plot = polygons.hvplot(tiles=True)
    assert plot.get(1).data.crs == 'EPSG:3857'
