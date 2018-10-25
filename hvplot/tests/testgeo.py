from unittest import TestCase, SkipTest


class TestGeo(TestCase):
    def setUp(self):
        try:
            import xarray as xr
            import rasterio  # noqa
            import geoviews  # noqa
            import cartopy.crs as ccrs
        except:
            raise SkipTest('xarray, rasterio, geoviews, or cartopy not available')
        import hvplot.xarray  # noqa
        self.da = (xr.open_rasterio(
            'https://github.com/mapbox/rasterio/raw/master/tests/data/RGB.byte.tif')
            .sel(band=1))
        self.crs = ccrs.epsg(self.da.crs.split('epsg:')[1])

    def assertCRS(self, plot, proj='utm'):
        assert plot.crs.proj4_params['proj'] == proj

    def test_plot_with_crs_as_object(self):
        plot = self.da.hvplot('x', 'y', crs=self.crs)
        self.assertCRS(plot)

    def test_plot_with_crs_as_proj_string(self):
        plot = self.da.hvplot('x', 'y', crs=self.da.crs)
        self.assertCRS(plot)

    def test_plot_with_geo_as_true_crs_undefined(self):
        plot = self.da.hvplot('x', 'y', geo=True)
        self.assertCRS(plot)

    def test_plot_with_crs_as_attr_str(self):
        da = self.da.copy()
        da.attrs = {'bar': self.crs}
        plot = da.hvplot('x', 'y', crs='bar')
        self.assertCRS(plot)

    def test_plot_with_crs_as_nonexistent_attr_str(self):
        with self.assertRaisesRegex(ValueError, "'foo' must be"):
            self.da.hvplot('x', 'y', crs='foo')

    def test_plot_with_geo_as_true_crs_no_crs_on_data_returns_default(self):
        da = self.da.copy()
        da.attrs = {'bar': self.crs}
        plot = da.hvplot('x', 'y', geo=True)
        self.assertCRS(plot, 'eqc')
