from itertools import pairwise

import holoviews as hv
import numpy as np
import pytest
from bokeh.models import HoverTool
from holoviews import Store

from hvplot.tests._deps import requires

# networkx is optional, it is imported in the tests.
pytestmark = requires('networkx')

# Nodes 1-10 in unsorted order
NODES = np.array([1, 4, 5, 10, 8, 9, 3, 7, 2, 6])


@pytest.fixture
def hvnx():
    import hvplot.networkx as hvnx

    return hvnx


@pytest.fixture
def graph():
    import networkx as nx

    g = nx.Graph()
    g.add_nodes_from(NODES)
    g.add_edges_from(pairwise(NODES))
    return g


@pytest.fixture
def path_graph():
    """0 - 1 - 2 - 3 with a `w` node attribute and a `weight` edge attribute."""
    import networkx as nx

    g = nx.path_graph(4)
    nx.set_node_attributes(g, {i: i * 100 for i in g}, 'w')
    nx.set_edge_attributes(g, {e: i + 1 for i, e in enumerate(g.edges)}, 'weight')
    return g


@pytest.fixture
def pos():
    return {i: (i, 0) for i in range(4)}


def style_opts(element):
    return Store.lookup_options('bokeh', element, 'style').kwargs


def plot_opts(element):
    return Store.lookup_options('bokeh', element, 'plot').kwargs


def test_nodes_are_not_sorted(hvnx, graph):
    plot = hvnx.draw(graph)
    assert all(NODES == plot.nodes.dimension_values(2))


def test_default_hover_tooltip(hvnx, graph):
    plot = hvnx.draw(graph)
    hover = next(t for t in plot.opts['tools'] if isinstance(t, HoverTool))
    assert hover.tooltips == [('index', '@{index_hover}')]


def test_draw_pos_dict(hvnx, path_graph, pos):
    plot = hvnx.draw(path_graph, pos)
    assert isinstance(plot, hv.Graph)
    assert plot.nodes.dimension_values('x').tolist() == [0, 1, 2, 3]
    assert plot.nodes.dimension_values('y').tolist() == [0, 0, 0, 0]


def test_draw_node_and_edge_attributes(hvnx, path_graph, pos):
    plot = hvnx.draw(path_graph, pos)
    assert plot.nodes.vdims == ['w']
    assert plot.vdims == ['weight']
    assert plot.dimension_values('weight').tolist() == [1, 2, 3]


def test_draw_skips_non_scalar_attributes(hvnx):
    import networkx as nx

    g = nx.Graph()
    g.add_node(0, lst=[1], tup=(1, 2), s='a')
    g.add_node(1, lst=[1], tup=(1, 2), s='b')
    g.add_edge(0, 1, lst=[1], dct={}, w=1)
    plot = hvnx.draw(g)
    assert plot.nodes.vdims == ['s']
    assert plot.vdims == ['w']


def test_draw_tuple_nodes_as_strings(hvnx):
    import networkx as nx

    plot = hvnx.draw(nx.grid_2d_graph(1, 2))
    assert plot.nodes.dimension_values('index').tolist() == ['(0, 0)', '(0, 1)']
    assert plot.dimension_values('start').tolist() == ['(0, 0)']
    assert plot.dimension_values('end').tolist() == ['(0, 1)']


def test_draw_default_opts(hvnx, path_graph, pos):
    plot = hvnx.draw(path_graph, pos)
    popts = plot_opts(plot)
    assert popts['directed'] is False
    assert (popts['width'], popts['height']) == (400, 400)
    assert (popts['xaxis'], popts['yaxis']) == (None, None)
    assert style_opts(plot)['node_fill_color'] == 'red'


def test_draw_directed(hvnx):
    import networkx as nx

    g = nx.DiGraph([(0, 1)])
    assert plot_opts(hvnx.draw(g))['directed'] is True
    assert plot_opts(hvnx.draw(g, arrows=False))['directed'] is False


def test_draw_plot_options(hvnx, path_graph, pos):
    plot = hvnx.draw(
        path_graph,
        pos,
        width=200,
        height=100,
        arrowhead_length=0.1,
        padding=0.2,
        colorbar=True,
        selection_policy='edges',
    )
    popts = plot_opts(plot)
    assert (popts['width'], popts['height']) == (200, 100)
    assert popts['arrowhead_length'] == 0.1
    assert popts['padding'] == 0.2
    assert popts['colorbar'] is True
    assert popts['selection_policy'] == 'edges'


def test_draw_style_options(hvnx, path_graph, pos):
    plot = hvnx.draw(
        path_graph,
        pos,
        node_color='blue',
        edge_color='green',
        alpha=0.5,
        linewidths=2,
        edge_width=3,
        style='dashed',
    )
    sopts = style_opts(plot)
    assert sopts['node_fill_color'] == 'blue'
    assert sopts['edge_line_color'] == 'green'
    assert sopts['node_alpha'] == sopts['edge_alpha'] == 0.5
    assert sopts['node_line_width'] == 2
    assert sopts['edge_line_width'] == 3
    assert sopts['edge_line_dash'] == 'dashed'


