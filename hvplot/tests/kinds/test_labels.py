from unittest import SkipTest

import pandas as pd
from holoviews import NdLayout, NdOverlay
from holoviews.core.dimension import Dimension
from holoviews.element.comparison import ComparisonTestCase


class TestChart1D(ComparisonTestCase):
    def setUp(self):
        import hvplot.pandas  # noqa: F401

        self.df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
        self.edge_df = pd.DataFrame(
            {
                'Latitude': [-34.58, -15.78, -33.45],
                'Longitude': [-58.66, -47.91, -70.66],
                'Volume {m3}': ['1', '2', '3'],
            }
        )

    def test_labels_format(self):
        plot = self.df.hvplot('x', 'y', text='({x}, {y})', kind='labels')
        assert list(plot.dimensions()) == [Dimension('x'), Dimension('y'), Dimension('label')]
        assert list(plot.data['label']) == ['(1, 2)', '(3, 4)', '(5, 6)']
        assert 'label' not in self.df

    def test_labels_no_format_edge_case(self):
        plot = self.edge_df.hvplot.labels('Longitude', 'Latitude')
        assert list(plot.dimensions()) == [
            Dimension('Longitude'),
            Dimension('Latitude'),
            Dimension('Volume {m3}'),
        ]
        assert list(plot.data['Volume {m3}']) == ['1', '2', '3']

    def test_labels_format_float(self):
        plot = self.edge_df.hvplot.labels(
            'Longitude', 'Latitude', text='{Longitude:.1f}E {Latitude:.2f}N'
        )
        assert list(plot.dimensions()) == [
            Dimension('Longitude'),
            Dimension('Latitude'),
            Dimension('label'),
        ]
        assert list(plot.data['label']) == ['-58.7E -34.58N', '-47.9E -15.78N', '-70.7E -33.45N']

    def test_labels_default_y(self):
        edge_df = self.edge_df.copy().drop(columns=['Volume {m3}'])
        plot = edge_df.hvplot.labels('Longitude', 'Latitude')
        assert list(plot.dimensions()) == [
            Dimension('Longitude'),
            Dimension('Latitude'),
            Dimension('Latitude'),
        ]
        assert plot.kdims == ['Longitude', 'Latitude']
        assert plot.vdims == ['Latitude']

    def test_labels_by(self):
        plot = self.edge_df.hvplot.labels(
            'Longitude', 'Latitude', text='{Longitude:.1f}E {Latitude:.2f}N', by='Volume {m3}'
        )
        assert isinstance(plot, NdOverlay)

    def test_labels_by_subplots(self):
        plot = self.edge_df.hvplot.labels(
            'Longitude',
            'Latitude',
            text='{Longitude:.1f}E {Latitude:.2f}N',
            by='Volume {m3}',
            subplots=True,
        )
        assert isinstance(plot, NdLayout)


class TestChart1DDask(TestChart1D):
    def setUp(self):
        super().setUp()
        try:
            import dask.dataframe as dd
        except ImportError:
            raise SkipTest('Dask not available')
        import hvplot.dask  # noqa: F401

        self.df = dd.from_pandas(self.df, npartitions=2)
