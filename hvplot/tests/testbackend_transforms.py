import holoviews
import pytest
from holoviews.core import Store
from holoviews.element import Area, Curve

from hvplot.backend_transforms import (
    _transfer_opts,
    _transform_size_to_mpl,
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
def test_transform_size_to_mpl(width, height, aspect, opts):
    assert _transform_size_to_mpl(width, height, aspect) == opts


@pytest.mark.parametrize(
    ('element', 'opt', 'val', 'backend', 'opt_kind', 'transf_opt', 'transf_val'),
    (
        (Curve([]), 'line_dash', 'dashed', 'matplotlib', 'style', 'linestyle', 'dashed'),
        (Curve([]), 'line_alpha', 0.123, 'matplotlib', 'style', None, None),
        (Area([]), 'line_cap', 'square', 'matplotlib', 'style', 'capstyle', 'projecting'),
        (Curve([]), 'line_dash', 'dashed', 'plotly', 'style', 'dash', 'dash'),
    )
)
def test_transfer_opts(element, opt, val, backend, opt_kind, transf_opt, transf_val):
    current_backend = Store.current_backend
    if backend not in Store.registry:
        holoviews.extension(backend)
    Store.set_current_backend(backend)
    try:
        element = element.opts(backend='bokeh', **{opt: val})
        new_element = element.apply(_transfer_opts, backend=backend)
        new_opts = new_element.opts.get(opt_kind).kwargs
        if transf_opt is None:
            assert val not in new_opts.values()
        else:
            assert transf_opt in new_opts
            assert new_opts[transf_opt] == transf_val
    finally:
        Store.set_current_backend(current_backend)

@pytest.mark.parametrize(
    ('opt', 'val', 'backend', 'opt_kind', 'transf_opt', 'transf_val'),
    (
        ('line_dash', 'dashed', 'matplotlib', 'style', 'linestyle', 'dashed'),
        ('line_dash', 'dashed', 'plotly', 'style', 'dash', 'dash'),
    )
)
def test_transfer_opts_compositeoverlay(opt, val, backend, opt_kind, transf_opt, transf_val):
    current_backend = Store.current_backend
    if backend not in Store.registry:
        holoviews.extension(backend)
    Store.set_current_backend(backend)
    try:
        element = Area([]) * Curve([]).opts(backend='bokeh', **{opt: val})
        new_element = element.apply(_transfer_opts, backend=backend)
        transformed_element = new_element.Curve.I
        new_opts = transformed_element.opts.get(opt_kind).kwargs
        assert transf_opt in new_opts
        assert new_opts[transf_opt] == transf_val
    finally:
        Store.set_current_backend(current_backend)

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
