import pytest

import hvplot
from hvplot.plotting import hvPlotTabular
from hvplot.tests._deps import requires

# polars is optional, it is imported in the tests.
pytestmark = requires('polars')


@pytest.fixture(autouse=True)
def hvplot_polars():
    import hvplot.polars  # noqa: F401


def test_polars_series_patched():
    import polars as pl

    pseries = pl.Series([0, 1, 2])
    assert isinstance(pseries.hvplot, hvPlotTabular)


def test_polars_dataframe_patched():
    import polars as pl

    pdf = pl.DataFrame({'x': [1, 3, 5], 'y': [2, 4, 6]})
    assert isinstance(pdf.hvplot, hvPlotTabular)


def test_polars_lazyframe_patched():
    import polars as pl

    pldf = pl.LazyFrame({'x': [1, 3, 5], 'y': [2, 4, 6]})
    assert isinstance(pldf.hvplot, hvPlotTabular)


def test_unpatch_polars():
    import polars as pl

    classes = [pl.DataFrame, pl.Series, pl.LazyFrame]

    hvplot.polars._unpatch()
    assert not any('hvplot' in vars(cls) or 'hvplot' in cls._accessors for cls in classes)
    assert 'hvplot.polars' not in hvplot._module_extensions

    # Ends patched, the _isolate_hvplot fixture unpatches it after the test.
    hvplot.polars.patch()
    assert all('hvplot' in vars(cls) and 'hvplot' in cls._accessors for cls in classes)
    assert 'hvplot.polars' in hvplot._module_extensions
