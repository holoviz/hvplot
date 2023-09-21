import re

import holoviews as hv
import pandas as pd
import hvplot.pandas
import hvplot.xarray
import xarray as xr

import pytest

from bokeh.sampledata import penguins
from hvplot.ui import hvDataFrameExplorer, hvGridExplorer

df = penguins.data


def test_explorer_basic():
    explorer = hvplot.explorer(df)

    assert isinstance(explorer, hvDataFrameExplorer)
    assert explorer.kind == "line"
    assert explorer.x == "index"
    assert explorer.y == "species"


def test_explorer_settings():
    explorer = hvplot.explorer(df)

    explorer.param.set_param(
        kind="scatter",
        x="bill_length_mm",
        y_multi=["bill_depth_mm"],
        by=["species"],
    )

    settings = explorer.settings()

    assert settings == dict(
        by=["species"],
        kind="scatter",
        x="bill_length_mm",
        y=["bill_depth_mm"],
    )


def test_explorer_plot_code():
    explorer = hvplot.explorer(df)

    explorer.param.set_param(
        kind="scatter",
        x="bill_length_mm",
        y_multi=["bill_depth_mm"],
        by=["species"],
    )

    hvplot_code = explorer.plot_code()

    assert (
        hvplot_code
        == "df.hvplot(by=['species'], kind='scatter', x='bill_length_mm', y=['bill_depth_mm'])"
    )

    hvplot_code = explorer.plot_code(var_name="othername")

    assert (
        hvplot_code
        == "othername.hvplot(by=['species'], kind='scatter', x='bill_length_mm', y=['bill_depth_mm'])"
    )


def test_explorer_hvplot():
    explorer = hvplot.explorer(df)

    explorer.param.set_param(
        kind="scatter",
        x="bill_length_mm",
        y_multi=["bill_depth_mm"],
    )

    plot = explorer.hvplot()

    assert isinstance(plot, hv.Scatter)
    assert plot.kdims[0].name == "bill_length_mm"
    assert plot.vdims[0].name == "bill_depth_mm"


def test_explorer_save(tmp_path):
    explorer = hvplot.explorer(df)

    explorer.param.set_param(
        kind="scatter",
        x="bill_length_mm",
        y_multi=["bill_depth_mm"],
    )

    outfile = tmp_path / "plot.html"

    explorer.save(outfile)

    assert outfile.exists()


def test_explorer_kwargs_controls():
    explorer = hvplot.explorer(df, title="Dummy title", width=200)

    assert explorer.labels.title == "Dummy title"
    assert explorer.axes.width == 200


def test_explorer_kwargs_controls_error_not_supported():
    with pytest.raises(
        TypeError,
        match=re.escape(
            "__init__() got keyword(s) not supported by any control: {'not_a_control_kwarg': None}"
        ),
    ):
        hvplot.explorer(df, title="Dummy title", not_a_control_kwarg=None)


def test_explorer_hvplot_gridded_basic():
    ds = xr.tutorial.open_dataset("air_temperature")
    explorer = hvplot.explorer(ds)

    assert isinstance(explorer, hvGridExplorer)
    assert isinstance(explorer._data, xr.DataArray)
    assert explorer.kind == "image"
    assert explorer.x == "lat"
    assert explorer.y == "lon"
    assert explorer.by == []
    assert explorer.groupby == ["time"]


def test_explorer_hvplot_gridded_2d():
    ds = xr.tutorial.open_dataset("air_temperature").isel(time=0)
    explorer = hvplot.explorer(ds)

    assert isinstance(explorer, hvGridExplorer)
    assert isinstance(explorer._data, xr.DataArray)
    assert explorer.kind == "image"
    assert explorer.x == "lat"
    assert explorer.y == "lon"
    assert explorer.by == []
    assert explorer.groupby == []


def test_explorer_hvplot_gridded_two_variables():
    ds = xr.tutorial.open_dataset("air_temperature")
    ds["airx2"] = ds["air"] * 2
    explorer = hvplot.explorer(ds)

    assert isinstance(explorer, hvGridExplorer)
    assert isinstance(explorer._data, xr.DataArray)
    assert list(explorer._data["variable"]) == ["air", "airx2"]
    assert explorer.kind == "image"
    assert explorer.x == "lat"
    assert explorer.y == "lon"
    assert explorer.by == []
    assert explorer.groupby == ["time", "variable"]


def test_explorer_hvplot_gridded_dataarray():
    da = xr.tutorial.open_dataset("air_temperature")["air"]
    explorer = hvplot.explorer(da)

    assert isinstance(explorer, hvGridExplorer)
    assert isinstance(explorer._data, xr.DataArray)
    assert explorer.kind == "image"
    assert explorer.x == "lat"
    assert explorer.y == "lon"
    assert explorer.by == []
    assert explorer.groupby == ['time']


def test_explorer_hvplot_gridded_options():
    ds = xr.tutorial.open_dataset("air_temperature")
    explorer = hvplot.explorer(ds)
    assert explorer._controls[0].groups.keys() == {"dataframe", "gridded", "geom"}


def test_explorer_hvplot_geo():
    df = pd.DataFrame({"x": [-9796115.18980811], "y": [4838471.398061159]})
    explorer = hvplot.explorer(df, geo=True)
    assert explorer.geographic.geo
    assert explorer.geographic.global_extent
    assert explorer.geographic.features == ["coastline"]
    assert explorer.geographic.crs == "GOOGLE_MERCATOR"
    assert explorer.geographic.projection == "GOOGLE_MERCATOR"
