import numpy as np
import pandas as pd
import pytest


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
