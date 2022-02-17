import holoviews.plotting.mpl  # noqa
import pytest
from holoviews.element import Area, Curve

from hvplot.backend_transforms import (
    _transfer_opts,
    _transform_size,
    _is_interactive_opt,
)


@pytest.mark.parametrize(
    ('width', 'height', 'aspect', 'opts'),
    (
        (300, 100, None, {'aspect': 3.0, 'fig_size': 100.0}),
        (300, None, 3, {'aspect': 3, 'fig_size': 100.0}),
        (None, 300, 3, {'aspect': 3, 'fig_size': 100.0}),
        (300, None, None, {'fig_size': 100.0}),
        (None, 300, None, {'fig_size': 100.0}),
    )
)
def test_transform_size(width, height, aspect, opts):
    assert _transform_size(width, height, aspect) == opts

@pytest.mark.parametrize(
    ('element', 'opt', 'val', 'backend', 'opt_kind', 'transf_opt', 'transf_val'),
    (
        (Curve([]), 'line_dash', '-', 'matplotlib', 'style', 'linestyle', '-'),
        (Curve([]), 'line_alpha', 0.123, 'matplotlib', 'style', None, None),
        (Area([]), 'line_cap', 'square', 'matplotlib', 'style', 'capstyle', 'projecting'),
    )
)
def test_transfer_opts(element, opt, val, backend, opt_kind, transf_opt, transf_val):
    element = element.opts(backend='bokeh', **{opt: val})
    new_element = element.apply(_transfer_opts, backend=backend)
    new_opts = new_element.opts.get(opt_kind).kwargs
    if transf_opt is None:
        assert val not in new_opts.values()
    else:
        assert new_opts[transf_opt] == transf_val


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
    assert _is_interactive_opt(bk_option) == expected
