"""Tests of the test suite infrastructure defined in conftest.py and _deps.py."""

import importlib.util
import socket

import pandas as pd
import pytest
from holoviews import Store

import hvplot
from hvplot.tests._deps import requires


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


def test_network_guard_blocks_remote_connection():
    # 192.0.2.1 is reserved for documentation (TEST-NET-1), it is never reached.
    with socket.socket() as sock, pytest.raises(RuntimeError, match='must not access the network'):
        sock.connect(('192.0.2.1', 80))


def test_network_guard_allows_loopback():
    with socket.create_server(('127.0.0.1', 0)) as server, socket.socket() as client:
        client.connect(server.getsockname())


@requires('a_module_that_does_not_exist')
def test_requires_skips():
    pytest.fail('should have been skipped')
