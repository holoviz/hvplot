from unittest import SkipTest, TestCase

import pandas as pd
import pytest

import hvplot
from hvplot.plotting import hvPlotTabular


class TestPatchDask(TestCase):
    def setUp(self):
        try:
            import dask.dataframe  # noqa: F401
        except ImportError:
            raise SkipTest('Dask not available')
        import hvplot.dask  # noqa: F401

    def test_dask_series_patched(self):
        import dask.dataframe as dd

        series = pd.Series([0, 1, 2])
        dseries = dd.from_pandas(series, 2)
        self.assertIsInstance(dseries.hvplot, hvPlotTabular)

    def test_dask_dataframe_patched(self):
        import dask.dataframe as dd

        df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
        ddf = dd.from_pandas(df, 2)
        self.assertIsInstance(ddf.hvplot, hvPlotTabular)


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


def test_unpatch_dask():
    dd = pytest.importorskip('dask.dataframe')
    import hvplot.dask

    _round_trip(hvplot.dask, [dd.DataFrame, dd.Series], ['hvplot', 'interactive'])
