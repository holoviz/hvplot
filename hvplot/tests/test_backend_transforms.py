import pandas as pd
import pytest
from holoviews.core import Store
from holoviews.element import Area, Curve

import hvplot
from hvplot.backend_transforms import (
    _is_interactive_opt,
    _transfer_opts,
    _transform_size_to_mpl,
)


@pytest.mark.parametrize(
    ('width', 'height', 'aspect', 'opts'),
    (
        (300, 100, None, {'aspect': 3.0, 'fig_size': 100.0}),
        (300, None, 3, {'aspect': 3, 'fig_size': 100.0}),
        (None, 300, 3, {'aspect': 3, 'fig_size': 100.0}),
        (300, None, None, {'fig_size': 100.0}),
        (None, 300, None, {'fig_size': 100.0}),
    ),
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
    ),
)
def test_transfer_opts(element, opt, val, backend, opt_kind, transf_opt, transf_val):
    Store.set_current_backend(backend)
    element = element.opts(backend='bokeh', **{opt: val})
    new_element = element.apply(_transfer_opts, backend=backend)
    new_opts = new_element.opts.get(opt_kind).kwargs
    if transf_opt is None:
        assert val not in new_opts.values()
    else:
        assert transf_opt in new_opts
        assert new_opts[transf_opt] == transf_val


@pytest.mark.parametrize(
    ('opt', 'val', 'backend', 'opt_kind', 'transf_opt', 'transf_val'),
    (
        ('line_dash', 'dashed', 'matplotlib', 'style', 'linestyle', 'dashed'),
        ('line_dash', 'dashed', 'plotly', 'style', 'dash', 'dash'),
    ),
)
def test_transfer_opts_compositeoverlay(opt, val, backend, opt_kind, transf_opt, transf_val):
    Store.set_current_backend(backend)
    element = Area([]) * Curve([]).opts(backend='bokeh', **{opt: val})
    new_element = element.apply(_transfer_opts, backend=backend)
    transformed_element = new_element.Curve.I
    new_opts = transformed_element.opts.get(opt_kind).kwargs
    assert transf_opt in new_opts
    assert new_opts[transf_opt] == transf_val


@pytest.mark.usefixtures('hvplot_pandas')
@pytest.mark.parametrize(
    ('backend_name', 'kind', 'kwargs', 'style_opt', 'expected'),
    [
        ('matplotlib', 'line', {'line_width': 3}, 'linewidth', 3),
        ('matplotlib', 'line', {'line_dash': 'dashed'}, 'linestyle', 'dashed'),
        ('matplotlib', 'area', {'fill_color': 'red'}, 'facecolor', 'red'),
        ('matplotlib', 'area', {'line_color': 'red'}, 'edgecolor', 'red'),
        ('matplotlib', 'scatter', {'alpha': 0.5}, 'alpha', 0.5),
        ('plotly', 'line', {'line_width': 3}, 'line_width', 3),
        ('plotly', 'line', {'line_dash': 'dashed'}, 'dash', 'dash'),
        pytest.param(
            'plotly',
            'scatter',
            {'alpha': 0.5},
            'alpha',
            0.5,
            marks=pytest.mark.xfail(
                reason='BUG: alpha is renamed to opacity, which plotly ignores, so it is dropped',
                raises=KeyError,
            ),
        ),
    ],
)
def test_bokeh_options_translated(backend_name, kind, kwargs, style_opt, expected):
    hvplot.extension(backend_name, compatibility='bokeh')
    df = pd.DataFrame({'x': [1, 3, 5], 'y': [2, 4, 6]})
    plot = getattr(df.hvplot, kind)('x', 'y', **kwargs)
    style = Store.lookup_options(backend_name, plot, 'style').kwargs
    assert style[style_opt] == expected


@pytest.mark.parametrize(
    ('bk_option', 'expected'),
    (
        ('height', False),
        ('hover_line_alpha', True),
        ('nonselection_line_alpha', True),
        ('muted_line_alpha', True),
        ('selection_line_alpha', True),
        ('annular_muted_alpha', True),
    ),
)
def test_is_interactive_opt(bk_option, expected):
    assert _is_interactive_opt(bk_option) == expected
