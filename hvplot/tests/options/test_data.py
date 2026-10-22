import holoviews as hv
import numpy as np
import pandas as pd
import pytest
import xarray as xr
from holoviews import NdOverlay
from holoviews.core.dimension import Dimension
from holoviews.element import Area, Curve, Scatter
from holoviews.testing import assert_data_equal, assert_element_equal

pytestmark = pytest.mark.usefixtures('hvplot_pandas')

pandas_and_dask = pytest.mark.parametrize('tabular_lib', ['pandas', 'dask'], indirect=True)

charts = pytest.mark.parametrize(
    ('kind', 'element'), [('line', Curve), ('area', Area), ('scatter', Scatter)]
)


@pytest.fixture
def xy_df():
    return pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])


@pytest.fixture
def cat_df():
    return pd.DataFrame([[1, 2, 'A'], [3, 4, 'B'], [5, 6, 'C']], columns=['x', 'y', 'category'])


@pytest.fixture
def time_df():
    return pd.DataFrame(
        {
            'time': pd.date_range('1/1/2000', periods=10, tz='UTC'),
            'A': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'B': list('abcdefghij'),
        }
    )


def test_transforms_pandas():
    df = pd.DataFrame({'value': np.random.randn(50), 'probability': np.random.rand(50)})
    percent = hv.dim('probability') * 100
    scatter = df.hvplot.scatter(x='value', y='probability', transforms={'probability': percent})
    assert_data_equal(scatter.data['probability'].values, df['probability'].values * 100)


def test_transforms_xarray(hvplot_xarray):
    data = np.arange(0, 60).reshape(6, 10)
    da = xr.DataArray(
        data, coords={'y': np.arange(6), 'x': np.arange(10)}, dims=('y', 'x'), name='value'
    )
    img = da.hvplot.image(transforms={'value': hv.dim('value') * 10})
    assert_data_equal(img.data.value.data, da.data * 10)


@pytest.mark.parametrize(
    'tabular_lib',
    [
        'pandas',
        pytest.param(
            'dask', marks=pytest.mark.skip(reason="Can't expand dt accessor columns with dask")
        ),
    ],
    indirect=True,
)
def test_by_datetime_accessor(tabular_lib):
    dt_df = pd.DataFrame(np.random.rand(90), index=pd.date_range('2019-01-01', '2019-03-31'))
    plot = tabular_lib(dt_df).hvplot.line('index.dt.day', '0', by='index.dt.month')
    expected = NdOverlay(
        {
            m: Curve((g.index.day, g[0]), 'index.dt.day', '0')
            for m, g in dt_df.groupby(dt_df.index.month)
        },
        'index.dt.month',
    )
    assert_element_equal(plot, expected)


@pandas_and_dask
def test_by_not_in_default_y(tabular_lib, cat_df):
    plot = tabular_lib(cat_df).hvplot.scatter(by='x')
    assert plot.kdims == ['x']
    assert plot[1].kdims == ['index']
    assert plot[1].vdims == ['y']


@pandas_and_dask
@charts
def test_value_label_and_group_label_wide(tabular_lib, xy_df, kind, element):
    df = tabular_lib(xy_df)
    plot = df.hvplot(kind=kind, value_label='Test', group_label='Category')
    expected = NdOverlay(
        {
            'x': element(df, 'index', Dimension('x', label='Test')),
            'y': element(df, 'index', Dimension('y', label='Test')),
        },
        'Category',
    )
    assert_element_equal(plot, expected)


@pandas_and_dask
@pytest.mark.parametrize('kind', ['line', 'area', 'scatter'])
def test_group_label_from_columns_name(tabular_lib, xy_df, kind):
    # Not set in place, dask would share the renamed columns with equal frames.
    df = tabular_lib(xy_df).rename_axis(columns='My Name')
    assert df.hvplot(kind=kind).kdims == ['My Name']


@pandas_and_dask
def test_group_label_hist_wide(tabular_lib, xy_df):
    plot = tabular_lib(xy_df).hvplot.hist(group_label='Test')
    assert plot.kdims[0].name == 'Test'


@pandas_and_dask
@pytest.mark.parametrize('kind', ['line', 'area', 'scatter'])
def test_use_index_false_uses_first_cols(tabular_lib, xy_df, kind):
    plot = tabular_lib(xy_df).hvplot(use_index=False, kind=kind)
    assert plot.kdims == ['x']
    assert plot.vdims == ['y']


