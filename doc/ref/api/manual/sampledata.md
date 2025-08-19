# hvplot.sampledata

The `hvplot.sampledata` module provides convenient access to sample datasets for learning, testing, and prototyping with hvPlot.

## Usage

```python
import hvplot.pandas  # noqa
import hvplot.xarray  # noqa

penguins = hvplot.sampledata.penguins("pandas")
air_temp = hvplot.sampledata.air_temperature("xarray")
landsat = hvplot.sampledata.landsat_rgb("rioxarray")
us_states = hvplot.sampledata.us_states("geopandas")
```

## Installation

The `hvsampledata` package is included as a dependency when installing hvPlot. If you installed hvPlot with minimal dependencies, you may need to install it separately:

::::{tab-set}

:::{tab-item} pip

```bash
pip install hvsampledata
```

:::

:::{tab-item} conda

```bash
conda install conda-forge::hvsampledata
```

:::
::::

## Available Datasets

The `hvsampledata` package provides the following datasets, all accessible through `hvplot.sampledata.<function_name>()`.

You can inspect the datasets through the `__all__` attribute which exposes its public datasets:

```python
import hvsampledata as hvs

print(hvs.__all__[1:])
```
This will print a list of all dataset functions available in your installed version of hvsampledata.

:::{note}
The first entry, __version__, is metadata and not a dataset, so we slice it off with [1:]. The remaining names are all dataset functions you can call, e.g `hvplot.sampledata.penguins("pandas")`
:::

:::{admonition} Notes
:class: note
- All datasets include comprehensive metadata and documentation
- Engines determine the return type (`pandas.DataFrame`, `polars.DataFrame`, `xarray.Dataset`, etc.)
- Geographic datasets require additional dependencies (geopandas)
- Some datasets support lazy evaluation for memory efficiency
- Data types and schemas are preserved across different engines where possible
:::
