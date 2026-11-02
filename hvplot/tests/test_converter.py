"""
Tests of the conversion of data to HoloViews objects that are not specific to
one option or one kind: wide and tidy data, default options, derived datetime
dimensions, labels inferred from xarray attrs, and panel widgets as arguments.
"""

import holoviews as hv
import numpy as np
import pandas as pd
import panel as pn
import pytest
import xarray as xr
from holoviews import NdOverlay, Store, render
from holoviews.core.dimension import Dimension
from holoviews.element import Area, Curve, Scatter
from holoviews.testing import assert_element_equal

from hvplot.tests._deps import pandas_and_dask

pytestmark = pytest.mark.usefixtures('hvplot_pandas', 'hvplot_xarray')

CHART_KINDS = [('line', Curve), ('area', Area), ('scatter', Scatter)]


def look_for_class(panel, classname, items=None):
    """
    Descend a panel object and find any instances of the given class
    """
    if items is None:
        items = []
    if isinstance(panel, pn.layout.ListPanel):
        for p in panel:
            items = look_for_class(p, classname, items)
    elif isinstance(panel, classname):
        items.append(panel)
    return items


@pytest.fixture
def flowers():
    # A few rows of the iris dataset.
    return pd.DataFrame(
        {
            'sepal_length': [5.1, 4.9, 7.0, 6.4, 6.3, 5.8],
            'sepal_width': [3.5, 3.0, 3.2, 3.2, 3.3, 2.7],
            'petal_length': [1.4, 1.4, 4.7, 4.5, 6.0, 5.1],
            'petal_width': [0.2, 0.2, 1.4, 1.5, 2.5, 1.9],
            'species': ['setosa', 'setosa', 'versicolor', 'versicolor', 'virginica', 'virginica'],
        }
    )


@pytest.fixture
def df():
    return pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])


@pytest.fixture
def cat_df():
    return pd.DataFrame([[1, 2, 'A'], [3, 4, 'B'], [5, 6, 'C']], columns=['x', 'y', 'category'])


@pytest.fixture
def cat_only_df():
    return pd.DataFrame([['A', 'a'], ['B', 'b'], ['C', 'c']], columns=['upper', 'lower'])


@pytest.fixture
def time_df():
    return pd.DataFrame(
        {
            'time': pd.date_range('1/1/2000', periods=10, tz='UTC'),
            'A': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'B': list('abcdefghij'),
        }
    )


@pytest.fixture
def xarr_with_attrs():
    da = xr.DataArray(
        np.random.default_rng(1).random((10, 10)),
        coords={'y': range(10), 'x': range(10)},
        dims=['y', 'x'],
        attrs={'long_name': 'luminosity', 'units': 'lm'},
    )
    da.x.attrs['long_name'] = 'Declination'
    da.y.attrs['long_name'] = 'Right Ascension'
    return da


@pytest.fixture
def da_rgb():
    coords = {'band': [1, 2, 3], 'y': [0, 1], 'x': [0, 1]}
    return xr.DataArray(np.arange(12).reshape((3, 2, 2)), coords, ['band', 'y', 'x'])


def test_using_explicit_widgets_works(flowers):
    cols = list(flowers.columns[:-1])
    x = pn.widgets.Select(label='x', value='sepal_length', options=cols)
    y = pn.widgets.Select(label='y', value='sepal_width', options=cols)
    kind = pn.widgets.Select(label='kind', value='scatter', options=['bivariate', 'scatter'])
    color = pn.widgets.ColorPicker(value='#ff0000')

    pane = flowers.hvplot(x, y=y, kind=kind.param.value, c=color)
    assert isinstance(pane, pn.param.ParamFunction)


def test_casting_widgets_to_different_classes(flowers):
    pane = flowers.hvplot.scatter(
        groupby='species', legend='top_right', widgets={'species': pn.widgets.DiscreteSlider}
    )

    assert len(look_for_class(pane, pn.widgets.DiscreteSlider)) == 1


def test_using_explicit_widgets_with_groupby_does_not_raise_error(flowers):
    cols = list(flowers.columns[:-1])
    x = pn.widgets.Select(label='x', value='sepal_length', options=cols)
    y = pn.widgets.Select(label='y', value='sepal_width', options=cols)

    pane = flowers.hvplot(x, y, groupby='species')
    assert isinstance(pane, pn.param.ParamFunction)


@pytest.fixture
def options_df():
    return pd.DataFrame(
        [[1, 2, 'A', 0.1], [3, 4, 'B', 0.2], [5, 6, 'C', 0.3]],
        columns=['x', 'y', 'category', 'number'],
    )


def test_hvplot_defaults(options_df, backend):
    plot = options_df.hvplot.scatter('x', 'y', c='category')
    opts = Store.lookup_options(backend, plot, 'plot')
    if backend == 'bokeh':
        assert opts.kwargs['height'] == 300
        assert opts.kwargs['width'] == 700
    elif backend == 'matplotlib':
        assert opts.kwargs['aspect'] == pytest.approx(2.333333)
        assert opts.kwargs['fig_size'] == pytest.approx(233.333333)
    if backend == 'bokeh':
        assert opts.kwargs['responsive'] is False
        assert opts.kwargs['shared_axes'] is True
        # legend_position shouldn't only be for Bokeh
        assert opts.kwargs['legend_position'] == 'right'
    assert opts.kwargs['show_grid'] is False
    assert opts.kwargs['show_legend'] is True
    assert opts.kwargs['logx'] is False
    assert opts.kwargs['logy'] is False
    assert opts.kwargs.get('logz') is None


