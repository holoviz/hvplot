"""
Tests patching of supported libraries
"""

from unittest import TestCase, SkipTest

import numpy as np

from hvplot.plotting import hvPlotTabular, hvPlot


class TestPatchPandas(TestCase):

    def setUp(self):
        import hvplot.pandas   # noqa

    def test_pandas_series_patched(self):
        import pandas as pd
        series = pd.Series([0, 1, 2])
        self.assertIsInstance(series.hvplot, hvPlotTabular)

    def test_pandas_dataframe_patched(self):
        import pandas as pd
        df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
        self.assertIsInstance(df.hvplot, hvPlotTabular)


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
        self.assertIsInstance(dseries.hvplot, hvPlotTabular)

    def test_dask_dataframe_patched(self):
        import pandas as pd
        import dask.dataframe as dd
        df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
        ddf = dd.from_pandas(df, 2)
        self.assertIsInstance(ddf.hvplot, hvPlotTabular)


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
        self.assertIsInstance(xr_array.hvplot, hvPlot)

    def test_xarray_dataset_patched(self):
        import xarray as xr
        array = np.random.rand(100, 100)
        xr_array = xr.DataArray(array, coords={'x': range(100), 'y': range(100)}, dims=('y', 'x'))
        xr_ds = xr.Dataset({'z': xr_array})
        self.assertIsInstance(xr_ds.hvplot, hvPlot)


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
