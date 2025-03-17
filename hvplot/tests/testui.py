import re
from textwrap import dedent
from unittest.mock import patch

import numpy as np
import holoviews as hv
import pandas as pd
import hvplot.pandas
import hvplot.xarray
import xarray as xr

import pytest

from bokeh.sampledata import penguins
from hvplot.ui import hvDataFrameExplorer, hvGridExplorer, MAX_ROWS

df = penguins.data
ds_air_temperature = xr.tutorial.open_dataset('air_temperature')


def test_explorer_basic():
    explorer = hvplot.explorer(df)

    assert isinstance(explorer, hvDataFrameExplorer)
    assert explorer.kind == 'scatter'
    assert explorer.x == 'index'
    assert explorer.y == 'species'


def test_explorer_settings():
    explorer = hvplot.explorer(df)

    explorer.param.update(
        kind='scatter',
        x='bill_length_mm',
        y_multi=['bill_depth_mm'],
        by=['species'],
    )

    settings = explorer.settings()

    assert settings == dict(
        by=['species'],
        kind='scatter',
        x='bill_length_mm',
        y=['bill_depth_mm'],
    )


def test_explorer_plot_code():
    explorer = hvplot.explorer(df)

    explorer.param.update(
        kind='scatter',
        x='bill_length_mm',
        y_multi=['bill_depth_mm'],
        by=['species'],
    )

    hvplot_code = explorer.plot_code()

    assert hvplot_code == (
        'df.hvplot(\n'
        "    by=['species'],\n"
        "    kind='scatter',\n"
        "    x='bill_length_mm',\n"
        "    y=['bill_depth_mm'],\n"
        "    legend='bottom_right',\n"
        "    widget_location='bottom',\n"
        ')'
    )

    hvplot_code = explorer.plot_code(var_name='othername')

    assert hvplot_code == (
        'othername.hvplot(\n'
        "    by=['species'],\n"
        "    kind='scatter',\n"
        "    x='bill_length_mm',\n"
        "    y=['bill_depth_mm'],\n"
        "    legend='bottom_right',\n"
        "    widget_location='bottom',\n"
        ')'
    )


def test_explorer_hvplot():
    explorer = hvplot.explorer(df)

    explorer.param.update(
        kind='scatter',
        x='bill_length_mm',
        y_multi=['bill_depth_mm'],
    )

    plot = explorer.hvplot()

    assert isinstance(plot, hv.Scatter)
    assert plot.kdims[0].name == 'bill_length_mm'
    assert plot.vdims[0].name == 'bill_depth_mm'


def test_explorer_save(tmp_path):
    explorer = hvplot.explorer(df)

    explorer.param.update(
        kind='scatter',
        x='bill_length_mm',
        y_multi=['bill_depth_mm'],
    )

    outfile = tmp_path / 'plot.html'

    explorer.save(outfile)

    assert outfile.exists()


def test_explorer_kwargs_controls():
    explorer = hvplot.explorer(df, title='Dummy title', width=200)

    assert explorer.labels.title == 'Dummy title'
    assert explorer.axes.width == 200


@pytest.mark.usefixtures('disable_param_warnings_as_exceptions')
def test_explorer_kwargs_controls_error_not_supported():
    with pytest.raises(
        TypeError,
        match=re.escape(
            "__init__() got keyword(s) not supported by any control: {'not_a_control_kwarg': None}"
        ),
    ):
        hvplot.explorer(df, title='Dummy title', not_a_control_kwarg=None)


def test_explorer_hvplot_gridded_basic():
    explorer = hvplot.explorer(ds_air_temperature)

    assert isinstance(explorer, hvGridExplorer)
    assert isinstance(explorer._data, xr.DataArray)
    assert explorer.kind == 'image'
    assert explorer.x == 'lat'
    assert explorer.y == 'lon'
    assert explorer.by == []
    assert explorer.groupby == ['time']


def test_explorer_hvplot_gridded_2d():
    ds = ds_air_temperature.isel(time=0)
    explorer = hvplot.explorer(ds)

    assert isinstance(explorer, hvGridExplorer)
    assert isinstance(explorer._data, xr.DataArray)
    assert explorer.kind == 'image'
    assert explorer.x == 'lat'
    assert explorer.y == 'lon'
    assert explorer.by == []
    assert explorer.groupby == []


