from unittest import SkipTest, expectedFailure
from parameterized import parameterized

import numpy as np
import pandas as pd
import pytest

from holoviews.core.dimension import Dimension
from holoviews import NdLayout, NdOverlay, Store, dim, render
from holoviews.element import Curve, Area, Scatter, Points, Path, HeatMap
from holoviews.element.comparison import ComparisonTestCase
from packaging.version import Version

from ..util import is_dask


class TestChart2D(ComparisonTestCase):
    def setUp(self):
        import hvplot.pandas  # noqa

        self.df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
        self.cat_df = pd.DataFrame(
            [[1, 2, 'A'], [3, 4, 'B'], [5, 6, 'C']], columns=['x', 'y', 'category']
        )
        self.time_df = pd.DataFrame(
            {
                'time': pd.date_range('1/1/2000', periods=5 * 24, freq='1h', tz='UTC'),
                'temp': np.sin(np.linspace(0, 5 * 2 * np.pi, 5 * 24)).cumsum(),
            }
        )

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
        self.assertEqual(plot, element(self.cat_df, ['x', 'y'], ['index']))

    @parameterized.expand([('points', Points), ('paths', Path)])
    def test_2d_set_hover_cols_to_all(self, kind, element):
        plot = self.cat_df.hvplot(x='x', y='y', hover_cols='all', kind=kind)
        self.assertEqual(plot, element(self.cat_df, ['x', 'y'], ['index', 'category']))

    @parameterized.expand([('points', Points), ('paths', Path)])
    def test_2d_set_hover_cols_to_all_with_use_index_as_false(self, kind, element):
        plot = self.cat_df.hvplot(x='x', y='y', hover_cols='all', use_index=False, kind=kind)
        self.assertEqual(plot, element(self.cat_df, ['x', 'y'], ['category']))

    def test_heatmap_2d_index_columns(self):
        plot = self.df.hvplot.heatmap()
        self.assertEqual(
            plot, HeatMap((['x', 'y'], [0, 1, 2], self.df.values), ['columns', 'index'], 'value')
        )

    def test_heatmap_2d_derived_x_and_y(self):
        plot = self.time_df.hvplot.heatmap(x='time.hour', y='time.day', C='temp')
        assert plot.kdims == ['time.hour', 'time.day']
        assert plot.vdims == ['temp']

    def test_xarray_dataset_with_attrs(self):
        try:
            import xarray as xr
            import hvplot.xarray  # noqa
        except ImportError:
            raise SkipTest('xarray not available')

        dset = xr.Dataset(
            {'u': ('t', [1, 3]), 'v': ('t', [4, 2])},
            coords={'t': ('t', [0, 1], {'long_name': 'time', 'units': 's'})},
        )
        ndoverlay = dset.hvplot.line()

        assert render(ndoverlay, 'bokeh').xaxis.axis_label == 'time (s)'


class TestChart2DDask(TestChart2D):
    def setUp(self):
        super().setUp()
        try:
            import dask.dataframe as dd
        except ImportError:
            raise SkipTest('Dask not available')
        import hvplot.dask  # noqa

        self.df = dd.from_pandas(self.df, npartitions=2)
        self.cat_df = dd.from_pandas(self.cat_df, npartitions=3)

    @expectedFailure
    def test_heatmap_2d_index_columns(self):
        self.df.hvplot.heatmap()

    @parameterized.expand([('points', Points), ('paths', Path)])
    def test_2d_set_hover_cols_including_index(self, kind, element):
        plot = self.cat_df.hvplot(x='x', y='y', hover_cols=['index'], kind=kind)
        data = plot.data[0] if kind == 'paths' else plot.data
        assert 'index' in data.columns
        self.assertEqual(plot, element(self.cat_df.reset_index(), ['x', 'y'], ['index']))

    @parameterized.expand([('points', Points), ('paths', Path)])
    def test_2d_set_hover_cols_to_all(self, kind, element):
        plot = self.cat_df.hvplot(x='x', y='y', hover_cols='all', kind=kind)
        data = plot.data[0] if kind == 'paths' else plot.data
        assert 'index' in data.columns
        self.assertEqual(
            plot, element(self.cat_df.reset_index(), ['x', 'y'], ['index', 'category'])
        )


