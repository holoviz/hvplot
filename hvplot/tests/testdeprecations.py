"""
Tests for deprecation warnings.
"""

import pandas as pd
import pytest

from hvplot.converter import HoloViewsConverter
from hvplot.plotting import plot
from hvplot.tests.util import makeDataFrame


def test_converter_argument_debug(disable_param_warnings_as_exceptions):
    df = pd.DataFrame({'x': [0, 1], 'y': [0, 1]})
    with pytest.warns(FutureWarning):
        HoloViewsConverter(df, 'x', 'y', debug=True)


def test_plotting_plot_duckdb():
    duckdb = pytest.importorskip('duckdb')
    connection = duckdb.connect(':memory:')
    relation = duckdb.from_df(makeDataFrame(), connection=connection)
    with pytest.warns(FutureWarning):
        plot(relation, 'line')


def test_converter_argument_hover_formatters():
    df = pd.DataFrame({'x': [0, 1], 'y': [0, 1]})
    with pytest.warns(DeprecationWarning):
        HoloViewsConverter(df, 'x', 'y', hover_formatters={'@{y}': 'printf'})
