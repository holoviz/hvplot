"""
Tests patching of supported libraries
"""

from unittest import TestCase, SkipTest

import numpy as np

from hvplot.plotting import hvPlotTab, hvPlotGridded


class TestPatchPandas(TestCase):

    def setUp(self):
        import hvplot.pandas   # noqa

    def test_pandas_series_patched(self):
        import pandas as pd
        series = pd.Series([0, 1, 2])
        self.assertIsInstance(series.hvplot, hvPlotTab)

    def test_pandas_dataframe_patched(self):
        import pandas as pd
        df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
        self.assertIsInstance(df.hvplot, hvPlotTab)


class TestPatchDask(TestCase):

    def setUp(self):
        try:
            import dask.dataframe as dd # noqa
        except:
            raise SkipTest('Dask not available')
        import hvplot.dask   # noqa

    def test_dask_series_patched(self):
        import pandas as pd
        import dask.dataframe as dd
        series = pd.Series([0, 1, 2])
        dseries = dd.from_pandas(series, 2)
        self.assertIsInstance(dseries.hvplot, hvPlotTab)

    def test_dask_dataframe_patched(self):
        import pandas as pd
        import dask.dataframe as dd
        df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
        ddf = dd.from_pandas(df, 2)
        self.assertIsInstance(ddf.hvplot, hvPlotTab)


class TestPatchXArray(TestCase):

    def setUp(self):
        try:
            import xarray as xr # noqa
        except:
            raise SkipTest('XArray not available')
        import hvplot.xarray # noqa

    def test_xarray_dataarray_patched(self):
        import xarray as xr
        array = np.random.rand(100, 100)
        xr_array = xr.DataArray(array, coords={'x': range(100), 'y': range(100)}, dims=('y', 'x'))
        self.assertIsInstance(xr_array.hvplot, hvPlotGridded)

    def test_xarray_dataset_patched(self):
        import xarray as xr
        array = np.random.rand(100, 100)
        xr_array = xr.DataArray(array, coords={'x': range(100), 'y': range(100)}, dims=('y', 'x'))
        xr_ds = xr.Dataset({'z': xr_array})
        self.assertIsInstance(xr_ds.hvplot, hvPlotGridded)


class TestPatchStreamz(TestCase):

    def setUp(self):
        try:
            import streamz # noqa
        except:
            raise SkipTest('streamz not available')
        import hvplot.streamz   # noqa

    def test_streamz_dataframe_patched(self):
        from streamz.dataframe import Random
        random_df = Random()
        self.assertIsInstance(random_df.hvplot, hvPlotTab)

    def test_streamz_series_patched(self):
        from streamz.dataframe import Random
        random_df = Random()
        self.assertIsInstance(random_df.x.hvplot, hvPlotTab)

    def test_streamz_dataframes_patched(self):
        from streamz.dataframe import Random
        random_df = Random()
        self.assertIsInstance(random_df.groupby('x').sum().hvplot, hvPlotTab)

    def test_streamz_seriess_patched(self):
        from streamz.dataframe import Random
        random_df = Random()
        self.assertIsInstance(random_df.groupby('x').sum().y.hvplot, hvPlotTab)
