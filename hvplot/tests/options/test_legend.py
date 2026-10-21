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
    def test_scatter_legend_position(self, df, backend):
        if backend == 'matplotlib':
            pytest.xfail('legend_position not supported w/ matplotlib for scatter')
        if backend == 'plotly':
            pytest.xfail('legend_position not supported w/ plotly for scatter')

        plot = df.hvplot.scatter('x', 'y', c='category', legend='left')
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['legend_position'] == 'left'

    def test_histogram_by_category_legend_position(self, df, backend):
        if backend == 'plotly':
            pytest.xfail('legend_position not supported w/ plotly for hist')

        plot = df.hvplot.hist('y', by='category', legend='left')
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['legend_position'] == 'left'

    def test_legend_cols(self, df, backend):
        if backend == 'plotly':
            pytest.skip('legend_cols not supported w/ plotly')

        plot = df.hvplot.scatter('x', 'y', by='category', legend_cols=2)
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['legend_cols'] == 2

    def test_legend_opts(self, df, backend):
        if backend == 'plotly':
            pytest.skip('legend_opts not supported w/ plotly')

        if backend == 'bokeh':
            lo = {'spacing': 20}
        elif backend == 'matplotlib':
            lo = {'labelspacing': 2}

        plot = df.hvplot.scatter('x', 'y', by='category', legend_opts=lo)
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['legend_opts'] == lo
