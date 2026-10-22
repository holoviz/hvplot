import holoviews as hv
import pandas as pd
import pytest
from holoviews import Store

from hvplot.plotting import parallel_coordinates


@pytest.fixture
def df():
    return pd.DataFrame({'class': ['A', 'B', 'A'], 'x': [0, 2, 1], 'y': [1, 1, 2]})


def style_opts(element):
    return Store.lookup_options('bokeh', element, 'style').kwargs


def plot_opts(element):
    return Store.lookup_options('bokeh', element, 'plot').kwargs


def test_parallel_coordinates_one_curve_per_row(df):
    plot = parallel_coordinates(df, 'class')
    assert isinstance(plot, hv.Overlay)
    assert [curve.label for curve in plot] == ['A', 'A', 'B']
    for curve in plot:
        assert curve.kdims == ['variable']
        assert curve.vdims == ['value']
    assert plot.get(0).array().tolist() == [['x', 0], ['y', 1]]
    assert plot_opts(plot)['legend_limit'] == 5000


def test_parallel_coordinates_defaults(df):
    curve = parallel_coordinates(df, 'class').get(0)
    assert style_opts(curve)['alpha'] == 0.5
    popts = plot_opts(curve)
    assert (popts['width'], popts['height']) == (600, 300)
    assert popts['labelled'] == []


def test_parallel_coordinates_one_color_per_class(df):
    plot = parallel_coordinates(df, 'class')
    colors = [style_opts(curve)['color'] for curve in plot]
    assert colors[0] == colors[1]
    assert colors[0] != colors[2]


def test_parallel_coordinates_cols(df):
    plot = parallel_coordinates(df, 'class', cols=['x'])
    assert plot.get(0).dimension_values('variable').tolist() == ['x']


@pytest.mark.parametrize('cmap_kwarg', ['cmap', 'colormap'])
def test_parallel_coordinates_cmap(df, cmap_kwarg):
    plot = parallel_coordinates(df, 'class', **{cmap_kwarg: ['red', 'blue']})
    assert [style_opts(curve)['color'] for curve in plot] == ['red', 'red', 'blue']


def test_parallel_coordinates_cmap_and_colormap(df):
    with pytest.raises(TypeError, match='Only specify one of `cmap` and `colormap`'):
        parallel_coordinates(df, 'class', cmap='Category10', colormap='Category10')


def test_parallel_coordinates_var_and_value_names(df):
    curve = parallel_coordinates(df, 'class', var_name='var', value_name='val').get(0)
    assert curve.kdims == ['var']
    assert curve.vdims == ['val']
    # Custom names are shown as axis labels.
    assert plot_opts(curve)['labelled'] == ['x', 'y']


def test_parallel_coordinates_options(df):
    curve = parallel_coordinates(df, 'class', alpha=0.8, width=100, height=50, line_width=3).get(0)
    sopts = style_opts(curve)
    assert sopts['alpha'] == 0.8
    assert sopts['line_width'] == 3
    popts = plot_opts(curve)
    assert (popts['width'], popts['height']) == (100, 50)
