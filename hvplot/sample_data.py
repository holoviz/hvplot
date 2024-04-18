"""
Loads hvPlot sample data using intake catalogue.
"""

import os

try:
    from intake import open_catalog
    import intake_parquet  # noqa
    import intake_xarray  # noqa
    import s3fs  # noqa
except ImportError:
    raise ImportError(
        """Loading hvPlot sample data requires:
                * intake
                * intake-parquet
                * intake-xarray
                * s3fs
             Install these using conda or pip before loading data."""
    )

_file_path = os.path.dirname(__file__)
_cat_path = os.path.join(_file_path, 'datasets.yaml')

# Load catalogue
catalogue = open_catalog(_cat_path)

# Add catalogue entries to namespace
for _c in catalogue:
    globals()[_c] = catalogue[_c]
