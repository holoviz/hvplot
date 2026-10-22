from itertools import pairwise

import numpy as np
import pytest
from bokeh.models import HoverTool

from hvplot.tests._deps import requires

# networkx is optional, it is imported in the tests.
pytestmark = requires('networkx')

# Nodes 1-10 in unsorted order
NODES = np.array([1, 4, 5, 10, 8, 9, 3, 7, 2, 6])


@pytest.fixture
def graph():
    import networkx as nx

    g = nx.Graph()
    g.add_nodes_from(NODES)
    g.add_edges_from(pairwise(NODES))
    return g


def test_nodes_are_not_sorted(graph):
    import hvplot.networkx as hvnx

    plot = hvnx.draw(graph)
    assert all(NODES == plot.nodes.dimension_values(2))


def test_default_hover_tooltip(graph):
    import hvplot.networkx as hvnx

    plot = hvnx.draw(graph)
    hover = next(t for t in plot.opts['tools'] if isinstance(t, HoverTool))
    assert hover.tooltips == [('index', '@{index_hover}')]
