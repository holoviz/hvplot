import pandas as pd
import pytest
from holoviews.element import Path
from holoviews.testing import assert_element_equal

from hvplot.tests._deps import requires

pytestmark = pytest.mark.usefixtures('hvplot_pandas')


@pytest.fixture
def df():
    return pd.DataFrame({'x': [1, 3, 5], 'y': [2, 4, 6], 'z': [0, 1, 0]})


def test_x(df):
    plot = df.hvplot.paths(x='z', y='y')
    assert_element_equal(plot, Path(df, ['z', 'y'], []))


def test_x_default(df):
    plot = df.hvplot.paths()
    assert_element_equal(plot, Path(df, ['x', 'y'], []))


def test_x_index(df):
    plot = df.hvplot.paths(x='index', y='y', c='x')
    assert_element_equal(plot, Path(df.reset_index(), ['index', 'y'], ['x']))


def test_y(df, tabular_lib):
    plot = tabular_lib(df).hvplot.paths(x='x', y='y')
    assert isinstance(plot, Path)
    assert plot.kdims == ['x', 'y']
    assert list(plot.dimension_values('y')) == [2, 4, 6]


@pytest.mark.geo
@requires('geopandas', 'shapely')
def test_x_y_default_geodataframe():
    import geopandas as gpd
    import shapely

    gdf = gpd.GeoDataFrame(
        {'v': [1, 2]},
        geometry=[shapely.LineString([(0, 0), (1, 0)]), shapely.LineString([(1, 1), (2, 1)])],
    )
    plot = gdf.hvplot.paths()
    assert isinstance(plot, Path)
    assert plot.kdims == ['x', 'y']
    assert len(plot.split()) == 2
