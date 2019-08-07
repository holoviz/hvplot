from unittest import SkipTest, expectedFailure
from parameterized import parameterized

from holoviews import NdOverlay, Store
from holoviews.element import Curve, Area, Scatter, Points, Path, HeatMap
from holoviews.element.comparison import ComparisonTestCase
from hvplot import patch
from ..util import is_dask


class TestChart2D(ComparisonTestCase):
    def setUp(self):
        try:
            import pandas as pd
        except:
            raise SkipTest('Pandas not available')
        patch('pandas')
        self.df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
        self.cat_df = pd.DataFrame([[1, 2, 'A'], [3, 4, 'B'], [5, 6, 'C']],
                                   columns=['x', 'y', 'category'])

    @parameterized.expand([('points', Points), ('paths', Path)])
    def test_2d_defaults(self, kind, element):
        plot = self.df.hvplot(kind=kind)
        self.assertEqual(plot, element(self.df, ['x', 'y']))

    @parameterized.expand([('points', Points), ('paths', Path)])
    def test_2d_chart(self, kind, element):
        plot = self.df.hvplot(x='x', y='y', kind=kind)
        self.assertEqual(plot, element(self.df, ['x', 'y']))

    @parameterized.expand([('points', Points), ('paths', Path)])
    def test_2d_index_and_c(self, kind, element):
        plot = self.df.hvplot(x='index', y='y', c='x', kind=kind)
        self.assertEqual(plot, element(self.df, ['index', 'y'], ['x']))

    @parameterized.expand([('points', Points), ('paths', Path)])
    def test_2d_set_hover_cols_to_list(self, kind, element):
        plot = self.cat_df.hvplot(x='x', y='y', hover_cols=['category'], kind=kind)
        self.assertEqual(plot, element(self.cat_df, ['x', 'y'], ['category']))

    @parameterized.expand([('points', Points), ('paths', Path)])
    def test_2d_set_hover_cols_including_index(self, kind, element):
        plot = self.cat_df.hvplot(x='x', y='y', hover_cols=['index'], kind=kind)
        assert 'index' in plot.data.columns
        self.assertEqual(plot, element(self.cat_df.reset_index(), ['x', 'y'], ['index']))

    @parameterized.expand([('points', Points), ('paths', Path)])
    def test_2d_set_hover_cols_to_all(self, kind, element):
        plot = self.cat_df.hvplot(x='x', y='y', hover_cols='all', kind=kind)
        assert 'index' in plot.data.columns
        self.assertEqual(plot, element(self.cat_df.reset_index(), ['x', 'y'], ['index', 'category']))

    @parameterized.expand([('points', Points), ('paths', Path)])
    def test_2d_set_hover_cols_to_all_with_use_index_as_false(self, kind, element):
        plot = self.cat_df.hvplot(x='x', y='y', hover_cols='all', use_index=False, kind=kind)
        self.assertEqual(plot, element(self.cat_df, ['x', 'y'], ['category']))

    def test_heatmap_2d_index_columns(self):
        plot = self.df.hvplot.heatmap()
        self.assertEqual(plot, HeatMap((['x', 'y'], [0, 1, 2], self.df.values),
                                       ['columns', 'index'], 'value'))


class TestChart2DDask(TestChart2D):

    def setUp(self):
        super().setUp()
        try:
            import dask.dataframe as dd
        except:
            raise SkipTest('Dask not available')
        patch('dask')
        self.df = dd.from_pandas(self.df, npartitions=2)
        self.cat_df = dd.from_pandas(self.cat_df, npartitions=3)

    @expectedFailure
    def test_heatmap_2d_index_columns(self):
        self.df.hvplot.heatmap()


