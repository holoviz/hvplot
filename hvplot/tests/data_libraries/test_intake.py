import pytest

import hvplot
from hvplot.tests._deps import requires

# intake is optional, it is imported in the tests.
pytestmark = [
    requires('intake'),
    pytest.mark.filterwarnings('ignore:hvplot.intake is deprecated:FutureWarning'),
]


@pytest.fixture(autouse=True)
def hvplot_intake():
    import hvplot.intake  # noqa: F401


def test_unpatch_intake():
    import intake

    # vars() and not hasattr() as intake's DataSource inherits its own `hvplot` property.
    cls = intake.source.base.DataSource

    hvplot.intake._unpatch()
    assert 'hvplot' not in vars(cls)
    assert 'hvplot.intake' not in hvplot._module_extensions

    # Ends patched, the _isolate_hvplot fixture unpatches it after the test.
    hvplot.intake.patch()
    assert 'hvplot' in vars(cls)
    assert 'hvplot.intake' in hvplot._module_extensions


def test_patch_without_intake(block_import):
    block_import('intake')
    with pytest.raises(ImportError, match='intake could not be imported'):
        hvplot.intake.patch()
