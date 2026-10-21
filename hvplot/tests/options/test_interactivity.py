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
    @pytest.mark.parametrize(
        'toolbar', ['right', 'left', 'above', 'below', None, False, True, 'disable']
    )
    def test_toolbar(self, df, backend, toolbar):
        if backend != 'bokeh':
            pytest.skip(f'toolbar not supported w/ {backend}')

        plot = df.hvplot.scatter('x', 'y', toolbar=toolbar)
        opts = Store.lookup_options(backend, plot, 'plot')
        if toolbar is True:
            toolbar = 'right'
        elif toolbar is False:
            toolbar = None
        assert opts.kwargs['toolbar'] == toolbar

    def test_autohide_toolbar(self, df, backend):
        if backend != 'bokeh':
            pytest.skip(f'autohide_toolbar not supported w/ {backend}')

        plot = df.hvplot.scatter('x', 'y', autohide_toolbar=True)
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['autohide_toolbar'] is True
