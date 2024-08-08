import os
import tempfile

from unittest import SkipTest
from collections import OrderedDict

import numpy as np
from holoviews import Store
from holoviews.element import RGB, Image
from holoviews.element.comparison import ComparisonTestCase

try:
    import xarray as xr
except ImportError:
    raise SkipTest('XArray not available')
else:
    import hvplot.xarray  # noqa


class TestGridPlots(ComparisonTestCase):
    def setUp(self):
        coords = OrderedDict([('band', [1, 2, 3]), ('y', [0, 1]), ('x', [0, 1])])
        self.da_rgb = xr.DataArray(np.arange(12).reshape((3, 2, 2)), coords, ['band', 'y', 'x'])
        coords = OrderedDict([('time', [0, 1]), ('band', [1, 2, 3]), ('y', [0, 1]), ('x', [0, 1])])
        self.da_rgb_by_time = xr.DataArray(
            np.arange(24).reshape((2, 3, 2, 2)), coords, ['time', 'band', 'y', 'x']
        )

        coords = OrderedDict([('time', [0, 1]), ('lat', [0, 1]), ('lon', [0, 1])])
        self.da_img_by_time = xr.DataArray(
            np.arange(8).reshape((2, 2, 2)), coords, ['time', 'lat', 'lon']
        ).assign_coords(lat1=xr.DataArray([2, 3], dims=['lat']))

        self.xarr_with_attrs = xr.DataArray(
            np.random.rand(10, 10),
            coords=[('x', range(10)), ('y', range(10))],
            dims=['y', 'x'],
            attrs={'long_name': 'luminosity', 'units': 'lm'},
        )
        self.xarr_with_attrs.x.attrs['long_name'] = 'Declination'
        self.xarr_with_attrs.y.attrs['long_name'] = 'Right Ascension'

        self.xds_with_attrs = xr.Dataset({'light': self.xarr_with_attrs})
        self.da_img = xr.DataArray(np.arange(-2, 2).reshape((2, 2)), name='foo')
        self.big_img = xr.DataArray(np.arange(-1e6, 1e6).reshape(1000, 2000))

        self.ds = xr.Dataset(
            {
                'temp': (('lon', 'lat'), 15 + 8 * np.random.randn(2, 2)),
                'precip': (('lon', 'lat'), 10 * np.random.rand(2, 2)),
            },
            coords={'lon': [-99.83, -99.32], 'lat': [42.25, 42.21]},
        )

        xs = np.linspace(0, 10, 5)
        lon = xs * xs[np.newaxis, :].T
        lat = xs + xs[:, np.newaxis]
        coords = {
            'lon': (('ny', 'nx'), lon),
            'lat': (('ny', 'nx'), lat),
            'time': [1, 2, 3],
            'samples': ('nsamples', [0, 1, 2, 3]),
        }
        self.ds_unindexed = xr.DataArray(
            np.random.rand(5, 5, 3, 4), coords=coords, dims=('nx', 'ny', 'time', 'nsamples')
        )

    def test_rgb_dataarray_no_args(self):
        rgb = self.da_rgb.hvplot()
        self.assertEqual(rgb, RGB(([0, 1], [0, 1]) + tuple(self.da_rgb.values)))

    def test_rgb_dataarray_explicit_args(self):
        rgb = self.da_rgb.hvplot('x', 'y')
        self.assertEqual(rgb, RGB(([0, 1], [0, 1]) + tuple(self.da_rgb.values)))

    def test_rgb_dataarray_explicit_args_and_kind(self):
        rgb = self.da_rgb.hvplot.rgb('x', 'y')
        self.assertEqual(rgb, RGB(([0, 1], [0, 1]) + tuple(self.da_rgb.values)))

    def test_rgb_dataset(self):
        rgb = self.da_rgb.to_dataset(name='z').hvplot.rgb()
        self.assertEqual(rgb, RGB(([0, 1], [0, 1]) + tuple(self.da_rgb.values)))

    def test_rgb_dataset_explicit_z(self):
        rgb = self.da_rgb.to_dataset(name='z').hvplot.rgb(z='z')
        self.assertEqual(rgb, RGB(([0, 1], [0, 1]) + tuple(self.da_rgb.values)))

    def test_rgb_dataset_robust(self):
        rgb = self.da_rgb.to_dataset(name='z').hvplot.rgb(robust=True)
        self.assertNotEqual(rgb, RGB(([0, 1], [0, 1]) + tuple(self.da_rgb.values)))

    def test_rgb_dataarray_groupby_explicit(self):
        rgb = self.da_rgb_by_time.hvplot.rgb('x', 'y', groupby='time')
        self.assertEqual(rgb[0], RGB(([0, 1], [0, 1]) + tuple(self.da_rgb_by_time.values[0])))
        self.assertEqual(rgb[1], RGB(([0, 1], [0, 1]) + tuple(self.da_rgb_by_time.values[1])))

    def test_rgb_dataarray_groupby_infer(self):
        rgb = self.da_rgb_by_time.hvplot.rgb('x', 'y', bands='band')
        self.assertEqual(rgb[0], RGB(([0, 1], [0, 1]) + tuple(self.da_rgb_by_time.values[0])))
        self.assertEqual(rgb[1], RGB(([0, 1], [0, 1]) + tuple(self.da_rgb_by_time.values[1])))

    def test_img_dataarray_infers_correct_other_dims(self):
        img = self.da_img_by_time[0].hvplot()
        self.assertEqual(img, Image(self.da_img_by_time[0], ['lon', 'lat'], ['value']))

    def test_img_dataarray_robust_to_clim_percentile(self):
        img = self.da_img_by_time[0].hvplot(robust=True)
        assert img.opts['clim_percentile'] is True

    def test_img_dataarray_groupby_infers_correct_other_dims(self):
        img = self.da_img_by_time.hvplot(groupby='time')
        self.assertEqual(img[0], Image(self.da_img_by_time[0], ['lon', 'lat'], ['value']))
        self.assertEqual(img[1], Image(self.da_img_by_time[1], ['lon', 'lat'], ['value']))

    def test_line_infer_dimension_params_from_xarray_attrs(self):
        hmap = self.xarr_with_attrs.hvplot.line(groupby='x', dynamic=False)
        self.assertEqual(hmap.kdims[0].label, 'Declination')
        self.assertEqual(hmap.last.kdims[0].label, 'Right Ascension')
        self.assertEqual(hmap.last.vdims[0].label, 'luminosity')
        self.assertEqual(hmap.last.vdims[0].unit, 'lm')

    def test_img_infer_dimension_params_from_xarray_attrs(self):
        img = self.xarr_with_attrs.hvplot.image(clim=(0, 2))
        self.assertEqual(img.kdims[0].label, 'Declination')
        self.assertEqual(img.kdims[1].label, 'Right Ascension')
        self.assertEqual(img.vdims[0].label, 'luminosity')
        self.assertEqual(img.vdims[0].unit, 'lm')
        self.assertEqual(img.vdims[0].range, (0, 2))

    def test_table_infer_dimension_params_from_xarray_ds_attrs(self):
        table = self.xds_with_attrs.hvplot.dataset()
        self.assertEqual(table.kdims[0].label, 'Declination')
        self.assertEqual(table.kdims[1].label, 'Right Ascension')
        self.assertEqual(table.vdims[0].label, 'luminosity')
        self.assertEqual(table.vdims[0].unit, 'lm')

    def test_points_infer_dimension_params_from_xarray_attrs(self):
        points = self.xarr_with_attrs.hvplot.points(c='value', clim=(0, 2))
        self.assertEqual(points.kdims[0].label, 'Declination')
        self.assertEqual(points.kdims[1].label, 'Right Ascension')
        self.assertEqual(points.vdims[0].label, 'luminosity')
        self.assertEqual(points.vdims[0].unit, 'lm')
        self.assertEqual(points.vdims[0].range, (0, 2))

    def test_dataset_infer_dimension_params_from_xarray_attrs(self):
        ds = self.xarr_with_attrs.hvplot.dataset()
        self.assertEqual(ds.kdims[0].label, 'Declination')
        self.assertEqual(ds.kdims[1].label, 'Right Ascension')
        self.assertEqual(ds.vdims[0].label, 'luminosity')
        self.assertEqual(ds.vdims[0].unit, 'lm')

    def test_table_infer_dimension_params_from_xarray_attrs(self):
        table = self.xarr_with_attrs.hvplot.dataset()
        self.assertEqual(table.kdims[0].label, 'Declination')
        self.assertEqual(table.kdims[1].label, 'Right Ascension')
        self.assertEqual(table.vdims[0].label, 'luminosity')
        self.assertEqual(table.vdims[0].unit, 'lm')

    def test_symmetric_img_deduces_symmetric(self):
        plot = self.da_img.hvplot.image()
        plot_opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(plot_opts.kwargs.get('symmetric'), True)
        style_opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(style_opts.kwargs['cmap'], 'coolwarm')

    def test_symmetric_img_with_symmetric_set_to_false(self):
        plot = self.da_img.hvplot.image(symmetric=False)
        plot_opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(plot_opts.kwargs.get('symmetric'), False)
        style_opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(style_opts.kwargs['cmap'], 'kbc_r')

    def test_symmetric_img_with_cmap_set(self):
        plot = self.da_img.hvplot.image(cmap='fire')
        plot_opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(plot_opts.kwargs.get('symmetric'), True)
        style_opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(style_opts.kwargs['cmap'], 'fire')

    def test_symmetric_with_big_img_sets_symmetric_to_false_without_calculating(self):
        plot = self.big_img.hvplot.image()
        plot_opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(plot_opts.kwargs.get('symmetric'), False)
        style_opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(style_opts.kwargs['cmap'], 'kbc_r')

    def test_symmetric_with_big_img_and_check_symmetric_max_calculates_symmetric(self):
        plot = self.big_img.hvplot.image(check_symmetric_max=int(1e7))
        plot_opts = Store.lookup_options('bokeh', plot, 'plot')
        self.assertEqual(plot_opts.kwargs.get('symmetric'), True)
        style_opts = Store.lookup_options('bokeh', plot, 'style')
        self.assertEqual(style_opts.kwargs['cmap'], 'coolwarm')

    def test_multiple_zs(self):
        plot = self.ds.hvplot(x='lat', y='lon', z=['temp', 'precip'], dynamic=False)
        assert 'temp' in plot.keys()
        assert 'precip' in plot.keys()
        assert plot['temp'].kdims == ['lat', 'lon']
        assert plot['precip'].kdims == ['lat', 'lon']

    def test_unindexed_quadmesh(self):
        plot = self.ds_unindexed.hvplot.quadmesh(x='lon', y='lat')
        assert len(plot.kdims) == 2
        assert plot.kdims[0].name == 'time'
        assert plot.kdims[1].name == 'nsamples'
        p = plot[1, 0]
        assert len(p.kdims) == 2
        assert p.kdims[0].name == 'lon'
        assert p.kdims[1].name == 'lat'

    def test_symmetric_dataset_not_in_memory(self):
        # Creating a netcdf file and loading it as to get an non in memory
        # DataArray.
        da = xr.DataArray(
            data=np.arange(-100, 100).reshape(10, 10, 2),
            dims=['x', 'y', 'z'],
            coords={'x': np.arange(10), 'y': np.arange(10), 'z': np.arange(2)},
        )
        ds = xr.Dataset(data_vars={'value': da})
        with tempfile.TemporaryDirectory() as tempdir:
            fpath = os.path.join(tempdir, 'data.nc')
            ds.to_netcdf(fpath)
            ds = xr.open_dataset(fpath)
            plot = ds.value.hvplot(x='x', y='y', check_symmetric_max=ds.value.size + 1)
            plot[(0)]
            plot_opts = Store.lookup_options('bokeh', plot.last, 'plot')
            # If a DataArray is not in memory, computing whether it's symmetric should
            # not be done and return False.
            assert not plot_opts.kwargs['symmetric']
            ds.close()

    def test_symmetric_dataset_in_memory(self):
        da = xr.DataArray(
            data=np.arange(-100, 100).reshape(10, 10, 2),
            dims=['x', 'y', 'z'],
            coords={'x': np.arange(10), 'y': np.arange(10), 'z': np.arange(2)},
        )
        ds = xr.Dataset(data_vars={'value': da})
        plot = ds.value.hvplot(x='x', y='y', check_symmetric_max=ds.value.size + 1)
        plot[(0)]
        plot_opts = Store.lookup_options('bokeh', plot.last, 'plot')
        # This DataArray happens to be symmetric.
        assert plot_opts.kwargs['symmetric']

    def test_dataarray_unnamed_label(self):
        plot = self.da_rgb.sel(band=1).hvplot.image(label='test')
        assert plot.vdims[0].name == 'test'

    def test_dataarray_unnamed_value_label(self):
        plot = self.da_rgb.sel(band=1).hvplot.image(value_label='test')
        assert plot.vdims[0].name == 'test'

    def test_dataarray_label_precedence(self):
        # name > label > value_label
        plot = self.da_rgb.sel(band=1).rename('a').hvplot.image(label='b')
        assert plot.vdims[0].name == 'a'

        plot = self.da_rgb.sel(band=1).hvplot.image(label='b', value_label='c')
        assert plot.vdims[0].name == 'b'

    def test_tiles_without_gv(self):
        plot = self.ds.hvplot('lon', 'lat', tiles=True)
        assert len(plot) == 2
        assert isinstance(plot.get(1), Image)
        assert 'x' in plot.get(1).data
        assert 'y' in plot.get(1).data
