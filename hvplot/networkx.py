import numpy as np
import networkx as nx
import holoviews as _hv

from holoviews import Graph, Nodes, Labels, dim
from holoviews.core.util import wrap_tuple
from holoviews.plotting.bokeh import GraphPlot, LabelsPlot

from .utilities import save, show # noqa

if _hv.extension and not getattr(_hv.extension, '_loaded', False):
    _hv.extension('bokeh', logo=False)


def draw(G, pos=None, **kwargs):
    """
    Draw the graph G using hvPlot.

    Draw the graph with hvPlot with options for node positions,
    labeling, titles, and many other drawing features.
    See draw() for simple drawing without labels or axes.

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
    node_color : color string, or array of floats, (default='r')
       Node color. Can be a single color format string,
       or a  sequence of colors with the same length as nodelist.
       If numeric values are specified they will be mapped to
       colors using the cmap and vmin,vmax parameters.  See
       matplotlib.scatter for more details.
    node_shape :  string, optional (default='o')
       The shape of the node.  Specification is as matplotlib.scatter
       marker, one of 'so^>v<dph8'.
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
       Edge color. Can be a single color format string,
       or a sequence of colors with the same length as edgelist.
       If numeric values are specified they will be mapped to
       colors using the edge_cmap and edge_vmin,edge_vmax parameters.
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
    font_color : string, optional (default='k' black)
       Font color string
    font_weight : string, optional (default='normal')
       Font weight
    font_family : string, optional (default='sans-serif')
       Font family
    label : string, optional
        Label for graph legend
    """

    # Construct Graph object
    if pos is None:
        pos = nx.drawing.spring_layout

    if isinstance(pos, dict):
        g = Graph.from_networkx(G, nx.circular_layout)
        if g.nodes.vdims:
            inds = g.nodes.dimension_values(2)
            values = g.nodes.array(g.nodes.vdims)
            lookup = {idx: tuple(vals) for idx, vals in zip(inds, values)}
        else:
            lookup = {}
        nodes = [tuple(v)+(k,)+lookup.get(k, ()) for k, v in pos.items()]
        g = g.clone((g.data, g.nodes.clone(nodes)))
    else:
        g = Graph.from_networkx(G, pos, **kwargs.get('layout_kwargs', {}))

    if 'nodelist' in kwargs:
        nodelist = list(kwargs['nodelist'])
        inds = g.nodes.dimension_values(2)
        node_alpha = [1 if i in nodelist else 0 for i in inds]
        g = g.clone((g.data, g.nodes.add_dimension('node_alpha', len(g.nodes.vdims), node_alpha, True)))
        kwargs['node_alpha'] = 'node_alpha'
    if 'edgelist' in kwargs:
        edges = g.array([0, 1])
        comparisons = []
        for edge in kwargs['edgelist']:
            comparisons.append(edges == edge)
        g = g.iloc[np.logical_and(*np.logical_or.reduce(comparisons).T)]

    # Compute options
    opts = dict(
        axiswise=True,
        arrowhead_length=kwargs.get('arrowhead_length', 0.025),
        directed=kwargs.pop('arrows', isinstance(G, nx.DiGraph)),
        colorbar=kwargs.pop('colorbar', False),
        padding=kwargs.get('padding', 0.1),
        width=kwargs.pop('width', 400),
        height=kwargs.pop('height', 400),
        selection_policy=kwargs.pop('selection_policy', 'nodes'),
        inspection_policy=kwargs.pop('inspection_policy', 'nodes'),
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
        opts['node_marker'] = opts.pop('node_shape')
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

    for node_style in ('node_fill_color', 'node_size', 'node_alpha', 'node_line_width'):
        if isinstance(opts.get(node_style), (np.ndarray, list, range)):
            g = g.clone((g.data, g.nodes.add_dimension(node_style, len(g.nodes.vdims), opts[node_style], True)))
            opts[node_style] = node_style

    for edge_style in ('edge_line_color', 'edge_line_alpha', 'edge_alpha', 'edge_line_width'):
        if isinstance(opts.get(edge_style), (np.ndarray, list, range)):
            g = g.add_dimension(edge_style, len(g.vdims), opts[edge_style], True)
            opts[edge_style] = edge_style

    if opts.get('node_fill_color') in g.nodes.dimensions():
        lims = (kwargs.get('vmin', None), kwargs.get('vmax', None))
        if lims != (None, None):
            dim = g.nodes.get_dimension(opts.get('node_fill_color'))
            dim.range = lims

    if opts.get('edge_line_color') in g.dimensions():
        lims = (kwargs.get('edge_vmin', None), kwargs.get('edge_vmax', None))
        if lims != (None, None):
            dim = g.get_dimension(opts.get('edge_line_color'))
            dim.range = lims

    g.opts(**opts)

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
            labels = Labels(data, g.nodes.kdims[:2], 'text')
        else:
            labels = Labels(g.nodes, g.nodes.kdims[:2], labels)
        g = g * labels.opts(**label_opts)

    # Apply label
    if 'label' in kwargs:
        g = g.relabel(kwargs.pop('label'))

    return g


def draw_networkx(G, pos=None, **kwargs):
    """Draw a networkx graph.

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
    graph: holoviews.Graph or (holoviews.Graph * holoviews.Labels)
       Graph element
    """
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
    graph: holoviews.Graph or (holoviews.Graph * holoviews.Labels)
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
    graph: holoviews.Graph or (holoviews.Graph * holoviews.Labels)
       Graph element
    """
    if 'alpha' in kwargs:
        kwargs['edge_alpha'] = kwargs.pop('alpha')
    kwargs.pop('nodelist', None)
    kwargs['node_alpha'] = 0
    kwargs['node_hover_alpha'] = 0
    kwargs['node_nonselection_alpha'] = 0
    kwargs['_axis_defaults'] = False
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
    graph: holoviews.Graph or (holoviews.Graph * holoviews.Labels)
       Graph element
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
    graph: holoviews.Graph or (holoviews.Graph * holoviews.Labels)
       Graph element
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
    graph: holoviews.Graph or (holoviews.Graph * holoviews.Labels)
       Graph element
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
    graph: holoviews.Graph or (holoviews.Graph * holoviews.Labels)
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
    graph: holoviews.Graph or (holoviews.Graph * holoviews.Labels)
       Graph element
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
    graph: holoviews.Graph or (holoviews.Graph * holoviews.Labels)
       Graph element
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
    graph: holoviews.Graph or (holoviews.Graph * holoviews.Labels)
       Graph element
    """
    return draw(G, nx.spring_layout, **kwargs)
