import pandas as pd
import pytest
from holoviews import NdLayout, NdOverlay
from holoviews.core.dimension import Dimension

pytestmark = pytest.mark.usefixtures('hvplot_pandas')


@pytest.fixture
def edge_df():
    return pd.DataFrame(
        {
            'Latitude': [-34.58, -15.78, -33.45],
            'Longitude': [-58.66, -47.91, -70.66],
            'Volume {m3}': ['1', '2', '3'],
        }
    )


@pytest.mark.parametrize('tabular_lib', ['pandas', 'dask'], indirect=True)
def test_labels_format(tabular_lib):
    df = tabular_lib(pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y']))
    plot = df.hvplot('x', 'y', text='({x}, {y})', kind='labels')
    assert list(plot.dimensions()) == [Dimension('x'), Dimension('y'), Dimension('label')]
    assert list(plot.data['label']) == ['(1, 2)', '(3, 4)', '(5, 6)']
    assert 'label' not in df


def test_labels_no_format_edge_case(edge_df):
    plot = edge_df.hvplot.labels('Longitude', 'Latitude')
    assert list(plot.dimensions()) == [
        Dimension('Longitude'),
        Dimension('Latitude'),
        Dimension('Volume {m3}'),
    ]
    assert list(plot.data['Volume {m3}']) == ['1', '2', '3']


def test_labels_format_float(edge_df):
    plot = edge_df.hvplot.labels('Longitude', 'Latitude', text='{Longitude:.1f}E {Latitude:.2f}N')
    assert list(plot.dimensions()) == [
        Dimension('Longitude'),
        Dimension('Latitude'),
        Dimension('label'),
    ]
    assert list(plot.data['label']) == ['-58.7E -34.58N', '-47.9E -15.78N', '-70.7E -33.45N']


def test_labels_default_y(edge_df):
    edge_df = edge_df.drop(columns=['Volume {m3}'])
    plot = edge_df.hvplot.labels('Longitude', 'Latitude')
    assert list(plot.dimensions()) == [
        Dimension('Longitude'),
        Dimension('Latitude'),
        Dimension('Latitude'),
    ]
    assert plot.kdims == ['Longitude', 'Latitude']
    assert plot.vdims == ['Latitude']


def test_labels_by(edge_df):
    plot = edge_df.hvplot.labels(
        'Longitude', 'Latitude', text='{Longitude:.1f}E {Latitude:.2f}N', by='Volume {m3}'
    )
    assert isinstance(plot, NdOverlay)


def test_labels_by_subplots(edge_df):
    plot = edge_df.hvplot.labels(
        'Longitude',
        'Latitude',
        text='{Longitude:.1f}E {Latitude:.2f}N',
        by='Volume {m3}',
        subplots=True,
    )
    assert isinstance(plot, NdLayout)
