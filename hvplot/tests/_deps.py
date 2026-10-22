from importlib.metadata import version
from importlib.util import find_spec

import pytest
from packaging.version import Version


def requires(*modules):
    """Skip marker for tests that need optional modules.

    Use it on a test (`@requires('datashader')`) or on a whole module
    (`pytestmark = requires('geoviews', 'cartopy')`).
    """
    missing = [m for m in modules if find_spec(m) is None]
    return pytest.mark.skipif(bool(missing), reason=f'requires {", ".join(missing)}')


# pl.NUMERIC_DTYPES, used by hvPlot, was removed in polars 2.0.
POLARS_2 = find_spec('polars') is not None and Version(version('polars')).major >= 2
