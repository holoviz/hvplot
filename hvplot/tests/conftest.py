import contextlib
import ipaddress
import socket
import sys

import dask
import holoviews as hv
import matplotlib
import numpy as np
import pandas as pd
import param
import pytest
from holoviews import Store
from holoviews.core.options import Options, OptionTree
from packaging.version import Version

import hvplot

param.parameterized.warnings_as_exceptions = True

if Version(dask.__version__).release < (2025, 1, 0):
    # From Dask 2024.3.0 they now use `dask_expr` by default
    # https://github.com/dask/dask/issues/10995
    dask.config.set({'dataframe.query-planning': False})

# Baseline state, set once per process (each pytest-xdist worker loads this module).
# All the backends are loaded up front so that the plotting state does not depend
# on which test happens to load a backend first. The first backend listed becomes
# the current one, and compatibility is left to None.
matplotlib.use('agg')
hvplot.extension('bokeh', 'matplotlib', 'plotly')
# GeoViews registers its elements' options when imported. Imported here, before the
# first snapshot of _isolate_hvplot, otherwise they would be lost after the first test.
with contextlib.suppress(ImportError):
    import geoviews  # noqa: F401


def pytest_addoption(parser):
    parser.addoption('--slow', action='store_true', help='Also run the tests marked as slow.')


def pytest_collection_modifyitems(config, items):
    if config.getoption('--slow'):
        return
    skip_slow = pytest.mark.skip(reason='Slow test, run it with --slow.')
    for item in items:
        if 'slow' in item.keywords:
            item.add_marker(skip_slow)


def pytest_collection_finish(session):
    # _isolate_hvplot can only undo the patching done while a test runs.
    if hvplot._module_extensions:
        # Reported as a collection error, as pytest-xdist workers would lose an exception.
        report = pytest.CollectReport(
            session.nodeid,
            'failed',
            longrepr=(
                f'{sorted(hvplot._module_extensions)} imported while collecting the tests. '
                'Test modules must not import hvplot extensions (e.g. hvplot.pandas) at import '
                'time: use the hvplot_pandas/hvplot_xarray fixtures or import them in the test.'
            ),
            result=[],
        )
        session.config.hook.pytest_collectreport(report=report)


def _is_local(sock, address):
    if sock.family == socket.AF_UNIX:
        return True
    host = address[0]
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:  # a host name
        return host == 'localhost'


def _local_only(connect):
    def guarded_connect(sock, address):
        if not _is_local(sock, address):
            raise RuntimeError(f'Tests must not access the network, tried to connect to {address}')
        return connect(sock, address)

    return guarded_connect


@pytest.fixture(scope='session', autouse=True)
def _block_network():
    """The test suite must never need internet: it would be slow, flaky and fail offline."""
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(socket.socket, 'connect', _local_only(socket.socket.connect))
        mp.setattr(socket.socket, 'connect_ex', _local_only(socket.socket.connect_ex))
        yield


@pytest.fixture(autouse=True)
def _isolate_hvplot():
    """Restore after each test the global state that hvPlot and HoloViews tests modify.

    It unpatches the data libraries (e.g. removes `pd.DataFrame.hvplot`) so the next
    test can only use an accessor if it imports it, and so it can run in any order.
    """
    current_backend = Store.current_backend
    renderers = Store.renderers.copy()
    options = {
        backend: OptionTree(
            sorted(Store.options(backend=backend).items()), groups=Options._option_groups
        )
        for backend in Store.loaded_backends()
    }
    compatibility = hvplot.extension.compatibility
    extension_loaded = hv.extension._loaded
    plotting_backend = pd.options.plotting.backend

    yield

    for ext in list(hvplot._module_extensions):
        # fugue gives no way to unregister the parser hvplot.fugue adds, so the module
        # stays imported and registered. Its tests must also request hvplot_pandas.
        if ext == 'hvplot.fugue':
            continue
        # Popped so that the next `import hvplot.<ext>` patches again.
        sys.modules.pop(ext)._unpatch()
    for backend, tree in options.items():
        Store.options(backend=backend, val=tree)
    Store._custom_options = {backend: {} for backend in Store._custom_options}
    Store.renderers = renderers
    if Store.current_backend != current_backend:
        # Only when needed, it runs hooks that cost ~20-40ms.
        Store.set_current_backend(current_backend)
    hvplot.extension.compatibility = compatibility
    hv.extension._loaded = extension_loaded
    pd.set_option('plotting.backend', plotting_backend)


@pytest.fixture
def disable_param_warnings_as_exceptions():
    original = param.parameterized.warnings_as_exceptions
    param.parameterized.warnings_as_exceptions = False
    try:
        yield
    finally:
        param.parameterized.warnings_as_exceptions = original


@pytest.fixture
def hvplot_pandas():
    """Add the .hvplot accessor to pandas objects, removed after the test."""
    import hvplot.pandas  # noqa: F401


@pytest.fixture
def hvplot_xarray():
    """Add the .hvplot accessor to xarray objects, removed after the test."""
    import hvplot.xarray  # noqa: F401


@pytest.fixture(params=['bokeh', 'matplotlib', 'plotly'])
def backend(request):
    """Make each plotting backend the current one, restored after the test.

    Restrict it with `@pytest.mark.parametrize('backend', ['bokeh'], indirect=True)`.
    Request it after the accessor fixtures: importing an accessor switches back to bokeh.
    """
    hvplot.extension(request.param, compatibility='bokeh')
    return request.param


@pytest.fixture(params=['pandas', 'dask', 'polars', 'duckdb', 'ibis'])
def tabular_lib(request):
    """Return a function converting a pandas DataFrame to the library's object.

    The library's accessor is imported. Libraries that are not installed are skipped.
    """
    # Optional libraries are imported here so the test modules can be collected without them.
    if request.param == 'pandas':
        import hvplot.pandas

        return lambda df: df
    elif request.param == 'dask':
        dd = pytest.importorskip('dask.dataframe')
        import hvplot.dask

        return lambda df: dd.from_pandas(df, npartitions=2)
    elif request.param == 'polars':
        pl = pytest.importorskip('polars')
        import hvplot.polars

        return pl.from_pandas
    elif request.param == 'duckdb':
        duckdb = pytest.importorskip('duckdb')
        import hvplot.duckdb

        return duckdb.from_df
    elif request.param == 'ibis':
        ibis = pytest.importorskip('ibis')
        import hvplot.ibis  # noqa: F401

        return ibis.memtable


@pytest.fixture(params=['xarray', 'dask'])
def gridded_lib(request):
    """Return a function converting an xarray object to one backed by the library.

    The xarray accessor is imported. Libraries that are not installed are skipped.
    """
    import hvplot.xarray  # noqa: F401

    if request.param == 'xarray':
        return lambda data: data
    elif request.param == 'dask':
        pytest.importorskip('dask.array')
        return lambda data: data.chunk()


@pytest.fixture
def block_import(monkeypatch):
    """Return a function that makes modules look not installed during the test.

    For each name, it and its already imported submodules are set to None in
    `sys.modules`, so importing them raises ModuleNotFoundError and
    `importlib.util.find_spec` returns None. Modules that import the blocked one
    at their own top level must be blocked too.

    Example::

        def test_tiles_without_geoviews(block_import):
            block_import('geoviews')
            ...
    """

    def block(*names):
        for name in names:
            for module in list(sys.modules):
                if module.startswith(f'{name}.'):
                    monkeypatch.setitem(sys.modules, module, None)
            monkeypatch.setitem(sys.modules, name, None)

    return block


@pytest.fixture
def rng():
    return np.random.default_rng(1)
