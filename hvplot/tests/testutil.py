"""
Tests  utilities to convert data and projections
"""
import numpy as np

from unittest import TestCase, SkipTest

from hvplot.util import process_xarray  # noqa


class TestProcessXarray(TestCase):

    def setUp(self):
        try:
            import xarray as xr
            import pandas as pd  # noqa
        except:
            raise SkipTest('xarray or pandas not available')
        self.default_kwargs = {
            'value_label': 'value',
            'label': None,
            'gridded': False,
            'persist': False,
            'use_dask': False,
            'groupby': None,
            'y': None,
            'x': None,
            'by': None,
            'other_dims': [],
        }
        self.ds = xr.tutorial.open_dataset('air_temperature')

    def test_process_1d_xarray_dataarray_with_no_coords(self):
        import xarray as xr
        import pandas as pd

        da = xr.DataArray(
            data=[1, 2, 3])

        data, x, y, by, groupby = process_xarray(data=da, **self.default_kwargs)
        assert isinstance(data, pd.DataFrame)
        assert x == 'index'
        assert y == ['value']
        assert not by
        assert not groupby

    def test_process_1d_xarray_dataarray_with_coords(self):
        import xarray as xr
        import pandas as pd

        da = xr.DataArray(
            data=[1, 2, 3],
            coords={'day': [5, 6, 7]},
            dims=['day'])

        data, x, y, by, groupby = process_xarray(data=da, **self.default_kwargs)
        assert isinstance(data, pd.DataFrame)
        assert x == 'day'
        assert y == ['value']
        assert not by
        assert not groupby

    def test_process_1d_xarray_dataarray_with_coords_and_name(self):
        import xarray as xr
        import pandas as pd

        da = xr.DataArray(
            data=[1, 2, 3],
            coords={'day': [5, 6, 7]},
            dims=['day'],
            name='temp')

        data, x, y, by, groupby = process_xarray(data=da, **self.default_kwargs)
        assert isinstance(data, pd.DataFrame)
        assert x == 'day'
        assert y == ['temp']
        assert not by
        assert not groupby

    def test_process_2d_xarray_dataarray_with_no_coords(self):
        import xarray as xr
        import pandas as pd

        da = xr.DataArray(np.random.randn(4,5))

        data, x, y, by, groupby = process_xarray(data=da, **self.default_kwargs)
        assert isinstance(data, pd.DataFrame)
        assert x == 'index'
        assert y == ['value']
        assert not by
        assert not groupby

    def test_process_2d_xarray_dataarray_with_no_coords_as_gridded(self):
        import xarray as xr

        da = xr.DataArray(np.random.randn(4,5))

        kwargs = self.default_kwargs
        kwargs.update(gridded=True)

        data, x, y, by, groupby = process_xarray(data=da, **kwargs)
        assert isinstance(data, xr.Dataset)
        assert list(data.data_vars.keys()) == ['value']
        assert x == 'dim_1'
        assert y == 'dim_0'
        assert not by
        assert not groupby

    def test_process_2d_xarray_dataarray_with_coords_as_gridded(self):
        import xarray as xr

        da = xr.DataArray(
            data=np.random.randn(4,5),
            coords={'y': [3, 4, 5, 6, 7]},
            dims=['x', 'y'])

        kwargs = self.default_kwargs
        kwargs.update(gridded=True)

        data, x, y, by, groupby = process_xarray(data=da, **kwargs)
        assert isinstance(data, xr.Dataset)
        assert list(data.data_vars.keys()) == ['value']
        assert x == 'y'
        assert y == 'x'
        assert not by
        assert not groupby

    def test_process_3d_xarray_dataset_with_coords(self):
        import pandas as pd

        data, x, y, by, groupby = process_xarray(data=self.ds, **self.default_kwargs)
        assert isinstance(data, pd.DataFrame)
        assert x == 'time'
        assert y == ['air']
        assert not by
        assert groupby == ['lon', 'lat']

    def test_process_3d_xarray_dataset_with_coords_as_gridded(self):
        import xarray as xr

        kwargs = self.default_kwargs
        kwargs.update(gridded=True, x='lon', y='lat')

        data, x, y, by, groupby = process_xarray(data=self.ds, **kwargs)
        assert isinstance(data, xr.Dataset)
        assert list(data.data_vars.keys()) == ['air']
        assert x == 'lon'
        assert y == 'lat'
        assert by is None
        assert groupby == ['time']

    def test_process_3d_xarray_dataset_with_coords_as_gridded_uses_axis_to_get_defaults(self):
        import xarray as xr

        kwargs = self.default_kwargs
        kwargs.update(gridded=True)

        data, x, y, by, groupby = process_xarray(data=self.ds, **kwargs)
        assert isinstance(data, xr.Dataset)
        assert list(data.data_vars.keys()) == ['air']
        assert x == 'lon'
        assert y == 'lat'
        assert not by
        assert groupby == ['time']

    def test_process_xarray_dataset_with_by_as_derived_datetime(self):
        import pandas as pd

        data = self.ds.mean(dim=['lat', 'lon'])
        kwargs = self.default_kwargs
        kwargs.update(gridded=False, y='air', by=['time.hour'])

        data, x, y, by, groupby = process_xarray(data=data, **kwargs)
        assert isinstance(data, pd.DataFrame)
        assert x == 'time'
        assert y == 'air'
        assert by == ['time.hour']
        assert not groupby

    def test_process_xarray_dataset_with_x_as_derived_datetime(self):
        import pandas as pd

        data = self.ds.mean(dim=['lat', 'lon'])
        kwargs = self.default_kwargs
        kwargs.update(gridded=False, y='air', x='time.dayofyear')

        data, x, y, by, groupby = process_xarray(data=data, **kwargs)
        assert isinstance(data, pd.DataFrame)
        assert x == 'time.dayofyear'
        assert y == 'air'
        assert not by
        assert not groupby


