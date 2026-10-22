import holoviews as hv
import pandas as pd
import pytest
from holoviews import Store
from holoviews.element import Polygons

from hvplot.tests._deps import requires

pytestmark = pytest.mark.usefixtures('hvplot_pandas')

# polygons is not supported by the plotly backend.
bokeh_and_mpl = pytest.mark.parametrize('backend', ['bokeh', 'matplotlib'], indirect=True)


@pytest.fixture
def df():
    # A single triangle.
    return pd.DataFrame({'x': [0, 1, 1], 'y': [0, 0, 1], 'lon': [5, 6, 6], 'v': [1, 1, 1]})


def test_x(df):
    plot = df.hvplot.polygons(x='lon', y='y')
    assert isinstance(plot, Polygons)
    assert plot.kdims == ['lon', 'y']
    # Polygons are closed, the first vertex is repeated.
    assert list(plot.dimension_values('lon')) == [5, 6, 6, 5]


@pytest.mark.parametrize(
    'tabular_lib',
    [
        'pandas',
        'dask',
        'polars',
        'duckdb',
        pytest.param(
            'ibis',
            marks=pytest.mark.render_xfail(
                reason='HoloViews: Polygons of an ibis table fails to render'
            ),
        ),
    ],
    indirect=True,
)
def test_y(df, tabular_lib):
    plot = tabular_lib(df).hvplot.polygons(x='x', y='lon')
    assert isinstance(plot, Polygons)
    assert plot.kdims == ['x', 'lon']
    assert list(plot.dimension_values('lon')) == [5, 6, 6, 5]


@pytest.mark.geo
@requires('geopandas', 'shapely')
def test_x_y_default_geodataframe():
    import geopandas as gpd
    import shapely

    gdf = gpd.GeoDataFrame(
        {'v': [1, 2]},
        geometry=[
            shapely.Polygon([(0, 0), (1, 0), (1, 1)]),
            shapely.Polygon([(1, 1), (2, 1), (2, 2)]),
        ],
    )
    plot = gdf.hvplot.polygons()
    assert isinstance(plot, Polygons)
    assert plot.kdims == ['x', 'y']
    assert len(plot.split()) == 2


@bokeh_and_mpl
def test_c(df, backend):
    plot = df.hvplot.polygons(x='x', y='y', c='v')
    assert plot.vdims == ['v']
    color = Store.lookup_options(backend, plot, 'style').kwargs['color']
    assert repr(color) == repr(hv.dim('v'))


@bokeh_and_mpl
def test_logz(df, backend):
    plot = df.hvplot.polygons(x='x', y='y', c='v', logz=True)
    assert Store.lookup_options(backend, plot, 'plot').kwargs['logz'] is True
