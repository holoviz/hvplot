from collections import defaultdict

import numpy as np
import networkx as nx
import holoviews as _hv

from bokeh.models import HoverTool
from holoviews import Graph, Labels, dim
from holoviews.core.options import Store
from holoviews.core.util import dimension_sanitizer
from holoviews.plotting.bokeh import GraphPlot, LabelsPlot
from holoviews.plotting.bokeh.styles import markers

from .backend_transforms import _transfer_opts_cur_backend
from .util import process_crs
from .utilities import save, show # noqa

if _hv.extension and not getattr(_hv.extension, '_loaded', False):
    _hv.extension('bokeh', logo=False)


def _from_networkx(G, positions, nodes=None, cls=Graph, **kwargs):
    """
    Generate a Graph element from a networkx.Graph object and networkx
    layout function or dictionary of node positions.  Any keyword
    arguments will be passed to the layout function. By default it
    will extract all node and edge attributes from the networkx.Graph
    but explicit node information may also be supplied. Any non-scalar
    attributes, such as lists or dictionaries will be ignored.

    Parameters
    ----------
    G : networkx.Graph
       Graph to convert to Graph element
    positions : dict or callable
       Node positions defined as a dictionary mapping from node id to
       (x, y) tuple or networkx layout function which computes a
       positions dictionary.
    kwargs : dict
       Keyword arguments for the element

    Returns
    -------
    graph : holoviews.Graph
       Graph element
    """

    # Unpack edges
    edges = defaultdict(list)
    for start, end in G.edges():
        for attr, value in sorted(G.adj[start][end].items()):
            if isinstance(value, (list, dict)):
                continue # Cannot handle list or dict attrs
            edges[attr].append(value)

        # Handle tuple node indexes (used in 2D grid Graphs)
        if isinstance(start, tuple):
            start = str(start)
        if isinstance(end, tuple):
            end = str(end)
        edges['start'].append(start)
        edges['end'].append(end)
    edge_cols = sorted(k for k in edges if k not in ('start', 'end')
                        and len(edges[k]) == len(edges['start']))
    edge_vdims = [str(col) if isinstance(col, int) else col for col in edge_cols]
    edge_data = tuple(edges[col] for col in ['start', 'end']+edge_cols)

    # Unpack user node info
    xdim, ydim, idim = cls.node_type.kdims[:3]
    if nodes:
        node_columns = nodes.columns()
        idx_dim = nodes.kdims[0].name
        info_cols, values = zip(*((k, v) for k, v in node_columns.items() if k != idx_dim))
        node_info = {i: vals for i, vals in zip(node_columns[idx_dim], zip(*values))}
    else:
        info_cols = []
        node_info = None
    node_columns = defaultdict(list)

    # Unpack node positions
    for idx, pos in positions.items():
        node = G.nodes.get(idx)
        if node is None:
            continue
        x, y = pos
        node_columns[xdim.name].append(x)
        node_columns[ydim.name].append(y)
        for attr, value in node.items():
            if isinstance(value, (list, dict, tuple)):
                continue
            node_columns[attr].append(value)
        for i, col in enumerate(info_cols):
            node_columns[col].append(node_info[idx][i])
        if isinstance(idx, tuple):
            idx = str(idx) # Tuple node indexes handled as strings
        node_columns[idim.name].append(idx)
    node_cols = sorted(k for k in node_columns if k not in cls.node_type.kdims
                        and len(node_columns[k]) == len(node_columns[xdim.name]))
    columns = [xdim.name, ydim.name, idim.name]+node_cols+list(info_cols)
    node_data = tuple(node_columns[col] for col in columns)

    # Construct nodes
    vdims = []
    for col in node_cols:
        if isinstance(col, int):
            dim = str(col)
        elif nodes is not None and col in nodes.vdims:
            dim = nodes.get_dimension(col)
        else:
            dim = col
        vdims.append(dim)
    nodes = cls.node_type(node_data, vdims=vdims)

    # Construct graph
    return cls((edge_data, nodes), vdims=edge_vdims)


