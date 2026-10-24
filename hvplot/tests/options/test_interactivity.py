import numpy as np
import pandas as pd
import pytest
import xarray as xr
from bokeh.models import HoverTool
from holoviews import Store
from holoviews.element import Area, Curve, Path, Points, Scatter
from holoviews.testing import assert_element_equal

from hvplot.tests._deps import pandas_and_dask, requires

pytestmark = pytest.mark.usefixtures('hvplot_pandas')


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


charts_1d = pytest.mark.parametrize(
    ('kind', 'element'), [('line', Curve), ('area', Area), ('scatter', Scatter)]
)
charts_2d = pytest.mark.parametrize(('kind', 'element'), [('points', Points), ('paths', Path)])


@pytest.fixture
def xy_df():
    return pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])


@pytest.fixture
def cat_df():
    return pd.DataFrame([[1, 2, 'A'], [3, 4, 'B'], [5, 6, 'C']], columns=['x', 'y', 'category'])


@pytest.mark.parametrize(
    'toolbar', ['right', 'left', 'above', 'below', None, False, True, 'disable']
)
def test_toolbar(cat_df, toolbar):
    plot = cat_df.hvplot.scatter('x', 'y', toolbar=toolbar)
    opts = Store.lookup_options('bokeh', plot, 'plot')
    if toolbar is True:
        toolbar = 'right'
    elif toolbar is False:
        toolbar = None
    assert opts.kwargs['toolbar'] == toolbar


def test_autohide_toolbar(cat_df):
    plot = cat_df.hvplot.scatter('x', 'y', autohide_toolbar=True)
    opts = Store.lookup_options('bokeh', plot, 'plot')
    assert opts.kwargs['autohide_toolbar'] is True


@pytest.mark.parametrize(
    ('tools', 'expected'),
    [
        ([], ['hover']),
        (['tap', 'box_select'], ['tap', 'box_select', 'hover']),
        # The hover tool is not added twice.
        (['hover', 'tap'], ['hover', 'tap']),
    ],
)
def test_tools(cat_df, tools, expected):
    plot = cat_df.hvplot.scatter('x', 'y', tools=tools)
    opts = Store.lookup_options('bokeh', plot, 'plot')
    assert opts.kwargs['tools'] == expected


@pandas_and_dask
@charts_2d
def test_hover_cols_list_2d(tabular_lib, cat_df, kind, element):
    df = tabular_lib(cat_df)
    plot = df.hvplot(x='x', y='y', hover_cols=['category'], kind=kind)
    assert_element_equal(plot, element(df, ['x', 'y'], ['category']))


@pandas_and_dask
@charts_2d
def test_hover_cols_index_2d(tabular_lib, cat_df, kind, element):
    df = tabular_lib(cat_df)
    plot = df.hvplot(x='x', y='y', hover_cols=['index'], kind=kind)
    assert_element_equal(plot, element(df.reset_index(), ['x', 'y'], ['index']))


@pandas_and_dask
@charts_2d
def test_hover_cols_all_2d(tabular_lib, cat_df, kind, element):
    df = tabular_lib(cat_df)
    plot = df.hvplot(x='x', y='y', hover_cols='all', kind=kind)
    assert_element_equal(plot, element(df.reset_index(), ['x', 'y'], ['index', 'category']))


@pandas_and_dask
@charts_2d
def test_hover_cols_all_and_use_index_false_2d(tabular_lib, cat_df, kind, element):
    df = tabular_lib(cat_df)
    plot = df.hvplot(x='x', y='y', hover_cols='all', use_index=False, kind=kind)
    assert_element_equal(plot, element(df, ['x', 'y'], ['category']))


@pandas_and_dask
@charts_1d
def test_hover_cols_list(tabular_lib, cat_df, kind, element):
    df = tabular_lib(cat_df)
    plot = df.hvplot(x='x', y='y', kind=kind, hover_cols=['category'])
    assert_element_equal(plot, element(df, 'x', ['y', 'category']))


@pandas_and_dask
@charts_1d
def test_hover_cols_index(tabular_lib, xy_df, kind, element):
    df = tabular_lib(xy_df)
    plot = df.hvplot(x='x', y='y', kind=kind, hover_cols=['index'])
    assert_element_equal(plot, element(df.reset_index(), 'x', ['y', 'index']))


