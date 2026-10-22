import pandas as pd
import pytest
from holoviews import NdOverlay
from holoviews.core.dimension import Dimension
from holoviews.element import Area
from holoviews.testing import assert_element_equal


@pytest.mark.parametrize('tabular_lib', ['pandas', 'dask'], indirect=True)
def test_area_stacked(tabular_lib):
    df = tabular_lib(pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y']))
    plot = df.hvplot.area(stacked=True)
    obj = NdOverlay(
        {
            'x': Area(df, 'index', Dimension('x', label='value')),
            'y': Area(df, 'index', Dimension('y', label='value')),
        },
        'Variable',
    )
    assert_element_equal(plot, Area.stack(obj))
