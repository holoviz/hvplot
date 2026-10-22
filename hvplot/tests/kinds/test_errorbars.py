import pandas as pd
import pytest
from holoviews import Store


@pytest.mark.parametrize('tabular_lib', ['pandas', 'dask'], indirect=True)
def test_errorbars_no_hover(tabular_lib):
    df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])
    df_desc = tabular_lib(df.describe().transpose().sort_values('mean'))
    plot = df_desc.hvplot.errorbars(y='mean', yerr1='std')
    assert list(plot.dimensions()) == ['index', 'mean', 'std']
    bkplot = Store.renderers['bokeh'].get_plot(plot)
    assert not bkplot.tools