def test_explorer_hvplot_gridded_two_variables():
    ds = ds_air_temperature.copy()
    ds['airx2'] = ds['air'] * 2
    explorer = hvplot.explorer(ds)

    assert isinstance(explorer, hvGridExplorer)
    assert isinstance(explorer._data, xr.DataArray)
    assert list(explorer._data['variable']) == ['air', 'airx2']
    assert explorer.kind == 'image'
    assert explorer.x == 'lat'
    assert explorer.y == 'lon'
    assert explorer.by == []
    assert explorer.groupby == ['time', 'variable']


def test_explorer_hvplot_gridded_dataarray():
    da = ds_air_temperature['air']
    explorer = hvplot.explorer(da)

    assert isinstance(explorer, hvGridExplorer)
    assert isinstance(explorer._data, xr.DataArray)
    assert explorer.kind == 'image'
    assert explorer.x == 'lat'
    assert explorer.y == 'lon'
    assert explorer.by == []
    assert explorer.groupby == ['time']


def test_explorer_hvplot_gridded_options():
    explorer = hvplot.explorer(ds_air_temperature)
    assert explorer._controls[0].groups.keys() == {'dataframe', 'gridded', 'geom'}


def test_explorer_hvplot_geo():
    pytest.importorskip('geoviews')
    df = pd.DataFrame({'x': [-9796115.18980811], 'y': [4838471.398061159]})
    explorer = hvplot.explorer(df, x='x', geo=True, kind='points')
    assert explorer.geographic.geo
    assert explorer.geographic.global_extent
    assert explorer.geographic.features == ['coastline']
    assert explorer.geographic.crs == 'GOOGLE_MERCATOR'
    assert explorer.geographic.projection == 'GOOGLE_MERCATOR'


def test_explorer_live_update_init():
    explorer = hvplot.explorer(df)
    assert explorer.statusbar.live_update is True

    explorer = hvplot.explorer(df, live_update=False)
    assert explorer._hv_pane.object is None
    assert 'live_update' not in explorer.settings()


def test_explorer_live_update_after_init():
    explorer = hvplot.explorer(df)
    assert explorer._hv_pane.object.type is hv.Scatter
    explorer.kind = 'line'
    assert explorer._hv_pane.object.type is hv.Curve

    explorer.statusbar.live_update = False
    explorer.kind = 'scatter'
    assert explorer._hv_pane.object.type is hv.Curve
    assert 'scatter' not in explorer.code

    explorer.statusbar.live_update = True
    assert explorer._hv_pane.object.type is hv.Scatter
    assert 'scatter' in explorer.code


def test_explorer_method_dataframe():
    explorer = df.hvplot.explorer()

    assert isinstance(explorer, hvDataFrameExplorer)
    assert explorer.kind == 'scatter'
    assert explorer.x == 'index'
    assert explorer.y == 'species'


def test_explorer_method_grid():
    explorer = ds_air_temperature.hvplot.explorer()

    assert isinstance(explorer, hvGridExplorer)
    assert explorer.kind == 'image'
    assert explorer.x == 'lat'
    assert explorer.y == 'lon'


def test_explorer_method_kind():
    explorer = df.hvplot.explorer(kind='scatter')

    assert isinstance(explorer, hvDataFrameExplorer)
    assert explorer.kind == 'scatter'
    assert explorer.x == 'index'
    assert explorer.y == 'species'


def test_explorer_method_as_kind():
    explorer = df.hvplot(kind='explorer')

    assert isinstance(explorer, hvDataFrameExplorer)
    assert explorer.kind == 'scatter'
    assert explorer.x == 'index'
    assert explorer.y == 'species'


def test_explorer_method_propagates_kwargs():
    explorer = df.hvplot.explorer(title='Dummy title', x='bill_length_mm')

    assert isinstance(explorer, hvDataFrameExplorer)
    assert explorer.kind == 'scatter'
    assert explorer.x == 'bill_length_mm'
    assert explorer.y == 'species'
    assert explorer.labels.title == 'Dummy title'


def test_explorer_code_dataframe():
    explorer = hvplot.explorer(df, x='bill_length_mm', kind='points')
    assert explorer.code == dedent("""\
        df.hvplot(
            kind='points',
            x='bill_length_mm',
            y='species',
            legend='bottom_right',
            widget_location='bottom',
        )""")
    assert explorer._code_pane.object == dedent("""\
        ```python
        df.hvplot(
            kind='points',
            x='bill_length_mm',
            y='species',
            legend='bottom_right',
            widget_location='bottom',
        )
        ```""")


