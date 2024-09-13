"""
Tests pandas.options.backend setting
"""

from unittest import TestCase

import holoviews as hv
import pandas as pd
import pytest

from parameterized import parameterized

from hvplot.converter import HoloViewsConverter
from hvplot.plotting import plot
from hvplot.tests.util import makeDataFrame

no_args = ['line', 'area', 'hist', 'box', 'kde', 'density', 'bar', 'barh']
x_y = ['scatter', 'hexbin']

no_args_mapping = [
    (kind, el) for kind, el in HoloViewsConverter._kind_mapping.items() if kind in no_args
]
x_y_mapping = [(kind, el) for kind, el in HoloViewsConverter._kind_mapping.items() if kind in x_y]


class TestPandasHoloviewsPlotting(TestCase):
    def setUp(self):
        pd.options.plotting.backend = 'holoviews'

    @parameterized.expand(no_args_mapping)
    def test_pandas_series_plot_returns_holoviews_object(self, kind, el):
        series = pd.Series([0, 1, 2])
        plot = getattr(series.plot, kind)()
        self.assertIsInstance(plot, el)

    @parameterized.expand(no_args_mapping)
    def test_pandas_dataframe_plot_returns_holoviews_object(self, kind, el):
        df = pd.DataFrame([0, 1, 2])
        plot = getattr(df.plot, kind)()
        self.assertIsInstance(plot, el)

    @parameterized.expand(x_y_mapping)
    def test_pandas_dataframe_plot_returns_holoviews_object_when_x_and_y_set(self, kind, el):
        df = pd.DataFrame({'a': [0, 1, 2], 'b': [5, 7, 2]})
        plot = getattr(df.plot, kind)(x='a', y='b')
        self.assertIsInstance(plot, el)

    def test_pandas_dataframe_plot_does_not_implement_pie(self):
        df = pd.DataFrame({'a': [0, 1, 2], 'b': [5, 7, 2]})
        with self.assertRaisesRegex(NotImplementedError, 'pie'):
            df.plot.pie(y='a')


class TestPandasHvplotPlotting(TestPandasHoloviewsPlotting):
    def setUp(self):
        pd.options.plotting.backend = 'hvplot'


def test_plot_supports_polars():
    pl = pytest.importorskip('polars')
    dfp = pl.DataFrame(makeDataFrame())
    out = plot(dfp, 'line')
    assert isinstance(out, hv.NdOverlay)
    assert out.keys() == dfp.columns
