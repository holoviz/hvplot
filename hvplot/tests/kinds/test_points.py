import pandas as pd
import pytest
from holoviews.element import Path, Points
from holoviews.testing import assert_element_equal

kinds = pytest.mark.parametrize(('kind', 'element'), [('points', Points), ('paths', Path)])
tabular_libs = pytest.mark.parametrize('tabular_lib', ['pandas', 'dask'], indirect=True)


@pytest.fixture
def df(tabular_lib):
    return tabular_lib(pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y']))


@tabular_libs
@kinds
def test_2d_defaults(df, kind, element):
    plot = df.hvplot(kind=kind)
    assert_element_equal(plot, element(df, ['x', 'y']))


@tabular_libs
@kinds
def test_2d_chart(df, kind, element):
    plot = df.hvplot(x='x', y='y', kind=kind)
    assert_element_equal(plot, element(df, ['x', 'y']))


@tabular_libs
@kinds
def test_2d_index_and_c(df, kind, element):
    plot = df.hvplot(x='index', y='y', c='x', kind=kind)
    assert_element_equal(plot, element(df, ['index', 'y'], ['x']))
