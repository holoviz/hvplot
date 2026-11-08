import importlib
import sys

import pytest

import hvplot
from hvplot.tests._deps import requires


@requires('hvsampledata')
def test_sampledata_exposes_hvsampledata():
    import hvsampledata

    # Only the loader functions are compared, calling them may download data.
    assert hvplot.sampledata.penguins is hvsampledata.penguins
    assert hvplot.sampledata.air_temperature is hvsampledata.air_temperature


@requires('hvsampledata')
def test_sampledata_unknown_dataset():
    with pytest.raises(AttributeError, match="has no attribute 'unknown'"):
        hvplot.sampledata.unknown  # noqa: B018


def test_sampledata_without_hvsampledata(block_import, monkeypatch):
    block_import('hvsampledata')
    # Import a fresh hvplot.sampledata, both restored after the test.
    monkeypatch.setattr(hvplot, 'sampledata', hvplot.sampledata)
    monkeypatch.delitem(sys.modules, 'hvplot.sampledata')
    sampledata = importlib.import_module('hvplot.sampledata')

    with pytest.raises(AttributeError, match="Install the package 'hvsampledata'"):
        sampledata.penguins  # noqa: B018
