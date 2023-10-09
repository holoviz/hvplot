import re
from textwrap import dedent

import holoviews as hv
import pandas as pd
import hvplot.pandas
import hvplot.xarray
import xarray as xr
import param

import pytest

from bokeh.sampledata import penguins
from hvplot.ui import hvDataFrameExplorer, hvGridExplorer, Controls

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
        hvplot_code == (
            "df.hvplot(\n"
            "    by=['species'],\n"
            "    kind='scatter',\n"
            "    x='bill_length_mm',\n"
            "    y=['bill_depth_mm']\n"
            ")"
        )
    )

    hvplot_code = explorer.plot_code(var_name="othername")

    assert (
        hvplot_code == (
            "othername.hvplot(\n"
            "    by=['species'],\n"
            "    kind='scatter',\n"
            "    x='bill_length_mm',\n"
            "    y=['bill_depth_mm']\n"
            ")"
        )
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
    assert explorer._controls[1].groups.keys() == {"dataframe", "gridded", "geom"}


def test_explorer_hvplot_geo():
    df = pd.DataFrame({"x": [-9796115.18980811], "y": [4838471.398061159]})
    explorer = hvplot.explorer(df, x="x", geo=True, kind="points")
    assert explorer.geographic.geo
    assert explorer.geographic.global_extent
    assert explorer.geographic.features == ["coastline"]
    assert explorer.geographic.crs == "GOOGLE_MERCATOR"
    assert explorer.geographic.projection == "GOOGLE_MERCATOR"

def test_explorer_hvplot_opts():
    ds = xr.tutorial.open_dataset("air_temperature").isel(time=0)
    explorer = hvplot.explorer(ds, opts={"color_levels": 3})
    assert explorer.hvplot().opts["color_levels"] == 3

def test_explorer_code_dataframe():
    explorer = hvplot.explorer(df, x="bill_length_mm", kind="points")
    assert explorer.code == dedent("""\
        df.hvplot(
            kind='points',
            x='bill_length_mm',
            y='species'
        )"""
    )
    assert explorer._code_pane.object == dedent("""\
        ```python
        import hvplot.pandas

        df.hvplot(
            kind='points',
            x='bill_length_mm',
            y='species'
        )
        ```"""
    )


def test_explorer_code_gridded():
    ds = xr.tutorial.open_dataset("air_temperature")
    explorer = hvplot.explorer(ds, x="lon", y="lat", kind="image")
    code = explorer.code
    assert code == dedent("""\
        ds['air'].hvplot(
            colorbar=True,
            groupby=['time'],
            kind='image',
            x='lon',
            y='lat'
        )""")

    assert explorer._code_pane.object == dedent("""\
        ```python
        import hvplot.xarray

        ds['air'].hvplot(
            colorbar=True,
            groupby=['time'],
            kind='image',
            x='lon',
            y='lat'
        )
        ```"""
    )


def test_explorer_code_gridded_dataarray():
    ds = xr.tutorial.open_dataset("air_temperature")["air"]
    explorer = hvplot.explorer(ds, x="lon", y="lat", kind="image")
    code = explorer.code
    assert code == dedent("""\
        da.hvplot(
            colorbar=True,
            groupby=['time'],
            kind='image',
            x='lon',
            y='lat'
        )""")

    assert explorer._code_pane.object == dedent("""\
        ```python
        import hvplot.xarray

        da.hvplot(
            colorbar=True,
            groupby=['time'],
            kind='image',
            x='lon',
            y='lat'
        )
        ```"""
    )

def test_explorer_code_opts():
    ds = xr.tutorial.open_dataset("air_temperature")["air"]
    explorer = hvplot.explorer(ds, x="lon", y="lat", kind="image", opts={"color_levels": 3})
    explorer._code()
    code = explorer.code
    assert code == dedent("""\
        da.hvplot(
            colorbar=True,
            groupby=['time'],
            kind='image',
            opts={'color_levels': 3},
            x='lon',
            y='lat'
        ).opts(
            color_levels=3
        )""")

    assert explorer._code_pane.object == dedent("""\
        ```python
        import hvplot.xarray

        da.hvplot(
            colorbar=True,
            groupby=['time'],
            kind='image',
            opts={'color_levels': 3},
            x='lon',
            y='lat'
        ).opts(
            color_levels=3
        )
        ```"""
    )

def test_explorer_refresh_plot_linked():
    explorer = hvplot.explorer(df)
    controls = [
        p.name
        for p in explorer.param.objects().values()
        if isinstance(p, param.ClassSelector)
        and issubclass(p.class_, Controls)
    ]
    # by default
    for control in controls:
        assert explorer.refresh_plot == getattr(explorer, control).refresh_plot

    # toggle top level
    explorer.refresh_plot = False
    for control in controls:
        assert explorer.refresh_plot == getattr(explorer, control).refresh_plot

    # toggle axes
    explorer.axes.refresh_plot = True
    for control in controls:
        assert explorer.refresh_plot == getattr(explorer, control).refresh_plot

def test_explorer_code_opts():
    ds = xr.tutorial.open_dataset("air_temperature")["air"]
    explorer = hvplot.explorer(ds, x="lon", y="lat", kind="image", opts={"color_levels": 3})
    explorer._code()
    code = explorer.code
    assert code == dedent("""\
        da.hvplot(
            colorbar=True,
            groupby=['time'],
            kind='image',
            x='lon',
            y='lat'
        ).opts(
            color_levels=3
        )""")

    assert explorer._code_pane.object == dedent("""\
        ```python
        import hvplot.xarray

        da.hvplot(
            colorbar=True,
            groupby=['time'],
            kind='image',
            x='lon',
            y='lat'
        ).opts(
            color_levels=3
        )
        ```"""
    )