def test_explorer_code_gridded():
    explorer = hvplot.explorer(ds_air_temperature, x='lon', y='lat', kind='image')
    code = explorer.code
    assert code == dedent("""\
        ds['air'].hvplot(
            colorbar=True,
            groupby=['time'],
            kind='image',
            x='lon',
            y='lat',
            legend='bottom_right',
            widget_location='bottom',
        )""")

    assert explorer._code_pane.object == dedent("""\
        ```python
        ds['air'].hvplot(
            colorbar=True,
            groupby=['time'],
            kind='image',
            x='lon',
            y='lat',
            legend='bottom_right',
            widget_location='bottom',
        )
        ```""")


def test_explorer_code_gridded_dataarray():
    da = ds_air_temperature['air']
    explorer = hvplot.explorer(da, x='lon', y='lat', kind='image')
    code = explorer.code
    assert code == dedent("""\
        da.hvplot(
            colorbar=True,
            groupby=['time'],
            kind='image',
            x='lon',
            y='lat',
            legend='bottom_right',
            widget_location='bottom',
        )""")

    assert explorer._code_pane.object == dedent("""\
        ```python
        da.hvplot(
            colorbar=True,
            groupby=['time'],
            kind='image',
            x='lon',
            y='lat',
            legend='bottom_right',
            widget_location='bottom',
        )
        ```""")


def test_explorer_code_opts():
    da = ds_air_temperature['air']
    explorer = hvplot.explorer(da, x='lon', y='lat', kind='image', opts={'color_levels': 3})
    code = explorer.code
    assert code == dedent("""\
        da.hvplot(
            colorbar=True,
            groupby=['time'],
            kind='image',
            x='lon',
            y='lat',
            legend='bottom_right',
            widget_location='bottom',
        ).opts(
            color_levels=3,
        )""")

    assert explorer._code_pane.object == dedent("""\
        ```python
        da.hvplot(
            colorbar=True,
            groupby=['time'],
            kind='image',
            x='lon',
            y='lat',
            legend='bottom_right',
            widget_location='bottom',
        ).opts(
            color_levels=3,
        )
        ```""")


def test_explorer_xarray_multi_var_extra_dims_no_coord():
    ds = xr.tutorial.open_dataset('air_temperature')
    ds['lat_bnds'] = (('bnds', 'lat'), np.vstack([ds['lat'], ds['lat']]))
    assert ds.hvplot.explorer()


@pytest.mark.usefixtures('disable_param_warnings_as_exceptions')
@pytest.mark.parametrize('kind_tuple', [('scatter', 'points'), ('line', 'paths')])
@pytest.mark.geo
def test_explorer_geo_revise_kind(kind_tuple):
    da = ds_air_temperature['air'].isel(time=0)
    explorer = hvplot.explorer(da, x='lon', y='lat', kind=kind_tuple[0], geo=True)
    assert explorer.kind == kind_tuple[1]


@pytest.mark.usefixtures('disable_param_warnings_as_exceptions')
def test_max_rows_curve():
    N = 100001
    x = np.linspace(0.0, 6.4, num=N)
    y = np.sin(x) + 10
    df = pd.DataFrame({'x': x, 'y': y})
    ui = hvplot.explorer(df, x='x', y='y', by=['#'], kind='line')
    assert ui._data.equals(df.head(MAX_ROWS))


@pytest.mark.usefixtures('disable_param_warnings_as_exceptions')
def test_max_rows_sample():
    N = 100001
    x = np.linspace(0.0, 6.4, num=N)
    y = np.sin(x) + 10
    df = pd.DataFrame({'x': x, 'y': y})
    ui = hvplot.explorer(df, x='x', y='y', by=['#'], kind='scatter')
    assert len(ui._data) == MAX_ROWS
    assert not ui._data.equals(df.head(MAX_ROWS))


def test_explorer_geo_no_import_error_when_false():
    da = ds_air_temperature['air'].isel(time=0)
    with patch('hvplot.util.import_geoviews', return_value=None):
        assert hvplot.explorer(da, x='lon', y='lat', geo=False)
