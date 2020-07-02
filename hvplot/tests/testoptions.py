from unittest import SkipTest, expectedFailure

from parameterized import parameterized

from holoviews import Store
from holoviews.core.options import Options, OptionTree
from holoviews.element.comparison import ComparisonTestCase
import holoviews as hv


class TestOptions(ComparisonTestCase):

    def setUp(self):
        try:
            import pandas as pd
        except:
            raise SkipTest('Pandas not available')
        self.backend = 'bokeh'
        hv.extension(self.backend)
        Store.current_backend = self.backend
        self.store_copy = OptionTree(sorted(Store.options().items()),
                                     groups=Options._option_groups)
        import hvplot.pandas   # noqa
        self.df = pd.DataFrame([[1, 2, 'A', 0.1], [3, 4, 'B', 0.2], [5, 6, 'C', 0.3]],
                               columns=['x', 'y', 'category', 'number'])
        self.symmetric_df = pd.DataFrame([[1, 2, -1], [3, 4, 0], [5, 6, 1]],
                                          columns=['x', 'y', 'number'])

    def tearDown(self):
        Store.options(val=self.store_copy)
        Store._custom_options = {k:{} for k in Store._custom_options.keys()}
        super(TestOptions, self).tearDown()

    def test_scatter_legend_position(self):
        plot = self.df.hvplot.scatter('x', 'y', c='category', legend='left')
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['legend_position'], 'left')

    def test_histogram_by_category_legend_position(self):
        plot = self.df.hvplot.hist('y', by='category', legend='left')
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['legend_position'], 'left')

    @parameterized.expand(['scatter', 'points'])
    def test_logz(self, kind):
        plot = self.df.hvplot('x', 'y', c='x', logz=True, kind=kind)
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['logz'], True)

    @parameterized.expand(['scatter', 'points'])
    def test_color_dim(self, kind):
        plot = self.df.hvplot('x', 'y', c='number', kind=kind)
        opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(opts.kwargs['color'], 'number')
        self.assertIn('number', plot.vdims)

    @parameterized.expand(['scatter', 'points'])
    def test_size_dim(self, kind):
        plot = self.df.hvplot('x', 'y', s='number', kind=kind)
        opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(opts.kwargs['size'], 'number')
        self.assertIn('number', plot.vdims)

    @parameterized.expand(['scatter', 'points'])
    def test_alpha_dim(self, kind):
        plot = self.df.hvplot('x', 'y', alpha='number', kind=kind)
        opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(opts.kwargs['alpha'], 'number')
        self.assertIn('number', plot.vdims)

    @parameterized.expand(['scatter', 'points'])
    def test_marker_dim(self, kind):
        plot = self.df.hvplot('x', 'y', marker='category', kind=kind)
        opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(opts.kwargs['marker'], 'category')
        self.assertIn('category', plot.vdims)

    @parameterized.expand(['scatter', 'points'])
    def test_color_dim_overlay(self, kind):
        plot = self.df.hvplot('x', 'y', c='number', by='category', kind=kind)
        opts = Store.lookup_options('bokeh', plot.last, 'style')
        self.assertEqual(opts.kwargs['color'], 'number')
        self.assertIn('number', plot.last.vdims)

    @parameterized.expand(['scatter', 'points'])
    def test_size_dim_overlay(self, kind):
        plot = self.df.hvplot('x', 'y', s='number', by='category', kind=kind)
        opts = Store.lookup_options('bokeh', plot.last, 'style')
        self.assertEqual(opts.kwargs['size'], 'number')
        self.assertIn('number', plot.last.vdims)

    @parameterized.expand(['scatter', 'points'])
    def test_alpha_dim_overlay(self, kind):
        plot = self.df.hvplot('x', 'y', alpha='number', by='category', kind=kind)
        opts = Store.lookup_options('bokeh', plot.last, 'style')
        self.assertEqual(opts.kwargs['alpha'], 'number')
        self.assertIn('number', plot.last.vdims)

    def test_hvplot_defaults(self):
        plot = self.df.hvplot.scatter('x', 'y', c='category')
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['show_legend'], True)
        self.assertEqual(opts.kwargs['legend_position'], 'right')
        self.assertEqual(opts.kwargs['show_grid'], False)
        self.assertEqual(opts.kwargs['responsive'], False)
        self.assertEqual(opts.kwargs['shared_axes'], True)
        self.assertEqual(opts.kwargs['height'], 300)
        self.assertEqual(opts.kwargs['width'], 700)
        self.assertEqual(opts.kwargs['logx'], False)
        self.assertEqual(opts.kwargs['logy'], False)
        self.assertEqual(opts.kwargs.get('logz'), None)

    def test_holoviews_defined_default_opts(self):
        hv.opts.defaults(hv.opts.Scatter( height=400, width=900 ,show_grid=True))
        plot = self.df.hvplot.scatter('x', 'y', c='category')
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['legend_position'], 'right')
        self.assertEqual(opts.kwargs['show_grid'], True)
        self.assertEqual(opts.kwargs['height'], 400)
        self.assertEqual(opts.kwargs['width'], 900)

    def test_holoviews_defined_default_opts_overwritten_in_call(self):
        hv.opts.defaults(hv.opts.Scatter(height=400, width=900, show_grid=True))
        plot = self.df.hvplot.scatter('x', 'y', c='category', width=300, legend='left')
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['legend_position'], 'left')
        self.assertEqual(opts.kwargs['show_grid'], True)
        self.assertEqual(opts.kwargs['height'], 400)
        self.assertEqual(opts.kwargs['width'], 300)

    def test_holoviews_defined_default_opts_are_not_mutable(self):
        hv.opts.defaults(hv.opts.Scatter(tools=['tap']))
        plot = self.df.hvplot.scatter('x', 'y', c='category')
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['tools'], ['tap', 'hover'])
        default_opts = Store.options(backend='bokeh')['Scatter'].groups['plot'].options
        self.assertEqual(default_opts['tools'], ['tap'])

    def test_axis_set_to_visible_by_default(self):
        plot = self.df.hvplot.scatter('x', 'y', c='category')
        opts = Store.lookup_options('bokeh', plot, 'plot')
        assert 'xaxis' not in opts.kwargs
        assert 'yaxis' not in opts.kwargs

    def test_axis_set_to_none(self):
        plot = self.df.hvplot.scatter('x', 'y', c='category', xaxis=None, yaxis=None)
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['xaxis'], None)
        self.assertEqual(opts.kwargs['yaxis'], None)

    def test_axis_set_to_false(self):
        plot = self.df.hvplot.scatter('x', 'y', c='category', xaxis=False, yaxis=False)
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['xaxis'], None)
        self.assertEqual(opts.kwargs['yaxis'], None)

    def test_axis_set_to_none_in_holoviews_opts_default(self):
        hv.opts.defaults(hv.opts.Scatter(xaxis=None, yaxis=None))
        plot = self.df.hvplot.scatter('x', 'y', c='category')
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['xaxis'], None)
        self.assertEqual(opts.kwargs['yaxis'], None)

    @expectedFailure
    def test_axis_set_to_none_in_holoviews_opts_default_overwrite_in_call(self):
        hv.opts.defaults(hv.opts.Scatter(xaxis=None, yaxis=None))
        plot = self.df.hvplot.scatter('x', 'y', c='category', xaxis=True, yaxis=True)
        opts = Store.lookup_options('bokeh', plot, 'plot')
        assert 'xaxis' not in opts.kwargs
        assert 'yaxis' not in opts.kwargs

    def test_loglog_opts(self):
        plot = self.df.hvplot.scatter('x', 'y', c='category', loglog=True)
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['logx'], True)
        self.assertEqual(opts.kwargs['logy'], True)
        self.assertEqual(opts.kwargs.get('logz'), None)

    def test_logy_opts(self):
        plot = self.df.hvplot.scatter('x', 'y', c='category', logy=True)
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['logx'], False)
        self.assertEqual(opts.kwargs['logy'], True)
        self.assertEqual(opts.kwargs.get('logz'), None)

    def test_holoviews_defined_default_opts_logx(self):
        hv.opts.defaults(hv.opts.Scatter(logx=True))
        plot = self.df.hvplot.scatter('x', 'y', c='category')
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['logx'], True)
        self.assertEqual(opts.kwargs['logy'], False)
        self.assertEqual(opts.kwargs.get('logz'), None)

    def test_holoviews_defined_default_opts_logx_overwritten_in_call(self):
        hv.opts.defaults(hv.opts.Scatter(logx=True))
        plot = self.df.hvplot.scatter('x', 'y', c='category', logx=False)
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['logx'], False)
        self.assertEqual(opts.kwargs['logy'], False)
        self.assertEqual(opts.kwargs.get('logz'), None)

    def test_hvplot_default_cat_cmap_opts(self):
        import colorcet as cc
        plot = self.df.hvplot.scatter('x', 'y', c='category')
        opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(opts.kwargs['cmap'], cc.palette['glasbey_category10'])

    def test_hvplot_default_num_cmap_opts(self):
        plot = self.df.hvplot.scatter('x', 'y', c='number')
        opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(opts.kwargs['cmap'], 'kbc_r')

    def test_cmap_opts_by_type(self):
        plot = self.df.hvplot.scatter('x', 'y', c='number', cmap='diverging')
        opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(opts.kwargs['cmap'], 'coolwarm')

    def test_cmap_opts_by_name(self):
        plot = self.df.hvplot.scatter('x', 'y', c='number', cmap='fire')
        opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(opts.kwargs['cmap'], 'fire')

    def test_colormap_opts_by_name(self):
        plot = self.df.hvplot.scatter('x', 'y', c='number', colormap='fire')
        opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(opts.kwargs['cmap'], 'fire')

    def test_cmap_opts_as_a_list(self):
        plot = self.df.hvplot.scatter('x', 'y', c='number', cmap=['red', 'blue', 'green'])
        opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(opts.kwargs['cmap'], ['red', 'blue', 'green'])

    @parameterized.expand([('aspect',), ('data_aspect',)])
    def test_aspect(self, opt):
        plot = self.df.hvplot(x='x', y='y', **{opt: 2})
        opts = Store.lookup_options('bokeh', plot, 'plot').kwargs
        self.assertEqual(opts[opt], 2)
        self.assertEqual(opts.get('width'), None)
        self.assertEqual(opts.get('height'), None)

    @parameterized.expand([('aspect',), ('data_aspect',)])
    def test_aspect_and_width(self, opt):
        plot = self.df.hvplot(x='x', y='y', width=150, **{opt: 2})
        opts = hv.Store.lookup_options('bokeh', plot, 'plot').kwargs
        self.assertEqual(opts[opt], 2)
        self.assertEqual(opts.get('width'), 150)
        self.assertEqual(opts.get('height'), None)

    def test_symmetric_dataframe(self):
        import pandas as pd
        df = pd.DataFrame([[1, 2, -1], [3, 4, 0], [5, 6, 1]],
                          columns=['x', 'y', 'number'])
        plot = df.hvplot.scatter('x', 'y', c='number')
        plot_opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(plot_opts.kwargs['symmetric'], True)
        style_opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(style_opts.kwargs['cmap'], 'coolwarm')

    def test_symmetric_is_deduced_dataframe(self):
        plot = self.symmetric_df.hvplot.scatter('x', 'y', c='number')
        plot_opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(plot_opts.kwargs['symmetric'], True)
        style_opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(style_opts.kwargs['cmap'], 'coolwarm')

    def test_symmetric_from_opts(self):
        plot = self.df.hvplot.scatter('x', 'y', c='number', symmetric=True)
        plot_opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(plot_opts.kwargs['symmetric'], True)
        style_opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(style_opts.kwargs['cmap'], 'coolwarm')

    def test_symmetric_from_opts_does_not_deduce(self):
        plot = self.symmetric_df.hvplot.scatter('x', 'y', c='number', symmetric=False)
        plot_opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(plot_opts.kwargs['symmetric'], False)
        style_opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(style_opts.kwargs['cmap'], 'kbc_r')

    def test_if_clim_is_set_symmetric_is_not_deduced(self):
        plot = self.symmetric_df.hvplot.scatter('x', 'y', c='number', clim=(-1,1))
        plot_opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(plot_opts.kwargs.get('symmetric'), None)
        style_opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(style_opts.kwargs['cmap'], 'kbc_r')

    def test_bivariate_opts(self):
        plot = self.df.hvplot.bivariate('x', 'y', bandwidth=0.2, cut=1, levels=5, filled=True)
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['bandwidth'], 0.2)
        self.assertEqual(opts.kwargs['cut'], 1)
        self.assertEqual(opts.kwargs['levels'], 5)
        self.assertEqual(opts.kwargs['filled'], True)

    def test_kde_opts(self):
        plot = self.df.hvplot.kde('x', bandwidth=0.2, cut=1, filled=True)
        opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(opts.kwargs['bandwidth'], 0.2)
        self.assertEqual(opts.kwargs['cut'], 1)
        self.assertEqual(opts.kwargs['filled'], True)
