from hvplot.backend_transforms import is_interactive_opt

import pytest

@pytest.mark.parametrize(
    ('bk_option', 'expected'),
    (
        ('height', False),
        ('hover_line_alpha', True),
        ('nonselection_line_alpha', True),
        ('muted_line_alpha', True),
        ('selection_line_alpha', True),
        ('annular_muted_alpha', True)
    )
)
def test_is_interactive_opt(bk_option, expected):
    assert is_interactive_opt(bk_option) == expected