def test_draw_node_shape(hvnx, path_graph, pos):
    plot = hvnx.draw(path_graph, pos, node_shape='square')
    assert style_opts(plot)['node_marker'] == 'square'


def test_draw_node_shape_with_angle(hvnx, path_graph, pos):
    # Matplotlib 'v' marker is translated to a rotated Bokeh triangle.
    plot = hvnx.draw(path_graph, pos, node_shape='v')
    sopts = style_opts(plot)
    assert sopts['node_marker'] == 'triangle'
    assert sopts['node_angle'] == np.pi


def test_draw_node_size_scalar(hvnx, path_graph, pos):
    # Matplotlib sizes are areas, Bokeh sizes are diameters.
    plot = hvnx.draw(path_graph, pos, node_size=100)
    assert style_opts(plot)['node_size'] == 10


def test_draw_node_size_attribute(hvnx, path_graph, pos):
    plot = hvnx.draw(path_graph, pos, node_size='w')
    assert repr(style_opts(plot)['node_size']) == "np.sqrt(dim('w'))"


def test_draw_node_size_array(hvnx, path_graph, pos):
    plot = hvnx.draw(path_graph, pos, node_size=[100, 400, 900, 1600])
    assert style_opts(plot)['node_size'] == 'node_size'
    assert plot.nodes.dimension_values('node_size').tolist() == [10, 20, 30, 40]


def test_draw_node_color_array(hvnx, path_graph, pos):
    colors = ['red', 'green', 'blue', 'black']
    plot = hvnx.draw(path_graph, pos, node_color=colors)
    assert style_opts(plot)['node_fill_color'] == 'node_fill_color'
    assert plot.nodes.dimension_values('node_fill_color').tolist() == colors
    # Style dimensions are not shown in the hover tooltip.
    hover = plot_opts(plot)['tools'][0]
    assert hover.tooltips == [('index', '@{index_hover}'), ('w', '@{w}')]


def test_draw_edge_width_array(hvnx, path_graph, pos):
    plot = hvnx.draw(path_graph, pos, edge_width=np.array([1, 2, 3]))
    assert style_opts(plot)['edge_line_width'] == 'edge_line_width'
    assert plot.dimension_values('edge_line_width').tolist() == [1, 2, 3]


def test_draw_vmin_vmax(hvnx, path_graph, pos):
    plot = hvnx.draw(path_graph, pos, node_color='w', vmin=0, vmax=500)
    assert style_opts(plot)['node_fill_color'] == 'w'
    assert plot.nodes.get_dimension('w').range == (0, 500)


def test_draw_edge_vmin_vmax(hvnx, path_graph, pos):
    plot = hvnx.draw(path_graph, pos, edge_color='weight', edge_vmin=0, edge_vmax=5)
    assert style_opts(plot)['edge_line_color'] == 'weight'
    assert plot.get_dimension('weight').range == (0, 5)


def test_draw_inspection_policy_edges(hvnx, path_graph, pos):
    plot = hvnx.draw(path_graph, pos, inspection_policy='edges')
    assert plot_opts(plot)['inspection_policy'] == 'edges'
    hover = plot_opts(plot)['tools'][0]
    assert hover.tooltips == [
        ('start', '@{start_values}'),
        ('end', '@{end_values}'),
        ('weight', '@{weight}'),
    ]


def test_draw_nodelist(hvnx, path_graph, pos):
    plot = hvnx.draw(path_graph, pos, nodelist=[0, 1])
    assert plot.nodes.dimension_values('index').tolist() == [0, 1]


@pytest.mark.xfail(strict=True, reason='BUG: nodelist is used as positions, not node ids')
def test_draw_nodelist_node_ids(hvnx, graph):
    plot = hvnx.draw(graph, nodelist=[4, 10])
    assert plot.nodes.dimension_values('index').tolist() == [4, 10]


def test_draw_edgelist(hvnx, path_graph, pos):
    plot = hvnx.draw(path_graph, pos, edgelist=[(1, 2)])
    assert plot.array(['start', 'end']).tolist() == [[1, 2]]


def test_draw_edgelist_empty(hvnx, path_graph, pos):
    plot = hvnx.draw(path_graph, pos, edgelist=[])
    assert len(plot) == 0


def test_draw_label(hvnx, path_graph, pos):
    plot = hvnx.draw(path_graph, pos, label='My graph')
    assert plot.label == 'My graph'


