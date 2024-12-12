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
