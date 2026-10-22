import pandas as pd
import pytest
from holoviews import NdLayout, NdOverlay, Store
from holoviews.core.dimension import Dimension
from holoviews.element import Labels

pytestmark = pytest.mark.usefixtures('hvplot_pandas')


@pytest.fixture
def df():
    return pd.DataFrame({'x': [1, 3, 5], 'y': [2, 4, 6], 'name': ['a', 'b', 'c']})


@pytest.fixture
def edge_df():
    return pd.DataFrame(
        {
            'Latitude': [-34.58, -15.78, -33.45],
            'Longitude': [-58.66, -47.91, -70.66],
            'Volume {m3}': ['1', '2', '3'],
        }
    )


def test_x(df):
    plot = df.hvplot.labels(x='y', y='x', text='name')
    assert isinstance(plot, Labels)
    assert plot.kdims == ['y', 'x']


def test_y(df, tabular_lib):
    plot = tabular_lib(df).hvplot.labels(x='x', y='y', text='name')
    assert isinstance(plot, Labels)
    assert plot.kdims == ['x', 'y']
    assert plot.vdims == ['name']
    assert list(plot.dimension_values('y')) == [2, 4, 6]


def test_y_default_text(edge_df):
    edge_df = edge_df.drop(columns=['Volume {m3}'])
    plot = edge_df.hvplot.labels('Longitude', 'Latitude')
    assert plot.kdims == ['Longitude', 'Latitude']
    assert plot.vdims == ['Latitude']


def test_text(df):
    plot = df.hvplot.labels('x', 'y', text='name')
    assert list(plot.dimension_values('name')) == ['a', 'b', 'c']


def test_text_default_column(edge_df):
    plot = edge_df.hvplot.labels('Longitude', 'Latitude')
    assert list(plot.dimensions()) == [
        Dimension('Longitude'),
        Dimension('Latitude'),
        Dimension('Volume {m3}'),
    ]
    assert list(plot.data['Volume {m3}']) == ['1', '2', '3']


@pytest.mark.parametrize('tabular_lib', ['pandas', 'dask'], indirect=True)
def test_text_template(tabular_lib):
    df = tabular_lib(pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y']))
    plot = df.hvplot('x', 'y', text='({x}, {y})', kind='labels')
    assert list(plot.dimensions()) == [Dimension('x'), Dimension('y'), Dimension('label')]
    assert list(plot.data['label']) == ['(1, 2)', '(3, 4)', '(5, 6)']
    assert 'label' not in df


def test_text_template_float(edge_df):
    plot = edge_df.hvplot.labels('Longitude', 'Latitude', text='{Longitude:.1f}E {Latitude:.2f}N')
    assert list(plot.dimensions()) == [
        Dimension('Longitude'),
        Dimension('Latitude'),
        Dimension('label'),
    ]
    assert list(plot.data['label']) == ['-58.7E -34.58N', '-47.9E -15.78N', '-70.7E -33.45N']


@pytest.mark.xfail(strict=True, reason='BUG: c is not applied to the labels text color')
def test_c(df):
    plot = df.hvplot.labels('x', 'y', text='name', c='red')
    assert Store.lookup_options('bokeh', plot, 'style').kwargs['text_color'] == 'red'


@pytest.mark.xfail(strict=True, reason='BUG: xoffset is dropped')
def test_xoffset(df):
    plot = df.hvplot.labels('x', 'y', text='name', xoffset=0.5)
    assert Store.lookup_options('bokeh', plot, 'plot').kwargs['xoffset'] == 0.5


@pytest.mark.xfail(strict=True, reason='BUG: yoffset is dropped')
def test_yoffset(df):
    plot = df.hvplot.labels('x', 'y', text='name', yoffset=0.5)
    assert Store.lookup_options('bokeh', plot, 'plot').kwargs['yoffset'] == 0.5


@pytest.mark.parametrize(
    'backend',
    [
        'bokeh',
        pytest.param('matplotlib', marks=pytest.mark.xfail(reason='text_font not translated')),
        pytest.param('plotly', marks=pytest.mark.xfail(reason='text_font not translated')),
    ],
    indirect=True,
)
def test_text_font(df, backend):
    plot = df.hvplot.labels('x', 'y', text='name', text_font='times')
    opts = Store.lookup_options(backend, plot, 'style').kwargs
    assert opts['family' if backend == 'matplotlib' else 'text_font'] == 'times'


@pytest.mark.parametrize(
    'backend',
    [
        'bokeh',
        'matplotlib',
        pytest.param('plotly', marks=pytest.mark.xfail(reason='text_font_size not translated')),
    ],
    indirect=True,
)
def test_text_font_size(df, backend):
    plot = df.hvplot.labels('x', 'y', text='name', text_font_size='20pt')
    opts = Store.lookup_options(backend, plot, 'style').kwargs
    assert opts['size' if backend == 'matplotlib' else 'text_font_size'] == '20pt'


def test_by(edge_df):
    plot = edge_df.hvplot.labels(
        'Longitude', 'Latitude', text='{Longitude:.1f}E {Latitude:.2f}N', by='Volume {m3}'
    )
    assert isinstance(plot, NdOverlay)


def test_by_subplots(edge_df):
    plot = edge_df.hvplot.labels(
        'Longitude',
        'Latitude',
        text='{Longitude:.1f}E {Latitude:.2f}N',
        by='Volume {m3}',
        subplots=True,
    )
    assert isinstance(plot, NdLayout)