class TestGeoUtil(TestCase):

    def setUp(self):
        try:
            import geoviews  # noqa
            import cartopy.crs as ccrs
        except:
            raise SkipTest('geoviews or cartopy not available')
        self.ccrs = ccrs

    def test_proj_to_cartopy(self):
        from ..util import proj_to_cartopy
        crs = proj_to_cartopy('+init=epsg:26911')

        assert isinstance(crs, self.ccrs.CRS)


class TestDynamicArgs(TestCase):

    def setUp(self):
        try:
            import panel as pn  # noqa
        except:
            raise SkipTest('panel not available')

    def test_dynamic_and_static(self):
        import panel as pn
        from ..util import process_dynamic_args

        x = 'sepal_width'
        y = pn.widgets.Select(name='y', value='sepal_length', options=['sepal_length', 'petal_length'])
        kind = pn.widgets.Select(name='kind', value='scatter', options=['bivariate', 'scatter'])

        dynamic, arg_deps, arg_names = process_dynamic_args(x, y, kind)
        assert 'x' not in dynamic
        assert 'y' in dynamic
        assert arg_deps == []

    def test_dynamic_kwds(self):
        import panel as pn
        from ..util import process_dynamic_args

        x = 'sepal_length'
        y = 'sepal_width'
        kind = 'scatter'
        color = pn.widgets.ColorPicker(value='#ff0000')

        dynamic, arg_deps, arg_names = process_dynamic_args(x, y, kind, c=color)
        assert 'x' not in dynamic
        assert 'c' in dynamic
        assert arg_deps == []

    def test_fn_kwds(self):
        import panel as pn
        from ..util import process_dynamic_args

        x = 'sepal_length'
        y = 'sepal_width'
        kind = 'scatter'
        by_species = pn.widgets.Checkbox(name='By species')
        color = pn.widgets.ColorPicker(value='#ff0000')

        @pn.depends(by_species.param.value, color.param.value)
        def by_species_fn(by_species, color):
            return 'species' if by_species else color

        dynamic, arg_deps, arg_names = process_dynamic_args(x, y, kind, c=by_species_fn)
        assert dynamic == {}
        assert arg_names == ['c', 'c']
        assert len(arg_deps) == 2
