import pandas as pd
import pytest
from holoviews.element import Table


# Only supported for pandas indexes.
def test_table_datetime_index_displayed(hvplot_pandas, rng):
    dt_df = pd.DataFrame(rng.random(90), index=pd.date_range('2019-01-01', '2019-03-31'))
    table = dt_df.hvplot.table()
    assert table.kdims[0] == 'index'


# Not tested with dask as it does not support MultiIndex DataFrames.
def test_table_multi_index_displayed(hvplot_pandas):
    df = pd.DataFrame({'A': [1, 2, 3, 4], 'B': ['a', 'a', 'b', 'b'], 'C': [0, 1, 2, 1.5]})
    multii_df = df.set_index(['A', 'B'])
    table = multii_df.hvplot.table()
    assert table.kdims[:2] == multii_df.index.names


@pytest.mark.parametrize(
    'index, kdim',
    [
        (pd.Index(['x', 'y', 'z'], name='name'), 'name'),
        (pd.Index(['x', 'y', 'z']), 'index'),
        (pd.Index([10, 20, 30], name='id'), 'id'),
        (pd.CategoricalIndex(['x', 'y', 'z'], name='cat'), 'cat'),
    ],
)
def test_table_informative_index_displayed(hvplot_pandas, index, kdim):
    df = pd.DataFrame({'A': [1, 2, 3], 'B': [0.5, 1.5, 2.5]}, index=index)
    table = df.hvplot.table()
    assert table.kdims == [kdim, 'A', 'B']
    assert list(table.dimension_values(kdim)) == list(index)


@pytest.mark.parametrize(
    'index',
    [pd.RangeIndex(3), pd.Index([3, 7, 9])],
    ids=['range', 'unnamed-integer'],
)
def test_table_row_number_index_not_displayed(hvplot_pandas, index):
    # An unnamed integer index only holds row numbers.
    df = pd.DataFrame({'A': [1, 2, 3], 'B': [0.5, 1.5, 2.5]}, index=index)
    table = df.hvplot.table()
    assert table.kdims == ['A', 'B']


@pytest.mark.lib_xfail('ibis', reason='BUG: reads the index of an ibis table')
def test_columns(tabular_lib):
    df = pd.DataFrame({'A': [1, 2], 'B': ['a', 'b'], 'C': [0.5, 1.5]})
    table = tabular_lib(df).hvplot.table(columns=['C', 'A'])
    assert isinstance(table, Table)
    assert table.kdims == ['C', 'A']
    assert list(table.dimension_values('A')) == [1, 2]
