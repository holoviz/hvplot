import pytest

import hvplot
from hvplot.plotting import hvPlotTabular
from hvplot.tests._deps import requires
from hvplot.util import _HV_VERSION

# streamz is optional, it is imported in the tests.
pytestmark = [
    requires('streamz'),
    pytest.mark.filterwarnings('ignore:streamz support has been deprecated:FutureWarning'),
]

hv_without_streamz = pytest.mark.skipif(
    _HV_VERSION >= (1, 23, 0), reason='streamz support has been removed in HoloViews >= 1.23.0'
)


@pytest.fixture(autouse=True)
def hvplot_streamz():
    import hvplot.streamz  # noqa: F401


@pytest.fixture
def random_df():
    from streamz.dataframe import Random

    return Random()


@hv_without_streamz
def test_streamz_dataframe_patched(random_df):
    assert isinstance(random_df.hvplot, hvPlotTabular)


@hv_without_streamz
def test_streamz_series_patched(random_df):
    assert isinstance(random_df.x.hvplot, hvPlotTabular)


@hv_without_streamz
def test_streamz_dataframes_patched(random_df):
    assert isinstance(random_df.groupby('x').sum().hvplot, hvPlotTabular)


@hv_without_streamz
def test_streamz_seriess_patched(random_df):
    assert isinstance(random_df.groupby('x').sum().y.hvplot, hvPlotTabular)


def test_unpatch_streamz():
    import streamz.dataframe as sdf

    classes = [sdf.DataFrame, sdf.DataFrames, sdf.Series, sdf.Seriess]

    hvplot.streamz._unpatch()
    assert not any('hvplot' in vars(cls) for cls in classes)
    assert 'hvplot.streamz' not in hvplot._module_extensions

    # Ends patched, the _isolate_hvplot fixture unpatches it after the test.
    hvplot.streamz.patch()
    assert all('hvplot' in vars(cls) for cls in classes)
    assert 'hvplot.streamz' in hvplot._module_extensions
