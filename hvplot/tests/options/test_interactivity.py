from unittest import SkipTest

import pandas as pd
import pytest
from holoviews import Store
from holoviews.element import Area, Curve, Path, Points, Scatter
from holoviews.element.comparison import ComparisonTestCase
from parameterized import parameterized


@pytest.fixture(scope='module')
def df():
    return pd.DataFrame(
        [[1, 2, 'A', 0.1], [3, 4, 'B', 0.2], [5, 6, 'C', 0.3]],
        columns=['x', 'y', 'category', 'number'],
    )


@pytest.mark.usefixtures('hvplot_pandas')
class TestOptions:
    @pytest.mark.parametrize(
        'toolbar', ['right', 'left', 'above', 'below', None, False, True, 'disable']
    )
    def test_toolbar(self, df, backend, toolbar):
        if backend != 'bokeh':
            pytest.skip(f'toolbar not supported w/ {backend}')

        plot = df.hvplot.scatter('x', 'y', toolbar=toolbar)
        opts = Store.lookup_options(backend, plot, 'plot')
        if toolbar is True:
            toolbar = 'right'
        elif toolbar is False:
            toolbar = None
        assert opts.kwargs['toolbar'] == toolbar

    def test_autohide_toolbar(self, df, backend):
        if backend != 'bokeh':
            pytest.skip(f'autohide_toolbar not supported w/ {backend}')

        plot = df.hvplot.scatter('x', 'y', autohide_toolbar=True)
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['autohide_toolbar'] is True


class TestChart2D(ComparisonTestCase):
    def setUp(self):
        import hvplot.pandas  # noqa: F401

        self.cat_df = pd.DataFrame(
            [[1, 2, 'A'], [3, 4, 'B'], [5, 6, 'C']], columns=['x', 'y', 'category']
        )

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


class TestChart2DDask(TestChart2D):
    def setUp(self):
        super().setUp()
        try:
            import dask.dataframe as dd
        except ImportError:
            raise SkipTest('Dask not available')
        import hvplot.dask  # noqa: F401

        self.cat_df = dd.from_pandas(self.cat_df, npartitions=3)

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
        import hvplot.pandas  # noqa: F401

        self.df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
        self.cat_df = pd.DataFrame(
            [[1, 2, 'A'], [3, 4, 'B'], [5, 6, 'C']], columns=['x', 'y', 'category']
        )

    def color_series(self):
        return self.cat_df['category'].map({'A': 'red', 'B': 'blue'})

    def size_series(self):
        return self.cat_df['y'] / 10

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

    def test_color_series_excluded_from_default_hover(self):
        color_series = self.color_series()
        plot = self.cat_df.hvplot.scatter(x='x', y='y', color=color_series)

        assert '_color' in plot.data.columns
        assert '_color' in plot.vdims

        # Check hover_tooltips option
        opts = Store.lookup_options('bokeh', plot, 'plot')
        hover_tooltips = opts.kwargs.get('hover_tooltips')

        # hover_tooltips should be set and not include _color
        assert hover_tooltips is not None
        tooltip_dims = [tt[0] if isinstance(tt, tuple) else tt for tt in hover_tooltips]
        assert '_color' not in tooltip_dims
        assert 'x' in tooltip_dims
        assert 'y' in tooltip_dims

    def test_size_series_excluded_from_default_hover(self):
        size_series = self.size_series()
        plot = self.cat_df.hvplot.scatter(x='x', y='y', s=size_series)

        assert '_size' in plot.data.columns
        assert '_size' in plot.vdims

        opts = Store.lookup_options('bokeh', plot, 'plot')
        hover_tooltips = opts.kwargs.get('hover_tooltips')

        # hover_tooltips should be set and not include _size
        assert hover_tooltips is not None
        tooltip_dims = [tt[0] if isinstance(tt, tuple) else tt for tt in hover_tooltips]
        assert '_size' not in tooltip_dims
        assert 'x' in tooltip_dims
        assert 'y' in tooltip_dims

    def test_explicit_hover_tooltips_respected_with_internal_columns(self):
        color_series = self.color_series()
        expected_htt = [('x', '@x'), ('color', '@_color')]
        plot = self.cat_df.hvplot.scatter(
            x='x', y='y', color=color_series, hover_tooltips=expected_htt
        )

        # Explicit hover_tooltips should be used
        opts = Store.lookup_options('bokeh', plot, 'plot')
        hover_tooltips = opts.kwargs.get('hover_tooltips')
        assert hover_tooltips == expected_htt

    def test_color_column_name_shown_in_hover(self):
        plot = self.cat_df.hvplot.scatter(x='x', y='y', color='category')

        assert 'category' in [d.name for d in plot.vdims]
        assert '_color' not in plot.data.columns

    def test_color_with_cmap_dict_shown_in_hover(self):
        plot = self.cat_df.hvplot.scatter(
            x='x', y='y', color='category', cmap={'A': 'red', 'B': 'blue'}
        )

        assert 'category' in [d.name for d in plot.vdims]
        assert '_color' not in plot.data.columns

    def test_both_color_and_size_series_excluded_from_hover(self):
        color_series = self.color_series()
        size_series = self.size_series()
        plot = self.cat_df.hvplot.scatter(x='x', y='y', color=color_series, s=size_series)

        # Both should be in data
        assert '_color' in plot.data.columns
        assert '_size' in plot.data.columns

        opts = Store.lookup_options('bokeh', plot, 'plot')
        hover_tooltips = opts.kwargs.get('hover_tooltips')

        assert hover_tooltips is not None
        tooltip_dims = [tt[0] if isinstance(tt, tuple) else tt for tt in hover_tooltips]
        assert '_color' not in tooltip_dims
        assert '_size' not in tooltip_dims
        assert 'x' in tooltip_dims
        assert 'y' in tooltip_dims

    @parameterized.expand(['vline', 'hline'])
    def test_hover_line(self, hover_mode):
        plot = self.df.hvplot('x', 'y', hover=hover_mode)
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['hover_mode'], hover_mode)

    def test_hover_tooltips(self):
        plot = self.df.hvplot('x', 'y', hover_tooltips=['x'])
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['hover_tooltips'], ['x'])

    @pytest.mark.filterwarnings('ignore:hover_formatters')
    def test_hover_formatter(self):
        plot = self.df.hvplot('x', 'y', hover_formatters={'x': 'datetime'})
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['hover_formatters'], {'x': 'datetime'})

    @pytest.mark.filterwarnings('ignore:hover_formatters')
    def test_hover_disabled(self):
        plot = self.df.hvplot(
            'x', 'y', hover_tooltips=['x'], hover_formatters={'x': 'datetime'}, hover=False
        )
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['tools'], [])
        assert 'hover_formatters' not in opts.kwargs
        assert 'hover_tooltips' not in opts.kwargs


class TestChart1DDask(TestChart1D):
    def setUp(self):
        super().setUp()
        try:
            import dask.dataframe as dd
        except ImportError:
            raise SkipTest('Dask not available')
        import hvplot.dask  # noqa: F401

        self.df = dd.from_pandas(self.df, npartitions=2)
        self.cat_df = dd.from_pandas(self.cat_df, npartitions=3)

    def color_series(self):
        # Passing lazy series not yet supported
        return self.cat_df['category'].map({'A': 'red', 'B': 'blue'}, meta='object').compute()

    def size_series(self):
        # Passing lazy series not yet supported
        return (self.cat_df['y'] / 10).compute()
