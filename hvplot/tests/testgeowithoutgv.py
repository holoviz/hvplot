"""
Geo tests **without** importing GeoViews.
"""

import holoviews as hv
import hvplot.pandas  # noqa
import numpy as np
import pandas as pd
import pytest

from hvplot.util import is_geodataframe
from holoviews.util.transform import lon_lat_to_easting_northing

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


@pytest.fixture
def lat_lon_df():
    return pd.DataFrame(
        {
            'lon': [-120.0, -100.0, -80.0],
            'lat': [30.0, 35.0, 40.0],
        }
    )


@pytest.fixture
def mercator_df():
    x_merc, y_merc = lon_lat_to_easting_northing(
        np.array([-120.0, -100.0, -80.0]), np.array([30.0, 35.0, 40.0])
    )
    return pd.DataFrame(
        {
            'x': x_merc,
            'y': y_merc,
        }
    )


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
        df = pd.DataFrame(
            {'lon': [-120.0, -100.0, -80.0], 'lat': [30.0, 35.0, 40.0], 'value': [1, 2, 3]}
        )
        plot = df.hvplot.points('lon', 'lat', tiles=True, xlim=(-130, -70), ylim=(25, 45))
        points = plot.get(1)

        assert 'x' in points.data.columns
        assert 'y' in points.data.columns

        xlim_expected_0, _ = lon_lat_to_easting_northing(-130, 0)
        xlim_expected_1, _ = lon_lat_to_easting_northing(-70, 0)
        _, ylim_expected_0 = lon_lat_to_easting_northing(0, 25)
        _, ylim_expected_1 = lon_lat_to_easting_northing(0, 45)

        bk_plot = bk_renderer.get_plot(plot)
        x_range_start = bk_plot.handles['plot'].x_range.start
        x_range_end = bk_plot.handles['plot'].x_range.end
        y_range_start = bk_plot.handles['plot'].y_range.start
        y_range_end = bk_plot.handles['plot'].y_range.end
        assert x_range_start == xlim_expected_0
        assert x_range_end == xlim_expected_1
        assert y_range_start == ylim_expected_0
        assert y_range_end == ylim_expected_1

    def test_xlim_only_conversion_with_tiles(self, lat_lon_df):
        """xlim should convert even when ylim is not provided."""

        plot = lat_lon_df.hvplot.points('lon', 'lat', tiles=True, xlim=(-130, -70))
        bk_plot = bk_renderer.get_plot(plot)

        x_start = bk_plot.state.x_range.start
        x_end = bk_plot.state.x_range.end

        np.testing.assert_almost_equal(x_start, -14471533.803125564)
        np.testing.assert_almost_equal(x_end, -7792364.355529151)
        assert x_start < x_end

    def test_ylim_only_conversion_with_tiles(self, lat_lon_df):
        """ylim should convert even when xlim is not provided."""
        plot = lat_lon_df.hvplot.points('lon', 'lat', tiles=True, ylim=(25, 45))
        bk_plot = bk_renderer.get_plot(plot)

        y_start = bk_plot.state.y_range.start
        y_end = bk_plot.state.y_range.end

        assert y_start > 2_000_000
        assert y_end > 5_000_000
        assert y_start < y_end

    def test_xlim_ylim_not_converted_without_tiles(self, lat_lon_df):
        """Test that xlim and ylim are NOT converted when tiles=False"""
        plot = lat_lon_df.hvplot.points('lon', 'lat', xlim=(-130, -70), ylim=(25, 45))
        bk_plot = bk_renderer.get_plot(plot)

        x_range_start = bk_plot.handles['plot'].x_range.start
        x_range_end = bk_plot.handles['plot'].x_range.end
        y_range_start = bk_plot.handles['plot'].y_range.start
        y_range_end = bk_plot.handles['plot'].y_range.end

        assert x_range_start == -130
        assert x_range_end == -70
        assert y_range_start == 25
        assert y_range_end == 45

    def test_xlim_ylim_out_of_bounds_not_converted(self, mercator_df):
        """Test that xlim and ylim are NOT converted when values are outside lat/lon bounds"""
        plot = mercator_df.hvplot.points('x', 'y', tiles=True, xlim=(1000, 3000), ylim=(400, 800))
        bk_plot = bk_renderer.get_plot(plot.get(1))

        x_range_start = bk_plot.handles['plot'].x_range.start
        x_range_end = bk_plot.handles['plot'].x_range.end
        y_range_start = bk_plot.handles['plot'].y_range.start
        y_range_end = bk_plot.handles['plot'].y_range.end

        assert x_range_start == 1000
        assert x_range_end == 3000
        assert y_range_start == 400
        assert y_range_end == 800
