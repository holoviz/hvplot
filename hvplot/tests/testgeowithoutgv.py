"""
Geo tests **without** importing GeoViews.
"""

import holoviews as hv
import hvplot.pandas  # noqa
import numpy as np
import pandas as pd
import pytest

from hvplot.util import is_geodataframe

try:
    import dask.dataframe as dd
    import hvplot.dask  # noqa
except ImportError:
    dd = None

try:
    import spatialpandas as spd
except ModuleNotFoundError:
    spd = None


bk_renderer = hv.Store.renderers['bokeh']


@pytest.fixture
def simple_df():
    return pd.DataFrame(np.random.rand(10, 2), columns=['x', 'y'])


class TestAnnotationNotGeo:
    def test_plot_tiles_doesnt_set_geo(self, simple_df):
        plot = simple_df.hvplot.points('x', 'y', tiles=True)
        assert len(plot) == 2
        assert isinstance(plot.get(0), hv.Tiles)
        assert 'openstreetmap' in plot.get(0).data
        assert 'x_' in plot.get(1).data
        assert 'y_' in plot.get(1).data
        bk_plot = bk_renderer.get_plot(plot)
        assert bk_plot.projection == 'mercator'

    def test_plot_specific_tiles_doesnt_set_geo(self, simple_df):
        plot = simple_df.hvplot.points('x', 'y', tiles='ESRI')
        assert len(plot) == 2
        assert isinstance(plot.get(0), hv.Tiles)
        assert 'ArcGIS' in plot.get(0).data
        assert 'x_' in plot.get(1).data
        assert 'y_' in plot.get(1).data
        bk_plot = bk_renderer.get_plot(plot)
        assert bk_plot.projection == 'mercator'

    def test_plot_with_specific_tile_class(self, simple_df):
        plot = simple_df.hvplot.points('x', 'y', tiles=hv.element.tiles.EsriImagery)
        assert len(plot) == 2
        assert isinstance(plot.get(0), hv.Tiles)
        assert 'ArcGIS' in plot.get(0).data
        bk_plot = bk_renderer.get_plot(plot)
        assert bk_plot.projection == 'mercator'

    def test_plot_with_specific_tile_obj(self, simple_df):
        plot = simple_df.hvplot.points('x', 'y', tiles=hv.element.tiles.EsriImagery())
        assert len(plot) == 2
        assert isinstance(plot.get(0), hv.Tiles)
        assert 'ArcGIS' in plot.get(0).data
        assert 'x_' in plot.get(1).data
        assert 'y_' in plot.get(1).data
        bk_plot = bk_renderer.get_plot(plot)
        assert bk_plot.projection == 'mercator'

    def test_plot_with_xyzservices_tileprovider(self, simple_df):
        xyzservices = pytest.importorskip('xyzservices')
        plot = simple_df.hvplot.points('x', 'y', tiles=xyzservices.providers.Esri.WorldImagery)
        assert 'x_' in plot.get(1).data
        assert 'y_' in plot.get(1).data
        assert len(plot) == 2
        assert isinstance(plot.get(0), hv.Tiles)
        assert isinstance(plot.get(0).data, xyzservices.TileProvider)
        bk_plot = bk_renderer.get_plot(plot)
        assert bk_plot.projection == 'mercator'

    @pytest.mark.skipif(dd is None, reason='dask not installed')
    def test_plot_with_dask(self, simple_df):
        ddf = dd.from_pandas(simple_df, npartitions=2)
        plot = ddf.hvplot.points('x', 'y', tiles=True)
        assert 'x_' not in plot.get(1).data
        assert 'y_' not in plot.get(1).data
        assert len(plot) == 2
        assert isinstance(plot.get(0), hv.Tiles)
        bk_plot = bk_renderer.get_plot(plot)
        assert bk_plot.projection == 'mercator'

    @pytest.mark.skipif(spd is None, reason='spatialpandas not installed')
    def test_plot_without_crs(self):
        square = spd.geometry.Polygon([(0.0, 0), (0, 1), (1, 1), (1, 0)])
        sdf = spd.GeoDataFrame({'geometry': spd.GeoSeries([square, square]), 'name': ['A', 'B']})
        plot = sdf.hvplot.polygons(tiles=True)

        assert len(plot) == 2
        assert is_geodataframe(sdf)
        assert not hasattr(sdf, 'crs')
        assert isinstance(plot.get(0), hv.Tiles)
        assert isinstance(plot.get(1), hv.Polygons)
        bk_plot = bk_renderer.get_plot(plot)
        assert bk_plot.projection == 'mercator'  # projection enabled due to `tiles=True`

    def test_xlim_ylim_conversion_with_tiles(self, simple_df):
        """Test that xlim and ylim are automatically converted to Web Mercator when tiles=True"""
        from holoviews.util.transform import lon_lat_to_easting_northing
        
        # Create a dataframe with lat/lon-like data
        df = pd.DataFrame({
            'lon': [-120.0, -100.0, -80.0],
            'lat': [30.0, 35.0, 40.0],
            'value': [1, 2, 3]
        })
        
        # Plot with xlim and ylim in lat/lon coordinates
        plot = df.hvplot.points('lon', 'lat', tiles=True, xlim=(-130, -70), ylim=(25, 45))
        
        # Get the Points element from the overlay
        points = plot.get(1)
        
        # Check that the coordinates were converted
        assert 'x' in points.data.columns or 'x_' in points.data.columns
        assert 'y' in points.data.columns or 'y_' in points.data.columns
        
        # Calculate expected xlim and ylim in Web Mercator
        xlim_expected_0, _ = lon_lat_to_easting_northing(-130, 0)
        xlim_expected_1, _ = lon_lat_to_easting_northing(-70, 0)
        _, ylim_expected_0 = lon_lat_to_easting_northing(0, 25)
        _, ylim_expected_1 = lon_lat_to_easting_northing(0, 45)
        
        # Get the plot opts
        bk_plot = bk_renderer.get_plot(plot)
        
        # Check that xlim and ylim were converted
        # The plot should have x_range and y_range set to the converted values
        assert hasattr(bk_plot.handles['plot'], 'x_range')
        assert hasattr(bk_plot.handles['plot'], 'y_range')
        
        # Verify the ranges are in Web Mercator (much larger values than lat/lon)
        x_range_start = bk_plot.handles['plot'].x_range.start
        x_range_end = bk_plot.handles['plot'].x_range.end
        y_range_start = bk_plot.handles['plot'].y_range.start
        y_range_end = bk_plot.handles['plot'].y_range.end
        
        # Web Mercator values should be much larger than lat/lon
        # xlim in Web Mercator should be around -14e6 to -7e6
        assert abs(x_range_start) > 10000000  # Much larger than -130
        assert abs(x_range_end) > 7000000  # Much larger than -70
        
        # ylim in Web Mercator should be around 2.8e6 to 5.6e6
        assert y_range_start > 2000000  # Much larger than 25
        assert y_range_end > 5000000  # Much larger than 45
        
        # Check that the values are approximately correct
        assert abs(x_range_start - xlim_expected_0) < 100000
        assert abs(x_range_end - xlim_expected_1) < 100000
        assert abs(y_range_start - ylim_expected_0) < 100000
        assert abs(y_range_end - ylim_expected_1) < 100000

    def test_xlim_ylim_not_converted_without_tiles(self):
        """Test that xlim and ylim are NOT converted when tiles=False"""
        # Create a dataframe with lat/lon-like data
        df = pd.DataFrame({
            'lon': [-120.0, -100.0, -80.0],
            'lat': [30.0, 35.0, 40.0],
            'value': [1, 2, 3]
        })
        
        # Plot without tiles - xlim/ylim should NOT be converted
        plot = df.hvplot.points('lon', 'lat', xlim=(-130, -70), ylim=(25, 45))
        
        # Get the plot opts - note: without tiles it's a Points element, not an overlay
        bk_plot = bk_renderer.get_plot(plot)
        
        # Check that xlim and ylim were NOT converted (still in lat/lon range)
        x_range_start = bk_plot.handles['plot'].x_range.start
        x_range_end = bk_plot.handles['plot'].x_range.end
        y_range_start = bk_plot.handles['plot'].y_range.start
        y_range_end = bk_plot.handles['plot'].y_range.end
        
        # Values should still be in lat/lon range
        assert -140 < x_range_start < -120
        assert -80 < x_range_end < -60
        assert 20 < y_range_start < 30
        assert 40 < y_range_end < 50

    def test_xlim_ylim_out_of_bounds_not_converted(self):
        """Test that xlim and ylim are NOT converted when values are outside lat/lon bounds"""
        # Create a dataframe with arbitrary data
        df = pd.DataFrame({
            'x': [1000.0, 2000.0, 3000.0],
            'y': [500.0, 600.0, 700.0],
            'value': [1, 2, 3]
        })
        
        # Plot with tiles but xlim/ylim outside lat/lon bounds
        plot = df.hvplot.points('x', 'y', tiles=True, xlim=(1000, 3000), ylim=(400, 800))
        
        # Get the plot opts
        bk_plot = bk_renderer.get_plot(plot.get(1))
        
        # Check that xlim and ylim were NOT converted (still in original range)
        x_range_start = bk_plot.handles['plot'].x_range.start
        x_range_end = bk_plot.handles['plot'].x_range.end
        y_range_start = bk_plot.handles['plot'].y_range.start
        y_range_end = bk_plot.handles['plot'].y_range.end
        
        # Values should still be in original range (not Web Mercator)
        assert 900 < x_range_start < 1100
        assert 2900 < x_range_end < 3100
        assert 300 < y_range_start < 500
        assert 700 < y_range_end < 900
