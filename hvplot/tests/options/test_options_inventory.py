"""Check that every plot option has a test, in the module of its group."""

import importlib

import pytest

from hvplot.converter import HoloViewsConverter
from hvplot.tests._inventory import collect_test_names, options_with_test


@pytest.mark.parametrize(
    ('group', 'option'),
    [
        (group, option)
        for group, options in HoloViewsConverter._options_groups.items()
        for option in options
    ],
)
def test_option_has_test(group, option):
    module = importlib.import_module(f'hvplot.tests.options.test_{group}')
    options = HoloViewsConverter._options_groups[group]
    assert option in options_with_test(collect_test_names(module), options), (
        f'Add a test named test_{option} or test_{option}_<detail> '
        f'to hvplot/tests/options/test_{group}.py'
    )
