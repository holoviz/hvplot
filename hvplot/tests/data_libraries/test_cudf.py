import pytest

import hvplot
from hvplot.plotting import hvPlotTabular
from hvplot.tests._deps import requires

# cudf is optional and needs a GPU, so these tests do not run on CI.
pytestmark = requires('cudf')


@pytest.fixture(autouse=True)
def hvplot_cudf():
    import hvplot.cudf  # noqa: F401


def test_cudf_dataframe_patched():
    import cudf

    df = cudf.DataFrame({'x': [1, 3, 5], 'y': [2, 4, 6]})
    assert isinstance(df.hvplot, hvPlotTabular)


def test_cudf_series_patched():
    import cudf

    assert isinstance(cudf.Series([0, 1, 2]).hvplot, hvPlotTabular)


def test_unpatch_cudf():
    import cudf

    classes = [cudf.DataFrame, cudf.Series]

    hvplot.cudf._unpatch()
    assert not any('hvplot' in vars(cls) or 'interactive' in vars(cls) for cls in classes)
    assert 'hvplot.cudf' not in hvplot._module_extensions

    # Ends patched, the _isolate_hvplot fixture unpatches it after the test.
    hvplot.cudf.patch()
    assert all('hvplot' in vars(cls) and 'interactive' in vars(cls) for cls in classes)
    assert 'hvplot.cudf' in hvplot._module_extensions
