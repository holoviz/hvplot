import numpy as np
import pytest
import xarray as xr


@pytest.fixture(scope='module')
def da():
    return xr.DataArray(
        data=np.arange(16).reshape((2, 2, 2, 2)),
        coords={'time': [0, 1], 'y': [0, 1], 'x': [0, 1], 'band': [0, 1]},
        dims=['time', 'y', 'x', 'band'],
        name='test',
    )


@pytest.fixture(scope='module')
def ds1(da):
    return xr.Dataset({'foo': da})


@pytest.mark.usefixtures('hvplot_xarray')
class TestXarray:
    def test_dataset_empty_raises(self, ds1, backend):
        with pytest.raises(ValueError, match=r'empty xarray.Dataset'):
            ds1.drop_vars('foo').hvplot()
