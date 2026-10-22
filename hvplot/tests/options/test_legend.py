import pandas as pd
import pytest
from holoviews import Store

pytestmark = pytest.mark.usefixtures('hvplot_pandas')

pandas_and_dask = pytest.mark.parametrize('tabular_lib', ['pandas', 'dask'], indirect=True)

no_legend_position = pytest.mark.xfail(reason='legend_position not supported w/ plotly')


@pytest.fixture
def df():
    return pd.DataFrame(
        [[1, 2, 'A', 0.1], [3, 4, 'B', 0.2], [5, 6, 'C', 0.3]],
        columns=['x', 'y', 'category', 'number'],
    )


@pytest.fixture
def xy_df():
    return pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])


@pandas_and_dask
@pytest.mark.parametrize(
    'backend',
    ['bokeh', 'matplotlib', pytest.param('plotly', marks=no_legend_position)],
    indirect=True,
)
def test_legend_scatter_c(tabular_lib, df, backend):
    plot = tabular_lib(df).hvplot.scatter('x', 'y', c='category', legend='left')
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['legend_position'] == 'left'


@pandas_and_dask
@pytest.mark.parametrize(
    'backend',
    ['bokeh', 'matplotlib', pytest.param('plotly', marks=no_legend_position)],
    indirect=True,
)
def test_legend_hist_by(tabular_lib, df, backend):
    plot = tabular_lib(df).hvplot.hist('y', by='category', legend='left')
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['legend_position'] == 'left'


@pandas_and_dask
@pytest.mark.parametrize('kind', ['line', 'area', 'scatter'])
def test_legend_wide(tabular_lib, xy_df, kind):
    df = tabular_lib(xy_df)
    plot = df.hvplot(kind=kind, value_label='Test', group_label='Category', legend='left')
    opts = Store.lookup_options('bokeh', plot, 'plot')
    assert opts.kwargs['legend_position'] == 'left'


@pandas_and_dask
@pytest.mark.parametrize('kind', ['line', 'area', 'scatter'])
def test_legend_by_index(tabular_lib, xy_df, kind):
    plot = tabular_lib(xy_df).hvplot(x='index', y='y', by='x', kind=kind, legend='left')
    opts = Store.lookup_options('bokeh', plot, 'plot')
    assert opts.kwargs['legend_position'] == 'left'


@pytest.mark.parametrize('backend', ['bokeh', 'matplotlib'], indirect=True)
def test_legend_cols(df, backend):
    plot = df.hvplot.scatter('x', 'y', by='category', legend_cols=2)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['legend_cols'] == 2


@pytest.mark.parametrize(
    ('backend', 'legend_opts'),
    [('bokeh', {'spacing': 20}), ('matplotlib', {'labelspacing': 2})],
    indirect=['backend'],
)
def test_legend_opts(df, backend, legend_opts):
    plot = df.hvplot.scatter('x', 'y', by='category', legend_opts=legend_opts)
    opts = Store.lookup_options(backend, plot, 'plot')
    assert opts.kwargs['legend_opts'] == legend_opts
