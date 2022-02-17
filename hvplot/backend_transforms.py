"""
Set of transforms to go from a Bokeh option to another backend's option.
"""
from holoviews.core.overlay import CompositeOverlay
from holoviews.core.options import Store
from holoviews.plotting.util import COLOR_ALIASES


UNSET = type('UNSET', (), {})

def _transform_size(width, height, aspect):
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
    elname = type(element).__name__
    options = Store.options(backend=backend)
    transforms = BACKEND_TRANSFORMS[backend]
    if isinstance(element, CompositeOverlay):
        element = element.apply(
            _transfer_opts, backend=backend, per_element=True
        )
    new_opts = {}
    # print(new_opts)
    el_options = element.opts.get(backend='bokeh', defaults=False).kwargs
    print('el_options\n', el_options)
    for grp, el_opts in options[elname].groups.items():
        print(grp, 'el_options allowed_keywords\n', el_opts.allowed_keywords)
        for opt, val in el_options.items():
            if backend == 'matplotlib' and is_interactive_opt(opt):
                transform = UNSET
            # print('    < before', opt, val)
            transform = transforms.get(grp, {}).get(opt, None)
            if transform is UNSET:
                print(f'Element: {elname: <10} | {backend: <10} | {grp: <6} | {opt: <20}: UNSET')
                continue
            elif transform:
                opt, val = transform(opt, val)
                if val is UNSET:
                    print(f'Element: {elname: <10} | {backend: <10} | {grp: <6} | {opt: <20}: UNSET')
                    continue
                print(f'Element: {elname: <10} | {backend: <10} | {grp: <6} | {opt: <20}: Transformed')
            if opt not in el_opts.allowed_keywords:
                if transform:
                    print(f'Element: {elname: <10} | {backend: <10} | {grp: <6} | {opt: <20}: Transformed but not supported by this element')
                else:
                    print(f'Element: {elname: <10} | {backend: <10} | {grp: <6} | {opt: <20}: Not supported at all')
                continue
            # print('    > after   ', opt, val)
            new_opts[opt] = val
    # print(new_opts)
    if backend == 'matplotlib':
        size_opts = _transform_size(
            el_options.get('width'), el_options.get('height'),
            el_options.get('aspect')
        )
        new_opts.update(size_opts)
    print(new_opts)
    new_element = element.opts(**new_opts, backend=backend)
    # breakpoint()
    return new_element

# Matplotlib transforms

_line_cap_bk_mpl_mapping = {
    'butt': 'butt',
    'round': 'round',
    'square': 'projecting',
}
_text_baseline_bk_mpl_mapping = {
    'top': 'top',
    'middle': 'center',
    'bottom': 'bottom',
    'alphabetic': UNSET,
    'hanging': UNSET,
    'ideographic': UNSET,
}

