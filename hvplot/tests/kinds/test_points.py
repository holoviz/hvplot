import holoviews as hv
import numpy as np
import pandas as pd
import pytest
from holoviews import Store
from holoviews.core.options import AbbreviatedException
from holoviews.element import Points
from holoviews.testing import assert_element_equal

from hvplot.tests._deps import pandas_and_dask, requires

pytestmark = pytest.mark.usefixtures('hvplot_pandas')


def size_opt(backend):
    """The name of the size option, as set by hvPlot for the backend."""
    return 's' if backend == 'matplotlib' else 'size'


@pytest.fixture
def cities():
    import geopandas as gpd

    geometry = gpd.points_from_xy(
        x=[12.45339, 12.44177, 9.51667, 6.13000, 158.14997],
        y=[41.90328, 43.93610, 47.13372, 49.61166, 6.91664],
        crs='EPSG:4326',
    )
    names = ['Vatican City', 'San Marino', 'Vaduz', 'Luxembourg', 'Palikir']
    return gpd.GeoDataFrame({'name': names}, geometry=geometry)


plotly_alpha_dropped = pytest.mark.xfail(
    reason='BUG: alpha is renamed to opacity, which plotly ignores, so it is dropped',
    raises=KeyError,
)
alpha_backends = pytest.mark.parametrize(
    'backend',
    [
        'bokeh',
        pytest.param(
            'matplotlib',
            marks=pytest.mark.xfail(
                reason='HoloViews: matplotlib cannot map a dim to alpha',
                strict=False,
                raises=AbbreviatedException,
            ),
        ),
        pytest.param(
            'plotly',
            marks=plotly_alpha_dropped,
        ),
    ],
    indirect=True,
)


@pytest.fixture
def df():
    return pd.DataFrame(
        {'cat': ['a', 'b', 'c'], 'x': [1, 3, 5], 'y': [2, 4, 6], 'number': [0.1, 0.2, 0.3]}
    )


def test_x(df):
    plot = df.hvplot.points(x='number', y='y')
    assert_element_equal(plot, Points(df, ['number', 'y'], []))


@pandas_and_dask
def test_x_default(df, tabular_lib):
    data = df.drop(columns='cat')
    plot = tabular_lib(data).hvplot.points()
    assert_element_equal(plot, Points(data, ['x', 'y'], []))


@pytest.mark.xfail(reason='BUG: points defaults x/y to the first two columns, not numeric ones')
def test_x_default_first_numeric(df):
    plot = df.hvplot.points()
    assert plot.kdims == ['x', 'y']


@pytest.mark.xfail(reason='BUG: a lone x or y is ignored, the first two columns are plotted')
@pytest.mark.parametrize('kwargs', [{'x': 'number'}, {'y': 'number'}])
def test_x_or_y_only(df, kwargs):
    plot = df.hvplot.points(**kwargs)
    assert 'number' in plot.kdims


@pandas_and_dask
def test_x_index(df, tabular_lib):
    plot = tabular_lib(df).hvplot.points(x='index', y='y', c='x')
    assert_element_equal(plot, Points(df.reset_index(), ['index', 'y'], ['x']))


def test_y(df, tabular_lib):
    plot = tabular_lib(df).hvplot.points(x='x', y='number')
    assert_element_equal(plot, Points(df, ['x', 'number'], []))


def test_c(df, backend):
    plot = df.hvplot.points('x', 'y', c='number')
    assert plot.vdims == ['number']
    color = Store.lookup_options(backend, plot, 'style').kwargs['color']
    assert repr(color) == repr(hv.dim('number'))
    assert Store.lookup_options(backend, plot, 'plot').kwargs['colorbar'] is True


def test_logz(df, backend):
    plot = df.hvplot.points('x', 'y', c='number', logz=True)
    assert Store.lookup_options(backend, plot, 'plot').kwargs['logz'] is True


def test_s(df, backend):
    # The marker area is proportional to s.
    plot = df.hvplot.points('x', 'y', s=16)
    assert Store.lookup_options(backend, plot, 'style').kwargs[size_opt(backend)] == 4


