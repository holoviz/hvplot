"""Check that every kind has a test module, with a test for each of its options."""

import importlib
from importlib.util import find_spec

import pytest

from hvplot.converter import HoloViewsConverter
from hvplot.tests._inventory import collect_test_names, options_with_test


def test_kind_options_keys_are_kinds():
    # A key that is not a kind (e.g. a typo) would otherwise be silently ignored.
    assert set(HoloViewsConverter._kind_options) <= set(HoloViewsConverter._kind_mapping)


@pytest.mark.parametrize('kind', sorted(HoloViewsConverter._kind_mapping))
def test_kind_has_module(kind):
    assert find_spec(f'hvplot.tests.kinds.test_{kind}'), (
        f'Add the module hvplot/tests/kinds/test_{kind}.py'
    )


@pytest.mark.parametrize(
    ('kind', 'option'),
    [
        (kind, option)
        for kind in sorted(HoloViewsConverter._kind_mapping)
        for option in HoloViewsConverter._kind_options.get(kind, [])
    ],
)
def test_kind_option_has_test(kind, option):
    if not find_spec(f'hvplot.tests.kinds.test_{kind}'):
        pytest.fail(f'Add the module hvplot/tests/kinds/test_{kind}.py')
    module = importlib.import_module(f'hvplot.tests.kinds.test_{kind}')
    options = HoloViewsConverter._kind_options[kind]
    assert option in options_with_test(collect_test_names(module), options), (
        f'Add a test named test_{option} or test_{option}_<detail> '
        f'to hvplot/tests/kinds/test_{kind}.py'
    )
