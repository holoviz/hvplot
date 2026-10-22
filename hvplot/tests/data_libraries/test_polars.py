import sys
from unittest import SkipTest, TestCase

import pytest

import hvplot
from hvplot.plotting import hvPlotTabular


class TestPatchPolars(TestCase):
    def setUp(self):
        if sys.platform == 'win32' and sys.version_info[:2] == (3, 9):
            raise SkipTest('stack overflow error')
        try:
            import polars  # noqa: F401
        except ImportError:
            raise SkipTest('Polars not available')
        import hvplot.polars  # noqa: F401

    def test_polars_series_patched(self):
        import polars as pl

        pseries = pl.Series([0, 1, 2])
        self.assertIsInstance(pseries.hvplot, hvPlotTabular)

    def test_polars_dataframe_patched(self):
        import polars as pl

        pdf = pl.DataFrame({'x': [1, 3, 5], 'y': [2, 4, 6]})
        self.assertIsInstance(pdf.hvplot, hvPlotTabular)

    def test_polars_lazyframe_patched(self):
        import polars as pl

        pldf = pl.LazyFrame({'x': [1, 3, 5], 'y': [2, 4, 6]})
        self.assertIsInstance(pldf.hvplot, hvPlotTabular)


def _patched(classes, attrs):
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


def test_unpatch_polars():
    pl = pytest.importorskip('polars')
    import hvplot.polars

    classes = [pl.DataFrame, pl.Series, pl.LazyFrame]
    _round_trip(hvplot.polars, classes)

    hvplot.polars._unpatch()
    assert not any('hvplot' in cls._accessors for cls in classes)
    hvplot.polars.patch()
    assert all('hvplot' in cls._accessors for cls in classes)
