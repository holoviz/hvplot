from collections import OrderedDict
from unittest import SkipTest

import holoviews as hv
import numpy as np
import pandas as pd
import pytest
import xarray as xr
from holoviews import NdOverlay
from holoviews.core.dimension import Dimension
from holoviews.element import Area, Curve, Scatter
from holoviews.element.comparison import ComparisonTestCase
from parameterized import parameterized


class TestPandasTransforms(ComparisonTestCase):
    def setUp(self):
        import hvplot.pandas  # noqa: F401

    def test_pandas_transform(self):
        demo_df = pd.DataFrame({'value': np.random.randn(50), 'probability': np.random.rand(50)})
        percent = hv.dim('probability') * 100
        scatter = demo_df.hvplot.scatter(
            x='value', y='probability', transforms={'probability': percent}
        )
        self.assertEqual((scatter.data['probability']).values, demo_df['probability'].values * 100)


class TestXArrayTransforms(ComparisonTestCase):
    def setUp(self):
        try:
            import xarray  # noqa: F401
        except ImportError:
            raise SkipTest('xarray not available')
        import hvplot.xarray  # noqa: F401

    def test_xarray_transform(self):
        import xarray as xr

        data = np.arange(0, 60).reshape(6, 10)
        x = np.arange(10)
        y = np.arange(6)
        da = xr.DataArray(data, coords={'y': y, 'x': x}, dims=('y', 'x'), name='value')
        img = da.hvplot.image(transforms={'value': hv.dim('value') * 10})
        self.assertEqual(img.data.value.data, da.data * 10)