class TestChart1D(ComparisonTestCase):

    def setUp(self):
        try:
            import pandas as pd
        except:
            raise SkipTest('Pandas not available')
        patch('pandas')
        self.df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
        self.cat_df = pd.DataFrame([[1, 2, 'A'], [3, 4, 'B'], [5, 6, 'C']],
                                   columns=['x', 'y', 'category'])
        self.cat_only_df = pd.DataFrame([['A', 'a'], ['B', 'b'], ['C', 'c']],
                                        columns=['upper', 'lower'])
        self.time_df = pd.DataFrame({
            'time': pd.date_range('1/1/2000', periods=10, tz='UTC'),
            'A': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'B': 'abcdefghij'})

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_wide_chart(self, kind, element):
        plot = self.df.hvplot(kind=kind)
        obj = NdOverlay({'x': element(self.df, 'index', 'x').redim(x='value'),
                         'y': element(self.df, 'index', 'y').redim(y='value')}, 'Variable')
        self.assertEqual(plot, obj)

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_wide_chart_labels(self, kind, element):
        plot = self.df.hvplot(kind=kind, value_label='Test', group_label='Category')
        obj = NdOverlay({'x': element(self.df, 'index', 'x').redim(x='Test'),
                         'y': element(self.df, 'index', 'y').redim(y='Test')}, 'Category')
        self.assertEqual(plot, obj)

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_wide_chart_legend_position(self, kind, element):
        plot = self.df.hvplot(kind=kind, value_label='Test', group_label='Category', legend='left')
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['legend_position'], 'left')

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_tidy_chart(self, kind, element):
        plot = self.df.hvplot(x='x', y='y', kind=kind)
        self.assertEqual(plot, element(self.df, 'x', 'y'))

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_tidy_chart_index(self, kind, element):
        plot = self.df.hvplot(x='index', y='y', kind=kind)
        self.assertEqual(plot, element(self.df, 'index', 'y'))

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_tidy_chart_index_by(self, kind, element):
        plot = self.df.hvplot(x='index', y='y', by='x', kind=kind)
        obj = NdOverlay({1: element(self.df[self.df.x==1], 'index', 'y'),
                         3: element(self.df[self.df.x==3], 'index', 'y'),
                         5: element(self.df[self.df.x==5], 'index', 'y')}, 'x')
        self.assertEqual(plot, obj)

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_tidy_chart_index_by_legend_position(self, kind, element):
        plot = self.df.hvplot(x='index', y='y', by='x', kind=kind, legend='left')
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['legend_position'], 'left')

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_use_index_disabled(self, kind, element):
        with self.assertRaises(ValueError):
            self.df.hvplot(use_index=False, kind=kind)

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_tidy_chart_ranges(self, kind, element):
        plot = self.df.hvplot(x='x', y='y', kind=kind, xlim=(0, 3), ylim=(5, 10))
        opts = Store.lookup_options('bokeh', plot, 'plot').options
        self.assertEqual(opts['xlim'], (0, 3))
        self.assertEqual(opts['ylim'], (5, 10))

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_wide_chart_ranges(self, kind, element):
        plot = self.df.hvplot(kind=kind, xlim=(0, 3), ylim=(5, 10))
        opts = Store.lookup_options('bokeh', plot.last, 'plot').options
        self.assertEqual(opts['xlim'], (0, 3))
        self.assertEqual(opts['ylim'], (5, 10))

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_tidy_chart_with_hover_cols(self, kind, element):
        plot = self.cat_df.hvplot(x='x', y='y', kind=kind, hover_cols=['category'])
        self.assertEqual(plot, element(self.cat_df, 'x', ['y', 'category']))

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_tidy_chart_with_index_in_hover_cols(self, kind, element):
        plot = self.df.hvplot(x='x', y='y', kind=kind, hover_cols=['index'])
        altered_df = self.df.reset_index()
        self.assertEqual(plot, element(altered_df, 'x', ['y', 'index']))

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_tidy_chart_with_hover_cols_as_all(self, kind, element):
        plot = self.cat_df.hvplot(x='x', y='y', kind=kind, hover_cols='all')
        altered_df = self.cat_df.reset_index()
        self.assertEqual(plot, element(altered_df, 'x', ['y', 'index', 'category']))

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_tidy_chart_with_hover_cols_as_all_with_use_index_as_false(self, kind, element):
        plot = self.cat_df.hvplot(x='x', y='y', kind=kind, hover_cols='all', use_index=False)
        self.assertEqual(plot, element(self.cat_df, 'x', ['y', 'category']))

    def test_area_stacked(self):
        plot = self.df.hvplot.area(stacked=True)
        obj = NdOverlay({'x': Area(self.df, 'index', 'x').redim(x='value'),
                         'y': Area(self.df, 'index', 'y').redim(y='value')}, 'Variable')
        self.assertEqual(plot, Area.stack(obj))

    def test_scatter_color_set_to_series(self):
        if is_dask(self.df['y']):
            y = self.df['y'].compute()
        else:
            y = self.df['y']
        actual = self.df.hvplot.scatter('x', 'y', c=y)
        altered_df = self.df.assign(_color=y)
        expected = altered_df.hvplot.scatter('x', 'y', c='_color')
        self.assertEqual(actual, expected)

    def test_scatter_size_set_to_series(self):
        if is_dask(self.df['y']):
            y = self.df['y'].compute()
        else:
            y = self.df['y']
        plot = self.df.hvplot.scatter('x', 'y', s=y)
        opts = Store.lookup_options('bokeh', plot, 'style')
        assert '_size' in plot.data.columns
        self.assertEqual(opts.kwargs['size'], '_size')

    def test_scatter_color_by_legend_position(self):
        plot = self.cat_df.hvplot('x', 'y', c='category', legend='left')
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['legend_position'], 'left')

    def test_histogram_by_category_legend_position(self):
        plot = self.cat_df.hvplot.hist('y', by='category', legend='left')
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['legend_position'], 'left')

    def test_histogram_legend_position(self):
        plot = self.cat_df.hvplot.hist('y', legend='left')
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['legend_position'], 'left')

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_only_includes_num_chart(self, kind, element):
        plot = self.cat_df.hvplot(kind=kind)
        obj = NdOverlay({'x': element(self.cat_df, 'index', 'x').redim(x='value'),
                         'y': element(self.cat_df, 'index', 'y').redim(y='value'),
                        }, 'Variable')
        self.assertEqual(plot, obj)

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_includes_str_if_no_num_chart(self, kind, element):
        plot = self.cat_only_df.hvplot(kind=kind)
        obj = NdOverlay({'upper': element(self.cat_only_df, 'index', 'upper').redim(upper='value'),
                         'lower': element(self.cat_only_df, 'index', 'lower').redim(lower='value'),
                        }, 'Variable')
        self.assertEqual(plot, obj)

    def test_time_df_sorts_on_plot(self):
        scrambled = self.time_df.sample(frac=1)
        plot = scrambled.hvplot(x='time')
        assert (plot.data == self.time_df).all().all()
        assert (plot.data.time.diff()[1:].astype('int') > 0).all()

    def test_time_df_does_not_sort_on_plot_if_sort_date_off(self):
        scrambled = self.time_df.sample(frac=1)
        plot = scrambled.hvplot(x='time', sort_date=False)
        assert (plot.data == scrambled).all().all()
        assert not (plot.data.time.diff()[1:].astype('int') > 0).all()

    def test_time_df_sorts_on_plot_using_index_as_x(self):
        df = self.time_df.set_index('time')
        scrambled = df.sample(frac=1)
        plot = scrambled.hvplot()
        assert (plot.data['time'] == df.index).all()
        assert (plot.data.time.diff()[1:].astype('int') > 0).all()

    def test_time_df_does_not_sort_on_plot_if_sort_date_off_using_index_as_x(self):
        df = self.time_df.set_index('time')
        scrambled = df.sample(frac=1)
        plot = scrambled.hvplot(sort_date=False)
        assert (plot.data.time == scrambled.index).all().all()
        assert not (plot.data.time.diff()[1:].astype('int') > 0).all()


class TestChart1DDask(TestChart1D):

    def setUp(self):
        super().setUp()
        try:
            import dask.dataframe as dd
        except:
            raise SkipTest('Dask not available')
        patch('dask')
        self.df = dd.from_pandas(self.df, npartitions=2)
        self.cat_df = dd.from_pandas(self.cat_df, npartitions=3)
        self.cat_only_df = dd.from_pandas(self.cat_only_df, npartitions=1)
