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


aspect_options = pytest.mark.parametrize(
    ('opt', 'backend'),
    [
        ('aspect', 'bokeh'),
        ('aspect', 'matplotlib'),
        ('aspect', 'plotly'),
        ('data_aspect', 'bokeh'),
        ('data_aspect', 'matplotlib'),
        pytest.param(
            'data_aspect',
            'plotly',
            marks=pytest.mark.xfail(reason='data_aspect not supported w/ plotly'),
        ),
    ],
    indirect=['backend'],
)


@aspect_options
def test_aspect(df, opt, backend):
    plot = df.hvplot(x='x', y='y', **{opt: 2})
    opts = Store.lookup_options(backend, plot, 'plot').kwargs
    assert opts[opt] == 2
    if backend in ['bokeh', 'plotly']:
        assert opts.get('width') is None
        assert opts.get('height') is None
    elif backend == 'matplotlib':
        assert opts.get('fig_size') is None


@aspect_options
def test_aspect_and_width(df, opt, backend):
    plot = df.hvplot(x='x', y='y', width=150, **{opt: 2})
    opts = Store.lookup_options(backend, plot, 'plot').kwargs
    assert opts[opt] == 2
    if backend in ['bokeh', 'plotly']:
        assert opts.get('width') == 150
        assert opts.get('height') is None
    elif backend == 'matplotlib':
        assert opts.get('fig_size') == pytest.approx(50.0)
