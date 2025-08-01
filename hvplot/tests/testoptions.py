import hvplot
import holoviews as hv
import numpy as np
import pandas as pd
import pytest
import xarray as xr

from holoviews import Store
from holoviews.core.options import Options, OptionTree


@pytest.fixture(scope='class')
def load_pandas_accessor():
    import hvplot.pandas  # noqa


@pytest.fixture(scope='class')
def load_xarray_accessor():
    import hvplot.xarray  # noqa


@pytest.fixture(params=['bokeh', 'matplotlib', 'plotly'], scope='class')
def backend(request):
    backend = request.param
    backend_copy = Store.current_backend
    if backend not in Store.registry:
        hvplot.extension(backend, compatibility='bokeh')
    Store.set_current_backend(backend)
    store_copy = OptionTree(sorted(Store.options().items()), groups=Options._option_groups)
    yield backend
    Store.options(val=store_copy)
    Store._custom_options = {k: {} for k in Store._custom_options.keys()}
    Store.set_current_backend(backend_copy)


@pytest.fixture(scope='module')
def df():
    return pd.DataFrame(
        [[1, 2, 'A', 0.1], [3, 4, 'B', 0.2], [5, 6, 'C', 0.3]],
        columns=['x', 'y', 'category', 'number'],
    )


@pytest.fixture(scope='module')
def symmetric_df():
    return pd.DataFrame([[1, 2, -1], [3, 4, 0], [5, 6, 1]], columns=['x', 'y', 'number'])


