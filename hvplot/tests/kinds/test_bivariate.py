import holoviews as hv
import numpy as np
import pandas as pd
import pytest
from holoviews import Store
from holoviews.element import Bivariate, Contours, Polygons


@pytest.fixture
def df(rng):
    # Not collinear, as a density cannot be estimated otherwise.
    x = rng.normal(size=20)
    return pd.DataFrame({'x': x, 'y': x + rng.normal(size=20)})


# plotly has no Bivariate options either, so the options are not found (and the plot can't render).
plotly_no_options = pytest.mark.xfail(
    reason='BUG: bivariate on plotly is not rejected, it has no options and fails with a KeyError',
    raises=KeyError,
)
backends = pytest.mark.parametrize(
    'backend',
    ['bokeh', 'matplotlib', pytest.param('plotly', marks=plotly_no_options)],
    indirect=True,
)
filled_backends = pytest.mark.parametrize(
    'backend',
    [
        'bokeh',
        'matplotlib',
        pytest.param(
            'plotly',
            marks=pytest.mark.render_xfail(
                reason='BUG: bivariate on plotly fails to render with a KeyError, '
                'not a NotImplementedError',
                raises=KeyError,
            ),
        ),
    ],
    indirect=True,
)


bokeh_and_mpl = pytest.mark.parametrize('backend', ['bokeh', 'matplotlib'], indirect=True)


def density_contours(plot, backend):
    """The contours that the backend draws, computed from the Bivariate element."""
    return hv.renderer(backend).get_plot(plot).hmap.last


def test_x(df, hvplot_pandas):
    plot = df.hvplot.bivariate(x='y', y='x')
    assert isinstance(plot, Bivariate)
    assert plot.kdims == ['y', 'x']


def test_y(df, tabular_lib):
    plot = tabular_lib(df).hvplot.bivariate(x='x', y='y')
    assert isinstance(plot, Bivariate)
    assert plot.kdims == ['x', 'y']
    assert plot.vdims == ['Density']


@backends
def test_bandwidth(df, hvplot_pandas, backend):
    plot = df.hvplot.bivariate('x', 'y', bandwidth=0.2)
    assert Store.lookup_options(backend, plot, 'plot').kwargs['bandwidth'] == 0.2


@backends
def test_cut(df, hvplot_pandas, backend):
    plot = df.hvplot.bivariate('x', 'y', cut=1)
    assert Store.lookup_options(backend, plot, 'plot').kwargs['cut'] == 1


@filled_backends
def test_filled(df, hvplot_pandas, backend):
    plot = df.hvplot.bivariate('x', 'y', filled=True)
    assert Store.lookup_options(backend, plot, 'plot').kwargs['filled'] is True


@backends
def test_levels(df, hvplot_pandas, backend):
    plot = df.hvplot.bivariate('x', 'y', levels=5)
    assert Store.lookup_options(backend, plot, 'plot').kwargs['levels'] == 5


@bokeh_and_mpl
def test_bandwidth_effect(df, hvplot_pandas, backend):
    narrow = density_contours(df.hvplot.bivariate('x', 'y', bandwidth=0.2), backend)
    wide = density_contours(df.hvplot.bivariate('x', 'y', bandwidth=2), backend)
    # A narrow kernel gives a peaked density, a wide one gives a spread out density.
    assert narrow.range('Density')[1] > 10 * wide.range('Density')[1]
    assert np.ptp(narrow.range('x')) < np.ptp(wide.range('x'))


@bokeh_and_mpl
def test_cut_effect(df, hvplot_pandas, backend):
    short = density_contours(df.hvplot.bivariate('x', 'y', cut=0.1), backend)
    long = density_contours(df.hvplot.bivariate('x', 'y', cut=5), backend)
    assert np.ptp(short.range('x')) < np.ptp(long.range('x'))


@bokeh_and_mpl
@pytest.mark.parametrize(('levels', 'n_contours'), [(3, 2), (7, 6)])
def test_levels_effect(df, hvplot_pandas, backend, levels, n_contours):
    contours = density_contours(df.hvplot.bivariate('x', 'y', levels=levels), backend)
    assert type(contours) is Contours
    assert len(contours.dimension_values('Density', expanded=False)) == n_contours


@bokeh_and_mpl
def test_filled_effect(df, hvplot_pandas, backend):
    # Polygons subclass Contours.
    assert type(density_contours(df.hvplot.bivariate('x', 'y', filled=True), backend)) is Polygons
    assert type(density_contours(df.hvplot.bivariate('x', 'y'), backend)) is Contours
