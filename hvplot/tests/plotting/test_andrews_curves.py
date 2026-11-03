import numpy as np
import pandas as pd
import pytest

from hvplot.plotting import andrews_curves


@pytest.fixture
def df():
    return pd.DataFrame(
        {
            'class': ['A', 'B', 'C'],
            'x': [0, 2, 1],
            'y': [1, 1, 2],
            'z': [2, 1, 1],
        }
    )


def test_andrews_curves_x_axis_data(df):
    curves = andrews_curves(df, 'class')
    assert len(curves) == len(df)
    c1 = curves.get(('Curve', 'A'))
    assert c1.data['t'].between(-np.pi, np.pi).all()