class TestChart1D(ComparisonTestCase):
    def setUp(self):
        import hvplot.pandas  # noqa

        self.df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
        self.df_desc = self.df.describe().transpose().sort_values('mean')
        self.dt_df = pd.DataFrame(
            np.random.rand(90), index=pd.date_range('2019-01-01', '2019-03-31')
        )
        self.cat_df = pd.DataFrame(
            [[1, 2, 'A'], [3, 4, 'B'], [5, 6, 'C']], columns=['x', 'y', 'category']
        )
        self.cat_df_index = self.cat_df.set_index('category')
        self.cat_df_index_y = self.cat_df.set_index('y')
        self.cat_only_df = pd.DataFrame(
            [['A', 'a'], ['B', 'b'], ['C', 'c']], columns=['upper', 'lower']
        )
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
        self.edge_df = pd.DataFrame(
            {
                'Latitude': [-34.58, -15.78, -33.45],
                'Longitude': [-58.66, -47.91, -70.66],
                'Volume {m3}': ['1', '2', '3'],
            }
        )
        self.df_hist = pd.DataFrame({'z': [1, 1, 4, 4]})

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_wide_chart(self, kind, element):
        plot = self.df.hvplot(kind=kind)
        obj = NdOverlay(
            {
                'x': element(self.df, 'index', Dimension('x', label='value')),
                'y': element(self.df, 'index', Dimension('y', label='value')),
            },
            'Variable',
        )
        self.assertEqual(plot, obj)

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
    def test_wide_chart_legend_position(self, kind, element):
        plot = self.df.hvplot(kind=kind, value_label='Test', group_label='Category', legend='left')
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['legend_position'], 'left')

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_wide_chart_auto_group_label(self, kind, element):
        self.df.columns.name = 'My Name'
        self.assertEqual(self.df.hvplot().kdims, ['My Name'])

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
        import dask

        plot = self.df.hvplot(x='index', y='y', by='x', kind=kind)
        # The new dask dataframe implementation that replace the old one
        # in 2025.1.0 doesn't guarantee the data order on `.unique()` calls
        # made internally by HoloViews when running a groupby operation.
        if Version(dask.__version__).release >= (2025, 1, 0):
            keys = list(plot.keys())
        else:
            keys = [1, 3, 5]
        obj = NdOverlay(
            {k: element(self.df[self.df.x == k], 'index', 'y') for k in keys},
            'x',
            sort=False,
        )
        self.assertEqual(plot, obj)

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_tidy_chart_index_by_legend_position(self, kind, element):
        plot = self.df.hvplot(x='index', y='y', by='x', kind=kind, legend='left')
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['legend_position'], 'left')

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_use_index_disabled_uses_first_cols(self, kind, element):
        plot = self.df.hvplot(use_index=False, kind=kind)
        self.assertEqual(plot.kdims, ['x'])
        self.assertEqual(plot.vdims, ['y'])

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
        obj = NdOverlay(
            {
                'x': Area(self.df, 'index', Dimension('x', label='value')),
                'y': Area(self.df, 'index', Dimension('y', label='value')),
            },
            'Variable',
        )
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
        plot = self.cat_df.hvplot.scatter('x', 'y', c='category', legend='left')
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['legend_position'], 'left')

    def test_histogram_by_category_legend_position(self):
        plot = self.cat_df.hvplot.hist('y', by='category', legend='left')
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['legend_position'], 'left')

    def test_histogram_wide_set_group_label(self):
        plot = self.df.hvplot.hist(group_label='Test')
        assert plot.kdims[0].name == 'Test'

    def test_histogram_subplots_no_shared_axes(self):
        plots = self.df.hvplot.hist(subplots=True, shared_axes=False)
        plot_0 = plots.grid_items()[0, 0][1]
        plot_1 = plots.grid_items()[0, 1][1]
        assert plot_0.opts['axiswise']
        assert plot_0.range('x') == (1, 5)
        assert plot_1.range('y') == (2, 6)

    def test_histogram_subplots_shared_axes(self):
        plots = self.df.hvplot.hist(subplots=True, shared_axes=True)
        plot_0 = plots.grid_items()[0, 0][1]
        plot_1 = plots.grid_items()[0, 1][1]
        assert not plot_0.opts['axiswise']
        assert plot_0.range('x') == (1, 6)
        assert plot_1.range('y') == (1, 6)

    def test_histogram_log_bins(self):
        df = pd.DataFrame({'z': [1, 1, 4, 4]})
        plot_logx = df.hvplot.hist(bins=2, logx=True)
        plot_loglog = df.hvplot.hist(bins=2, loglog=True)
        np.testing.assert_array_equal(plot_logx.data['z'], np.array([1.0, 2.0, 4.0]))
        np.testing.assert_array_equal(plot_loglog.data['z'], np.array([1.0, 2.0, 4.0]))

    def test_scatter_color_internally_set_to_dim(self):
        altered_df = self.cat_df.copy().rename(columns={'category': 'red'})
        plot = altered_df.hvplot.scatter('x', 'y', c='red')
        opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertIsInstance(opts.kwargs['color'], dim)
        self.assertEqual(opts.kwargs['color'].dimension.name, 'red')

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_only_includes_num_chart(self, kind, element):
        plot = self.cat_df.hvplot(kind=kind)
        obj = NdOverlay(
            {
                'x': element(self.cat_df, 'index', Dimension('x', label='value')),
                'y': element(self.cat_df, 'index', Dimension('y', label='value')),
            },
            'Variable',
        )
        self.assertEqual(plot, obj)

    @parameterized.expand([('line', Curve), ('area', Area), ('scatter', Scatter)])
    def test_includes_str_if_no_num_chart(self, kind, element):
        plot = self.cat_only_df.hvplot(kind=kind)
        obj = NdOverlay(
            {
                'upper': element(self.cat_only_df, 'index', Dimension('upper', label='value')),
                'lower': element(self.cat_only_df, 'index', Dimension('lower', label='value')),
            },
            'Variable',
            sort=False,
        )
        self.assertEqual(plot, obj)

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

    def test_time_df_with_groupby_as_derived_datetime(self):
        plot = self.time_df.hvplot(groupby='time.dayofweek', dynamic=False)
        assert list(plot.keys()) == [0, 1, 2, 3, 4, 5, 6]
        assert list(plot.dimensions()) == ['time.dayofweek', 'index', 'A']

    def test_time_df_with_by_as_derived_datetime(self):
        plot = self.time_df.hvplot(by='time.month', dynamic=False)
        assert list(plot.keys()) == [1]
        assert list(plot.dimensions()) == ['time.month', 'index', 'A']

    def test_time_df_with_x_as_derived_datetime(self):
        plot = self.time_df.hvplot.scatter(x='time.day', dynamic=False)
        assert list(plot.dimensions()) == ['time.day', 'A']

    def test_time_df_as_index_with_x_as_derived_datetime_using_name(self):
        indexed = self.time_df.set_index('time')
        plot = indexed.hvplot.scatter(x='time.day', dynamic=False)
        assert list(plot.dimensions()) == ['time.day', 'A']

    def test_time_df_as_index_with_x_as_derived_datetime_using_index(self):
        indexed = self.time_df.set_index('time')
        plot = indexed.hvplot.scatter(x='index.day', dynamic=False)
        assert list(plot.dimensions()) == ['index.day', 'A']

    def test_default_y_not_in_by(self):
        plot = self.cat_df.hvplot.scatter(by='x')
        assert plot.kdims == ['x']
        assert plot[1].kdims == ['index']
        assert plot[1].vdims == ['y']

    def test_errorbars_no_hover(self):
        plot = self.df_desc.hvplot.errorbars(y='mean', yerr1='std')
        assert list(plot.dimensions()) == ['index', 'mean', 'std']
        bkplot = Store.renderers['bokeh'].get_plot(plot)
        assert not bkplot.tools

    @parameterized.expand(['vline', 'hline'])
    def test_hover_line(self, hover_mode):
        plot = self.df.hvplot('x', 'y', hover=hover_mode)
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['hover_mode'], hover_mode)

    def test_hover_tooltips(self):
        plot = self.df.hvplot('x', 'y', hover_tooltips=['x'])
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['hover_tooltips'], ['x'])

    def test_hover_formatter(self):
        plot = self.df.hvplot('x', 'y', hover_formatters={'x': 'datetime'})
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['hover_formatters'], {'x': 'datetime'})

    def test_hover_disabled(self):
        plot = self.df.hvplot(
            'x', 'y', hover_tooltips=['x'], hover_formatters={'x': 'datetime'}, hover=False
        )
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['tools'], [])
        assert 'hover_formatters' not in opts.kwargs
        assert 'hover_tooltips' not in opts.kwargs

    def test_labels_format(self):
        plot = self.df.hvplot('x', 'y', text='({x}, {y})', kind='labels')
        assert list(plot.dimensions()) == [Dimension('x'), Dimension('y'), Dimension('label')]
        assert list(plot.data['label']) == ['(1, 2)', '(3, 4)', '(5, 6)']
        assert 'label' not in self.df

    def test_labels_no_format_edge_case(self):
        plot = self.edge_df.hvplot.labels('Longitude', 'Latitude')
        assert list(plot.dimensions()) == [
            Dimension('Longitude'),
            Dimension('Latitude'),
            Dimension('Volume {m3}'),
        ]
        assert list(plot.data['Volume {m3}']) == ['1', '2', '3']

    def test_labels_format_float(self):
        plot = self.edge_df.hvplot.labels(
            'Longitude', 'Latitude', text='{Longitude:.1f}E {Latitude:.2f}N'
        )
        assert list(plot.dimensions()) == [
            Dimension('Longitude'),
            Dimension('Latitude'),
            Dimension('label'),
        ]
        assert list(plot.data['label']) == ['-58.7E -34.58N', '-47.9E -15.78N', '-70.7E -33.45N']

    def test_labels_by(self):
        plot = self.edge_df.hvplot.labels(
            'Longitude', 'Latitude', text='{Longitude:.1f}E {Latitude:.2f}N', by='Volume {m3}'
        )
        assert isinstance(plot, NdOverlay)

    def test_labels_by_subplots(self):
        plot = self.edge_df.hvplot.labels(
            'Longitude',
            'Latitude',
            text='{Longitude:.1f}E {Latitude:.2f}N',
            by='Volume {m3}',
            subplots=True,
        )
        assert isinstance(plot, NdLayout)

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

    @pytest.mark.xfail(reason='See https://github.com/holoviz/hvplot/issues/1364')
    def test_hierarchical_columns_auto_stack(self):
        arrays = [
            ['bar', 'bar', 'baz', 'baz', 'foo', 'foo', 'qux', 'qux'],
            ['one', 'two', 'one', 'two', 'one', 'two', 'one', 'two'],
        ]
        tuples = list(zip(*arrays))
        index = pd.MultiIndex.from_tuples(tuples)
        df = pd.DataFrame(np.random.randn(3, 8), index=['A', 'B', 'C'], columns=index)
        df.hvplot.scatter()

    def test_bar_y_from_index_with_by(self):
        # Testing a somewhat silly plot but that seemed to be supported
        # https://github.com/holoviz/hvplot/blob/6c96c7e9abcd44380d2122e3d86827dedab32dea/hvplot/converter.py#L1996-L1999
        plot = self.cat_df_index_y.hvplot.bar(x='x', y='y', by='category')
        assert plot.kdims == ['x', 'category']
        assert plot.vdims == ['y']

    def test_table_datetime_index_displayed(self):
        table = self.dt_df.hvplot.table()
        assert table.kdims[0] == 'index'

    def test_table_multi_index_displayed(self):
        table = self.multii_df.hvplot.table()
        assert table.kdims[:2] == self.multii_df.index.names