def is_interactive_opt(bk_opt):
    """
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
        'line_cap': lambda k, v: ('capstyle', _line_cap_bk_mpl_mapping.get(v, v)),
        'line_color': lambda k, v: ('edgecolor', v),
        'line_dash': lambda k, v: ('linestyle', v),
        'line_join': lambda k, v: ('joinstyle', v),
        'line_width': lambda k, v: ('linewidth', v),
        'nonselection_alpha': UNSET,
        'nonselection_color': UNSET,
        'nonselection_line_alpha': UNSET,
        'nonselection_line_color': UNSET,
        'selection_alpha': UNSET,
        'selection_color': UNSET,
        'selection_line_alpha': UNSET,
        'selection_line_color': UNSET,
        'hover_alpha': UNSET,
        'hover_color': UNSET,
        'hover_line_alpha': UNSET,
        'hover_line_color': UNSET,
        'muted': UNSET,
        'muted_alpha': UNSET,
        'muted_color': UNSET,
        'muted_line_alpha': UNSET,
        'muted_line_color': UNSET,
        'click_policy': UNSET,
        'annular_alpha': UNSET,
        'annular_color': UNSET,
        'annular_fill_alpha': UNSET,
        'annular_fill_color': UNSET,
        'annular_hover_alpha': UNSET,
        'annular_hover_color': UNSET,
        'annular_hover_fill_alpha': UNSET,
        'annular_hover_fill_color': UNSET,
        'annular_hover_line_alpha': UNSET,
        'annular_hover_line_color': UNSET,
        'annular_line_alpha': UNSET,
        'annular_line_cap': UNSET,
        'annular_line_color': lambda k, v: ('annular_edgecolors', v),
        'annular_line_dash': UNSET,
        'annular_line_join': UNSET,
        'annular_line_width': lambda k, v: ('annular_linewidth', v),
        'annular_muted': UNSET,
        'annular_muted_alpha': UNSET,
        'annular_muted_color': UNSET,
        'annular_muted_fill_alpha': UNSET,
        'annular_muted_fill_color': UNSET,
        'annular_muted_line_alpha': UNSET,
        'annular_muted_line_color': UNSET,
        'annular_nonselection_alpha': UNSET,
        'annular_nonselection_color': UNSET,
        'annular_nonselection_fill_alpha': UNSET,
        'annular_nonselection_fill_color': UNSET,
        'annular_nonselection_line_alpha': UNSET,
        'annular_nonselection_line_color': UNSET,
        'annular_selection_alpha': UNSET,
        'annular_selection_color': UNSET,
        'annular_selection_fill_alpha': UNSET,
        'annular_selection_fill_color': UNSET,
        'annular_selection_line_alpha': UNSET,
        'annular_selection_line_color': UNSET,
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
        'xmarks_hover_alpha': UNSET,
        'xmarks_hover_color': UNSET,
        'xmarks_hover_line_alpha': UNSET,
        'xmarks_hover_line_color': UNSET,
        'xmarks_line_alpha': UNSET,
        'xmarks_line_cap': UNSET,
        'xmarks_line_color': lambda k, v: ('xmarks_edgecolor', v),
        'xmarks_line_dash': UNSET,
        'xmarks_line_join': UNSET,
        'xmarks_line_width': lambda k, v: ('xmarks_linewidth', v),
        'xmarks_muted': UNSET,
        'xmarks_muted_alpha': UNSET,
        'xmarks_muted_color': UNSET,
        'xmarks_muted_line_alpha': UNSET,
        'xmarks_muted_line_color': UNSET,
        'xmarks_nonselection_alpha': UNSET,
        'xmarks_nonselection_color': UNSET,
        'xmarks_nonselection_line_alpha': UNSET,
        'xmarks_nonselection_line_color': UNSET,
        'xmarks_selection_alpha': UNSET,
        'xmarks_selection_color': UNSET,
        'xmarks_selection_line_alpha': UNSET,
        'xmarks_selection_line_color': UNSET,
        'xmarks_visible': UNSET,
        'ymarks_alpha': UNSET,
        'ymarks_color': UNSET,
        'ymarks_hover_alpha': UNSET,
        'ymarks_hover_color': UNSET,
        'ymarks_hover_line_alpha': UNSET,
        'ymarks_hover_line_color': UNSET,
        'ymarks_line_alpha': UNSET,
        'ymarks_line_cap': UNSET,
        'ymarks_line_color': lambda k, v: ('ymarks_edgecolor', v),
        'ymarks_line_dash': UNSET,
        'ymarks_line_join': UNSET,
        'ymarks_line_width': lambda k, v: ('ymarks_linewidth', v),
        'ymarks_muted': UNSET,
        'ymarks_muted_alpha': UNSET,
        'ymarks_muted_color': UNSET,
        'ymarks_muted_line_alpha': UNSET,
        'ymarks_muted_line_color': UNSET,
        'ymarks_nonselection_alpha': UNSET,
        'ymarks_nonselection_color': UNSET,
        'ymarks_nonselection_line_alpha': UNSET,
        'ymarks_nonselection_line_color': UNSET,
        'ymarks_selection_alpha': UNSET,
        'ymarks_selection_color': UNSET,
        'ymarks_selection_line_alpha': UNSET,
        'ymarks_selection_line_color': UNSET,
        'ymarks_visible': UNSET,
        'lower_head': lambda k, v: ('lolims', v),
        'upper_head': lambda k, v: ('uplims', v),
        'whisker_color': UNSET,
        'outlier_color': UNSET,
        'text_align': lambda k, v: ('horizontalalignment', v),
        'text_alpha': lambda k, v: ('alpha', v),
        'text_baseline': lambda k, v: ('verticalalignment', _text_baseline_bk_mpl_mapping.get(v, v)),
        'text_color': lambda k, v: ('color', v),
        'text_font': UNSET, 
        'text_font_size': lambda k, v: ('size', v),
        'text_font_style': UNSET,
        'box_alpha': UNSET,
        'box_cmap': UNSET,
        'box_fill_alpha': UNSET,
        'box_fill_color': UNSET,
        'box_hover_alpha': UNSET,
        'box_hover_color': UNSET,
        'box_hover_fill_alpha': UNSET,
        'box_hover_fill_color': UNSET,
        'box_hover_line_alpha': UNSET,
        'box_hover_line_color': UNSET,
        'box_line_alpha': UNSET,
        'box_line_cap': UNSET,
        'box_line_color': UNSET,
        'box_line_dash': UNSET,
        'box_line_join': UNSET,
        'box_line_width': UNSET,
        'box_muted': UNSET,
        'box_muted_alpha': UNSET,
        'box_muted_color': UNSET,
        'box_muted_fill_alpha': UNSET,
        'box_muted_fill_color': UNSET,
        'box_muted_line_alpha': UNSET,
        'box_muted_line_color': UNSET,
        'box_nonselection_alpha': UNSET,
        'box_nonselection_color': UNSET,
        'box_nonselection_fill_alpha': UNSET,
        'box_nonselection_fill_color': UNSET,
        'box_nonselection_line_alpha': UNSET,
        'box_nonselection_line_color': UNSET,
        'box_selection_alpha': UNSET,
        'box_selection_color': UNSET,
        'box_selection_fill_alpha': UNSET,
        'box_selection_fill_color': UNSET,
        'box_selection_line_alpha': UNSET,
        'box_selection_line_color': UNSET,
        'box_visible': UNSET,
        'median_alpha': UNSET,
        'median_color': UNSET,
        'outline_alpha': UNSET,
        'outline_color': UNSET,
        'outline_hover_alpha': UNSET,
        'outline_hover_color': UNSET,
        'outline_hover_line_alpha': UNSET,
        'outline_hover_line_color': UNSET,
        'outline_line_alpha': UNSET,
        'outline_line_cap': UNSET,
        'outline_line_color': UNSET,
        'outline_line_dash': UNSET,
        'outline_line_join': UNSET,
        'outline_line_width': UNSET,
        'outline_muted': UNSET,
        'outline_muted_alpha': UNSET,
        'outline_muted_color': UNSET,
        'outline_muted_line_alpha': UNSET,
        'outline_muted_line_color': UNSET,
        'outline_nonselection_alpha': UNSET,
        'outline_nonselection_color': UNSET,
        'outline_nonselection_line_alpha': UNSET,
        'outline_nonselection_line_color': UNSET,
        'outline_selection_alpha': UNSET,
        'outline_selection_color': UNSET,
        'outline_selection_line_alpha': UNSET,
        'outline_selection_line_color': UNSET,
        'outline_visible': UNSET,
        'stats_alpha': UNSET,
        'stats_hover_alpha': UNSET,
        'stats_hover_color': UNSET,
        'stats_hover_line_alpha': UNSET,
        'stats_hover_line_color': UNSET,
        'stats_line_alpha': UNSET,
        'stats_line_cap': UNSET,
        'stats_line_color': UNSET,
        'stats_line_dash': UNSET,
        'stats_line_join': UNSET,
        'stats_line_width': UNSET,
        'stats_muted': UNSET,
        'stats_muted_alpha': UNSET,
        'stats_muted_color': UNSET,
        'stats_muted_line_alpha': UNSET,
        'stats_muted_line_color': UNSET,
        'stats_nonselection_alpha': UNSET,
        'stats_nonselection_color': UNSET,
        'stats_nonselection_line_alpha': UNSET,
        'stats_nonselection_line_color': UNSET,
        'stats_selection_alpha': UNSET,
        'stats_selection_color': UNSET,
        'stats_selection_line_alpha': UNSET,
        'stats_selection_line_color': UNSET,
        'stats_visible': UNSET,
        'violin_alpha': UNSET,
        'violin_cmap': UNSET,
        'violin_color': UNSET,
        'violin_fill_alpha': UNSET,
        'violin_fill_color': UNSET,
        'violin_hover_alpha': UNSET,
        'violin_hover_color': UNSET,
        'violin_hover_fill_alpha': UNSET,
        'violin_hover_fill_color': UNSET,
        'violin_hover_line_alpha': UNSET,
        'violin_hover_line_color': UNSET,
        'violin_line_alpha': UNSET,
        'violin_line_cap': UNSET,
        'violin_line_color': UNSET,
        'violin_line_dash': UNSET,
        'violin_line_join': UNSET,
        'violin_line_width': UNSET,
        'violin_muted': UNSET,
        'violin_muted_alpha': UNSET,
        'violin_muted_color': UNSET,
        'violin_muted_fill_alpha': UNSET,
        'violin_muted_fill_color': UNSET,
        'violin_muted_line_alpha': UNSET,
        'violin_muted_line_color': UNSET,
        'violin_nonselection_alpha': UNSET,
        'violin_nonselection_color': UNSET,
        'violin_nonselection_fill_alpha': UNSET,
        'violin_nonselection_fill_color': UNSET,
        'violin_nonselection_line_alpha': UNSET,
        'violin_nonselection_line_color': UNSET,
        'violin_selection_alpha': UNSET,
        'violin_selection_color': UNSET,
        'violin_selection_fill_alpha': UNSET,
        'violin_selection_fill_color': UNSET,
        'violin_selection_line_alpha': UNSET,
        'violin_selection_line_color': UNSET,
        'violin_visible': UNSET,
        'editable': UNSET,
        'fit_columns': UNSET,
        'index_position': UNSET,
        'row_headers': UNSET,
        'scroll_to_selection': UNSET,
        'selectable': UNSET,
        'sortable': UNSET
    },
}

# Plotly transforms

PLOTLY_TRANSFORMS = {
    'plot': {
        'min_height': UNSET,
        'min_width': UNSET,
        'max_height': UNSET,
        'max_width': UNSET,
        'frame_width': UNSET,
        'frame_height': UNSET,
        'batched': UNSET,
        'legend_limit': UNSET,
        'tools': UNSET
    },
    'style': {
        'alpha': lambda k, v: ('opacity', v),
        'color': lambda k, v: (k, COLOR_ALIASES.get(v, v)),
        'fill_color': lambda k, v: ('fillcolor', COLOR_ALIASES.get(v, v)),
        'line_color': lambda k, v: (k, COLOR_ALIASES.get(v, v)),
        'muted_alpha': UNSET,
    }
}


BACKEND_TRANSFORMS = dict(
    matplotlib=MATPLOTLIB_TRANSFORMS,
    plotly=PLOTLY_TRANSFORMS,
)
