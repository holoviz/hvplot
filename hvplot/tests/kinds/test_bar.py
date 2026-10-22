import pandas as pd
import pytest


@pytest.mark.parametrize('tabular_lib', ['pandas', 'dask'], indirect=True)
def test_bar_y_from_index_with_by(tabular_lib):
    cat_df = pd.DataFrame([[1, 2, 'A'], [3, 4, 'B'], [5, 6, 'C']], columns=['x', 'y', 'category'])
    df = tabular_lib(cat_df.set_index('y'))
    # Testing a somewhat silly plot but that seemed to be supported
    # https://github.com/holoviz/hvplot/blob/6c96c7e9abcd44380d2122e3d86827dedab32dea/hvplot/converter.py#L1996-L1999
    plot = df.hvplot.bar(x='x', y='y', by='category')
    assert plot.kdims == ['x', 'category']
    assert plot.vdims == ['y']