@pandas_and_dask
@charts_1d
def test_hover_cols_all(tabular_lib, cat_df, kind, element):
    df = tabular_lib(cat_df)
    plot = df.hvplot(x='x', y='y', kind=kind, hover_cols='all')
    assert_element_equal(plot, element(df.reset_index(), 'x', ['y', 'index', 'category']))


@pandas_and_dask
@charts_1d
def test_hover_cols_all_and_use_index_false(tabular_lib, cat_df, kind, element):
    df = tabular_lib(cat_df)
    plot = df.hvplot(x='x', y='y', kind=kind, hover_cols='all', use_index=False)
    assert_element_equal(plot, element(df, 'x', ['y', 'category']))


def test_hover_cols_string(cat_df):
    plot = cat_df.hvplot.scatter('x', 'y', hover_cols='category')
    assert plot.vdims == ['y', 'category']


@pytest.mark.xfail(
    reason='BUG: hover_cols raises on an xarray Dataset, the other data variables are dropped',
    strict=True,
)
@pytest.mark.parametrize('hover_cols', [['w'], 'all'])
@pytest.mark.parametrize('kind', ['image', 'quadmesh'])
def test_hover_cols_gridded(hvplot_xarray, kind, hover_cols):
    data = np.arange(6.0).reshape(2, 3)
    ds = xr.Dataset(
        {'v': (('y', 'x'), data), 'w': (('y', 'x'), data * 2)},
        coords={'x': [0, 1, 2], 'y': [0, 1]},
    )
    plot = ds.hvplot(kind=kind, x='x', y='y', z='v', hover_cols=hover_cols)
    assert plot.vdims == ['v', 'w']


def test_tools_hover_instance_not_duplicated(cat_df):
    hover = HoverTool()
    plot = cat_df.hvplot.scatter('x', 'y', tools=[hover])
    opts = Store.lookup_options('bokeh', plot, 'plot')
    assert opts.kwargs['tools'] == [hover]


@pytest.mark.xfail(
    reason="BUG: hover_mode is dropped when 'hover' is also in tools",
    strict=True,
)
def test_hover_line_mode_with_hover_tool(xy_df):
    plot = xy_df.hvplot('x', 'y', hover='vline', tools=['hover'])
    opts = Store.lookup_options('bokeh', plot, 'plot')
    assert opts.kwargs['hover_mode'] == 'vline'


def _tooltip_dims(plot):
    hover_tooltips = Store.lookup_options('bokeh', plot, 'plot').kwargs.get('hover_tooltips')
    assert hover_tooltips is not None
    return [tt[0] if isinstance(tt, tuple) else tt for tt in hover_tooltips]


@pandas_and_dask
def test_hover_tooltips_default_exclude_color_series(tabular_lib, cat_df):
    # A pandas series also with dask, passing lazy series is not yet supported.
    color_series = cat_df['category'].map({'A': 'red', 'B': 'blue'})
    plot = tabular_lib(cat_df).hvplot.scatter(x='x', y='y', color=color_series)

    assert '_color' in plot.data.columns
    assert '_color' in plot.vdims
    tooltip_dims = _tooltip_dims(plot)
    assert '_color' not in tooltip_dims
    assert 'x' in tooltip_dims
    assert 'y' in tooltip_dims


@pandas_and_dask
def test_hover_tooltips_default_exclude_size_series(tabular_lib, cat_df):
    plot = tabular_lib(cat_df).hvplot.scatter(x='x', y='y', s=cat_df['y'] / 10)

    assert '_size' in plot.data.columns
    assert '_size' in plot.vdims
    tooltip_dims = _tooltip_dims(plot)
    assert '_size' not in tooltip_dims
    assert 'x' in tooltip_dims
    assert 'y' in tooltip_dims


@pandas_and_dask
def test_hover_tooltips_default_exclude_color_and_size_series(tabular_lib, cat_df):
    color_series = cat_df['category'].map({'A': 'red', 'B': 'blue'})
    plot = tabular_lib(cat_df).hvplot.scatter(x='x', y='y', color=color_series, s=cat_df['y'] / 10)

    assert '_color' in plot.data.columns
    assert '_size' in plot.data.columns
    tooltip_dims = _tooltip_dims(plot)
    assert '_color' not in tooltip_dims
    assert '_size' not in tooltip_dims
    assert 'x' in tooltip_dims
    assert 'y' in tooltip_dims


