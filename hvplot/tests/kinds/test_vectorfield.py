import numpy as np
import pandas as pd
import pytest
import xarray as xr
from holoviews.element import VectorField


@pytest.fixture
def df():
    return pd.DataFrame(
        {
            'x': [-1, 0, 1, 0],
            'y': [0, -1, 0, 1],
            'angle': [0, np.pi / 2, np.pi, 3 * np.pi / 2],
            'mag': [2, 4, 6, 8],
        }
    )


@pytest.fixture
def ds():
    return xr.Dataset(
        {
            'angle': (('lat', 'lon'), np.zeros((2, 3))),
            'mag': (('lat', 'lon'), np.ones((2, 3))),
        },
        coords={'lat': [10, 20], 'lon': [0, 1, 2]},
    )


def test_x(ds, gridded_lib):
    plot = gridded_lib(ds).hvplot.vectorfield(x='lon', y='lat', angle='angle', mag='mag')
    assert isinstance(plot, VectorField)
    assert plot.kdims == ['lon', 'lat']
    assert sorted(set(plot.dimension_values('lon'))) == [0, 1, 2]


@pytest.mark.lib_render_xfail(
    'ibis', reason='HoloViews: VectorField of an ibis table fails to render'
)
def test_y(df, tabular_lib):
    plot = tabular_lib(df).hvplot.vectorfield(x='x', y='y', angle='angle', mag='mag')
    assert isinstance(plot, VectorField)
    assert plot.kdims == ['x', 'y']
    assert list(plot.dimension_values('y')) == [0, -1, 0, 1]


def test_angle(df, hvplot_pandas):
    plot = df.hvplot.vectorfield(x='x', y='y', angle='angle', mag='mag')
    # VectorField expects the angle as its first value dimension.
    assert plot.vdims[0] == 'angle'
    np.testing.assert_allclose(plot.dimension_values('angle'), df['angle'])


def test_mag(df, hvplot_pandas):
    plot = df.hvplot.vectorfield(x='x', y='y', angle='angle', mag='mag')
    # VectorField expects the magnitude as its second value dimension.
    assert plot.vdims[1] == 'mag'
    assert list(plot.dimension_values('mag')) == [2, 4, 6, 8]
