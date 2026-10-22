import importlib

import pytest


def test_sample_data_without_intake(block_import):
    # Loading the catalog itself needs intake plugins and the network, not tested.
    block_import('intake')
    with (
        pytest.warns(FutureWarning, match="'hvplot.sample_data' module is deprecated"),
        pytest.raises(ImportError, match='Loading hvPlot sample data requires'),
    ):
        importlib.import_module('hvplot.sample_data')