# Default opts are only supported with bokeh.
def test_holoviews_defined_default_opts(options_df):
    hv.opts.defaults(hv.opts.Scatter(height=400, width=900, show_grid=True))
    plot = options_df.hvplot.scatter('x', 'y', c='category')
    opts = Store.lookup_options('bokeh', plot, 'plot')
    assert opts.kwargs['legend_position'] == 'right'
    assert opts.kwargs['show_grid'] is True
    assert opts.kwargs['height'] == 400
    assert opts.kwargs['width'] == 900


def test_holoviews_defined_default_opts_overwritten_in_call(options_df):
    hv.opts.defaults(hv.opts.Scatter(height=400, width=900, show_grid=True))
    plot = options_df.hvplot.scatter('x', 'y', c='category', width=300, legend='left')
    opts = Store.lookup_options('bokeh', plot, 'plot')
    assert opts.kwargs['legend_position'] == 'left'
    assert opts.kwargs['show_grid'] is True
    assert opts.kwargs['height'] == 400
    assert opts.kwargs['width'] == 300


def test_holoviews_defined_default_opts_are_not_mutable(options_df):
    hv.opts.defaults(hv.opts.Scatter(tools=['tap']))
    plot = options_df.hvplot.scatter('x', 'y', c='category')
    opts = Store.lookup_options('bokeh', plot, 'plot')
    assert opts.kwargs['tools'] == ['tap', 'hover']
    default_opts = Store.options(backend='bokeh')['Scatter'].groups['plot'].options
    assert default_opts['tools'] == ['tap']


def test_xarray_dataset_with_attrs():
    dset = xr.Dataset(
        {'u': ('t', [1, 3]), 'v': ('t', [4, 2])},
        coords={'t': ('t', [0, 1], {'long_name': 'time', 'units': 's'})},
    )
    ndoverlay = dset.hvplot.line()

    assert render(ndoverlay, 'bokeh').xaxis.axis_label == 'time (s)'


def test_xarray_dataset_empty_error():
    ds = xr.Dataset({'foo': (('y', 'x'), [[0, 1], [2, 3]])}, coords={'x': [0, 1], 'y': [0, 1]})
    with pytest.raises(ValueError, match=r'empty xarray.Dataset'):
        ds.drop_vars('foo').hvplot()


@pandas_and_dask
@pytest.mark.parametrize(('kind', 'element'), CHART_KINDS)
def test_wide_chart(df, tabular_lib, kind, element):
    data = tabular_lib(df)
    plot = data.hvplot(kind=kind)
    obj = NdOverlay(
        {
            'x': element(data, 'index', Dimension('x', label='value')),
            'y': element(data, 'index', Dimension('y', label='value')),
        },
        'Variable',
    )
    assert_element_equal(plot, obj)


@pandas_and_dask
@pytest.mark.parametrize(('kind', 'element'), CHART_KINDS)
def test_tidy_chart(df, tabular_lib, kind, element):
    data = tabular_lib(df)
    plot = data.hvplot(x='x', y='y', kind=kind)
    assert_element_equal(plot, element(data, 'x', 'y'))


@pandas_and_dask
@pytest.mark.parametrize(('kind', 'element'), CHART_KINDS)
def test_tidy_chart_index(df, tabular_lib, kind, element):
    data = tabular_lib(df)
    plot = data.hvplot(x='index', y='y', kind=kind)
    assert_element_equal(plot, element(data, 'index', 'y'))


@pandas_and_dask
@pytest.mark.parametrize(('kind', 'element'), CHART_KINDS)
def test_tidy_chart_index_by(df, tabular_lib, kind, element):
    data = tabular_lib(df)
    plot = data.hvplot(x='index', y='y', by='x', kind=kind)
    if isinstance(data, pd.DataFrame):
        keys = [1, 3, 5]
    else:
        # dask doesn't guarantee the order of the `.unique()` calls made
        # by HoloViews when running a groupby operation.
        keys = list(plot.keys())
    obj = NdOverlay(
        {k: element(data[data.x == k], 'index', 'y') for k in keys},
        'x',
        sort=False,
    )
    assert_element_equal(plot, obj)


@pandas_and_dask
@pytest.mark.parametrize(('kind', 'element'), CHART_KINDS)
def test_only_includes_num_chart(cat_df, tabular_lib, kind, element):
    data = tabular_lib(cat_df)
    plot = data.hvplot(kind=kind)
    obj = NdOverlay(
        {
            'x': element(data, 'index', Dimension('x', label='value')),
            'y': element(data, 'index', Dimension('y', label='value')),
        },
        'Variable',
    )
    assert_element_equal(plot, obj)


