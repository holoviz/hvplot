"""Fugue test suite"""

import pandas as pd
import holoviews as hv
import pytest

try:
    import duckdb
    import hvplot.duckdb  # noqa: F401
except ImportError:
    pytest.skip(allow_module_level=True)


@pytest.fixture
def table():
    df = pd.DataFrame(
        {
            'g': ['a', 'b', 'a', 'b', 'a', 'b'],
            'x': [1, 2, 3, 4, 5, 6],
            'y': [1, 2, 3, 4, 5, 6],
        }
    )
    return df


@pytest.fixture
def connection():
    return duckdb.connect(':memory:')


def test_duckdb_relation(table, connection):
    plot = duckdb.from_df(table, connection=connection).hvplot(
        x='x', y='y', groupby='g', kind='scatter'
    )
    assert isinstance(plot, hv.HoloMap)
    assert plot.kdims == [hv.Dimension('g')]

    a_plot = plot['a']
    assert isinstance(a_plot, hv.Scatter)
    assert a_plot.kdims == [hv.Dimension('x')]
    assert a_plot.vdims == [hv.Dimension('y')]


def test_duckdb_connection(table, connection):
    duckdb.from_df(table, connection=connection).to_view('test_connection')
    plot = connection.execute('SELECT * FROM test_connection').hvplot(
        x='x', y='y', groupby='g', kind='scatter'
    )
    assert isinstance(plot, hv.HoloMap)
    assert plot.kdims == [hv.Dimension('g')]

    a_plot = plot['a']
    assert isinstance(a_plot, hv.Scatter)
    assert a_plot.kdims == [hv.Dimension('x')]
    assert a_plot.vdims == [hv.Dimension('y')]
