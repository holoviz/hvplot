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
    def test_kde_opts(self, df, backend):
        plot = df.hvplot.kde('x', bandwidth=0.2, cut=1, filled=True)
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['bandwidth'] == 0.2
        assert opts.kwargs['cut'] == 1
        assert opts.kwargs['filled'] is True