@pandas_and_dask
@pytest.mark.parametrize(
    ('kind', 'element'),
    [
        ('line', Curve),
        pytest.param(
            'area',
            Area,
            marks=pytest.mark.render_xfail(
                reason='HoloViews: Area with string values fails', strict=False
            ),
        ),
        ('scatter', Scatter),
    ],
)
def test_includes_str_if_no_num_chart(cat_only_df, tabular_lib, kind, element):
    data = tabular_lib(cat_only_df)
    plot = data.hvplot(kind=kind)
    obj = NdOverlay(
        {
            'upper': element(data, 'index', Dimension('upper', label='value')),
            'lower': element(data, 'index', Dimension('lower', label='value')),
        },
        'Variable',
        sort=False,
    )
    assert_element_equal(plot, obj)


def test_time_df_with_groupby_as_derived_datetime(time_df):
    plot = time_df.hvplot(groupby='time.dayofweek', dynamic=False)
    assert list(plot.keys()) == [0, 1, 2, 3, 4, 5, 6]
    assert list(plot.dimensions()) == ['time.dayofweek', 'index', 'A']


def test_time_df_with_by_as_derived_datetime(time_df):
    plot = time_df.hvplot(by='time.month', dynamic=False)
    assert list(plot.keys()) == [1]
    assert list(plot.dimensions()) == ['time.month', 'index', 'A']


def test_time_df_with_x_as_derived_datetime(time_df):
    plot = time_df.hvplot.scatter(x='time.day', dynamic=False)
    assert list(plot.dimensions()) == ['time.day', 'A']


def test_time_df_as_index_with_x_as_derived_datetime_using_name(time_df):
    indexed = time_df.set_index('time')
    plot = indexed.hvplot.scatter(x='time.day', dynamic=False)
    assert list(plot.dimensions()) == ['time.day', 'A']


def test_time_df_as_index_with_x_as_derived_datetime_using_index(time_df):
    indexed = time_df.set_index('time')
    plot = indexed.hvplot.scatter(x='index.day', dynamic=False)
    assert list(plot.dimensions()) == ['index.day', 'A']


@pytest.mark.xfail(reason='BUG: hierarchical columns are not auto stacked, see issue 1364')
def test_hierarchical_columns_auto_stack(rng):
    arrays = [
        ['bar', 'bar', 'baz', 'baz', 'foo', 'foo', 'qux', 'qux'],
        ['one', 'two', 'one', 'two', 'one', 'two', 'one', 'two'],
    ]
    tuples = list(zip(*arrays, strict=True))
    index = pd.MultiIndex.from_tuples(tuples)
    df = pd.DataFrame(rng.standard_normal((3, 8)), index=['A', 'B', 'C'], columns=index)
    df.hvplot.scatter()


def test_line_infer_dimension_params_from_xarray_attrs(xarr_with_attrs):
    hmap = xarr_with_attrs.hvplot.line(groupby='x', dynamic=False)
    assert hmap.kdims[0].label == 'Declination'
    assert hmap.last.kdims[0].label == 'Right Ascension'
    assert hmap.last.vdims[0].label == 'luminosity'
    assert hmap.last.vdims[0].unit == 'lm'


def test_img_infer_dimension_params_from_xarray_attrs(xarr_with_attrs):
    img = xarr_with_attrs.hvplot.image(clim=(0, 2))
    assert img.kdims[0].label == 'Declination'
    assert img.kdims[1].label == 'Right Ascension'
    assert img.vdims[0].label == 'luminosity'
    assert img.vdims[0].unit == 'lm'
    assert img.vdims[0].range == (0, 2)


def test_points_infer_dimension_params_from_xarray_attrs(xarr_with_attrs):
    points = xarr_with_attrs.hvplot.points(c='value', clim=(0, 2))
    assert points.kdims[0].label == 'Declination'
    assert points.kdims[1].label == 'Right Ascension'
    assert points.vdims[0].label == 'luminosity'
    assert points.vdims[0].unit == 'lm'
    assert points.vdims[0].range == (0, 2)


def test_dataset_infer_dimension_params_from_xarray_attrs(xarr_with_attrs):
    ds = xarr_with_attrs.hvplot.dataset()
    assert ds.kdims[0].label == 'Declination'
    assert ds.kdims[1].label == 'Right Ascension'
    assert ds.vdims[0].label == 'luminosity'
    assert ds.vdims[0].unit == 'lm'


def test_dataset_infer_dimension_params_from_xarray_ds_attrs(xarr_with_attrs):
    ds = xr.Dataset({'light': xarr_with_attrs}).hvplot.dataset()
    assert ds.kdims[0].label == 'Declination'
    assert ds.kdims[1].label == 'Right Ascension'
    assert ds.vdims[0].label == 'luminosity'
    assert ds.vdims[0].unit == 'lm'


def test_dataarray_label_precedence(da_rgb):
    # name > label > value_label
    plot = da_rgb.sel(band=1).rename('a').hvplot.image(label='b')
    assert plot.vdims[0].name == 'a'

    plot = da_rgb.sel(band=1).hvplot.image(label='b', value_label='c')
    assert plot.vdims[0].name == 'b'