def test_draw_with_labels(hvnx, path_graph, pos):
    plot = hvnx.draw(
        path_graph,
        pos,
        with_labels=True,
        font_size='20pt',
        font_color='blue',
        font_family='mono',
        xoffset=1,
        yoffset=2,
    )
    assert isinstance(plot, hv.Overlay)
    labels = plot.Labels.I
    assert labels.dimension_values('index').tolist() == [0, 1, 2, 3]
    sopts = style_opts(labels)
    assert sopts['text_font_size'] == '20pt'
    assert sopts['text_color'] == 'blue'
    assert sopts['text_font'] == 'mono'
    assert plot_opts(labels)['xoffset'] == 1
    assert plot_opts(labels)['yoffset'] == 2


def test_draw_labels_dict(hvnx, path_graph, pos):
    plot = hvnx.draw(path_graph, pos, labels={0: 'a', 2: 'c'})
    labels = plot.Labels.I
    assert labels.array().tolist() == [[0, 0, 'a'], [2, 0, 'c']]


def test_draw_labels_attribute(hvnx, path_graph, pos):
    plot = hvnx.draw(path_graph, pos, labels='w')
    assert plot.Labels.I.vdims == ['w']


@pytest.mark.geo
def test_draw_geo(hvnx, path_graph, pos):
    import geoviews as gv

    plot = hvnx.draw(path_graph, pos, geo=True, with_labels=True)
    assert isinstance(plot.Graph.I, gv.Graph)
    assert isinstance(plot.Labels.I, gv.Labels)


def test_draw_geo_without_geoviews(hvnx, path_graph, pos, block_import):
    block_import('geoviews')
    with pytest.raises(ImportError, match='geoviews library must be available'):
        hvnx.draw(path_graph, pos, geo=True)


@pytest.mark.xfail(strict=True, reason='BUG: draw_networkx hides the axes like draw')
def test_draw_networkx_shows_axes(hvnx, path_graph, pos):
    plot = hvnx.draw_networkx(path_graph, pos)
    assert 'xaxis' not in plot_opts(plot)


def test_draw_networkx(hvnx, path_graph, pos):
    plot = hvnx.draw_networkx(path_graph, pos)
    assert isinstance(plot, hv.Graph)
    assert plot.nodes.dimension_values('x').tolist() == [0, 1, 2, 3]


def test_draw_networkx_nodes(hvnx, path_graph, pos):
    plot = hvnx.draw_networkx_nodes(path_graph, pos, alpha=0.3, edgelist=[(0, 1)])
    sopts = style_opts(plot)
    assert sopts['node_alpha'] == 0.3
    assert sopts['edge_alpha'] == sopts['edge_hover_alpha'] == 0
    # edgelist is ignored, the edges are hidden anyway.
    assert len(plot) == 3


def test_draw_networkx_edges(hvnx, path_graph, pos):
    plot = hvnx.draw_networkx_edges(
        path_graph,
        pos,
        alpha=0.3,
        nodelist=[0],
        selection_policy='nodes',
        inspection_policy='nodes',
    )
    sopts = style_opts(plot)
    assert sopts['edge_alpha'] == 0.3
    assert sopts['node_alpha'] == sopts['node_hover_alpha'] == 0
    popts = plot_opts(plot)
    assert popts['selection_policy'] == popts['inspection_policy'] == 'edges'
    # nodelist is ignored, the nodes are hidden anyway.
    assert len(plot.nodes) == 4


def test_draw_networkx_labels(hvnx, path_graph, pos):
    labels = hvnx.draw_networkx_labels(path_graph, pos)
    assert isinstance(labels, hv.Labels)
    assert labels.array().tolist() == [[0, 0, 0], [1, 0, 1], [2, 0, 2], [3, 0, 3]]


@pytest.mark.parametrize(
    ('func', 'layout'),
    [
        ('draw_circular', 'circular_layout'),
        ('draw_kamada_kawai', 'kamada_kawai_layout'),
        ('draw_shell', 'shell_layout'),
        ('draw_spectral', 'spectral_layout'),
        ('draw_planar', 'planar_layout'),
    ],
)
def test_draw_layout(hvnx, path_graph, func, layout):
    import networkx as nx

    plot = getattr(hvnx, func)(path_graph)
    expected = getattr(nx, layout)(path_graph)
    np.testing.assert_allclose(plot.nodes.array(['x', 'y']), [expected[i] for i in range(4)])


@pytest.mark.parametrize('func', ['draw_random', 'draw_spring'])
def test_draw_random_layout(hvnx, path_graph, func):
    plot = getattr(hvnx, func)(path_graph)
    assert plot.nodes.dimension_values('index').tolist() == [0, 1, 2, 3]
    assert len(plot) == 3


def test_draw_shell_nlist(hvnx, path_graph):
    import networkx as nx

    nlist = [[0], [1, 2, 3]]
    plot = hvnx.draw_shell(path_graph, nlist=nlist)
    expected = nx.shell_layout(path_graph, nlist=nlist)
    np.testing.assert_allclose(plot.nodes.array(['x', 'y']), [expected[i] for i in range(4)])
    # Node 0 is alone in the inner shell, at the center.
    np.testing.assert_allclose(expected[0], [0, 0])
