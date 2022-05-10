"""
Set of transforms to go from a Bokeh option to another backend's option.
"""
from holoviews.core.overlay import CompositeOverlay
from holoviews.core.options import Store
from holoviews.plotting.util import COLOR_ALIASES


UNSET = type('UNSET', (), {})


def _transform_size_to_mpl(width, height, aspect):
    opts = {}
    if width and height:
        opts = {'aspect': width/height, 'fig_size': (width/300.)*100}
    elif aspect and width:
        opts = {'aspect': aspect, 'fig_size': (width/300.)*100}
    elif aspect and height:
        opts = {'aspect': aspect, 'fig_size': (height/300.)*100}
    elif width:
        opts = {'fig_size': (width/300.)*100}
    elif height:
        opts = {'fig_size': (height/300.)*100}
    return opts


def _transfer_opts(element, backend):
    """
    Transfer the bokeh options of an element to another backend
    based on an internal mapping of option transforms.
    """
    elname = type(element).__name__
    options = Store.options(backend=backend)
    transforms = BACKEND_TRANSFORMS[backend]
    if isinstance(element, CompositeOverlay):
        element = element.apply(
            _transfer_opts, backend=backend, per_element=True
        )
    new_opts = {}
    el_options = element.opts.get(backend='bokeh', defaults=False).kwargs
    for grp, el_opts in options[elname].groups.items():
        for opt, val in el_options.items():
            transform = transforms.get(grp, {}).get(opt, None)
            # This condition could be applied to matplotlib only
            # but is applied to plotly too since there seems to be
            # no interactive options available like for the bokeh backend
            if transform is None and _is_interactive_opt(opt):
                transform = UNSET
            if transform is UNSET:
                continue
            elif transform:
                opt, val = transform(opt, val)
                if val is UNSET:
                    continue
            if opt not in el_opts.allowed_keywords:
                continue
            new_opts[opt] = val
    if backend == 'matplotlib':
        size_opts = _transform_size_to_mpl(
            el_options.get('width'), el_options.get('height'),
            el_options.get('aspect')
        )
        new_opts.update(size_opts)
    return element.opts(**new_opts, backend=backend)


def _is_interactive_opt(bk_opt):
    """
    Heuristics to detect if a bokeh option is about interactivity, like
    'selection_alpha'.

    >>> is_interactive_opt('height')
    False
    >>> is_interactive_opt('annular_muted_alpha')
    True
    """
    interactive_flags = [
        'hover',
        'muted',
        'nonselection',
        'selection',
    ]
    return any(part in interactive_flags for part in bk_opt.split('_'))


def _transfer_opts_cur_backend(element):
    if Store.current_backend != 'bokeh':
        element = element.apply(_transfer_opts, backend=Store.current_backend)
    return element


# Matplotlib transforms

_line_cap_bk_mpl_mapping = {
    'butt': 'butt',
    'round': 'round',
    'square': 'projecting',
}

_line_dash_bk_mpl_mapping = {
    'solid': 'solid',
    'dashed': 'dashed',
    'dotted': 'dotted',
    'dotdash': UNSET,
    'dashdot': 'dashdot',
}

_text_baseline_bk_mpl_mapping = {
    'top': 'top',
    'middle': 'center',
    'bottom': 'bottom',
    'alphabetic': UNSET,
    'hanging': UNSET,
    'ideographic': UNSET,
}

