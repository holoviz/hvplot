import holoviews as hv
import numpy as np
import pandas as pd
import pytest
import xarray as xr

import hvplot.pandas
import hvplot.xarray  # noqa: F401


@pytest.mark.parametrize('data_kind', ['pandas', 'xarray'])
@pytest.mark.parametrize('mag', ['speed', 'Magnitude'])
def test_vectorfield_mag_controls_rendered_lengths(data_kind, mag):
    if data_kind == 'pandas':
        data = pd.DataFrame({'x': [0, 1], 'y': [0, 0], 'angle': [0, 0], mag: [1, 2]})
    else:
        data = xr.Dataset(
            {'angle': (('y', 'x'), [[0, 0]]), mag: (('y', 'x'), [[1, 2]])},
            coords={'x': [0, 1], 'y': [0]},
        )
    vectors = data.hvplot.vectorfield(x='x', y='y', angle='angle', mag=mag)
    plot = hv.renderer('bokeh').get_plot(vectors)

    assert plot.magnitude == mag
    source = plot.handles['source'].data
    lengths = np.abs(source['x1'][:2] - source['x0'][:2])
    np.testing.assert_allclose(lengths[1], 2 * lengths[0])
    assert lengths[0] > 0


def test_vectorfield_mag_matplotlib():
    current_backend = hv.Store.current_backend
    hv.extension('matplotlib')
    hv.Store.set_current_backend('matplotlib')
    try:
        data = pd.DataFrame({'x': [0, 1], 'y': [0, 0], 'angle': [0, 0], 'speed': [1, 2]})
        vectors = data.hvplot.vectorfield(x='x', y='y', angle='angle', mag='speed')
        plot = hv.renderer('matplotlib').get_plot(vectors)
        assert plot.magnitude == 'speed'
        np.testing.assert_allclose(plot.handles['artist'].U, [0.5, 1])
    finally:
        hv.Store.set_current_backend(current_backend)