def draw(G, pos=None, **kwargs):
    """
    Draw the graph G using hvPlot.

    Draw the graph with hvPlot with options for node positions,
    labeling, titles, and many other drawing features.

    Parameters
    ----------
    G : graph
       A networkx graph
    pos : dictionary, optional
       A dictionary with nodes as keys and positions as values.
       If not specified a spring layout positioning will be computed.
       See :py:mod:`networkx.drawing.layout` for functions that
       compute node positions.
    arrows : bool, optional (default=True)
       For directed graphs, if True draw arrowheads.
       Note: Arrows will be the same color as edges.
    arrowhead_length : float, optional (default=0.025)
       The length of the arrows as fraction of the overall extent of
       the graph
    with_labels :  bool, optional (default=True)
       Set to True to draw labels on the nodes.
    nodelist : list, optional (default G.nodes())
       Draw only specified nodes
    edgelist : list, optional (default=G.edges())
       Draw only specified edges
    node_size : scalar or array, optional (default=300)
       Size of nodes.  If an array is specified it must be the
       same length as nodelist.
    node_color : color string, node attribute, or array of floats, (default='r')
       Can be a single color, the name of an attribute on the nodes or
       sequence of colors with the same length as nodelist.  If the
       node_color references an attribute on the nodes or is a list of
       values they will be colormapped using the cmap and vmin, vmax
       parameters.
    node_shape :  string, optional (default='o')
       The shape of the node. Specification is as valid bokeh marker.
    alpha : float, optional (default=1.0)
       The node and edge transparency
    cmap : Colormap, optional (default=None)
       Colormap for mapping intensities of nodes
    vmin,vmax : float, optional (default=None)
       Minimum and maximum for node colormap scaling
    linewidths : [None | scalar | sequence]
       Line width of symbol border (default =1.0)
    edge_width : float, optional (default=1.0)
       Line width of edges
    edge_color : color string, or array of floats (default='r')
       Can be a single color, the name of an attribute on the edges or
       sequence of colors with the same length as the edges.  If the
       edge_color references an attribute on the edges or is a list of
       values they will be colormapped using the edge_cmap and
       edge_vmin, edge_vmax parameters.
    edge_cmap : Matplotlib colormap, optional (default=None)
       Colormap for mapping intensities of edges
    edge_vmin,edge_vmax : floats, optional (default=None)
       Minimum and maximum for edge colormap scaling
    style : string, optional (default='solid')
       Edge line style (solid|dashed|dotted,dashdot)
    labels : dictionary or string, optional (default=None)
       Node labels in a dictionary keyed by node of text labels or
       a string referencing a node attribute
    font_size : int, optional (default=12)
       Font size for text labels
    font_color : string, optional (default='black')
       Font color string
    font_family : string, optional (default='sans-serif')
       Font family
    label : string, optional
       Label for graph legend
    selection_policy : string, optional (default='nodes')
       Whether to select 'nodes', 'edges' or None on tap and selection
       events.
    inspection_policy : string, optional (default='nodes')
       Whether to select 'nodes', 'edges' or None on tap and selection
       events.
    geo : boolean, optional (default=False)
       Whether to return a GeoViews graph
    crs : cartopy.crs.CRS
       A cartopy coordinate reference system (enables a geographic plot)
    height : int, optional (default=400)
       The height of the plot in pixels
    width : int, optional (default=400)
       The width of the plot in pixels
    """
    if pos is None:
        pos = nx.drawing.spring_layout

    if not isinstance(pos, dict):
        pos = pos(G, **kwargs.get('layout_kwargs', {}))

    params, label_params = {}, {}
    label_element = Labels
    if kwargs.get('geo', False) or 'crs' in kwargs:
        try:
            import geoviews
        except ImportError:
            raise ImportError('In order to use geo-related features '
                              'the geoviews library must be available. '
                              'It can be installed with:\n  conda '
                              'install -c pyviz geoviews')
        crs = process_crs(kwargs.get('crs'))
        label_element = geoviews.Labels
        params['cls'] = geoviews.Graph
        params['crs'] = crs
        label_params['crs'] = crs

    # Construct Graph object
    g = _from_networkx(G, pos, **params)

    if 'nodelist' in kwargs:
        g.nodes.data = g.nodes.data.iloc[list(kwargs['nodelist'])]

    if 'edgelist' in kwargs:
        edges = g.array([0, 1])
        comparisons = []
        for edge in kwargs['edgelist']:
            comparisons.append(edges == edge)
        if len(comparisons):
            selector = np.logical_and(*np.logical_or.reduce(comparisons).T)
            g = g.iloc[selector]
        else:
            g = g.iloc[:0]

    # Compute options
    inspection_policy = kwargs.pop('inspection_policy', 'nodes')
    opts = dict(
        axiswise=True,
        arrowhead_length=kwargs.get('arrowhead_length', 0.025),
        directed=kwargs.pop('arrows', isinstance(G, nx.DiGraph)),
        colorbar=kwargs.pop('colorbar', False),
        padding=kwargs.get('padding', 0.1),
        width=kwargs.pop('width', 400),
        height=kwargs.pop('height', 400),
        selection_policy=kwargs.pop('selection_policy', 'nodes'),
        inspection_policy=inspection_policy,
        node_fill_color='red')

    if '_axis_defaults':
        opts.update(xaxis=None, yaxis=None, show_frame=False)

    opts.update({k: kwargs.pop(k) for k in list(kwargs) if k in GraphPlot.style_opts})
    if 'node_size' in opts:
        if isinstance(opts['node_size'], str):
            opts['node_size'] = dim(opts['node_size'])
        opts['node_size'] = np.sqrt(opts['node_size'])
    if 'node_color' in opts:
        opts['node_fill_color'] = opts.pop('node_color')
    if 'edge_color' in opts:
        opts['edge_line_color'] = opts.pop('edge_color')
    if 'node_shape' in kwargs:
        marker = kwargs.pop('node_shape')
        if marker in markers:
            marker_opts = markers[marker]
            marker = marker_opts['marker']
            if 'angle' in marker_opts:
                Store.add_style_opts(Graph, ['node_angle'], 'bokeh')
                opts['node_angle'] = marker_opts['angle']
        opts['node_marker'] = marker
    if 'alpha' in kwargs:
        alpha = kwargs.pop('alpha')
        opts['node_alpha'] = alpha
        opts['edge_alpha'] = alpha
    if 'linewidths' in kwargs:
        opts['node_line_width'] = kwargs.pop('linewidths')
    if 'edge_width' in kwargs:
        opts['edge_line_width'] = kwargs.pop('edge_width')
    if 'style' in kwargs:
        opts['edge_line_dash'] = kwargs.pop('style')

    node_styles = ('node_fill_color', 'node_size', 'node_alpha', 'node_line_width')
    for node_style in node_styles:
        if isinstance(opts.get(node_style), (np.ndarray, list, range)):
            g = g.clone((g.data, g.nodes.add_dimension(node_style, len(g.nodes.vdims), opts[node_style], True)))
            opts[node_style] = node_style

    edge_styles = ('edge_line_color', 'edge_line_alpha', 'edge_alpha', 'edge_line_width')
    for edge_style in edge_styles:
        if isinstance(opts.get(edge_style), (np.ndarray, list, range)):
            g = g.add_dimension(edge_style, len(g.vdims), opts[edge_style], True)
            opts[edge_style] = edge_style

    if opts.get('node_fill_color') in g.nodes.dimensions():
        lims = (kwargs.get('vmin', None), kwargs.get('vmax', None))
        if lims != (None, None):
            dimension = g.nodes.get_dimension(opts.get('node_fill_color'))
            dimension.range = lims

    if opts.get('edge_line_color') in g.dimensions():
        lims = (kwargs.get('edge_vmin', None), kwargs.get('edge_vmax', None))
        if lims != (None, None):
            dimension = g.get_dimension(opts.get('edge_line_color'))
            dimension.range = lims

    if inspection_policy == 'nodes':
        tooltip_dims = [(d.label, 'index_hover' if d in g.nodes.kdims else d.name)
                        for d in g.nodes.kdims[2:] + g.nodes.vdims]
    else:
        tooltip_dims = [(d.label, d.name+'_values' if d in g.kdims else d.name)
                        for d in g.kdims + g.vdims]
    tooltips = [(label, '@{%s}' % dimension_sanitizer(name))
                for label, name in tooltip_dims if name not in node_styles + edge_styles]
    opts['tools'] = [HoverTool(tooltips=tooltips), 'tap']

    g.opts(**opts, backend='bokeh')

    # Construct Labels
    if kwargs.get('with_labels', kwargs.get('labels', False)):
        label_opts = {k: kwargs.pop(k) for k in list(kwargs) if k in LabelsPlot.style_opts}
        if 'xoffset' in kwargs:
            label_opts['xoffset'] = kwargs.pop('xoffset')
        if 'yoffset' in kwargs:
            label_opts['yoffset'] = kwargs.pop('yoffset')
        if 'font_size' in kwargs:
            label_opts['text_font_size'] = kwargs.pop('font_size')
        if 'font_color' in kwargs:
            label_opts['text_color'] = kwargs.pop('font_color')
        if 'font_family' in kwargs:
            label_opts['text_font'] = kwargs.pop('font_family')
        labels = kwargs.get('labels', g.nodes.kdims[2])
        if isinstance(labels, dict):
            values = g.nodes.array(g.nodes.kdims)
            data = [(x, y, labels[i]) for (x, y, i) in values if i in labels]
            labels = label_element(data, g.nodes.kdims[:2], 'text', **label_params)
        else:
            labels = label_element(g.nodes, g.nodes.kdims[:2], labels, **label_params)
        g = g * labels.opts(**label_opts, backend='bokeh')

    # Apply label
    if 'label' in kwargs:
        g = g.relabel(kwargs.pop('label'))

    # Process options
    g = _transfer_opts_cur_backend(g)

    return g