class TestChart1DDask(TestChart1D):
    def setUp(self):
        super().setUp()
        try:
            import dask.dataframe as dd
        except ImportError:
            raise SkipTest('Dask not available')
        import hvplot.dask  # noqa

        self.df = dd.from_pandas(self.df, npartitions=2)
        self.dt_df = dd.from_pandas(self.dt_df, npartitions=3)
        self.cat_df = dd.from_pandas(self.cat_df, npartitions=3)
        self.cat_df_index = dd.from_pandas(self.cat_df_index, npartitions=3)
        self.cat_df_index_y = dd.from_pandas(self.cat_df_index_y, npartitions=3)
        self.cat_only_df = dd.from_pandas(self.cat_only_df, npartitions=1)
        self.df_hist = dd.from_pandas(self.df_hist, npartitions=1)

    def test_by_datetime_accessor(self):
        raise SkipTest("Can't expand dt accessor columns when using dask")

    def test_multi_index_groupby_from_index(self):
        raise SkipTest('Dask does not support MultiIndex Dataframes.')

    def test_table_datetime_index_displayed(self):
        raise SkipTest('Only supported for Pandas DatetimeIndex.')

    def test_table_multi_index_displayed(self):
        raise SkipTest('Dask does not support MultiIndex Dataframes.')


def test_cmap_LinearSegmentedColormap():
    # test for https://github.com/holoviz/hvplot/pull/1461
    xr = pytest.importorskip('xarray')
    mpl = pytest.importorskip('matplotlib')
    import hvplot.xarray  # noqa

    data = np.arange(25).reshape(5, 5)
    xr_da = xr.DataArray(data)
    xr_da.hvplot.image(cmap=mpl.colormaps['viridis'])
