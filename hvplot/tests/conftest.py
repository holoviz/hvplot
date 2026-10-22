import sys
from importlib.util import find_spec

import dask
import holoviews as hv
import matplotlib
import numpy as np
import pandas as pd
import param
import pytest
from holoviews import Store
from holoviews.core.data import Dataset, Interface
from holoviews.core.options import Compositor, Options, OptionTree
from holoviews.element import Path
from packaging.version import Version

import hvplot
from hvplot.plotting.core import hvPlotBase
from hvplot.tests._deps import GRIDDED_LIBS, TABULAR_LIBS

param.parameterized.warnings_as_exceptions = True

if Version(dask.__version__).release < (2025, 1, 0):
    # From Dask 2024.3.0 they now use `dask_expr` by default
    # https://github.com/dask/dask/issues/10995
    dask.config.set({'dataframe.query-planning': False})


def _copy_options(tree):
    return OptionTree(sorted(tree.items()), groups=Options._option_groups)


def _save_hv_state():
    """Copy the HoloViews global state that tests and `import geoviews` modify."""
    return {
        'current_backend': Store.current_backend,
        'renderers': Store.renderers.copy(),
        'registry': {backend: plots.copy() for backend, plots in Store.registry.items()},
        'options': {
            backend: _copy_options(Store.options(backend=backend))
            for backend in Store.loaded_backends()
        },
        'extension_hooks': {
            backend: hooks.copy() for backend, hooks in hv.extension._backend_hooks.items()
        },
        'compositors': Compositor.definitions.copy(),
        'interfaces': Interface.interfaces.copy(),
        'datatypes': {cls: list(cls.datatype) for cls in (Dataset, Path)},
    }


def _restore_hv_state(state):
    # Everything is copied again, as a saved state is restored many times and tests
    # must not modify it. Containers are updated in place as HoloViews may hold them.
    for backend, tree in state['options'].items():
        Store.options(backend=backend, val=_copy_options(tree))
    Store._custom_options = {backend: {} for backend in Store._custom_options}
    Store.renderers = state['renderers'].copy()
    for backend, plots in state['registry'].items():
        Store.registry[backend].clear()
        Store.registry[backend].update(plots)
    hv.extension._backend_hooks.clear()
    hv.extension._backend_hooks.update(
        {backend: hooks.copy() for backend, hooks in state['extension_hooks'].items()}
    )
    Compositor.definitions[:] = state['compositors']
    Interface.interfaces.clear()
    Interface.interfaces.update(state['interfaces'])
    for cls, datatype in state['datatypes'].items():
        cls.datatype = list(datatype)
    if Store.current_backend != state['current_backend']:
        # Only when needed, it runs hooks that cost ~20-40ms.
        Store.set_current_backend(state['current_backend'])


# Baseline state, set once per process (each pytest-xdist worker loads this module).
# All the backends are loaded up front so that the plotting state does not depend
# on which test happens to load a backend first. The first backend listed becomes
# the current one, and compatibility is left to None.
matplotlib.use('agg')
hvplot.extension('bokeh', 'matplotlib', 'plotly')
# Importing GeoViews changes HoloViews for good (plot classes, options, extension hooks,
# data interfaces). It is imported once to save that state, which only the tests marked
# with `geo` get. All the other tests run as if GeoViews had never been imported.
_PLAIN_HV_STATE = _save_hv_state()
_GEO_HV_STATE = None
if find_spec('geoviews') and find_spec('cartopy'):
    import geoviews  # noqa: F401

    _GEO_HV_STATE = _save_hv_state()
    _restore_hv_state(_PLAIN_HV_STATE)


def pytest_addoption(parser):
    parser.addoption('--slow', action='store_true', help='Also run the tests marked as slow.')
    parser.addoption(
        '--no-render',
        action='store_true',
        help='Do not render the plots returned by hvPlot, which is faster.',
    )


def _render_returned_plot(call):
    def call_and_render(self, *args, **kwargs):
        obj = call(self, *args, **kwargs)
        # A plain Dataset (kind='dataset') has no plotting class.
        if isinstance(obj, hv.core.Dimensioned) and type(obj) is not Dataset:
            hv.renderer(Store.current_backend).get_plot(obj)
        return obj

    return call_and_render


