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
    def test_bivariate_opts(self, df, backend):
        if backend == 'plotly':
            pytest.xfail('bandwidth, cut, levels not supported w/ plotly for bivariate')

        plot = df.hvplot.bivariate('x', 'y', bandwidth=0.2, cut=1, levels=5, filled=True)
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['bandwidth'] == 0.2
        assert opts.kwargs['cut'] == 1
        assert opts.kwargs['levels'] == 5
        assert opts.kwargs['filled'] is True