def draw_networkx(G, pos=None, **kwargs):
    """Draw a networkx graph.

    Draw the graph with hvPlot with options for node positions,
    labeling, titles, and many other drawing features. See draw() for
    simple drawing without labels or axes.

    Parameters
    ----------
    G : graph
       A networkx graph
    pos : dictionary, optional
       A dictionary with nodes as keys and positions as values or a
       layout `networkx.drawing.layout` function.  If not specified a
       spring layout positioning will be computed. See
       :py:mod:`networkx.drawing.layout` for functions that compute
       node positions.
    kwargs : optional keywords
       See hvplot.networkx.draw() for a description of optional
       keywords, with the exception of the pos parameter which is not
       used by this function.

    Returns
    -------
    graph : holoviews.Graph or holoviews.Overlay
       Graph element
    """
    kwargs['_axis_defaults'] = False
    return draw(G, pos, **kwargs)


def draw_networkx_nodes(G, pos, **kwargs):
    """Draw networkx graph nodes.

    Parameters
    ----------
    G : graph
       A networkx graph
    kwargs : optional keywords
       See hvplot.networkx.draw() for a description of optional
       keywords, with the exception of the pos parameter which is not
       used by this function.

    Returns
    -------
    graph: holoviews.Graph or holoviews.Overlay
       Graph element
    """
    if 'alpha' in kwargs:
        kwargs['node_alpha'] = kwargs.pop('alpha')
    kwargs.pop('edgelist', None)
    kwargs['_axis_defaults'] = False
    kwargs['edge_alpha'] = 0
    kwargs['edge_hover_alpha'] = 0
    kwargs['edge_nonselection_alpha'] = 0
    return draw(G, pos, **kwargs)


