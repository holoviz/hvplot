import numpy as np
import pandas as pd
import pytest
import xarray as xr
from holoviews import Dataset

from hvplot.tests._deps import POLARS_2


@pytest.fixture(scope='module')
def df():
    return pd.DataFrame({'x': [1, 2, 3], 'y': [1.0, 4.0, 2.0], 'z': [0.5, 1.0, 1.5]})


@pytest.mark.lib_xfail(
    'polars', condition=POLARS_2, reason='BUG: uses pl.NUMERIC_DTYPES, removed in polars 2.0'
)
def test_dataset_tabular(df, tabular_lib):
    plot = tabular_lib(df).hvplot.dataset()
    assert type(plot) is Dataset
    assert plot.dimensions() == ['x', 'y', 'z']


def test_dataset_gridded(gridded_lib):
    da = xr.DataArray(np.ones((2, 3)), coords={'y': [0, 1], 'x': [0, 1, 2]}, name='v')
    plot = gridded_lib(da).hvplot.dataset()
    assert type(plot) is Dataset
    assert plot.kdims == ['x', 'y']
    assert plot.vdims == ['v']


@pytest.mark.xfail(
    strict=True,
    reason='BUG: dataset keeps all the columns, `columns` is only used by a dead branch '
    "('dataset' is always handled as gridded)",
)
def test_columns(df, hvplot_pandas):
    plot = df.hvplot.dataset(columns=['x', 'y'])
    assert plot.dimensions() == ['x', 'y']
