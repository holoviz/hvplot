from unittest import TestCase, SkipTest

try:
    import numpy as np
    import networkx as nx
    import hvplot.networkx as hvnx
except ImportError:
    raise SkipTest('NetworkX not available')


class TestOptions(TestCase):
    def setUp(self):
        # Create nodes (1-10) in unsorted order
        nodes = np.array([1, 4, 5, 10, 8, 9, 3, 7, 2, 6])
        edges = list(zip(nodes[:-1], nodes[1:]))

        g = nx.Graph()
        g.add_nodes_from(nodes)
        g.add_edges_from(edges)

        self.nodes = nodes
        self.g = g

    def test_nodes_are_not_sorted(self):
        plot = hvnx.draw(self.g)
        assert all(self.nodes == plot.nodes.dimension_values(2))

    def test_default_hover_tooltip(self):
        from bokeh.models import HoverTool

        plot = hvnx.draw(self.g)
        hover = next(t for t in plot.opts['tools'] if isinstance(t, HoverTool))
        assert [('index', '@{index_hover}')] == hover.tooltips