def draw_networkx_edges(G, pos, **kwargs):
    """Draw networkx graph edges.

    Parameters
    ----------
    G : graph
       A networkx graph
    kwargs : optional keywords
       See hvplot.networkx.draw() for a description of optional
       keywords, with the exception of the pos parameter which is not
       used by this function.

    Returns
    -------
    graph : holoviews.Graph or (holoviews.Graph * holoviews.Labels)
       Graph element
    """
    if 'alpha' in kwargs:
        kwargs['edge_alpha'] = kwargs.pop('alpha')
    kwargs.pop('nodelist', None)
    kwargs['node_alpha'] = 0
    kwargs['node_hover_alpha'] = 0
    kwargs['node_nonselection_alpha'] = 0
    kwargs['_axis_defaults'] = False
    if kwargs.get('selection_policy') is not None:
        kwargs['selection_policy'] = 'edges'
    if kwargs.get('inspection_policy') is not None:
        kwargs['inspection_policy'] = 'edges'
    return draw(G, pos, **kwargs)


def draw_networkx_labels(G, pos, **kwargs):
    """Draw networkx graph node labels.

    Parameters
    ----------
    G : graph
       A networkx graph
    kwargs : optional keywords
       See hvplot.networkx.draw() for a description of optional
       keywords, with the exception of the pos parameter which is not
       used by this function.

    Returns
    -------
    graph : Labels element
       Labels element
    """
    g = draw(G, pos, **kwargs)
    return Labels(g.nodes, g.nodes.kdims[:2], g.nodes.kdims[2])


