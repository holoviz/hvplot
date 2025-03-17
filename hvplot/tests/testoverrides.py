from collections import OrderedDict

import numpy as np
import pandas as pd
import pytest
import xarray as xr

from hvplot.plotting import hvPlot, hvPlotTabular
from holoviews import Store, Scatter
from holoviews.element.comparison import ComparisonTestCase


class TestOverrides(ComparisonTestCase):
    def setUp(self):
        import hvplot.pandas  # noqa

        self.df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])

    def test_define_default_options(self):
        hvplot = hvPlotTabular(self.df, width=42, height=42)
        curve = hvplot(y='y')
        opts = Store.lookup_options('bokeh', curve, 'plot')
        self.assertEqual(opts.options.get('width'), 42)
        self.assertEqual(opts.options.get('height'), 42)

    def test_define_custom_method(self):
        hvplot = hvPlotTabular(self.df, {'custom_scatter': {'width': 42, 'height': 42}})
        custom_scatter = hvplot.custom_scatter(y='y')
        scatter = hvplot.scatter(y='y')
        custom_opts = Store.lookup_options('bokeh', custom_scatter, 'plot')
        opts = Store.lookup_options('bokeh', scatter, 'plot')
        self.assertEqual(custom_opts.options.get('width'), 42)
        self.assertEqual(custom_opts.options.get('height'), 42)
        self.assertNotEqual(opts.options.get('width'), 42)
        self.assertNotEqual(opts.options.get('height'), 42)

    def test_define_customize_method(self):
        hvplot = hvPlotTabular(self.df, {'scatter': {'width': 42, 'height': 42}})
        custom_scatter = hvplot.scatter(y='y')
        curve = hvplot.line(y='y')
        custom_opts = Store.lookup_options('bokeh', custom_scatter, 'plot')
        opts = Store.lookup_options('bokeh', curve, 'plot')
        self.assertEqual(custom_opts.options.get('width'), 42)
        self.assertEqual(custom_opts.options.get('height'), 42)
        self.assertNotEqual(opts.options.get('width'), 42)
        self.assertNotEqual(opts.options.get('height'), 42)

    @pytest.mark.usefixtures('disable_param_warnings_as_exceptions')
    def test_attempt_to_override_kind_on_method(self):
        hvplot = hvPlotTabular(self.df, {'scatter': {'kind': 'line'}})
        self.assertIsInstance(hvplot.scatter(y='y'), Scatter)

    def test_pandas_query_metadata(self):
        hvplot = hvPlotTabular(self.df, query='x>2')
        assert len(hvplot._data) == 2


class TestXArrayOverrides(ComparisonTestCase):
    def setUp(self):
        coords = OrderedDict([('time', [0, 1]), ('lat', [0, 1]), ('lon', [0, 1])])
        self.da_img_by_time = xr.DataArray(
            np.arange(8).reshape((2, 2, 2)), coords, ['time', 'lat', 'lon']
        ).assign_coords(lat1=xr.DataArray([2, 3], dims=['lat']))

    def test_xarray_isel_scalar_metadata(self):
        hvplot = hvPlot(self.da_img_by_time, isel={'time': 1})
        assert hvplot._data.ndim == 2

    def test_xarray_isel_nonscalar_metadata(self):
        hvplot = hvPlot(self.da_img_by_time, isel={'time': [1]})
        assert hvplot._data.ndim == 3
        assert len(hvplot._data.time) == 1

    def test_xarray_sel_metadata(self):
        hvplot = hvPlot(self.da_img_by_time, sel={'time': 1})
        assert hvplot._data.ndim == 2
