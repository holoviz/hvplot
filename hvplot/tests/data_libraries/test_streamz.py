from unittest import SkipTest, TestCase

import pytest

import hvplot
from hvplot.plotting import hvPlotTabular
from hvplot.util import _HV_VERSION


class TestPatchStreamz(TestCase):
    def setUp(self):
        if _HV_VERSION >= (1, 23, 0):
            raise SkipTest('streamz support has been removed in HoloViews >= 1.23.0')
        try:
            import streamz  # noqa: F401
        except ImportError:
            raise SkipTest('streamz not available')
        import hvplot.streamz  # noqa: F401

    def test_streamz_dataframe_patched(self):
        from streamz.dataframe import Random

        random_df = Random()
        self.assertIsInstance(random_df.hvplot, hvPlotTabular)

    def test_streamz_series_patched(self):
        from streamz.dataframe import Random

        random_df = Random()
        self.assertIsInstance(random_df.x.hvplot, hvPlotTabular)

    def test_streamz_dataframes_patched(self):
        from streamz.dataframe import Random

        random_df = Random()
        self.assertIsInstance(random_df.groupby('x').sum().hvplot, hvPlotTabular)

    def test_streamz_seriess_patched(self):
        from streamz.dataframe import Random

        random_df = Random()
        self.assertIsInstance(random_df.groupby('x').sum().y.hvplot, hvPlotTabular)


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


@pytest.mark.filterwarnings('ignore:streamz support has been deprecated:FutureWarning')
def test_unpatch_streamz():
    sdf = pytest.importorskip('streamz.dataframe')
    import hvplot.streamz

    classes = [sdf.DataFrame, sdf.DataFrames, sdf.Series, sdf.Seriess]
    _round_trip(hvplot.streamz, classes)