def test_s_dim(df, backend):
    plot = df.hvplot.points('x', 'y', s='number')
    assert 'number' in plot.vdims
    size = Store.lookup_options(backend, plot, 'style').kwargs[size_opt(backend)]
    np.testing.assert_allclose(size.apply(plot), np.sqrt(df['number']))


def test_s_dim_overlay(df, backend):
    plot = df.hvplot.points('x', 'y', s='number', by='cat')
    size = Store.lookup_options(backend, plot.last, 'style').kwargs[size_opt(backend)]
    np.testing.assert_allclose(size.apply(plot.last), np.sqrt([0.3]))
    assert 'number' in plot.last.vdims


def test_scale(df, backend):
    plot = df.hvplot.points('x', 'y', s=16, scale=2)
    assert Store.lookup_options(backend, plot, 'style').kwargs[size_opt(backend)] == 8


def test_scale_dim(df, backend):
    plot = df.hvplot.points('x', 'y', s='number', scale=2)
    size = Store.lookup_options(backend, plot, 'style').kwargs[size_opt(backend)]
    np.testing.assert_allclose(size.apply(plot), np.sqrt(df['number']) * 2)


def test_scale_dim_expression(df, backend):
    plot = df.hvplot.points('x', 'y', s=hv.dim('number') * 10, scale=2)
    size = Store.lookup_options(backend, plot, 'style').kwargs[size_opt(backend)]
    np.testing.assert_allclose(size.apply(plot), df['number'] * 20)


def test_marker(df, backend):
    plot = df.hvplot.points('x', 'y', marker='^')
    assert Store.lookup_options(backend, plot, 'style').kwargs['marker'] == '^'


# hvPlot does not document that matplotlib cannot map a marker to a column.
@pytest.mark.parametrize(
    'backend',
    [
        'bokeh',
        pytest.param(
            'matplotlib',
            marks=pytest.mark.render_xfail(
                reason='HoloViews: matplotlib cannot map a dim to marker',
                strict=False,
                raises=AbbreviatedException,
            ),
        ),
        'plotly',
    ],
    indirect=True,
)
def test_marker_dim(df, backend):
    plot = df.hvplot.points('x', 'y', marker='cat')
    assert 'cat' in plot.vdims
    assert Store.lookup_options(backend, plot, 'style').kwargs['marker'] == 'cat'


@alpha_backends
def test_alpha_dim(df, backend):
    plot = df.hvplot.points('x', 'y', alpha='number')
    opts = Store.lookup_options(backend, plot, 'style')
    assert opts.kwargs['alpha'] == 'number'
    assert 'number' in plot.vdims
    hv.render(plot, backend=backend)


# Unlike without `by`, the alpha mapping renders with matplotlib.
@pytest.mark.parametrize(
    'backend',
    [
        'bokeh',
        'matplotlib',
        pytest.param(
            'plotly',
            marks=plotly_alpha_dropped,
        ),
    ],
    indirect=True,
)
def test_alpha_dim_overlay(df, backend):
    plot = df.hvplot.points('x', 'y', alpha='number', by='cat')
    opts = Store.lookup_options(backend, plot.last, 'style')
    assert opts.kwargs['alpha'] == 'number'
    assert 'number' in plot.last.vdims
    hv.render(plot, backend=backend)


@pytest.mark.geo
@requires('geopandas', 'shapely')
def test_c_positional_geodataframe(cities):
    points = cities.hvplot('name')
    assert points.kdims == ['x', 'y']
    assert points.vdims == ['name']
    opts = Store.lookup_options('bokeh', points, 'style').kwargs
    assert repr(opts['color']) == repr(hv.dim('name'))


@pytest.mark.geo
@requires('geopandas', 'shapely')
def test_c_geodataframe(cities):
    points = cities.hvplot(c='name')
    assert points.kdims == ['x', 'y']
    assert points.vdims == ['name']
    opts = Store.lookup_options('bokeh', points, 'style').kwargs
    assert repr(opts['color']) == repr(hv.dim('name'))


@pytest.mark.geo
@requires('geopandas', 'shapely')
def test_by_geodataframe(cities):
    points = cities.hvplot(by='name')
    assert isinstance(points, hv.NdOverlay)
    assert points.kdims == ['name']
    assert points.vdims == []
    for element in points.values():
        assert element.kdims == ['x', 'y']
        assert element.vdims == []
