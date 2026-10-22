import numpy as np
import pandas as pd
import pytest
from holoviews.element import Table


@pytest.mark.parametrize(
    'tabular_lib',
    [
        'pandas',
        pytest.param(
            'dask',
            marks=pytest.mark.xfail(strict=True, reason='Only supported for pandas DatetimeIndex'),
        ),
    ],
    indirect=True,
)
def test_table_datetime_index_displayed(tabular_lib):
    dt_df = pd.DataFrame(np.random.rand(90), index=pd.date_range('2019-01-01', '2019-03-31'))
    table = tabular_lib(dt_df).hvplot.table()
    assert table.kdims[0] == 'index'


# Not tested with dask as it does not support MultiIndex DataFrames.
def test_table_multi_index_displayed(hvplot_pandas):
    df = pd.DataFrame({'A': [1, 2, 3, 4], 'B': ['a', 'a', 'b', 'b'], 'C': [0, 1, 2, 1.5]})
    multii_df = df.set_index(['A', 'B'])
    table = multii_df.hvplot.table()
    assert table.kdims[:2] == multii_df.index.names


@pytest.mark.parametrize(
    'tabular_lib',
    [
        'pandas',
        'dask',
        pytest.param(
            'polars',
            marks=pytest.mark.xfail(
                strict=True, reason='BUG: uses pl.NUMERIC_DTYPES, removed from polars'
            ),
        ),
        'duckdb',
        pytest.param(
            'ibis',
            marks=pytest.mark.xfail(strict=True, reason='BUG: reads the index of an ibis table'),
        ),
    ],
    indirect=True,
)
def test_columns(tabular_lib):
    df = pd.DataFrame({'A': [1, 2], 'B': ['a', 'b'], 'C': [0.5, 1.5]})
    table = tabular_lib(df).hvplot.table(columns=['C', 'A'])
    assert isinstance(table, Table)
    assert table.kdims == ['C', 'A']
    assert list(table.dimension_values('A')) == [1, 2]
