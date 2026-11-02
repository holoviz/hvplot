import numpy as np
import pandas as pd
import pytest
import xarray as xr
from holoviews.element import Path
from holoviews.testing import assert_element_equal

from hvplot.tests._deps import pandas_and_dask, requires

pytestmark = pytest.mark.usefixtures('hvplot_pandas')


@pytest.fixture
def df():
    return pd.DataFrame({'x': [1, 3, 5], 'y': [2, 4, 6], 'z': [0, 1, 0]})


def test_x(df):
    plot = df.hvplot.paths(x='z', y='y')
    assert_element_equal(plot, Path(df, ['z', 'y'], []))


@pandas_and_dask
def test_x_default(df, tabular_lib):
    plot = tabular_lib(df).hvplot.paths()
    assert_element_equal(plot, Path(df, ['x', 'y'], []))


@pandas_and_dask
def test_x_index(df, tabular_lib):
    plot = tabular_lib(df).hvplot.paths(x='index', y='y', c='x')
    assert_element_equal(plot, Path(df.reset_index(), ['index', 'y'], ['x']))


def test_y(df, tabular_lib):
    plot = tabular_lib(df).hvplot.paths(x='x', y='z')
    assert_element_equal(plot, Path(df, ['x', 'z'], []))


@pytest.mark.xfail(reason='BUG: a lone x or y is ignored, the first two columns are plotted')
@pytest.mark.parametrize('kwargs', [{'x': 'z'}, {'y': 'z'}])
def test_x_or_y_only(df, kwargs):
    plot = df.hvplot.paths(**kwargs)
    assert 'z' in plot.kdims


@pytest.fixture
def grid():
    return xr.DataArray(
        np.arange(6.0).reshape(2, 3), coords={'y': [0, 1], 'x': [10, 20, 30]}, name='v'
    )


def test_gridded(grid, gridded_lib):
    plot = gridded_lib(grid).hvplot.paths(x='x', y='y')
    assert isinstance(plot, Path)
    assert plot.kdims == ['x', 'y']
    # A single path through all the grid points.
    assert len(plot.split()) == 1
    assert list(plot.dimension_values('x')) == [10, 20, 30, 10, 20, 30]


@pytest.mark.xfail(
    reason='BUG: gridded paths without x and y have only one key dimension, failing to render'
)
def test_gridded_default(grid, hvplot_xarray):
    plot = grid.hvplot.paths()
    assert plot.kdims == ['x', 'y']


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
