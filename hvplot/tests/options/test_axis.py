import holoviews as hv
import numpy as np
import pandas as pd
import pytest
import xarray as xr
from holoviews import Store


@pytest.fixture(scope='module')
def df():
    return pd.DataFrame(
        [[1, 2, 'A', 0.1], [3, 4, 'B', 0.2], [5, 6, 'C', 0.3]],
        columns=['x', 'y', 'category', 'number'],
    )


@pytest.mark.usefixtures('hvplot_pandas')
class TestOptions:
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

    def test_holoviews_defined_default_opts_logx(self, df, backend):
        if backend != 'bokeh':
            pytest.xfail(f'default opts not supported w/ {backend}')

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
    return xr.Dataset({'foo': da})


@pytest.fixture(scope='module')
def ds2(da, da2):
    return xr.Dataset({'foo': da, 'bar': da2})


@pytest.mark.usefixtures('hvplot_xarray')
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


@pytest.mark.usefixtures('hvplot_xarray')
class TestXarrayCticks:
    def test_cticks(self, da2):
        plot = da2.isel(other=0).hvplot(cticks=[5, 10])
        handles = hv.renderer('bokeh').get_plot(plot).handles
        assert handles['colorbar'].ticker.ticks == [5, 10]


def test_subcoordinate_y_bool(hvplot_pandas):
    df = pd.DataFrame(np.random.random((10, 3)), columns=list('ABC'))
    plot = df.hvplot.line(subcoordinate_y=True)
    opts = Store.lookup_options('bokeh', plot, 'plot')
    assert opts.kwargs['subcoordinate_y'] is True


def test_subcoordinate_y_dict(hvplot_pandas):
    df = pd.DataFrame(np.random.random((10, 3)), columns=list('ABC'))
    plot = df.hvplot.line(subcoordinate_y={'subcoordinate_scale': 2})
    opts = Store.lookup_options('bokeh', plot, 'plot')
    assert opts.kwargs['subcoordinate_y'] is True
    assert opts.kwargs['subcoordinate_scale'] == 2
