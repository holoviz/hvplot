import pandas as pd
import pytest
from holoviews import Store


@pytest.fixture(scope='module')
def df():
    return pd.DataFrame(
        [[1, 2, 'A', 0.1], [3, 4, 'B', 0.2], [5, 6, 'C', 0.3]],
        columns=['x', 'y', 'category', 'number'],
    )


@pytest.mark.usefixtures('hvplot_pandas')
class TestOptions:
    @pytest.mark.parametrize('opt', ['aspect', 'data_aspect'])
    def test_aspect(self, df, opt, backend):
        if opt == 'data_aspect' and backend == 'plotly':
            pytest.xfail('data_aspect not supported w/ plotly')

        plot = df.hvplot(x='x', y='y', **{opt: 2})
        opts = Store.lookup_options(backend, plot, 'plot').kwargs
        assert opts[opt] == 2
        if backend in ['bokeh', 'matplotlib']:
            assert opts.get('width') is None
            assert opts.get('height') is None
        elif backend == 'matplotlib':
            assert opts.get('fig_size') is None

    @pytest.mark.parametrize('opt', ['aspect', 'data_aspect'])
    def test_aspect_and_width(self, df, opt, backend):
        if opt == 'data_aspect' and backend == 'plotly':
            pytest.xfail('data_aspect not supported w/ plotly')

        plot = df.hvplot(x='x', y='y', width=150, **{opt: 2})
        opts = Store.lookup_options(backend, plot, 'plot').kwargs
        assert opts[opt] == 2
        if backend in ['bokeh', 'plotly']:
            assert opts.get('width') == 150
            assert opts.get('height') is None
        elif backend == 'matplotlib':
            assert opts.get('fig_size') == pytest.approx(50.0)
