# API

## Utilities

```{eval-rst}
.. currentmodule:: hvplot

.. autosummary::
   :toctree: generated/

   help
   hvplot_extension
   extension
   output
   render
   save
   show
```

(api-plotting)=
## Plotting

### `hvPlot` / `.hvplot`

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

This section documents all the plotting methods of the `hvPlot` class, which as described above are also available via the `hvplot` namespace.

#### Common

```{eval-rst}
.. currentmodule:: hvplot

.. autosummary::

   hvPlot.area
   hvPlot.bar
   hvPlot.barh
   hvPlot.box
   hvPlot.bivariate
   hvPlot.dataset
   hvPlot.density
   hvPlot.errorbars
   hvPlot.heatmap
   hvPlot.hexbin
   hvPlot.hist
   hvPlot.kde
   hvPlot.labels
   hvPlot.line
   hvPlot.ohlc
   hvPlot.paths
   hvPlot.points
   hvPlot.polygons
   hvPlot.scatter
   hvPlot.step
   hvPlot.table
   hvPlot.vectorfield
   hvPlot.violin
```

#### Gridded

```{eval-rst}
.. currentmodule:: hvplot

.. autosummary::

   hvPlot.contour
   hvPlot.contourf
   hvPlot.image
   hvPlot.quadmesh
   hvPlot.rgb
```

### `plotting` module

hvPlot's structure is based on Pandas' plotting API and as such provides special plotting functions in the `hvplot.plotting` module.

```{eval-rst}
.. currentmodule:: hvplot.plotting

.. autosummary::

   andrews_curves
   lag_plot
   parallel_coordinates
   scatter_matrix
```

```{toctree}
:hidden: true
:maxdepth: 2
:titlesonly: true

hvplot.hvPlot.hvplot_area <hvplot_api/hvplot.hvPlot.area>
hvplot.hvPlot.bar <hvplot_api/hvplot.hvPlot.bar>
hvplot.hvPlot.barh <hvplot_api/hvplot.hvPlot.barh>
hvplot.hvPlot.box <hvplot_api/hvplot.hvPlot.box>
hvplot.hvPlot.bivariate <hvplot_api/hvplot.hvPlot.bivariate>
hvplot.hvPlot.contour <hvplot_api/hvplot.hvPlot.contour>
hvplot.hvPlot.contourf <hvplot_api/hvplot.hvPlot.contourf>
hvplot.hvPlot.dataset <hvplot_api/hvplot.hvPlot.dataset>
hvplot.hvPlot.density <hvplot_api/hvplot.hvPlot.density>
hvplot.hvPlot.errorbars <hvplot_api/hvplot.hvPlot.errorbars>
hvplot.hvPlot.explorer <hvplot_api/hvplot.hvPlot.explorer>
hvplot.hvPlot.heatmap <hvplot_api/hvplot.hvPlot.heatmap>
hvplot.hvPlot.hexbin <hvplot_api/hvplot.hvPlot.hexbin>
hvplot.hvPlot.hist <hvplot_api/hvplot.hvPlot.hist>
hvplot.hvPlot.image <hvplot_api/hvplot.hvPlot.image>
hvplot.hvPlot.kde <hvplot_api/hvplot.hvPlot.kde>
hvplot.hvPlot.labels <hvplot_api/hvplot.hvPlot.labels>
hvplot.hvPlot.line <hvplot_api/hvplot.hvPlot.line>
hvplot.hvPlot.ohlc <hvplot_api/hvplot.hvPlot.ohlc>
hvplot.hvPlot.paths <hvplot_api/hvplot.hvPlot.paths>
hvplot.hvPlot.points <hvplot_api/hvplot.hvPlot.points>
hvplot.hvPlot.polygons <hvplot_api/hvplot.hvPlot.polygons>
hvplot.hvPlot.quadmesh <hvplot_api/hvplot.hvPlot.quadmesh>
hvplot.hvPlot.rgb <hvplot_api/hvplot.hvPlot.rgb>
hvplot.hvPlot.scatter <hvplot_api/hvplot.hvPlot.scatter>
hvplot.hvPlot.step <hvplot_api/hvplot.hvPlot.step>
hvplot.hvPlot.table <hvplot_api/hvplot.hvPlot.table>
hvplot.hvPlot.vectorfield <hvplot_api/hvplot.hvPlot.vectorfield>
hvplot.hvPlot.violin <hvplot_api/hvplot.hvPlot.violin>
hvplot.plotting.andrews_curves <hvplot_api/hvplot.plotting.andrews_curves>
hvplot.plotting.lag_plot <hvplot_api/hvplot.plotting.lag_plot>
hvplot.plotting.parallel_coordinates <hvplot_api/hvplot.plotting.parallel_coordinates>
hvplot.plotting.scatter_matrix <hvplot_api/hvplot.plotting.scatter_matrix>
```

(api-networkx)=
### NetworkX

The hvPlot NetworkX plotting API is meant as a drop-in replacement for the [`networkx.draw` methods](https://networkx.org/documentation/stable/reference/drawing.html).

:::{note}
Please chime in this [issue](https://github.com/holoviz/hvplot/issues/487) if you have opinions about NetworkX plotting API in hvPlot.
:::

```{eval-rst}
.. currentmodule:: hvplot.networkx

.. autosummary::
   :toctree: generated/

   draw
   draw_networkx
   draw_networkx_nodes
   draw_networkx_edges
   draw_networkx_labels
   draw_circular
   draw_kamada_kawai
   draw_random
   draw_planar
   draw_shell
   draw_spectral
   draw_spring
```

## Explorer

The explorer interface can easily be created from the `hvPlot` / `.hvplot` namespace:

```{eval-rst}
.. currentmodule:: hvplot

.. autosummary::
   :toctree: generated/

    hvPlot.explorer
```

It is also available from the top-level `explorer` function:

```{eval-rst}
.. currentmodule:: hvplot.ui

.. autosummary::
   :toctree: generated/

    explorer
```

Calling the `explorer` function/method returns an `hvPlotExplorer` object:

```{eval-rst}
.. autosummary::
   :toctree: generated/

    hvPlotExplorer
    hvPlotExplorer.hvplot
    hvPlotExplorer.plot_code
    hvPlotExplorer.save
    hvPlotExplorer.servable
    hvPlotExplorer.settings
    hvPlotExplorer.show
```
