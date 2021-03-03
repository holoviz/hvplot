from unittest import SkipTest

import holoviews as hv
import numpy as np
import pandas as pd

from holoviews.element.comparison import ComparisonTestCase


class TestPandasTransforms(ComparisonTestCase):

    def setUp(self):
        import hvplot.pandas # noqa

    def test_pandas_transform(self):
        demo_df = pd.DataFrame({'value':np.random.randn(50), 'probability':np.random.rand(50)})
        percent = hv.dim('probability')*100
        scatter = demo_df.hvplot.scatter(
            x='value', y='probability', transforms=dict(probability=percent)
        )
        self.assertEqual((scatter.data['probability']).values,
                         demo_df['probability'].values*100)


class TestXArrayTransforms(ComparisonTestCase):

    def setUp(self):

        try:
            import xarray as xr # noqa
        except:
            raise SkipTest('xarray not available')
        import hvplot.xarray # noqa

    def test_xarray_transform(self):
        import xarray as xr
        data = np.arange(0, 60).reshape(6, 10)
        x = np.arange(10)
        y = np.arange(6)
        da = xr.DataArray(data, coords={'y': y, 'x': x}, dims=('y', 'x'), name='value')
        img = da.hvplot.image(
            transforms=dict(value=hv.dim('value')*10)
        )
        self.assertEqual(img.data.value.data, da.data*10)
