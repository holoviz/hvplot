"""
Tests patching of supported libraries
"""

from unittest import TestCase, SkipTest

import numpy as np

from holoplot import patch, HoloPlot


class TestPatchPandas(TestCase):

    def setUp(self):
        try:
            import pandas as pd # noqa
        except:
            raise SkipTest('Pandas not available')
        patch('pandas')

    def test_pandas_series_patched(self):
        import pandas as pd
        series = pd.Series([0, 1, 2])
        self.assertIsInstance(series.plot, HoloPlot)

    def test_pandas_dataframe_patched(self):
        import pandas as pd
        df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
        self.assertIsInstance(df.plot, HoloPlot)


class TestPatchDask(TestCase):

    def setUp(self):
        try:
            import dask.dataframe as dd # noqa
        except:
            raise SkipTest('Dask not available')
        patch('dask')

    def test_dask_series_patched(self):
        import pandas as pd
        import dask.dataframe as dd
        series = pd.Series([0, 1, 2])
        dseries = dd.from_pandas(series, 2)
        self.assertIsInstance(dseries.plot, HoloPlot)

    def test_dask_dataframe_patched(self):
        import pandas as pd
        import dask.dataframe as dd
        df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
        ddf = dd.from_pandas(df, 2)
        self.assertIsInstance(ddf.plot, HoloPlot)


class TestPatchXArray(TestCase):

    def setUp(self):
        try:
            import xarray as xr # noqa
        except:
            raise SkipTest('XArray not available')
        patch('xarray')

    def test_xarray_dataarray_patched(self):
        import xarray as xr
        array = np.random.rand(100, 100)
        xr_array = xr.DataArray(array, coords={'x': range(100), 'y': range(100)}, dims=('y', 'x'))
        self.assertIsInstance(xr_array.plot, HoloPlot)


class TestPatchStreamz(TestCase):

    def setUp(self):
        try:
            import streamz # noqa
        except:
            raise SkipTest('streamz not available')
        patch('streamz')

    def test_streamz_dataframe_patched(self):
        from streamz.dataframe import Random
        random_df = Random()
        self.assertIsInstance(random_df.plot, HoloPlot)

    def test_streamz_series_patched(self):
        from streamz.dataframe import Random
        random_df = Random()
        self.assertIsInstance(random_df.x.plot, HoloPlot)

    def test_streamz_dataframes_patched(self):
        from streamz.dataframe import Random
        random_df = Random()
        self.assertIsInstance(random_df.groupby('x').sum().plot, HoloPlot)

    def test_streamz_seriess_patched(self):
        from streamz.dataframe import Random
        random_df = Random()
        self.assertIsInstance(random_df.groupby('x').sum().y.plot, HoloPlot)
