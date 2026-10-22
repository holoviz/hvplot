import pytest

import hvplot


def _patched(classes, attrs):
    # vars() and not hasattr() as intake's DataSource inherits its own `hvplot` property.
    return all(attr in vars(cls) for cls in classes for attr in attrs)


def _unpatched(classes, attrs):
    return not any(attr in vars(cls) for cls in classes for attr in attrs)


def _round_trip(ext, classes, attrs=('hvplot',)):
    # Ends patched, so the _isolate_hvplot fixture unpatches the extension
    # and removes its module from sys.modules after the test.
    ext.patch()
    assert _patched(classes, attrs)
    assert ext.__name__ in hvplot._module_extensions

    ext._unpatch()
    assert _unpatched(classes, attrs)
    assert ext.__name__ not in hvplot._module_extensions

    ext.patch()
    assert _patched(classes, attrs)
    assert ext.__name__ in hvplot._module_extensions


@pytest.mark.filterwarnings('ignore:hvplot.intake is deprecated:FutureWarning')
def test_unpatch_intake():
    intake = pytest.importorskip('intake')
    import hvplot.intake

    _round_trip(hvplot.intake, [intake.source.base.DataSource])
