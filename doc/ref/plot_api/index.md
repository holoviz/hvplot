# Plotting API

## Main methods

hvPlot's plotting API is most often invoked by installing the `hvplot` namespace on a data source via a special import:

```python
import pandas as pd
import hvplot.pandas  # noqa
df = pd.DataFrame()

df.hvplot.scatter()
# or
df.hvplot(kind='scatter')
```

Under the hood, these special imports like `import hvplot.pandas` register an accessor that returns an instance of an `hvPlotBase` class. Tabular-like data sources rely on the `hvPlotTabular` class and gridded-like sources on `hvPlot` (subclass of `hvPlotTabular` extended with methods like {meth}`image  <hvplot.hvPlot.image>`):

- `hvPlotTabular`: cuDF, Dask, Fugue, Ibis, Pandas, Streamz
- `hvPlotTabularDuckDB`: DuckDB
- `hvPlotTabularPolars`: Polars
- `hvPlot`: Xarray

Instead of using the `hvplot` namespace, one can directly generate hvPlot plots with these classes:

```python
import pandas as pd
from hvplot import hvPlot
df = pd.DataFrame()

hvPlot(df).scatter()
# or
hvPlot(df)(kind='scatter')
```

This page documents all the plotting methods of the `hvPlot` class, which as described above are also available via the `hvplot` namespace.

```{eval-rst}
.. currentmodule:: hvplot
```

### `hvPlot`

```{eval-rst}
.. autosummary::
   :toctree: api/

   hvPlot.area
   hvPlot.bar
   hvPlot.barh
   hvPlot.box
   hvPlot.bivariate
   hvPlot.contour
   hvPlot.contourf
   hvPlot.dataset
   hvPlot.density
   hvPlot.errorbars
   hvPlot.explorer
   hvPlot.heatmap
   hvPlot.hexbin
   hvPlot.hist
   hvPlot.image
   hvPlot.kde
   hvPlot.labels
   hvPlot.line
   hvPlot.ohlc
   hvPlot.paths
   hvPlot.points
   hvPlot.polygons
   hvPlot.quadmesh
   hvPlot.rgb
   hvPlot.scatter
   hvPlot.step
   hvPlot.table
   hvPlot.vectorfield
   hvPlot.violin
```


## `plotting` module

hvPlot's structure is based on Pandas' plotting API and as such provides special plotting functions in the `hvplot.plotting` module.

```{eval-rst}
.. currentmodule:: hvplot.plotting

```

```{eval-rst}
.. autosummary::
   :toctree: api/

   andrews_curves
   lag_plot
   parallel_coordinates
   scatter_matrix
```
