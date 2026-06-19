"""
Tests for deprecation warnings.
"""

import os
import sys
import importlib
import tempfile
import pandas as pd
import pytest

from hvplot import hvPlot
from hvplot.converter import HoloViewsConverter
from hvplot.plotting import plot
from hvplot.tests.util import makeDataFrame
from hvplot.util import _HV_VERSION


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


def test_streamz_patch():
    pytest.importorskip('streamz')
    if _HV_VERSION >= (1, 23, 0):
        pytest.skip('streamz support has been removed in HoloViews >= 1.23.0')
    with pytest.warns(
        FutureWarning,
        match='streamz support has been deprecated',
    ):
        from hvplot.streamz import patch

        patch()


def test_sample_data_deprecation():
    pytest.importorskip('intake')
    pytest.importorskip('intake_parquet')
    pytest.importorskip('intake_xarray')
    pytest.importorskip('s3fs')
    with pytest.warns(FutureWarning):
        importlib.import_module('hvplot.sample_data')
    sys.modules.pop('hvplot.sample_data', None)


def test_intake_deprecation():
    pytest.importorskip('intake')
    with pytest.warns(FutureWarning):
        importlib.import_module('hvplot.intake')
    sys.modules.pop('hvplot.intake', None)


def test_intake_datasource_hvplot_deprecation(disable_param_warnings_as_exceptions):
    intake = pytest.importorskip('intake')

    from intake.source.base import DataSource

    # Patch .hvplot onto DataSource manually to avoid importing hvplot.intake,
    # which fires its own separate FutureWarning and would pollute this test.
    if not hasattr(DataSource, 'hvplot'):
        DataSource.hvplot = property(lambda self: hvPlot(self))

    df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
        df.to_csv(f, index=False)
        tmppath = f.name

    try:
        src = intake.open_csv(tmppath)
        with pytest.warns(FutureWarning, match='intake DataSource'):
            src.hvplot.line(x='x', y='y')
    finally:
        os.unlink(tmppath)
