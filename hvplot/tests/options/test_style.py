import holoviews as hv
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


@pytest.mark.parametrize(
    'backend',
    [
        'bokeh',
        'matplotlib',
        pytest.param(
            'plotly',
            marks=pytest.mark.render_xfail(reason='HoloViews: plotly fails on a numeric fontsize'),
        ),
    ],
    indirect=True,
)
def test_fontsize_number(df, backend):
    plot = df.hvplot.scatter('x', 'y', fontsize=12)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['fontsize'] == 12


@pytest.mark.parametrize(
    'backend',
    [
        'bokeh',
        pytest.param(
            'matplotlib',
            marks=pytest.mark.render_xfail(
                reason='BUG: the documented fontsize dict with 15pt or 5px fails on matplotlib'
            ),
        ),
        'plotly',
    ],
    indirect=True,
)
def test_fontsize_dict(df, backend):
    fontsize = {'title': '15pt', 'ylabel': '5px', 'ticks': 20}
    plot = df.hvplot.scatter('x', 'y', fontsize=fontsize)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['fontsize'] == fontsize


def test_grid(df, backend):
    plot = df.hvplot.scatter('x', 'y', grid=True)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['show_grid'] is True


def test_grid_false_overrides_holoviews_defaults(df, backend):
    # The grid is off by default, so the default has to be changed to see the option.
    hv.opts.defaults(hv.opts.Scatter(show_grid=True))
    plot = df.hvplot.scatter('x', 'y', grid=False)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['show_grid'] is False