@pandas_and_dask
def test_groupby_index(tabular_lib, cat_df):
    df = tabular_lib(cat_df.set_index('category'))
    hmap = df.hvplot.scatter(x='x', y='y', groupby='category', dynamic=False)
    assert hmap.kdims == ['category']
    assert hmap.vdims == []
    assert list(hmap.keys()) == ['A', 'B', 'C']
    assert hmap.last.kdims == ['x']
    assert hmap.last.vdims == ['y']


@pytest.mark.parametrize(
    'tabular_lib',
    [
        'pandas',
        pytest.param(
            'dask', marks=pytest.mark.skip(reason='Dask does not support MultiIndex DataFrames')
        ),
    ],
    indirect=True,
)
def test_groupby_multiindex_level(tabular_lib):
    df = pd.DataFrame({'A': [1, 2, 3, 4], 'B': ['a', 'a', 'b', 'b'], 'C': [0, 1, 2, 1.5]})
    hmap = tabular_lib(df.set_index(['A', 'B'])).hvplot.scatter(
        x='A', y='C', groupby='B', dynamic=False
    )
    assert hmap.kdims == ['B']
    assert hmap.vdims == []
    assert list(hmap.keys()) == ['a', 'b']
    assert hmap.last.kdims == ['A']
    assert hmap.last.vdims == ['C']


def test_sort_date_default(time_df):
    scrambled = time_df.sample(frac=1)
    plot = scrambled.hvplot(x='time')
    assert (plot.data == time_df).all().all()
    assert len(plot.data.time.unique()) == len(plot.data.time)


def test_sort_date_false(time_df):
    scrambled = time_df.sample(frac=1)
    plot = scrambled.hvplot(x='time', sort_date=False)
    assert (plot.data == scrambled).all().all()
    assert len(plot.data.time.unique()) == len(plot.data.time)


def test_sort_date_default_index(time_df):
    df = time_df.set_index('time')
    scrambled = df.sample(frac=1)
    plot = scrambled.hvplot()
    time = plot.data.index
    assert (time == df.index).all()
    assert len(time.unique()) == len(time)


def test_sort_date_false_index(time_df):
    df = time_df.set_index('time')
    scrambled = df.sample(frac=1)
    plot = scrambled.hvplot(sort_date=False)
    time = plot.data.index
    assert (time == scrambled.index).all()
    assert len(time.unique()) == len(time)


def test_sort_date_default_multiindex(time_df):
    df = time_df.set_index(['B', 'time'])
    scrambled = df.sample(frac=1)
    plot = scrambled.hvplot(x='time')
    time = plot.data.index.get_level_values('time')
    assert plot.kdims == ['time']
    assert (time == df.index.get_level_values('time')).all()
    assert len(time.unique()) == len(time)


def test_sort_date_false_multiindex(time_df):
    df = time_df.set_index(['B', 'time'])
    scrambled = df.sample(frac=1)
    plot = scrambled.hvplot(x='time', sort_date=False)
    time = plot.data.index.get_level_values('time')
    assert plot.kdims == ['time']
    assert (time == scrambled.index.get_level_values('time')).all()
    assert len(time.unique()) == len(time)


def test_sort_date_default_multiindex_level0(time_df):
    df = time_df.set_index(['time', 'B'])
    scrambled = df.sample(frac=1)
    plot = scrambled.hvplot()
    time = plot.data.index.get_level_values('time')
    assert plot.kdims == ['time']
    assert (time == df.index.get_level_values('time')).all()
    assert len(time.unique()) == len(time)


def test_sort_date_false_multiindex_level0(time_df):
    df = time_df.set_index(['time', 'B'])
    scrambled = df.sample(frac=1)
    plot = scrambled.hvplot(sort_date=False)
    time = plot.data.index.get_level_values('time')
    assert plot.kdims == ['time']
    assert (time == scrambled.index.get_level_values('time')).all()
    assert len(time.unique()) == len(time)


@pytest.fixture
def unnamed_da():
    return xr.DataArray(np.arange(4).reshape((2, 2)), coords={'y': [0, 1], 'x': [0, 1]})


def test_label_dataarray_unnamed(hvplot_xarray, unnamed_da):
    plot = unnamed_da.hvplot.image(label='test')
    assert plot.vdims[0].name == 'test'


def test_value_label_dataarray_unnamed(hvplot_xarray, unnamed_da):
    plot = unnamed_da.hvplot.image(value_label='test')
    assert plot.vdims[0].name == 'test'
