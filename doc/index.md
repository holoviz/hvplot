---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  name: python3
---

# hvPlot

***A familiar and high-level API for data exploration and visualization***

```{image} ./assets/diagram.svg
---
alt: hvPlot diagram
align: center
width: 70%
---
```

---

**`.hvplot()` for a more versatile and powerful `.plot()` API**

By replacing `.plot()` by `.hvplot()` you get an interactive [Bokeh](https://bokeh.org/) plot.

```{code-cell} ipython3
import hvplot.pandas  # noqa
from bokeh.sampledata.penguins import data as df

df.hvplot.scatter(x='bill_length_mm', y='bill_depth_mm', by='species')
```

`.hvplot()` supports many data structures of the PyData ecosystem on top of [Pandas](https://pandas.pydata.org/):

::::{tab-set}

:::{tab-item} Xarray
```python
import hvplot.xarray  # noqa
import xarray as xr

xr_ds = xr.tutorial.open_dataset('air_temperature').load().sel(time='2013-06-01 12:00')
xr_ds.hvplot()
```
```{image} ./_static/home/xarray.gif
---
alt: xarray support
align: center
---
```
:::

:::{tab-item} Dask
```python
import dask
import hvplot.dask  # noqa

df_dask = dask.dataframe.from_pandas(df, npartitions=2)
df_dask.hvplot.scatter(x='bill_length_mm', y='bill_depth_mm', by='species')
```
```{image} ./_static/home/dask.gif
---
alt: dask support
align: center
---
:::

:::{tab-item} GeoPandas
```python
import geopandas as gpd
import hvplot.pandas  # noqa

gdf = gpd.read_file(gpd.datasets.get_path('naturalearth_cities'))
gdf.hvplot(global_extent=True, tiles=True)
```
```{image} ./_static/home/geopandas.gif
---
alt: geopandas support
align: center
---
:::

:::{tab-item} NetworkX
```python
import hvplot.networkx as hvnx
import networkx as nx

G = nx.petersen_graph()
hvnx.draw(G, with_labels=True)
```
```{image} ./_static/home/networkx.gif
---
alt: networkx support
align: center
---
:::

:::{tab-item} Intake
```python
import hvplot.intake  # noqa
from hvplot.sample_data import catalogue as cat

cat.us_crime.hvplot.line(x='Year', y='Violent Crime rate')
```
```{image} ./_static/home/intake.gif
---
alt: intake support
align: center
---
:::

:::{tab-item} Streamz
```python
import hvplot.streamz  # noqa
from streamz.dataframe import Random

df_streamz = Random(interval='200ms', freq='50ms')
df_streamz.hvplot()
```
```{image} ./assets/streamz_demo.gif
---
alt: streamz support
align: center
---
:::

::::

`.hvplot()` can also generate plots with [Matplotlib](https://matplotlib.org/) or [Plotly](https://plotly.com/).


::::{tab-set}

:::{tab-item} Bokeh
```{code-cell} ipython3
import hvplot.pandas  # noqa
from bokeh.sampledata.penguins import data as df

df.hvplot.scatter(x='bill_length_mm', y='bill_depth_mm', by='species')
```
:::

:::{tab-item} Matplotlib
```python
import hvplot.pandas
import pandas
from bokeh.sampledata.penguins import data as df

hvplot.extension('matplotlib')

df.hvplot.scatter(x='bill_length_mm', y='bill_depth_mm', by='species')
```
```{image} ./_static/home/matplotlib.png
---
alt: matplotlib as a plotting backend
align: center
---
```
:::

:::{tab-item} Plotly
```python
import hvplot.pandas
import pandas
from bokeh.sampledata.penguins import data as df

hvplot.extension('plotly')

df.hvplot.scatter(x='bill_length_mm', y='bill_depth_mm', by='species')
```
```{image} ./_static/home/plotly.gif
---
alt: plotly as a plotting backend
align: center
---
:::

::::

`.hvplot()` sources its power in the [HoloViz](https://holoviz.org/) ecosystem. With [HoloViews](https://holoviews.org/) you get the ability to easily layout and overlay plots, with [Panel](https://panel.holoviz.org) you can get more interactive control of your plots with widgets, with [DataShader](https://datashader.org/) you can visualize and interactively explore very large data, and with [GeoViews](http://geoviews.org/) you can create geographic plots.

::::{tab-set}

:::{tab-item} Layout
```python
import hvplot.pandas  # noqa
from hvplot.sample_data import us_crime as df

plot1 = df.hvplot(x='Year', y='Violent Crime rate', width=400)
plot2 = df.hvplot(x='Year', y='Burglary rate', width=400)
plot1 + plot2
```
```{image} ./_static/home/layout.gif
---
alt: laying out plots
align: center
---
```
:::

:::{tab-item} Overlay
```python
import hvplot.pandas  # noqa
import pandas
from bokeh.sampledata.penguins import data

df = data.groupby('species')['bill_length_mm'].describe().sort_values('mean')
df.hvplot.scatter(y='mean') * dff.hvplot.errorbars(y='mean', yerr1='std')
```
```{image} ./_static/home/overlay.png
---
alt: overlaying plots
align: center
---
```
:::

:::{tab-item} Widgets
```python
import hvplot.pandas  # noqa
from bokeh.sampledata.penguins import data as df

df.hvplot.scatter(x='bill_length_mm', y='bill_depth_mm', groupby='island', widget_location='top')
```
```{image} ./_static/home/widgets.gif
---
alt: more control with widgets
align: center
---
```
:::

:::{tab-item} Large Data
```python
import hvplot.pandas  # noqa
from hvplot.sample_data import catalogue as cat

df = cat.airline_flights.read()
df.hvplot.scatter(x='distance', y='airtime', rasterize=True, cnorm='eq_hist', width=500)
```
```{image} ./_static/home/large_data.gif
---
alt: visualize and explore large data
align: center
---
```
:::

:::{tab-item} Geographic plots
```python
import hvplot.xarray  # noqa
import xarray as xr, cartopy.crs as crs

air_ds = xr.tutorial.open_dataset('air_temperature').load()
air_ds.air.sel(time='2013-06-01 12:00').hvplot.quadmesh(
    'lon', 'lat', projection=crs.Orthographic(-90, 30), project=True,
    global_extent=True, cmap='viridis', coastline=True
)
```
```{image} ./_static/home/geo.gif
---
alt: geographic plots
align: center
---
```
:::

::::

---

**`.interactive()` to turn data pipelines into widget-based interactive applications**

By starting a data pipeline with `.interactive()` you can then inject widgets into an extract and transform data pipeline. The pipeline output dynamically updates with widget changes, making data exploration in Jupyter notebooks in particular a lot more efficient.

::::{tab-set}

:::{tab-item} Pandas
```python
import hvplot.pandas  # noqa
import panel as pn
from bokeh.sampledata.penguins import data as df

w_sex = pn.widgets.MultiSelect(name='Sex', value=['MALE'], options=['MALE', 'FEMALE'])
w_body_mass = pn.widgets.FloatSlider(name='Min body mass', start=2700, end=6300, step=50)

dfi = df.interactive(loc='left')
dfi.loc[(dfi['sex'].isin(w_sex)) & (dfi['body_mass_g'] > w_body_mass)]['bill_length_mm'].describe()
```
```{image} ./_static/home/interactive_pandas.gif
---
alt: interactive app from pandas
align: center
---
```
:::

:::{tab-item} Xarray
```python
import hvplot.xarray  # noqa
import panel as pn
import xarray as xr

w_time = pn.widgets.IntSlider(name='time', start=0, end=10)

da = xr.tutorial.open_dataset('air_temperature').air
da.interactive.isel(time=w_time).mean().item() - da.mean().item()
```
```{image} ./_static/home/interactive_xarray.gif
---
alt: interactive app from xarray
align: center
---
```
:::

::::

`.interactive()` supports displaying the pipeline output with `.hvplot()`.

```python
import hvplot.xarray  # noqa
import panel as pn
import xarray as xr

da = xr.tutorial.open_dataset('air_temperature').air
w_quantile = pn.widgets.FloatSlider(name='quantile', start=0, end=1)
w_time = pn.widgets.IntSlider(name='time', start=0, end=10)

da.interactive(loc='left') \
.isel(time=w_time) \
.quantile(q=w_quantile, dim='lon') \
.hvplot(ylabel='Air Temperature [K]', width=500)
```

```{image} ./_static/home/interactive_hvplot.gif
---
alt: interactive pipeline with an hvplot output
align: center
---
```

---

**`explorer()` to explore data in a web application**

The *Explorer* is a [Panel](https://panel.holoviz.org) web application that can be displayed in a Jupyter notebook and that can be used to quickly create customized plots.

```python
import hvplot.pandas
from bokeh.sampledata.penguins import data as df

hvexplorer = hvplot.explorer(df)
hvexplorer
```
```{image} ./_static/home/explorer.gif
---
alt: explore data with the hvplot explorer
align: center
---
```

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

Home <self>
Getting Started <getting_started/index>
User Guide <user_guide/index>
Reference Gallery <reference/index>
Topics <topics>
Developer Guide <developer_guide/index>
Releases <releases>
About <about>
```
