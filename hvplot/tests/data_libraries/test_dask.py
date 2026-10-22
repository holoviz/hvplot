import pandas as pd
import pytest

import hvplot
from hvplot.plotting import hvPlotTabular
from hvplot.tests._deps import requires

# dask is optional, it is imported in the tests.
pytestmark = requires('dask')


@pytest.fixture(autouse=True)
def hvplot_dask():
    import hvplot.dask  # noqa: F401


def test_dask_series_patched():
    import dask.dataframe as dd

    dseries = dd.from_pandas(pd.Series([0, 1, 2]), npartitions=2)
    assert isinstance(dseries.hvplot, hvPlotTabular)


def test_dask_dataframe_patched():
    import dask.dataframe as dd

    df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
    ddf = dd.from_pandas(df, npartitions=2)
    assert isinstance(ddf.hvplot, hvPlotTabular)


def test_unpatch_dask():
    import dask.dataframe as dd

    classes = [dd.DataFrame, dd.Series]

    hvplot.dask._unpatch()
    assert not any('hvplot' in vars(cls) or 'interactive' in vars(cls) for cls in classes)
    assert 'hvplot.dask' not in hvplot._module_extensions

    # Ends patched, the _isolate_hvplot fixture unpatches it after the test.
    hvplot.dask.patch()
    assert all('hvplot' in vars(cls) and 'interactive' in vars(cls) for cls in classes)
    assert 'hvplot.dask' in hvplot._module_extensions