def pytest_configure(config):
    # hvPlot configures HoloViews objects, but an invalid configuration often only
    # fails when the plot is built. So every plot returned by hvPlot is rendered
    # with the current backend, unless --no-render is passed.
    if not config.getoption('--no-render'):
        hvPlotBase.__call__ = _render_returned_plot(hvPlotBase.__call__)


def _apply_lib_marks(item, render):
    """Apply the `lib_*` marks naming the library (`tabular_lib` or `gridded_lib`) of the item."""
    params = item.callspec.params if hasattr(item, 'callspec') else {}
    lib = params.get('tabular_lib') or params.get('gridded_lib')
    marks = {'lib_xfail': pytest.mark.xfail, 'lib_skip': pytest.mark.skip}
    if render:
        marks['lib_render_xfail'] = pytest.mark.xfail
    for name, make_mark in marks.items():
        for mark in item.iter_markers(name):
            if not set(mark.args) <= {*TABULAR_LIBS, *GRIDDED_LIBS}:
                raise pytest.UsageError(f'{item.nodeid}: unknown library in {name}{mark.args}')
            if lib in mark.args:
                item.add_marker(make_mark(**mark.kwargs))


def pytest_collection_modifyitems(config, items):
    skip_slow = pytest.mark.skip(reason='Slow test, run it with --slow.')
    skip_geo = pytest.mark.skip(reason='GeoViews test, requires geoviews and cartopy.')
    render = not config.getoption('--no-render')
    for item in items:
        # The test suite must never need internet: it would be slow, flaky and fail offline.
        # pytest-socket blocks the creation of sockets, unless the test has `enable_socket`.
        item.add_marker(pytest.mark.disable_socket)
        if 'slow' in item.keywords and not config.getoption('--slow'):
            item.add_marker(skip_slow)
        if 'geo' in item.keywords and _GEO_HV_STATE is None:
            item.add_marker(skip_geo)
        # For tests that only fail when the plot is rendered.
        render_xfail = item.get_closest_marker('render_xfail')
        if render_xfail and render:
            item.add_marker(pytest.mark.xfail(*render_xfail.args, **render_xfail.kwargs))
        # For tests that fail or don't apply with some of the data libraries.
        _apply_lib_marks(item, render)


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


@pytest.fixture(autouse=True)
def _isolate_hvplot(request):
    """Restore after each test the global state that hvPlot and HoloViews tests modify.

    It unpatches the data libraries (e.g. removes `pd.DataFrame.hvplot`) so the next
    test can only use an accessor if it imports it, and so it can run in any order.
    Tests marked with `geo` run with the HoloViews state set by importing GeoViews.
    """
    if request.node.get_closest_marker('geo'):
        _restore_hv_state(_GEO_HV_STATE)
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
        module = sys.modules.pop(ext, None)
        if module is None:
            # Its import failed after patching: forget it rather than failing all the next tests.
            hvplot._module_extensions.discard(ext)
            continue
        module._unpatch()
    # Each test starts from the plain state: restoring it costs one copy, saving it would add one.
    _restore_hv_state(_PLAIN_HV_STATE)
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

    It is set up as most users do, with `hvplot.extension(backend)`, so tests read the
    options named by the backend (e.g. `linewidth` for matplotlib). To test the bokeh
    option names on another backend, call `hvplot.extension(backend, compatibility='bokeh')`.

    Restrict it with `@pytest.mark.parametrize('backend', ['bokeh'], indirect=True)`.
    """
    hvplot.extension(request.param)
    yield request.param
    assert Store.current_backend == request.param, (
        'The backend changed during the test, request `backend` after the accessor fixtures '
        '(importing an accessor switches back to bokeh).'
    )


@pytest.fixture(params=TABULAR_LIBS)
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


@pytest.fixture(params=GRIDDED_LIBS)
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

    Code checking whether a module is already imported with `name in sys.modules`
    sees a blocked module as imported. To test it, remove the module instead with
    `monkeypatch.delitem(sys.modules, name, raising=False)`.

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
