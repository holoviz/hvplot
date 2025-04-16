import dask
import param
import pytest

from packaging.version import Version

param.parameterized.warnings_as_exceptions = True

optional_markers = {
    'geo': {
        'help': 'Run the tests that require GeoViews',
        'marker-descr': 'Geo test marker',
        'skip-reason': 'Test only runs with the --geo option.',
    },
}


def pytest_addoption(parser):
    for marker, info in optional_markers.items():
        parser.addoption(f'--{marker}', action='store_true', default=False, help=info['help'])


def pytest_configure(config):
    for marker, info in optional_markers.items():
        config.addinivalue_line('markers', '{}: {}'.format(marker, info['marker-descr']))


def pytest_collection_modifyitems(config, items):
    skipped, selected = [], []
    markers = [m for m in optional_markers if config.getoption(f'--{m}')]
    empty = not markers
    for item in items:
        if empty and any(m in item.keywords for m in optional_markers):
            skipped.append(item)
        elif empty:
            selected.append(item)
        elif not empty and any(m in item.keywords for m in markers):
            selected.append(item)
        else:
            skipped.append(item)

    config.hook.pytest_deselected(items=skipped)
    items[:] = selected


if Version(dask.__version__).release < (2025, 1, 0):
    # From Dask 2024.3.0 they now use `dask_expr` by default
    # https://github.com/dask/dask/issues/10995
    dask.config.set({'dataframe.query-planning': False})


@pytest.fixture
def disable_param_warnings_as_exceptions():
    original = param.parameterized.warnings_as_exceptions
    param.parameterized.warnings_as_exceptions = False
    try:
        yield
    finally:
        param.parameterized.warnings_as_exceptions = original
