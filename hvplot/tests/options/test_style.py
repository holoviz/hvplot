import pandas as pd
import pytest
from holoviews import Store

pytestmark = pytest.mark.usefixtures('hvplot_pandas')


@pytest.fixture
def df():
    return pd.DataFrame(
        [[1, 2, 'A', 0.1], [3, 4, 'B', 0.2], [5, 6, 'C', 0.3]],
        columns=['x', 'y', 'category', 'number'],
    )


@pytest.mark.parametrize(
    ('backend', 'backend_opts'),
    [
        ('bokeh', {'plot.xgrid.grid_line_color': 'grey'}),
        ('matplotlib', {'axes.frame_on': False}),
    ],
    indirect=['backend'],
)
def test_backend_opts(df, backend, backend_opts):
    plot = df.hvplot.scatter('x', 'y', backend_opts=backend_opts)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['backend_opts'] == backend_opts


def test_fontscale(df, backend):
    plot = df.hvplot.scatter('x', 'y', fontscale=1.5)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['fontscale'] == 1.5


@pytest.mark.parametrize('fontsize', [12, {'title': '15pt', 'ylabel': '5px', 'ticks': 20}])
def test_fontsize(df, backend, fontsize):
    plot = df.hvplot.scatter('x', 'y', fontsize=fontsize)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['fontsize'] == fontsize


@pytest.mark.parametrize('grid', [True, False])
def test_grid(df, backend, grid):
    plot = df.hvplot.scatter('x', 'y', grid=grid)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['show_grid'] is grid