@pandas_and_dask
def test_hover_tooltips_explicit_with_color_series(tabular_lib, cat_df):
    color_series = cat_df['category'].map({'A': 'red', 'B': 'blue'})
    expected_htt = [('x', '@x'), ('color', '@_color')]
    plot = tabular_lib(cat_df).hvplot.scatter(
        x='x', y='y', color=color_series, hover_tooltips=expected_htt
    )
    opts = Store.lookup_options('bokeh', plot, 'plot')
    assert opts.kwargs.get('hover_tooltips') == expected_htt


@pandas_and_dask
def test_hover_shows_color_column(tabular_lib, cat_df):
    plot = tabular_lib(cat_df).hvplot.scatter(x='x', y='y', color='category')
    assert 'category' in [d.name for d in plot.vdims]
    assert '_color' not in plot.data.columns


@pandas_and_dask
def test_hover_shows_color_column_with_cmap_dict(tabular_lib, cat_df):
    cmap = {'A': 'red', 'B': 'blue'}
    plot = tabular_lib(cat_df).hvplot.scatter(x='x', y='y', color='category', cmap=cmap)
    assert 'category' in [d.name for d in plot.vdims]
    assert '_color' not in plot.data.columns
    assert Store.lookup_options('bokeh', plot, 'style').kwargs['cmap'] == cmap


@pandas_and_dask
@pytest.mark.parametrize('hover_mode', ['vline', 'hline'])
def test_hover_line_mode(tabular_lib, xy_df, hover_mode):
    plot = tabular_lib(xy_df).hvplot('x', 'y', hover=hover_mode)
    opts = Store.lookup_options('bokeh', plot, 'plot')
    assert opts.kwargs['hover_mode'] == hover_mode


@pandas_and_dask
@pytest.mark.filterwarnings('ignore:hover_formatters')
def test_hover_false(tabular_lib, xy_df):
    plot = tabular_lib(xy_df).hvplot(
        'x', 'y', hover_tooltips=['x'], hover_formatters={'x': 'datetime'}, hover=False
    )
    opts = Store.lookup_options('bokeh', plot, 'plot')
    assert opts.kwargs['tools'] == []
    assert 'hover_formatters' not in opts.kwargs
    assert 'hover_tooltips' not in opts.kwargs


@pandas_and_dask
def test_hover_tooltips(tabular_lib, xy_df):
    plot = tabular_lib(xy_df).hvplot('x', 'y', hover_tooltips=['x'])
    opts = Store.lookup_options('bokeh', plot, 'plot')
    assert opts.kwargs['hover_tooltips'] == ['x']


@pandas_and_dask
@pytest.mark.filterwarnings('ignore:hover_formatters')
def test_hover_formatters(tabular_lib, xy_df):
    plot = tabular_lib(xy_df).hvplot('x', 'y', hover_formatters={'x': 'datetime'})
    opts = Store.lookup_options('bokeh', plot, 'plot')
    assert opts.kwargs['hover_formatters'] == {'x': 'datetime'}


@pytest.mark.geo
@requires('geopandas', 'shapely')
def test_hover_cols_default_geodataframe(cities):
    points = cities.hvplot()
    assert points.kdims == ['x', 'y']
    assert points.vdims == []


@pytest.mark.geo
@requires('geopandas', 'shapely')
def test_hover_cols_all_geodataframe(cities):
    """The geometry is not a hover column."""
    points = cities.hvplot(x='x', y='y', hover_cols='all')
    assert points.kdims == ['x', 'y']
    assert points.vdims == ['index', 'name']


@pytest.mark.geo
@requires('geopandas', 'shapely')
def test_hover_cols_all_no_index_geodataframe(cities):
    points = cities.hvplot(x='x', hover_cols='all', use_index=False)
    assert points.kdims == ['x', 'y']
    assert points.vdims == ['name']


@pytest.mark.geo
@requires('geopandas', 'shapely')
def test_hover_cols_index_geodataframe(cities):
    points = cities.hvplot(y='y', hover_cols=['index'])
    assert points.kdims == ['x', 'y']
    assert points.vdims == ['index']


@pytest.mark.geo
@requires('geopandas', 'shapely')
def test_hover_geodataframe_without_fields(polygons):
    plot = polygons.hvplot(geo=True)
    opts = Store.lookup_options('bokeh', plot, 'plot').kwargs
    assert 'hover' not in opts.get('tools')
