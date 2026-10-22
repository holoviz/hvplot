import pandas as pd
import panel as pn
import pytest
from holoviews import Store

pytestmark = pytest.mark.usefixtures('hvplot_pandas')


@pytest.fixture
def df():
    return pd.DataFrame(
        [[1, 2, 'A', 0.1], [3, 4, 'B', 0.2], [5, 6, 'C', 0.3]],
        columns=['x', 'y', 'category', 'number'],
    )


def test_aspect(df, backend):
    plot = df.hvplot(x='x', y='y', aspect=2)
    opts = Store.lookup_options(backend, plot, 'plot').kwargs
    assert opts['aspect'] == 2
    if backend in ['bokeh', 'plotly']:
        assert opts.get('width') is None
        assert opts.get('height') is None
    elif backend == 'matplotlib':
        assert opts.get('fig_size') is None


def test_aspect_and_width(df, backend):
    plot = df.hvplot(x='x', y='y', width=150, aspect=2)
    opts = Store.lookup_options(backend, plot, 'plot').kwargs
    assert opts['aspect'] == 2
    if backend in ['bokeh', 'plotly']:
        assert opts.get('width') == 150
        assert opts.get('height') is None
    elif backend == 'matplotlib':
        assert opts.get('fig_size') == pytest.approx(50.0)


data_aspect_backends = pytest.mark.parametrize(
    'backend',
    [
        'bokeh',
        'matplotlib',
        pytest.param(
            'plotly', marks=pytest.mark.xfail(reason='data_aspect not supported w/ plotly')
        ),
    ],
    indirect=True,
)


@data_aspect_backends
def test_data_aspect(df, backend):
    plot = df.hvplot(x='x', y='y', data_aspect=2)
    opts = Store.lookup_options(backend, plot, 'plot').kwargs
    assert opts['data_aspect'] == 2
    if backend == 'bokeh':
        assert opts.get('width') is None
        assert opts.get('height') is None
    elif backend == 'matplotlib':
        assert opts.get('fig_size') is None


@data_aspect_backends
def test_data_aspect_and_width(df, backend):
    plot = df.hvplot(x='x', y='y', width=150, data_aspect=2)
    opts = Store.lookup_options(backend, plot, 'plot').kwargs
    assert opts['data_aspect'] == 2
    if backend == 'bokeh':
        assert opts.get('width') == 150
        assert opts.get('height') is None
    elif backend == 'matplotlib':
        assert opts.get('fig_size') == pytest.approx(50.0)


@pytest.mark.parametrize(
    ('backend', 'expected'),
    [
        ('bokeh', {'width': 700, 'height': 300}),
        ('matplotlib', {'fig_size': 700 / 3, 'aspect': 700 / 300}),
        ('plotly', {'width': 700, 'height': 300}),
    ],
    indirect=['backend'],
)
def test_width_and_height_default(df, backend, expected):
    plot = df.hvplot(x='x', y='y')
    opts = Store.lookup_options(backend, plot, 'plot').kwargs
    assert {k: opts[k] for k in expected} == pytest.approx(expected)


@pytest.mark.parametrize(
    ('backend', 'expected'),
    [
        ('bokeh', {'width': 200, 'height': 300}),
        # matplotlib has no pixel size, it gets a figure size and aspect instead.
        ('matplotlib', {'fig_size': 200 / 3, 'aspect': 200 / 300}),
        ('plotly', {'width': 200, 'height': 300}),
    ],
    indirect=['backend'],
)
def test_width(df, backend, expected):
    plot = df.hvplot(x='x', y='y', width=200)
    opts = Store.lookup_options(backend, plot, 'plot').kwargs
    assert {k: opts[k] for k in expected} == pytest.approx(expected)


@pytest.mark.parametrize(
    ('backend', 'expected'),
    [
        ('bokeh', {'width': 700, 'height': 200}),
        ('matplotlib', {'fig_size': 700 / 3, 'aspect': 700 / 200}),
        ('plotly', {'width': 700, 'height': 200}),
    ],
    indirect=['backend'],
)
def test_height(df, backend, expected):
    plot = df.hvplot(x='x', y='y', height=200)
    opts = Store.lookup_options(backend, plot, 'plot').kwargs
    assert {k: opts[k] for k in expected} == pytest.approx(expected)


# frame_width/frame_height and the min/max sizes are Bokeh only options.


def test_frame_width(df):
    plot = df.hvplot(x='x', y='y', frame_width=200)
    opts = Store.lookup_options('bokeh', plot, 'plot').kwargs
    assert opts['frame_width'] == 200
    # The default width and height are not set, they would override it.
    assert opts.get('width') is None
    assert opts.get('height') is None


def test_frame_height(df):
    plot = df.hvplot(x='x', y='y', frame_height=200)
    opts = Store.lookup_options('bokeh', plot, 'plot').kwargs
    assert opts['frame_height'] == 200
    assert opts.get('width') is None
    assert opts.get('height') is None


def test_max_height(df):
    plot = df.hvplot(x='x', y='y', responsive=True, max_height=400)
    opts = Store.lookup_options('bokeh', plot, 'plot').kwargs
    assert opts['max_height'] == 400


def test_max_width(df):
    plot = df.hvplot(x='x', y='y', responsive=True, max_width=400)
    opts = Store.lookup_options('bokeh', plot, 'plot').kwargs
    assert opts['max_width'] == 400


def test_min_height(df):
    plot = df.hvplot(x='x', y='y', responsive=True, min_height=100)
    opts = Store.lookup_options('bokeh', plot, 'plot').kwargs
    assert opts['min_height'] == 100


def test_min_width(df):
    plot = df.hvplot(x='x', y='y', responsive=True, min_width=100)
    opts = Store.lookup_options('bokeh', plot, 'plot').kwargs
    assert opts['min_width'] == 100


@pytest.mark.parametrize('padding', [0.2, (0.1, 0.3)])
def test_padding(df, backend, padding):
    plot = df.hvplot(x='x', y='y', padding=padding)
    opts = Store.lookup_options(backend, plot, 'plot').kwargs
    assert opts['padding'] == padding


@pytest.mark.parametrize('backend', ['bokeh', 'plotly'], indirect=True)
def test_responsive(df, backend):
    plot = df.hvplot(x='x', y='y', responsive=True)
    opts = Store.lookup_options(backend, plot, 'plot').kwargs
    assert opts['responsive'] is True
    # The default width and height are not set, they would fix the size.
    assert opts.get('width') is None
    assert opts.get('height') is None


@pytest.mark.parametrize(
    ('location', 'layout_type', 'widgets_index'),
    [('bottom', pn.Column, 1), ('left_top', pn.Row, 0), ('right', pn.Row, 1)],
)
def test_widget_location(df, location, layout_type, widgets_index):
    # With widget_location, hvPlot returns a Panel layout instead of a DynamicMap.
    layout = df.hvplot(x='x', y='y', groupby='category', widget_location=location)
    assert isinstance(layout, layout_type)
    assert isinstance(layout[widgets_index], pn.WidgetBox)
    assert layout[1 - widgets_index].widget_location == location