@pytest.mark.usefixtures('load_pandas_accessor')
class TestOptions:
    @pytest.mark.parametrize(
        'backend',
        [
            'bokeh',
            pytest.param(
                'matplotlib',
                marks=pytest.mark.xfail(
                    reason='legend_position not supported w/ matplotlib for scatter'
                ),
            ),
            pytest.param(
                'plotly',
                marks=pytest.mark.xfail(
                    reason='legend_position not supported w/ plotly for scatter'
                ),
            ),
        ],
        indirect=True,
    )
    def test_scatter_legend_position(self, df, backend):
        plot = df.hvplot.scatter('x', 'y', c='category', legend='left')
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['legend_position'] == 'left'

    @pytest.mark.parametrize(
        'backend',
        [
            'bokeh',
            'matplotlib',
            pytest.param(
                'plotly',
                marks=pytest.mark.xfail(reason='legend_position not supported w/ plotly for hist'),
            ),
        ],
        indirect=True,
    )
    def test_histogram_by_category_legend_position(self, df, backend):
        plot = df.hvplot.hist('y', by='category', legend='left')
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['legend_position'] == 'left'

    @pytest.mark.parametrize('kind', ['scatter', 'points'])
    def test_logz(self, df, kind, backend):
        plot = df.hvplot('x', 'y', c='x', logz=True, kind=kind)
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['logz'] is True

    @pytest.mark.parametrize('kind', ['scatter', 'points'])
    def test_color_dim(self, df, kind, backend):
        plot = df.hvplot('x', 'y', c='number', kind=kind)
        opts = Store.lookup_options(backend, plot, 'style')
        assert opts.kwargs['color'] == 'number'
        assert 'number' in plot.vdims

    @pytest.mark.parametrize('kind', ['scatter', 'points'])
    def test_size_dim(self, df, kind, backend):
        plot = df.hvplot('x', 'y', s='number', kind=kind)
        opts = Store.lookup_options(backend, plot, 'style')
        if backend in ['bokeh', 'plotly']:
            param = 'size'
        elif backend == 'matplotlib':
            param = 's'
        assert opts.kwargs[param] == 'number'
        assert 'number' in plot.vdims

    @pytest.mark.parametrize(
        'backend',
        [
            'bokeh',
            pytest.param(
                'matplotlib',
                marks=pytest.mark.xfail(reason='cannot map a dim to alpha w/ matplotlib'),
            ),
            pytest.param(
                'plotly', marks=pytest.mark.xfail(reason='cannot map a dim to alpha w/ plotly')
            ),
        ],
        indirect=True,
    )
    @pytest.mark.parametrize('kind', ['scatter', 'points'])
    def test_alpha_dim(self, df, kind, backend):
        plot = df.hvplot('x', 'y', alpha='number', kind=kind)
        opts = Store.lookup_options(backend, plot, 'style')
        assert opts.kwargs['alpha'] == 'number'
        assert 'number' in plot.vdims
        # Special matplotlib code to trigger an error that happens on render
        if backend == 'matplotlib':
            mpl_renderer = hv.Store.renderers['matplotlib']
            mpl_renderer.get_plot(plot)

    @pytest.mark.parametrize('kind', ['scatter', 'points'])
    def test_marker_dim(self, df, kind, backend):
        plot = df.hvplot('x', 'y', marker='category', kind=kind)
        opts = Store.lookup_options(backend, plot, 'style')
        assert opts.kwargs['marker'] == 'category'
        assert 'category' in plot.vdims

    @pytest.mark.parametrize('kind', ['scatter', 'points'])
    def test_color_dim_overlay(self, df, kind, backend):
        plot = df.hvplot('x', 'y', c='number', by='category', kind=kind)
        opts = Store.lookup_options(backend, plot.last, 'style')
        assert opts.kwargs['color'] == 'number'
        assert 'number' in plot.last.vdims

    @pytest.mark.parametrize('kind', ['scatter', 'points'])
    def test_size_dim_overlay(self, df, kind, backend):
        plot = df.hvplot('x', 'y', s='number', by='category', kind=kind)
        opts = Store.lookup_options(backend, plot.last, 'style')
        if backend in ['bokeh', 'plotly']:
            param = 'size'
        elif backend == 'matplotlib':
            param = 's'
        assert opts.kwargs[param] == 'number'
        assert 'number' in plot.last.vdims

    @pytest.mark.parametrize(
        'backend',
        [
            'bokeh',
            'matplotlib',
            pytest.param(
                'plotly', marks=pytest.mark.xfail(reason='cannot map a dim to alpha w/ plotly')
            ),
        ],
        indirect=True,
    )
    @pytest.mark.parametrize('kind', ['scatter', 'points'])
    def test_alpha_dim_overlay(self, df, kind, backend):
        plot = df.hvplot('x', 'y', alpha='number', by='category', kind=kind)
        opts = Store.lookup_options(backend, plot.last, 'style')
        assert opts.kwargs['alpha'] == 'number'
        assert 'number' in plot.last.vdims

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

    @pytest.mark.parametrize(
        'backend',
        [
            'bokeh',
            pytest.param(
                'matplotlib',
                marks=pytest.mark.xfail(reason='default opts not supported w/ matplotlib'),
            ),
            pytest.param(
                'plotly', marks=pytest.mark.xfail(reason='default opts not supported w/ plotly')
            ),
        ],
        indirect=True,
    )
    def test_holoviews_defined_default_opts(self, df, backend):
        hv.opts.defaults(hv.opts.Scatter(height=400, width=900, show_grid=True))
        plot = df.hvplot.scatter('x', 'y', c='category')
        opts = Store.lookup_options(backend, plot, 'plot')
        # legend_position shouldn't apply only to bokeh
        if backend == 'bokeh':
            assert opts.kwargs['legend_position'] == 'right'
        assert opts.kwargs['show_grid'] is True
        assert opts.kwargs['height'] == 400
        assert opts.kwargs['width'] == 900

    @pytest.mark.parametrize(
        'backend',
        [
            'bokeh',
            pytest.param(
                'matplotlib',
                marks=pytest.mark.xfail(reason='default opts not supported w/ matplotlib'),
            ),
            pytest.param(
                'plotly', marks=pytest.mark.xfail(reason='default opts not supported w/ plotly')
            ),
        ],
        indirect=True,
    )
    def test_holoviews_defined_default_opts_overwritten_in_call(self, df, backend):
        hv.opts.defaults(hv.opts.Scatter(height=400, width=900, show_grid=True))
        plot = df.hvplot.scatter('x', 'y', c='category', width=300, legend='left')
        opts = Store.lookup_options(backend, plot, 'plot')
        # legend_position shouldn't apply only to bokeh
        if backend == 'bokeh':
            assert opts.kwargs['legend_position'] == 'left'
        assert opts.kwargs['show_grid'] is True
        assert opts.kwargs['height'] == 400
        assert opts.kwargs['width'] == 300

    @pytest.mark.parametrize(
        'backend',
        [
            'bokeh',
            pytest.param(
                'matplotlib',
                marks=pytest.mark.xfail(
                    reason='default opts not supported not supported w/ matplotlib'
                ),
            ),
            pytest.param(
                'plotly',
                marks=pytest.mark.xfail(
                    reason='default opts not supported not supported w/ plotly'
                ),
            ),
        ],
        indirect=True,
    )
    def test_holoviews_defined_default_opts_are_not_mutable(self, df, backend):
        hv.opts.defaults(hv.opts.Scatter(tools=['tap']))
        plot = df.hvplot.scatter('x', 'y', c='category')
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['tools'] == ['tap', 'hover']
        default_opts = Store.options(backend=backend)['Scatter'].groups['plot'].options
        assert default_opts['tools'] == ['tap']

    def test_axis_set_to_visible_by_default(self, df, backend):
        plot = df.hvplot.scatter('x', 'y', c='category')
        opts = Store.lookup_options(backend, plot, 'plot')
        assert 'xaxis' not in opts.kwargs
        assert 'yaxis' not in opts.kwargs

    def test_axis_set_to_none(self, df, backend):
        plot = df.hvplot.scatter('x', 'y', c='category', xaxis=None, yaxis=None)
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['xaxis'] is None
        assert opts.kwargs['yaxis'] is None

    def test_axis_set_to_false(self, df, backend):
        plot = df.hvplot.scatter('x', 'y', c='category', xaxis=False, yaxis=False)
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['xaxis'] is None
        assert opts.kwargs['yaxis'] is None

    def test_axis_set_to_some_value(self, df, backend):
        plot = df.hvplot.scatter('x', 'y', c='category', xaxis='top', yaxis='right')
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['xaxis'] == 'top'
        assert opts.kwargs['yaxis'] == 'right'

    def test_axis_set_to_none_in_holoviews_opts_default(self, df, backend):
        hv.opts.defaults(hv.opts.Scatter(xaxis=None, yaxis=None))
        plot = df.hvplot.scatter('x', 'y', c='category')
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['xaxis'] is None
        assert opts.kwargs['yaxis'] is None

    def test_axis_set_to_some_value_in_holoviews_opts_default(self, df, backend):
        hv.opts.defaults(hv.opts.Scatter(xaxis='top', yaxis='right'))
        plot = df.hvplot.scatter('x', 'y', c='category')
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['xaxis'] == 'top'
        assert opts.kwargs['yaxis'] == 'right'

    def test_axis_set_to_none_in_holoviews_opts_default_overwrite_in_call(self, df, backend):
        hv.opts.defaults(hv.opts.Scatter(xaxis=None, yaxis=None))
        plot = df.hvplot.scatter('x', 'y', c='category', xaxis=True, yaxis=True)
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['xaxis'] is True
        assert opts.kwargs['yaxis'] is True

    def test_axis_set_to_some_value_in_holoviews_opts_default_overwrite_in_call(self, df, backend):
        hv.opts.defaults(hv.opts.Scatter(xaxis='top', yaxis='right'))
        plot = df.hvplot.scatter('x', 'y', c='category', xaxis='top-bare', yaxis='right-bare')
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['xaxis'] == 'top-bare'
        assert opts.kwargs['yaxis'] == 'right-bare'

    def test_loglog_opts(self, df, backend):
        plot = df.hvplot.scatter('x', 'y', c='category', loglog=True)
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['logx'] is True
        assert opts.kwargs['logy'] is True
        assert opts.kwargs.get('logz') is None

    def test_logy_opts(self, df, backend):
        plot = df.hvplot.scatter('x', 'y', c='category', logy=True)
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['logx'] is False
        assert opts.kwargs['logy'] is True
        assert opts.kwargs.get('logz') is None

    @pytest.mark.parametrize(
        'backend',
        [
            'bokeh',
            pytest.param(
                'matplotlib',
                marks=pytest.mark.xfail(reason='default opts not supported w/ matplotlib'),
            ),
            pytest.param(
                'plotly', marks=pytest.mark.xfail(reason='defaykt opts not supported w/ plotly')
            ),
        ],
        indirect=True,
    )
    def test_holoviews_defined_default_opts_logx(self, df, backend):
        hv.opts.defaults(hv.opts.Scatter(logx=True))
        plot = df.hvplot.scatter('x', 'y', c='category')
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['logx'] is True
        assert opts.kwargs['logy'] is False
        assert opts.kwargs.get('logz') is None

    def test_holoviews_defined_default_opts_logx_overwritten_in_call(self, df, backend):
        hv.opts.defaults(hv.opts.Scatter(logx=True))
        plot = df.hvplot.scatter('x', 'y', c='category', logx=False)
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['logx'] is False
        assert opts.kwargs['logy'] is False
        assert opts.kwargs.get('logz') is None

    def test_hvplot_default_cat_cmap_opts(self, df, backend):
        import colorcet as cc

        plot = df.hvplot.scatter('x', 'y', c='category')
        opts = Store.lookup_options(backend, plot, 'style')
        assert opts.kwargs['cmap'] == cc.palette['glasbey_category10']

    def test_hvplot_default_num_cmap_opts(self, df, backend):
        plot = df.hvplot.scatter('x', 'y', c='number')
        opts = Store.lookup_options(backend, plot, 'style')
        assert opts.kwargs['cmap'] == 'kbc_r'

    def test_cmap_opts_by_type(self, df, backend):
        plot = df.hvplot.scatter('x', 'y', c='number', cmap='diverging')
        opts = Store.lookup_options(backend, plot, 'style')
        assert opts.kwargs['cmap'] == 'coolwarm'

    def test_cmap_opts_by_name(self, df, backend):
        plot = df.hvplot.scatter('x', 'y', c='number', cmap='fire')
        opts = Store.lookup_options(backend, plot, 'style')
        assert opts.kwargs['cmap'] == 'fire'

    def test_colormap_opts_by_name(self, df, backend):
        plot = df.hvplot.scatter('x', 'y', c='number', colormap='fire')
        opts = Store.lookup_options(backend, plot, 'style')
        assert opts.kwargs['cmap'] == 'fire'

    def test_cmap_opts_as_a_list(self, df, backend):
        plot = df.hvplot.scatter('x', 'y', c='number', cmap=['red', 'blue', 'green'])
        opts = Store.lookup_options(backend, plot, 'style')
        assert opts.kwargs['cmap'] == ['red', 'blue', 'green']

    @pytest.mark.parametrize(
        ('opt', 'backend'),
        [
            ('aspect', 'bokeh'),
            ('aspect', 'matplotlib'),
            ('aspect', 'plotly'),
            ('data_aspect', 'bokeh'),
            ('data_aspect', 'matplotlib'),
            pytest.param(
                'data_aspect',
                'plotly',
                marks=pytest.mark.xfail(reason='data_aspect not supported w/ plotly'),
            ),
        ],
        indirect=['backend'],
    )
    def test_aspect(self, df, opt, backend):
        plot = df.hvplot(x='x', y='y', **{opt: 2})
        opts = Store.lookup_options(backend, plot, 'plot').kwargs
        assert opts[opt] == 2
        if backend in ['bokeh', 'matplotlib']:
            assert opts.get('width') is None
            assert opts.get('height') is None
        elif backend == 'matplotlib':
            assert opts.get('fig_size') is None

    @pytest.mark.parametrize(
        ('opt', 'backend'),
        [
            ('aspect', 'bokeh'),
            ('aspect', 'matplotlib'),
            ('aspect', 'plotly'),
            ('data_aspect', 'bokeh'),
            ('data_aspect', 'matplotlib'),
            pytest.param(
                'data_aspect',
                'plotly',
                marks=pytest.mark.xfail(reason='data_aspect not supported w/ plotly'),
            ),
        ],
        indirect=['backend'],
    )
    def test_aspect_and_width(self, df, opt, backend):
        plot = df.hvplot(x='x', y='y', width=150, **{opt: 2})
        opts = hv.Store.lookup_options(backend, plot, 'plot').kwargs
        assert opts[opt] == 2
        if backend in ['bokeh', 'plotly']:
            assert opts.get('width') == 150
            assert opts.get('height') is None
        elif backend == 'matplotlib':
            assert opts.get('fig_size') == pytest.approx(50.0)

    def test_symmetric_dataframe(self, backend):
        df = pd.DataFrame([[1, 2, -1], [3, 4, 0], [5, 6, 1]], columns=['x', 'y', 'number'])
        plot = df.hvplot.scatter('x', 'y', c='number')
        plot_opts = Store.lookup_options(backend, plot, 'plot')
        assert plot_opts.kwargs['symmetric'] is True
        style_opts = Store.lookup_options(backend, plot, 'style')
        assert style_opts.kwargs['cmap'] == 'coolwarm'

    def test_symmetric_is_deduced_dataframe(self, symmetric_df, backend):
        plot = symmetric_df.hvplot.scatter('x', 'y', c='number')
        plot_opts = Store.lookup_options(backend, plot, 'plot')
        assert plot_opts.kwargs['symmetric'] is True
        style_opts = Store.lookup_options(backend, plot, 'style')
        assert style_opts.kwargs['cmap'] == 'coolwarm'

    def test_symmetric_from_opts(self, df, backend):
        plot = df.hvplot.scatter('x', 'y', c='number', symmetric=True)
        plot_opts = Store.lookup_options(backend, plot, 'plot')
        assert plot_opts.kwargs['symmetric'] is True
        style_opts = Store.lookup_options(backend, plot, 'style')
        assert style_opts.kwargs['cmap'] == 'coolwarm'

    def test_symmetric_from_opts_does_not_deduce(self, symmetric_df, backend):
        plot = symmetric_df.hvplot.scatter('x', 'y', c='number', symmetric=False)
        plot_opts = Store.lookup_options(backend, plot, 'plot')
        assert plot_opts.kwargs['symmetric'] is False
        style_opts = Store.lookup_options(backend, plot, 'style')
        assert style_opts.kwargs['cmap'] == 'kbc_r'

    def test_if_clim_is_set_symmetric_is_not_deduced(self, symmetric_df, backend):
        plot = symmetric_df.hvplot.scatter('x', 'y', c='number', clim=(-1, 1))
        plot_opts = Store.lookup_options(backend, plot, 'plot')
        assert plot_opts.kwargs.get('symmetric') is None
        style_opts = Store.lookup_options(backend, plot, 'style')
        assert style_opts.kwargs['cmap'] == 'kbc_r'

    @pytest.mark.parametrize(
        'backend',
        [
            'bokeh',
            'matplotlib',
            pytest.param(
                'plotly',
                marks=pytest.mark.xfail(
                    reason='bandwidth, cut, levels not supported w/ plotly for bivariate'
                ),
            ),
        ],
        indirect=True,
    )
    def test_bivariate_opts(self, df, backend):
        plot = df.hvplot.bivariate('x', 'y', bandwidth=0.2, cut=1, levels=5, filled=True)
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['bandwidth'] == 0.2
        assert opts.kwargs['cut'] == 1
        assert opts.kwargs['levels'] == 5
        assert opts.kwargs['filled'] is True

    def test_kde_opts(self, df, backend):
        plot = df.hvplot.kde('x', bandwidth=0.2, cut=1, filled=True)
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['bandwidth'] == 0.2
        assert opts.kwargs['cut'] == 1
        assert opts.kwargs['filled'] is True

    def test_bgcolor(self, df, backend):
        plot = df.hvplot.scatter('x', 'y', bgcolor='black')
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['bgcolor'] == 'black'

    @pytest.mark.parametrize(
        'backend',
        [
            'bokeh',
            pytest.param(
                'matplotlib',
                marks=pytest.mark.skip(reason='toolbar not supported w/ matplotlib'),
            ),
            pytest.param(
                'plotly',
                marks=pytest.mark.skip(reason='toolbar not supported w/ plotly'),
            ),
        ],
        indirect=True,
    )
    @pytest.mark.parametrize(
        'toolbar', ['right', 'left', 'above', 'below', None, False, True, 'disable']
    )
    def test_toolbar(self, df, backend, toolbar):
        plot = df.hvplot.scatter('x', 'y', toolbar=toolbar)
        opts = Store.lookup_options(backend, plot, 'plot')
        if toolbar is True:
            toolbar = 'right'
        elif toolbar is False:
            toolbar = None
        assert opts.kwargs['toolbar'] == toolbar

    @pytest.mark.parametrize(
        'backend',
        [
            'bokeh',
            pytest.param(
                'matplotlib',
                marks=pytest.mark.skip(reason='autohide_toolbar not supported w/ matplotlib'),
            ),
            pytest.param(
                'plotly',
                marks=pytest.mark.skip(reason='autohide_toolbar not supported w/ plotly'),
            ),
        ],
        indirect=True,
    )
    def test_autohide_toolbar(self, df, backend):
        plot = df.hvplot.scatter('x', 'y', autohide_toolbar=True)
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['autohide_toolbar'] is True

    @pytest.mark.parametrize(
        'backend',
        [
            'bokeh',
            'matplotlib',
            pytest.param(
                'plotly',
                marks=pytest.mark.skip(reason='backend_opts not supported w/ plotly'),
            ),
        ],
        indirect=True,
    )
    def test_backend_opts(self, df, backend):
        if backend == 'bokeh':
            bo = {'plot.xgrid.grid_line_color': 'grey'}
        elif backend == 'matplotlib':
            bo = {'axes.frame_on': False}
        plot = df.hvplot.scatter('x', 'y', backend_opts=bo)
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['backend_opts'] == bo

    @pytest.mark.parametrize(
        'backend',
        [
            'bokeh',
            'matplotlib',
            pytest.param(
                'plotly',
                marks=pytest.mark.skip(reason='legend_cols not supported w/ plotly'),
            ),
        ],
        indirect=True,
    )
    def test_legend_cols(self, df, backend):
        plot = df.hvplot.scatter('x', 'y', by='category', legend_cols=2)
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['legend_cols'] == 2

    @pytest.mark.parametrize(
        'backend',
        [
            'bokeh',
            'matplotlib',
            pytest.param(
                'plotly',
                marks=pytest.mark.skip(reason='legend_opts not supported w/ plotly'),
            ),
        ],
        indirect=True,
    )
    def test_legend_opts(self, df, backend):
        if backend == 'bokeh':
            lo = {'spacing': 20}
        elif backend == 'matplotlib':
            lo = {'labelspacing': 2}

        plot = df.hvplot.scatter('x', 'y', by='category', legend_opts=lo)
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['legend_opts'] == lo


