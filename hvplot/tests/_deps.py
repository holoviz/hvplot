from importlib.util import find_spec

import pytest


def requires(*modules):
    """Skip marker for tests that need optional modules.

    Use it on a test (`@requires('datashader')`) or on a whole module
    (`pytestmark = requires('geoviews', 'cartopy')`).
    """
    missing = [m for m in modules if find_spec(m) is None]
    return pytest.mark.skipif(bool(missing), reason=f'requires {", ".join(missing)}')