class TestChart1D(ComparisonTestCase):
    def setUp(self):
        import hvplot.pandas  # noqa: F401

        self.df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
        self.dt_df = pd.DataFrame(
            np.random.rand(90), index=pd.date_range('2019-01-01', '2019-03-31')
        )
        self.cat_df = pd.DataFrame(
            [[1, 2, 'A'], [3, 4, 'B'], [5, 6, 'C']], columns=['x', 'y', 'category']
        )
        self.cat_df_index = self.cat_df.set_index('category')
        multii_df = pd.DataFrame(
            {'A': [1, 2, 3, 4], 'B': ['a', 'a', 'b', 'b'], 'C': [0, 1, 2, 1.5]}
        )
        self.multii_df = multii_df.set_index(['A', 'B'])
        self.time_df = pd.DataFrame(
            {
                'time': pd.date_range('1/1/2000', periods=10, tz='UTC'),
                'A': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                'B': list('abcdefghij'),
            }
        )

    def test_by_datetime_accessor(self):
        plot = self.dt_df.hvplot.line('index.dt.day', '0', by='index.dt.month')
        obj = NdOverlay(
            {
                m: Curve((g.index.day, g[0]), 'index.dt.day', '0')
                for m, g in self.dt_df.groupby(self.dt_df.index.month)
            },
            'index.dt.month',
        )
        self.assertEqual(plot, obj)

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_wide_chart_labels(self, kind, element):
        plot = self.df.hvplot(kind=kind, value_label='Test', group_label='Category')
        obj = NdOverlay(
            {
                'x': element(self.df, 'index', Dimension('x', label='Test')),
                'y': element(self.df, 'index', Dimension('y', label='Test')),
            },
            'Category',
        )
        self.assertEqual(plot, obj)

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_wide_chart_auto_group_label(self, kind, element):
        # Not set in place, dask would share the renamed columns with equal frames.
        df = self.df.rename_axis(columns='My Name')
        self.assertEqual(df.hvplot().kdims, ['My Name'])

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_use_index_disabled_uses_first_cols(self, kind, element):
        plot = self.df.hvplot(use_index=False, kind=kind)
        self.assertEqual(plot.kdims, ['x'])
        self.assertEqual(plot.vdims, ['y'])

    def test_histogram_wide_set_group_label(self):
        plot = self.df.hvplot.hist(group_label='Test')
        assert plot.kdims[0].name == 'Test'

    def test_time_df_sorts_on_plot(self):
        scrambled = self.time_df.sample(frac=1)
        plot = scrambled.hvplot(x='time')
        assert (plot.data == self.time_df).all().all()
        assert len(plot.data.time.unique()) == len(plot.data.time)

    def test_time_df_does_not_sort_on_plot_if_sort_date_off(self):
        scrambled = self.time_df.sample(frac=1)
        plot = scrambled.hvplot(x='time', sort_date=False)
        assert (plot.data == scrambled).all().all()
        assert len(plot.data.time.unique()) == len(plot.data.time)

    def test_time_df_sorts_on_plot_using_index_as_x(self):
        df = self.time_df.set_index('time')
        scrambled = df.sample(frac=1)
        plot = scrambled.hvplot()
        time = plot.data.index
        assert (time == df.index).all()
        assert len(time.unique()) == len(time)

    def test_time_df_does_not_sort_on_plot_if_sort_date_off_using_index_as_x(self):
        df = self.time_df.set_index('time')
        scrambled = df.sample(frac=1)
        plot = scrambled.hvplot(sort_date=False)
        time = plot.data.index
        assert (time == scrambled.index).all().all()
        assert len(time.unique()) == len(time)

    def test_time_df_sorts_on_plot_multiindex(self):
        df = self.time_df.set_index(['B', 'time'])
        scrambled = df.sample(frac=1)
        plot = scrambled.hvplot(x='time')
        time = plot.data.index.get_level_values('time')
        assert plot.kdims == ['time']
        assert (time == df.index.get_level_values('time')).all()
        assert len(time.unique()) == len(time)

    def testtime_df_does_not_sort_on_plot_if_sort_date_off_multiindex(self):
        df = self.time_df.set_index(['B', 'time'])
        scrambled = df.sample(frac=1)
        plot = scrambled.hvplot(x='time', sort_date=False)
        time = plot.data.index.get_level_values('time')
        assert plot.kdims == ['time']
        assert (time == scrambled.index.get_level_values('time')).all().all()
        assert len(time.unique()) == len(time)

    def test_time_df_sorts_on_plot_using_multiindex_level0_as_x(self):
        df = self.time_df.set_index(['time', 'B'])
        scrambled = df.sample(frac=1)
        plot = scrambled.hvplot()
        time = plot.data.index.get_level_values('time')
        assert plot.kdims == ['time']
        assert (time == df.index.get_level_values('time')).all()
        assert len(time.unique()) == len(time)

    def testtime_df_does_not_sort_on_plot_if_sort_date_off_using_multiindex_level0_as_x(self):
        df = self.time_df.set_index(['time', 'B'])
        scrambled = df.sample(frac=1)
        plot = scrambled.hvplot(sort_date=False)
        time = plot.data.index.get_level_values('time')
        assert plot.kdims == ['time']
        assert (time == scrambled.index.get_level_values('time')).all().all()
        assert len(time.unique()) == len(time)

    def test_default_y_not_in_by(self):
        plot = self.cat_df.hvplot.scatter(by='x')
        assert plot.kdims == ['x']
        assert plot[1].kdims == ['index']
        assert plot[1].vdims == ['y']

    def test_groupby_from_index(self):
        hmap = self.cat_df_index.hvplot.scatter(x='x', y='y', groupby='category', dynamic=False)
        assert hmap.kdims == ['category']
        assert hmap.vdims == []
        assert list(hmap.keys()) == ['A', 'B', 'C']
        assert hmap.last.kdims == ['x']
        assert hmap.last.vdims == ['y']

    def test_multi_index_groupby_from_index(self):
        hmap = self.multii_df.hvplot.scatter(x='A', y='C', groupby='B', dynamic=False)
        assert hmap.kdims == ['B']
        assert hmap.vdims == []
        assert list(hmap.keys()) == ['a', 'b']
        assert hmap.last.kdims == ['A']
        assert hmap.last.vdims == ['C']


class TestChart1DDask(TestChart1D):
    def setUp(self):
        super().setUp()
        try:
            import dask.dataframe as dd
        except ImportError:
            raise SkipTest('Dask not available')
        import hvplot.dask  # noqa: F401

        self.df = dd.from_pandas(self.df, npartitions=2)
        self.dt_df = dd.from_pandas(self.dt_df, npartitions=3)
        self.cat_df = dd.from_pandas(self.cat_df, npartitions=3)
        self.cat_df_index = dd.from_pandas(self.cat_df_index, npartitions=3)

    def test_by_datetime_accessor(self):
        raise SkipTest("Can't expand dt accessor columns when using dask")

    def test_multi_index_groupby_from_index(self):
        raise SkipTest('Dask does not support MultiIndex Dataframes.')


@pytest.mark.usefixtures('hvplot_xarray')
class TestGridPlots(ComparisonTestCase):
    def setUp(self):
        coords = OrderedDict([('band', [1, 2, 3]), ('y', [0, 1]), ('x', [0, 1])])
        self.da_rgb = xr.DataArray(np.arange(12).reshape((3, 2, 2)), coords, ['band', 'y', 'x'])

    def test_dataarray_unnamed_label(self):
        plot = self.da_rgb.sel(band=1).hvplot.image(label='test')
        assert plot.vdims[0].name == 'test'

    def test_dataarray_unnamed_value_label(self):
        plot = self.da_rgb.sel(band=1).hvplot.image(value_label='test')
        assert plot.vdims[0].name == 'test'