def draw_circular(G, **kwargs):
    """Draw networkx graph with circular layout.

    Parameters
    ----------
    G : graph
       A networkx graph
    kwargs : optional keywords
       See hvplot.networkx.draw() for a description of optional
       keywords, with the exception of the pos parameter which is not
       used by this function.

    Returns
    -------
    graph : holoviews.Graph or holoviews.Overlay
       Graph element or Graph and Labels
    """
    return draw(G, pos=nx.circular_layout, **kwargs)


def draw_kamada_kawai(G, **kwargs):
    """Draw networkx graph with circular layout.

    Parameters
    ----------
    G : graph
       A networkx graph
    kwargs : optional keywords
       See hvplot.networkx.draw() for a description of optional
       keywords, with the exception of the pos parameter which is not
       used by this function.

    Returns
    -------
    graph : holoviews.Graph or holoviews.Overlay
       Graph element or Graph and Labels
    """
    return draw(G, pos=nx.kamada_kawai_layout, **kwargs)


def draw_random(G, **kwargs):
    """Draw networkx graph with random layout.

    Parameters
    ----------
    G : graph
       A networkx graph
    kwargs : optional keywords
       See hvplot.networkx.draw() for a description of optional
       keywords, with the exception of the pos parameter which is not
       used by this function.

    Returns
    -------
    graph : holoviews.Graph or holoviews.Overlay
       Graph element
    """
    return draw(G, nx.random_layout, **kwargs)


def draw_shell(G, **kwargs):
    """Draw networkx graph with shell layout.

    Parameters
    ----------
    G : graph
       A networkx graph
    kwargs : optional keywords
       See hvplot.networkx.draw() for a description of optional
       keywords, with the exception of the pos parameter which is not
       used by this function.

    Returns
    -------
    graph : holoviews.Graph or holoviews.Overlay
       Graph element or Graph and Labels
    """
    nlist = kwargs.pop('nlist', None)
    if nlist is not None:
        kwargs['layout_kwargs'] = {'nlist': nlist}
    return draw(G, nx.shell_layout, **kwargs)


def draw_spectral(G, **kwargs):
    """Draw networkx graph with spectral layout.

    Parameters
    ----------
    G : graph
       A networkx graph
    kwargs : optional keywords
       See hvplot.networkx.draw() for a description of optional
       keywords, with the exception of the pos parameter which is not
       used by this function.

    Returns
    -------
    graph : holoviews.Graph or holoviews.Overlay
       Graph element or Graph and Labels
    """
    return draw(G, nx.spectral_layout, **kwargs)


def draw_spring(G, **kwargs):
    """Draw networkx graph with spring layout.

    Parameters
    ----------
    G : graph
       A networkx graph
    kwargs : optional keywords
       See hvplot.networkx.draw() for a description of optional
       keywords, with the exception of the pos parameter which is not
       used by this function.

    Returns
    -------
    graph : holoviews.Graph or holoviews.Overlay
       Graph element or Graph and Labels
    """
    return draw(G, nx.spring_layout, **kwargs)

def draw_planar(G, **kwargs):
    """Draw networkx graph with planar layout.

    Parameters
    ----------
    G : graph
       A networkx graph
    kwargs : optional keywords
       See hvplot.networkx.draw() for a description of optional
       keywords, with the exception of the pos parameter which is not
       used by this function.

    Returns
    -------
    graph : holoviews.Graph or holoviews.Overlay
       Graph element or Graph and Labels
    """
    return draw(G, nx.planar_layout, **kwargs)
