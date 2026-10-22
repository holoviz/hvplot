import pandas as pd
import pytest

import hvplot
from hvplot.plotting import hvPlotTabular

pytestmark = pytest.mark.usefixtures('hvplot_pandas')


def test_pandas_series_patched():
    series = pd.Series([0, 1, 2])
    assert isinstance(series.hvplot, hvPlotTabular)


def test_pandas_dataframe_patched():
    df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
    assert isinstance(df.hvplot, hvPlotTabular)


def test_unpatch_pandas():
    classes = [pd.DataFrame, pd.Series]

    hvplot.pandas._unpatch()
    assert not any('hvplot' in vars(cls) or 'interactive' in vars(cls) for cls in classes)
    assert 'hvplot.pandas' not in hvplot._module_extensions

    # Ends patched, the _isolate_hvplot fixture unpatches it after the test.
    hvplot.pandas.patch()
    assert all('hvplot' in vars(cls) and 'interactive' in vars(cls) for cls in classes)
    assert 'hvplot.pandas' in hvplot._module_extensions