@pytest.fixture(scope='module')
def da():
    return xr.DataArray(
        data=np.arange(16).reshape((2, 2, 2, 2)),
        coords={'time': [0, 1], 'y': [0, 1], 'x': [0, 1], 'band': [0, 1]},
        dims=['time', 'y', 'x', 'band'],
        name='test',
    )


@pytest.fixture(scope='module')
def da2():
    return xr.DataArray(
        data=np.arange(27).reshape((3, 3, 3)),
        coords={'y': [0, 1, 2], 'x': [0, 1, 2]},
        dims=['y', 'x', 'other'],
        name='test2',
    )


@pytest.fixture(scope='module')
def ds1(da):
    return xr.Dataset(dict(foo=da))


@pytest.fixture(scope='module')
def ds2(da, da2):
    return xr.Dataset(dict(foo=da, bar=da2))


@pytest.mark.usefixtures('load_xarray_accessor')
class TestXarrayTitle:
    def test_dataarray_2d_with_title(self, da, backend):
        da_sel = da.sel(time=0, band=0)
        plot = da_sel.hvplot()  # Image plot
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['title'] == 'time = 0, band = 0'

    def test_dataarray_1d_with_title(self, da, backend):
        da_sel = da.sel(time=0, band=0, x=0)
        plot = da_sel.hvplot()  # Line plot
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['title'] == 'time = 0, x = 0, band = 0'

    def test_dataarray_1d_and_by_with_title(self, da, backend):
        da_sel = da.sel(time=0, band=0, x=[0, 1])
        plot = da_sel.hvplot(by='x')  # Line plot with hue/by
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['title'] == 'time = 0, band = 0'

    def test_override_title(self, da, backend):
        da_sel = da.sel(time=0, band=0)
        plot = da_sel.hvplot(title='title')  # Image plot
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['title'] == 'title'

    def test_dataarray_4d_line_no_title(self, da, backend):
        plot = da.hvplot.line(dynamic=False)  # Line plot with widgets
        opts = Store.lookup_options(backend, plot.last, 'plot')
        assert 'title' not in opts.kwargs

    def test_dataarray_3d_histogram_with_title(self, da, backend):
        da_sel = da.sel(time=0)
        plot = da_sel.hvplot()  # Histogram and no widgets
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['title'] == 'time = 0'

    def test_dataset_empty_raises(self, ds1, backend):
        with pytest.raises(ValueError, match='empty xarray.Dataset'):
            ds1.drop_vars('foo').hvplot()

    def test_dataset_one_var_behaves_like_dataarray(self, ds1, backend):
        ds_sel = ds1.sel(time=0, band=0)
        plot = ds_sel.hvplot()  # Image plot
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['title'] == 'time = 0, band = 0'

    def test_dataset_scatter_with_title(self, ds2, backend):
        ds_sel = ds2.sel(time=0, band=0, x=0, y=0)
        plot = ds_sel.hvplot.scatter(x='foo', y='bar')  # Image plot
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['title'] == 'time = 0, y = 0, x = 0, band = 0'


@pytest.mark.usefixtures('load_xarray_accessor')
class TestXarrayCticks:
    def test_cticks(self, da2):
        plot = da2.isel(other=0).hvplot(cticks=[5, 10])
        handles = hv.renderer('bokeh').get_plot(plot).handles
        assert handles['colorbar'].ticker.ticks == [5, 10]


def test_subcoordinate_y_bool(load_pandas_accessor):
    df = pd.DataFrame(np.random.random((10, 3)), columns=list('ABC'))
    plot = df.hvplot.line(subcoordinate_y=True)
    opts = Store.lookup_options('bokeh', plot, 'plot')
    assert opts.kwargs['subcoordinate_y'] is True


def test_subcoordinate_y_dict(load_pandas_accessor):
    df = pd.DataFrame(np.random.random((10, 3)), columns=list('ABC'))
    plot = df.hvplot.line(subcoordinate_y={'subcoordinate_scale': 2})
    opts = Store.lookup_options('bokeh', plot, 'plot')
    assert opts.kwargs['subcoordinate_y'] is True
    assert opts.kwargs['subcoordinate_scale'] == 2
