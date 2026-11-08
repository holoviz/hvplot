"""Helpers for the meta tests checking that every option and kind has a test."""


def collect_test_names(module):
    """Return the names of the test functions and test methods of a module."""
    names = [name for name in vars(module) if name.startswith('test_')]
    for name, obj in vars(module).items():
        if name.startswith('Test') and isinstance(obj, type):
            names.extend(attr for attr in vars(obj) if attr.startswith('test_'))
    return names


def options_with_test(test_names, options):
    """Return the options that have a test named `test_<option>` or `test_<option>_<detail>`.

    A test name counts for the longest option it starts with, e.g. `test_color_key_*`
    counts for `color_key` and not for `color`. Matching ignores case, for `C`.
    """
    tested = set()
    for test_name in test_names:
        test_name = test_name.lower()
        matches = [
            option
            for option in options
            if test_name == f'test_{option.lower()}'
            or test_name.startswith(f'test_{option.lower()}_')
        ]
        if matches:
            tested.add(max(matches, key=len))
    return tested
