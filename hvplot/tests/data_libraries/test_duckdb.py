import numpy as np
import pandas as pd
import pytest

import hvplot
from hvplot.plotting import hvPlotTabular
from hvplot.tests._deps import requires

# duckdb is optional, it is imported in the tests.
pytestmark = requires('duckdb')


@pytest.fixture(autouse=True)
def hvplot_duckdb():
    import hvplot.duckdb  # noqa: F401


@pytest.fixture
def connection():
    import duckdb

    connection = duckdb.connect(':memory:')
    yield connection
    connection.close()


def test_duckdb_relation_patched(connection):
    import duckdb

    df = pd.DataFrame({'x': [1, 2, 3], 'y': [1, 2, 3]})
    relation = duckdb.from_df(df, connection=connection)
    assert isinstance(relation.hvplot, hvPlotTabular)


def test_duckdb_connection_patched(connection):
    import duckdb

    df = pd.DataFrame({'x': [1, 2, 3], 'y': [1, 2, 3]})
    duckdb.from_df(df, connection=connection).to_view('test_connection')
    assert isinstance(connection.execute('SELECT * FROM test_connection').hvplot, hvPlotTabular)


@pytest.mark.usefixtures('hvplot_pandas')
@pytest.mark.parametrize(
    'kwargs',
    [
        {},
        {'hover_cols': ['z']},
        pytest.param(
            {'hover_cols': 'all'},
            marks=pytest.mark.xfail(reason='BUG: hover_cols="all" raises UnboundLocalError'),
        ),
    ],
    ids=['default', 'hover_cols', 'hover_cols_all'],
)
def test_plot_connection_result(connection, kwargs):
    df = pd.DataFrame({'x': [1.0, 2.0, 3.0], 'y': [2.0, 4.0, 3.0], 'z': [0.1, 0.2, 0.3]})
    connection.register('test_connection', df)

    plot = connection.execute('SELECT * FROM test_connection').hvplot.scatter(
        x='x', y='y', **kwargs
    )

    expected = df.hvplot.scatter(x='x', y='y', **kwargs)
    assert plot.kdims == expected.kdims
    assert plot.vdims == expected.vdims
    np.testing.assert_array_equal(plot.dimension_values('y'), df['y'])


def test_unpatch_duckdb():
    import duckdb

    classes = [duckdb.DuckDBPyRelation, duckdb.DuckDBPyConnection]

    hvplot.duckdb._unpatch()
    assert not any('hvplot' in vars(cls) for cls in classes)
    assert 'hvplot.duckdb' not in hvplot._module_extensions

    # Ends patched, the _isolate_hvplot fixture unpatches it after the test.
    hvplot.duckdb.patch()
    assert all('hvplot' in vars(cls) for cls in classes)
    assert 'hvplot.duckdb' in hvplot._module_extensions