MATPLOTLIB_TRANSFORMS = {
    'plot': {
        'height': UNSET,
        'width': UNSET,
        'min_height': UNSET,
        'min_width': UNSET,
        'max_height': UNSET,
        'max_width': UNSET,
        'frame_width': UNSET,
        'frame_height': UNSET,
        'sizing_mode': UNSET,
        'responsive': UNSET,
        'shared_axes': UNSET,
        'shared_datasource': UNSET,
        'selected': UNSET,
        'tools': UNSET,
        'active_tools': UNSET,
        'default_tools': UNSET,
        'toolbar': UNSET,
        'align': UNSET,
        'lod': UNSET,
        'margin': UNSET,
        'border': UNSET,
        'jitter': UNSET,
        'legend_muted': UNSET,
        'legend_offset': UNSET,
        'gridstyle': UNSET,
        'colorbar_position': UNSET,
        'violin_width': UNSET,
    },
    'style': {
        'bar_width': UNSET,
        'size': lambda k, v: ('s', v),
        'fill_color': lambda k, v: ('facecolor', v),
        'fill_alpha': UNSET,
        'line_alpha': UNSET,
        'line_cap': lambda k, v: ('capstyle', _line_cap_bk_mpl_mapping.get(v, UNSET)),
        'line_color': lambda k, v: ('edgecolor', v),
        'line_dash': lambda k, v: ('linestyle', _line_dash_bk_mpl_mapping.get(v, UNSET)),
        'line_join': lambda k, v: ('joinstyle', v),
        'line_width': lambda k, v: ('linewidth', v),
        'palette': UNSET,
        'click_policy': UNSET,
        'annular_alpha': UNSET,
        'annular_color': UNSET,
        'annular_fill_alpha': UNSET,
        'annular_fill_color': UNSET,
        'annular_line_alpha': UNSET,
        'annular_line_cap': UNSET,
        'annular_line_color': lambda k, v: ('annular_edgecolors', v),
        'annular_line_dash': UNSET,
        'annular_line_join': UNSET,
        'annular_line_width': lambda k, v: ('annular_linewidth', v),
        'annular_visible': UNSET,
        'dilate': UNSET,
        'ticks_text_align': UNSET,
        'ticks_text_alpha': UNSET,
        'ticks_text_baseline': UNSET,
        'ticks_text_color': UNSET,
        'ticks_text_font': UNSET,
        'ticks_text_font_size': UNSET,
        'ticks_text_font_style': UNSET,
        'xmarks_alpha': UNSET,
        'xmarks_color': UNSET,
        'xmarks_line_alpha': UNSET,
        'xmarks_line_cap': UNSET,
        'xmarks_line_color': lambda k, v: ('xmarks_edgecolor', v),
        'xmarks_line_dash': UNSET,
        'xmarks_line_join': UNSET,
        'xmarks_line_width': lambda k, v: ('xmarks_linewidth', v),
        'xmarks_visible': UNSET,
        'ymarks_alpha': UNSET,
        'ymarks_color': UNSET,
        'ymarks_line_alpha': UNSET,
        'ymarks_line_cap': UNSET,
        'ymarks_line_color': lambda k, v: ('ymarks_edgecolor', v),
        'ymarks_line_dash': UNSET,
        'ymarks_line_join': UNSET,
        'ymarks_line_width': lambda k, v: ('ymarks_linewidth', v),
        'ymarks_visible': UNSET,
        'lower_head': lambda k, v: ('lolims', v),
        'upper_head': lambda k, v: ('uplims', v),
        'whisker_color': UNSET,
        'outlier_color': UNSET,
        'text_align': lambda k, v: ('horizontalalignment', v),
        'text_alpha': lambda k, v: ('alpha', v),
        'text_baseline': lambda k, v: ('verticalalignment', _text_baseline_bk_mpl_mapping.get(v, UNSET)),
        'text_color': lambda k, v: ('color', v),
        'text_font': UNSET, 
        'text_font_size': lambda k, v: ('size', v),
        'text_font_style': UNSET,
        'box_alpha': UNSET,
        'box_cmap': UNSET,
        'box_fill_alpha': UNSET,
        'box_fill_color': UNSET,
        'box_line_alpha': UNSET,
        'box_line_cap': UNSET,
        'box_line_color': UNSET,
        'box_line_dash': UNSET,
        'box_line_join': UNSET,
        'box_line_width': UNSET,
        'box_visible': UNSET,
        'median_alpha': UNSET,
        'median_color': UNSET,
        'outline_alpha': UNSET,
        'outline_color': UNSET,
        'outline_line_alpha': UNSET,
        'outline_line_cap': UNSET,
        'outline_line_color': UNSET,
        'outline_line_dash': UNSET,
        'outline_line_join': UNSET,
        'outline_line_width': UNSET,
        'outline_visible': UNSET,
        'stats_alpha': UNSET,
        'stats_line_alpha': UNSET,
        'stats_line_cap': UNSET,
        'stats_line_color': UNSET,
        'stats_line_dash': UNSET,
        'stats_line_join': UNSET,
        'stats_line_width': UNSET,
        'stats_visible': UNSET,
        'violin_alpha': UNSET,
        'violin_cmap': UNSET,
        'violin_color': UNSET,
        'violin_fill_alpha': UNSET,
        'violin_fill_color': UNSET,
        'violin_line_alpha': UNSET,
        'violin_line_cap': UNSET,
        'violin_line_color': UNSET,
        'violin_line_dash': UNSET,
        'violin_line_join': UNSET,
        'violin_line_width': UNSET,
        'violin_visible': UNSET,
        'editable': UNSET,
        'fit_columns': UNSET,
        'index_position': UNSET,
        'row_headers': UNSET,
        'scroll_to_selection': UNSET,
        'selectable': UNSET,
        'sortable': UNSET,
        'edge_alpha': lambda k, v: ('edge_alpha', v),
        'edge_cmap': lambda k, v: ('edge_cmap', v),
        'edge_color': lambda k, v: ('edge_color', v),
        'edge_fill_alpha': UNSET,
        'edge_fill_color': UNSET,
        'edge_line_alpha': UNSET,
        'edge_line_cap': UNSET,
        'edge_line_color': lambda k, v: ('edge_color', v),
        'edge_line_dash': lambda k, v: ('edge_linestyle', v),
        'edge_line_join': UNSET,
        'edge_line_width': lambda k, v: ('edge_linewidth', v),
        'edge_visible': UNSET,  
        'node_alpha': lambda k, v: ('node_alpha', v), 
        'node_cmap': lambda k, v: ('node_cmap', v), 
        'node_color': lambda k, v: ('node_color', v), 
        'node_fill_alpha': UNSET, 
        'node_fill_color': lambda k, v: ('node_facecolors', v), 
        'node_line_alpha': UNSET, 
        'node_line_cap': UNSET, 
        'node_line_color': lambda k, v: ('node_edgecolors', v), 
        'node_line_dash': UNSET, 
        'node_line_join': UNSET, 
        'node_line_width': lambda k, v: ('node_linewidth', v), 
        'node_marker': lambda k, v: ('node_marker', v), 
        'node_radius': UNSET, 
        'node_size': lambda k, v: ('node_size', v), 
        'node_visible': lambda k, v: ('visible', v),
    },
}

