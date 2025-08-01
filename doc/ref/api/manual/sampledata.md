# hvplot.sampledata

The `hvplot.sampledata` module provides convenient access to sample datasets for learning, testing, and prototyping with hvPlot.

## Usage

```python
import hvplot.pandas  # noqa
import hvplot.xarray  # noqa

# Recommended: Use the hvplot.sampledata namespace directly
penguins = hvplot.sampledata.penguins("pandas")
air_temp = hvplot.sampledata.air_temperature("xarray")
landsat = hvplot.sampledata.landsat_rgb("rioxarray")
us_states = hvplot.sampledata.us_states("geopandas")

# Alternative: Import the module separately
from hvplot import sampledata
penguins = sampledata.penguins("pandas")
```

## Installation

The `hvsampledata` package is included as a dependency when installing hvPlot with example dependencies. If you installed hvPlot with minimal dependencies, you may need to install it separately:

::::{tab-set}

:::{tab-item} pip

```bash
pip install hvsampledata
```

:::

:::{tab-item} conda

```bash
conda install -c conda-forge hvsampledata
```

:::
::::

## Available Datasets

The `hvsampledata` package provides the following datasets, all accessible through `hvplot.sampledata.<function_name>()`:

### Tabular Data

- **`penguins(engine)`** - Palmer penguins dataset (344 rows) with species measurements
- **`earthquakes(engine)`** - Global earthquake events from USGS (596 rows)
- **`apple_stocks(engine)`** - Apple Inc. daily stock data 2019-2024 (1,509 rows)
- **`stocks(engine)`** - Tech company weekly stock comparison (261 rows)
- **`synthetic_clusters(engine)`** - Large synthetic dataset with 5 clusters (configurable size)
- **`us_states(engine)`** - US state boundaries with demographic data (49 states, requires geopandas)

### Gridded Data

- **`air_temperature(engine)`** - NCEP/NCAR weather reanalysis (53×25×20 grid, requires xarray)
- **`landsat_rgb(engine)`** - Landsat satellite RGB imagery (requires rioxarray)
- **`penguins_rgba(engine)`** - Penguin image with transparency (100×100×4, requires xarray)

All functions accept an `engine` parameter to specify the data format:

- Tabular: `"pandas"`, `"polars"`, `"dask"`
- Gridded: `"xarray"`, `"rioxarray"`
- Geographic: `"geopandas"`


:::{admonition} Notes
:class: note
- All datasets include comprehensive metadata and documentation
- Engines determine the return type (`pandas.DataFrame`, `polars.DataFrame`, `xarray.Dataset`, etc.)
- Geographic datasets require additional dependencies (geopandas)
- Some datasets support lazy evaluation for memory efficiency
- Data types and schemas are preserved across different engines where possible
:::

:::{seealso}
For complete documentation, usage examples, and function signatures, see the **[Sample Data Tutorial](../../../tutorials/sample_data.ipynb)** which demonstrates how to use each dataset with hvPlot.
:::
