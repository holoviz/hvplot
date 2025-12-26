from unittest import SkipTest

import holoviews as hv
import numpy as np
import pandas as pd

from holoviews.element.comparison import ComparisonTestCase


class TestPandasTransforms(ComparisonTestCase):
    def setUp(self):
        import hvplot.pandas  # noqa

    def test_pandas_transform(self):
        demo_df = pd.DataFrame({'value': np.random.randn(50), 'probability': np.random.rand(50)})
        percent = hv.dim('probability') * 100
        scatter = demo_df.hvplot.scatter(
            x='value', y='probability', transforms=dict(probability=percent)
        )
        self.assertEqual((scatter.data['probability']).values, demo_df['probability'].values * 100)

    def test_pandas_dim_size_alias(self):
        df = pd.DataFrame({'x': np.linspace(0, 4, 5), 'y': np.linspace(1, 5, 5)})
        dim_expr = hv.dim('y') * 10
        scatter = df.hvplot.scatter('x', 'y', s=dim_expr)
        plot_opts = scatter.opts.get().kwargs
        assert repr(plot_opts.get('size')) == repr(dim_expr)

    def test_pandas_dim_color_expression(self):
        df = pd.DataFrame({'x': np.linspace(0, 4, 5), 'y': np.linspace(-2, 2, 5)})
        dim_expr = hv.dim('y') * 10
        scatter = df.hvplot.scatter('x', 'y', color=dim_expr)
        plot_opts = scatter.opts.get().kwargs
        assert repr(plot_opts.get('color')) == repr(dim_expr)
        assert plot_opts.get('colorbar') is True

    def test_pandas_color_alias_column(self):
        df = pd.DataFrame({'x': np.linspace(0, 4, 5), 'y': np.linspace(1, 5, 5)})
        scatter = df.hvplot.scatter('x', 'y', c='y')
        plot_opts = scatter.opts.get().kwargs
        assert repr(plot_opts.get('color')) == repr(hv.dim('y'))

    # def test_pandas_dim_size_matplotlib_backend(self):
    #     hv.extension('matplotlib')

    #     df = pd.DataFrame({'x': np.linspace(0, 4, 5), 'y': np.linspace(1, 5, 5)})
    #     dim_expr = hv.dim('y') * 10

    #     scatter = df.hvplot.scatter('x', 'y', size=dim_expr)
    #     plot_opts = scatter.opts.get().kwargs
    #     # Matplotlib uses 's' not 'size'
    #     assert 's' in plot_opts


class TestXArrayTransforms(ComparisonTestCase):
    def setUp(self):
        try:
            import xarray as xr  # noqa
        except ImportError:
            raise SkipTest('xarray not available')
        import hvplot.xarray  # noqa

    def test_xarray_transform(self):
        import xarray as xr

        data = np.arange(0, 60).reshape(6, 10)
        x = np.arange(10)
        y = np.arange(6)
        da = xr.DataArray(data, coords={'y': y, 'x': x}, dims=('y', 'x'), name='value')
        img = da.hvplot.image(transforms=dict(value=hv.dim('value') * 10))
        self.assertEqual(img.data.value.data, da.data * 10)