# Plotly transforms

_line_dash_bk_plotly_mapping = {
    'solid': 'solid',
    'dashed': 'dash',
    'dotted': 'dot',
    'dotdash': UNSET,
    'dashdot': 'dashdot',
}

PLOTLY_TRANSFORMS = {
    'plot': {
        'alpha': lambda k, v: ('opacity', v),
        'min_height': UNSET,
        'min_width': UNSET,
        'max_height': UNSET,
        'max_width': UNSET,
        'frame_width': UNSET,
        'frame_height': UNSET,
        'batched': UNSET,
        'legend_limit': UNSET,
        'tools': UNSET,
        'shared_xaxis': UNSET,
        'shared_yaxis': UNSET,
    },
    'style': {
        'alpha': lambda k, v: ('opacity', v),
        'color': lambda k, v: (k, COLOR_ALIASES.get(v, v)),
        'fill_color': lambda k, v: ('fillcolor', COLOR_ALIASES.get(v, v)),
        'line_color': lambda k, v: (k, COLOR_ALIASES.get(v, v)),
        'line_dash': lambda k, v: ('dash', _line_dash_bk_plotly_mapping.get(v, UNSET)),
        'line_width': lambda k, v: ('line_width', v),
        'muted_alpha': UNSET,
        'palette': UNSET,
    }
}


BACKEND_TRANSFORMS = dict(
    matplotlib=MATPLOTLIB_TRANSFORMS,
    plotly=PLOTLY_TRANSFORMS,
)
