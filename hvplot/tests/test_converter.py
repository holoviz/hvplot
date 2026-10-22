"""
Tests for panel widgets and param objects as arguments
"""

from collections import OrderedDict
from unittest import SkipTest, TestCase

import holoviews as hv
import numpy as np
import pandas as pd
import panel as pn
import pytest
import xarray as xr
from holoviews import NdOverlay, Store, render
from holoviews.core.dimension import Dimension
from holoviews.element import Area, Curve, Scatter
from holoviews.element.comparison import ComparisonTestCase
from packaging.version import Version
from parameterized import parameterized

from hvplot.util import process_xarray  # noqa: F401


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


class TestPanelObjects(TestCase):
    def setUp(self):
        from bokeh.sampledata.iris import flowers

        import hvplot.pandas  # noqa: F401

        self.flowers = flowers
        self.cols = list(self.flowers.columns[:-1])

    def test_using_explicit_widgets_works(self):
        x = pn.widgets.Select(label='x', value='sepal_length', options=self.cols)
        y = pn.widgets.Select(label='y', value='sepal_width', options=self.cols)
        kind = pn.widgets.Select(label='kind', value='scatter', options=['bivariate', 'scatter'])
        by_species = pn.widgets.Checkbox(label='By species')
        color = pn.widgets.ColorPicker(value='#ff0000')

        @pn.depends(by_species.param.value, color.param.value)
        def by_species_fn(by_species, color):
            return 'species' if by_species else color

        self.flowers.hvplot(x, y=y, kind=kind.param.value, c=color)

    def test_casting_widgets_to_different_classes(self):
        pane = self.flowers.hvplot.scatter(
            groupby='species', legend='top_right', widgets={'species': pn.widgets.DiscreteSlider}
        )

        assert len(look_for_class(pane, pn.widgets.DiscreteSlider)) == 1

    def test_using_explicit_widgets_with_groupby_does_not_raise_error(self):
        x = pn.widgets.Select(label='x', value='sepal_length', options=self.cols)
        y = pn.widgets.Select(label='y', value='sepal_width', options=self.cols)

        pane = self.flowers.hvplot(x, y, groupby='species')
        assert isinstance(pane, pn.param.ParamFunction)


@pytest.fixture(scope='module')
def df():
    return pd.DataFrame(
        [[1, 2, 'A', 0.1], [3, 4, 'B', 0.2], [5, 6, 'C', 0.3]],
        columns=['x', 'y', 'category', 'number'],
    )


@pytest.mark.usefixtures('hvplot_pandas')
class TestOptions:
    def test_hvplot_defaults(self, df, backend):
        plot = df.hvplot.scatter('x', 'y', c='category')
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

    def test_holoviews_defined_default_opts(self, df, backend):
        if backend != 'bokeh':
            pytest.xfail(f'default opts not supported w/ {backend}')

        hv.opts.defaults(hv.opts.Scatter(height=400, width=900, show_grid=True))
        plot = df.hvplot.scatter('x', 'y', c='category')
        opts = Store.lookup_options(backend, plot, 'plot')
        # legend_position shouldn't apply only to bokeh
        if backend == 'bokeh':
            assert opts.kwargs['legend_position'] == 'right'
        assert opts.kwargs['show_grid'] is True
        assert opts.kwargs['height'] == 400
        assert opts.kwargs['width'] == 900

    def test_holoviews_defined_default_opts_overwritten_in_call(self, df, backend):
        if backend != 'bokeh':
            pytest.xfail(f'default opts not supported w/ {backend}')

        hv.opts.defaults(hv.opts.Scatter(height=400, width=900, show_grid=True))
        plot = df.hvplot.scatter('x', 'y', c='category', width=300, legend='left')
        opts = Store.lookup_options(backend, plot, 'plot')
        # legend_position shouldn't apply only to bokeh
        if backend == 'bokeh':
            assert opts.kwargs['legend_position'] == 'left'
        assert opts.kwargs['show_grid'] is True
        assert opts.kwargs['height'] == 400
        assert opts.kwargs['width'] == 300

    def test_holoviews_defined_default_opts_are_not_mutable(self, df, backend):
        if backend != 'bokeh':
            pytest.xfail(f'default opts not supported w/ {backend}')

        hv.opts.defaults(hv.opts.Scatter(tools=['tap']))
        plot = df.hvplot.scatter('x', 'y', c='category')
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['tools'] == ['tap', 'hover']
        default_opts = Store.options(backend=backend)['Scatter'].groups['plot'].options
        assert default_opts['tools'] == ['tap']


class TestChart2D(ComparisonTestCase):
    def setUp(self):
        import hvplot.pandas  # noqa: F401

    def test_xarray_dataset_with_attrs(self):
        try:
            import xarray as xr

            import hvplot.xarray  # noqa: F401
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
            import dask.dataframe  # noqa: F401
        except ImportError:
            raise SkipTest('Dask not available')
        import hvplot.dask  # noqa: F401


