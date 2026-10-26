"""Tests of the test suite infrastructure defined in conftest.py and _deps.py."""

import importlib.util
import socket

import holoviews as hv
import pandas as pd
import pytest
from holoviews import Store
from holoviews.plotting.bokeh import OverlayPlot
from pytest_socket import SocketBlockedError

import hvplot
from hvplot.tests._deps import pandas_and_dask, requires


@pytest.fixture
def baseline_state():
    # Checked before each run of the test below: whichever run comes second
    # (in any order) proves that _isolate_hvplot undid the changes of the first.
    assert 'hvplot' not in vars(pd.DataFrame)
    assert 'hvplot.pandas' not in hvplot._module_extensions
    assert Store.current_backend == 'bokeh'
    assert hvplot.extension.compatibility is None


@pytest.mark.parametrize('run', [1, 2])
def test_isolate_hvplot(baseline_state, run):
    import hvplot.pandas

    # Fails on the second run if the module was not popped from sys.modules.
    assert 'hvplot' in vars(pd.DataFrame)
    hvplot.extension('matplotlib', compatibility='bokeh')


@requires('geoviews')
def test_block_import(block_import):
    block_import('geoviews')

    with pytest.raises(ModuleNotFoundError):
        import geoviews  # noqa: F401
    assert importlib.util.find_spec('geoviews') is None


def test_block_import_geoviews_then_extension(block_import):
    block_import('geoviews')

    hvplot.extension('bokeh')


def test_without_geo_marker_holoviews_state():
    assert Store.registry['bokeh'][hv.Overlay] is OverlayPlot
    assert not hv.extension._backend_hooks['bokeh']


@pytest.mark.geo
def test_geo_marker_geoviews_state():
    from geoviews.plotting.bokeh import GeoOverlayPlot

    assert Store.registry['bokeh'][hv.Overlay] is GeoOverlayPlot
    assert 'Feature' in Store.options(backend='bokeh')


def test_sockets_blocked():
    with pytest.raises(SocketBlockedError):
        socket.socket()


@pytest.mark.enable_socket
def test_sockets_enabled_by_marker():
    with socket.create_server(('127.0.0.1', 0)) as server, socket.socket() as client:
        client.connect(server.getsockname())


@requires('a_module_that_does_not_exist')
def test_requires_skips():
    pytest.fail('should have been skipped')


def test_plots_returned_by_hvplot_are_rendered(request, hvplot_pandas, backend, monkeypatch):
    if request.config.getoption('--no-render'):
        pytest.skip('Plots are not rendered with --no-render.')
    rendered = []
    monkeypatch.setattr(hv.renderer(backend), 'get_plot', rendered.append)
    plot = pd.DataFrame({'x': [1, 2], 'y': [3, 4]}).hvplot.scatter('x', 'y')
    assert rendered == [plot]


@pytest.mark.render_xfail(reason='Checks that render_xfail is applied when rendering.')
def test_render_xfail(request):
    assert request.config.getoption('--no-render')


# The body fails with dask only, so the tests below pass only if the lib_* mark is applied to
# the dask item, and not to the pandas item (xfail is strict).
@pandas_and_dask
@pytest.mark.lib_xfail('dask', reason='Checks that lib_xfail is applied to the library.')
def test_lib_xfail(tabular_lib, request):
    assert request.node.callspec.params['tabular_lib'] != 'dask'


@pandas_and_dask
@pytest.mark.lib_skip('dask', reason='Checks that lib_skip is applied to the library.')
def test_lib_skip(tabular_lib, request):
    assert request.node.callspec.params['tabular_lib'] != 'dask'


@pytest.mark.lib_render_xfail('dask', reason='Checks that lib_render_xfail is applied (gridded).')
def test_lib_render_xfail(gridded_lib, request):
    # With dask, it only fails when the plots are rendered.
    dask_item = request.node.callspec.params['gridded_lib'] == 'dask'
    assert not dask_item or request.config.getoption('--no-render')
