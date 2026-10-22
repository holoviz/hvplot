import pandas as pd
import pytest
from holoviews import Store
from holoviews.element import Area, Curve, Path, Points, Scatter
from holoviews.testing import assert_element_equal

pytestmark = pytest.mark.usefixtures('hvplot_pandas')

pandas_and_dask = pytest.mark.parametrize('tabular_lib', ['pandas', 'dask'], indirect=True)

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
    plot = tabular_lib(cat_df).hvplot.scatter(
        x='x', y='y', color='category', cmap={'A': 'red', 'B': 'blue'}
    )
    assert 'category' in [d.name for d in plot.vdims]
    assert '_color' not in plot.data.columns


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