class TestChart1D(ComparisonTestCase):
    def setUp(self):
        import hvplot.pandas  # noqa: F401

        self.df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
        self.cat_df = pd.DataFrame(
            [[1, 2, 'A'], [3, 4, 'B'], [5, 6, 'C']], columns=['x', 'y', 'category']
        )
        self.cat_only_df = pd.DataFrame(
            [['A', 'a'], ['B', 'b'], ['C', 'c']], columns=['upper', 'lower']
        )
        self.time_df = pd.DataFrame(
            {
                'time': pd.date_range('1/1/2000', periods=10, tz='UTC'),
                'A': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                'B': list('abcdefghij'),
            }
        )

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

    @pytest.mark.xfail(reason='See https://github.com/holoviz/hvplot/issues/1364')
    def test_hierarchical_columns_auto_stack(self):
        arrays = [
            ['bar', 'bar', 'baz', 'baz', 'foo', 'foo', 'qux', 'qux'],
            ['one', 'two', 'one', 'two', 'one', 'two', 'one', 'two'],
        ]
        tuples = list(zip(*arrays, strict=True))
        index = pd.MultiIndex.from_tuples(tuples)
        df = pd.DataFrame(np.random.randn(3, 8), index=['A', 'B', 'C'], columns=index)
        df.hvplot.scatter()


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
        self.cat_only_df = dd.from_pandas(self.cat_only_df, npartitions=1)


@pytest.mark.usefixtures('hvplot_xarray')
class TestGridPlots(ComparisonTestCase):
    def setUp(self):
        coords = OrderedDict([('band', [1, 2, 3]), ('y', [0, 1]), ('x', [0, 1])])
        self.da_rgb = xr.DataArray(np.arange(12).reshape((3, 2, 2)), coords, ['band', 'y', 'x'])

        self.xarr_with_attrs = xr.DataArray(
            np.random.rand(10, 10),
            coords=[('x', range(10)), ('y', range(10))],
            dims=['y', 'x'],
            attrs={'long_name': 'luminosity', 'units': 'lm'},
        )
        self.xarr_with_attrs.x.attrs['long_name'] = 'Declination'
        self.xarr_with_attrs.y.attrs['long_name'] = 'Right Ascension'

        self.xds_with_attrs = xr.Dataset({'light': self.xarr_with_attrs})

    def test_line_infer_dimension_params_from_xarray_attrs(self):
        hmap = self.xarr_with_attrs.hvplot.line(groupby='x', dynamic=False)
        self.assertEqual(hmap.kdims[0].label, 'Declination')
        self.assertEqual(hmap.last.kdims[0].label, 'Right Ascension')
        self.assertEqual(hmap.last.vdims[0].label, 'luminosity')
        self.assertEqual(hmap.last.vdims[0].unit, 'lm')

    def test_img_infer_dimension_params_from_xarray_attrs(self):
        img = self.xarr_with_attrs.hvplot.image(clim=(0, 2))
        self.assertEqual(img.kdims[0].label, 'Declination')
        self.assertEqual(img.kdims[1].label, 'Right Ascension')
        self.assertEqual(img.vdims[0].label, 'luminosity')
        self.assertEqual(img.vdims[0].unit, 'lm')
        self.assertEqual(img.vdims[0].range, (0, 2))

    def test_table_infer_dimension_params_from_xarray_ds_attrs(self):
        table = self.xds_with_attrs.hvplot.dataset()
        self.assertEqual(table.kdims[0].label, 'Declination')
        self.assertEqual(table.kdims[1].label, 'Right Ascension')
        self.assertEqual(table.vdims[0].label, 'luminosity')
        self.assertEqual(table.vdims[0].unit, 'lm')

    def test_points_infer_dimension_params_from_xarray_attrs(self):
        points = self.xarr_with_attrs.hvplot.points(c='value', clim=(0, 2))
        self.assertEqual(points.kdims[0].label, 'Declination')
        self.assertEqual(points.kdims[1].label, 'Right Ascension')
        self.assertEqual(points.vdims[0].label, 'luminosity')
        self.assertEqual(points.vdims[0].unit, 'lm')
        self.assertEqual(points.vdims[0].range, (0, 2))

    def test_dataset_infer_dimension_params_from_xarray_attrs(self):
        ds = self.xarr_with_attrs.hvplot.dataset()
        self.assertEqual(ds.kdims[0].label, 'Declination')
        self.assertEqual(ds.kdims[1].label, 'Right Ascension')
        self.assertEqual(ds.vdims[0].label, 'luminosity')
        self.assertEqual(ds.vdims[0].unit, 'lm')

    def test_table_infer_dimension_params_from_xarray_attrs(self):
        table = self.xarr_with_attrs.hvplot.dataset()
        self.assertEqual(table.kdims[0].label, 'Declination')
        self.assertEqual(table.kdims[1].label, 'Right Ascension')
        self.assertEqual(table.vdims[0].label, 'luminosity')
        self.assertEqual(table.vdims[0].unit, 'lm')

    def test_dataarray_label_precedence(self):
        # name > label > value_label
        plot = self.da_rgb.sel(band=1).rename('a').hvplot.image(label='b')
        assert plot.vdims[0].name == 'a'

        plot = self.da_rgb.sel(band=1).hvplot.image(label='b', value_label='c')
        assert plot.vdims[0].name == 'b'
