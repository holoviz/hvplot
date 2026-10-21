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
    def test_backend_opts(self, df, backend):
        if backend == 'plotly':
            pytest.skip('backend_opts not supported w/ plotly')

        if backend == 'bokeh':
            bo = {'plot.xgrid.grid_line_color': 'grey'}
        elif backend == 'matplotlib':
            bo = {'axes.frame_on': False}
        plot = df.hvplot.scatter('x', 'y', backend_opts=bo)
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['backend_opts'] == bo
