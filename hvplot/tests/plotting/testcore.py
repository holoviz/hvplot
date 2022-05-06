import numpy as np
import pandas as pd
import hvplot.pandas  # noqa

import pytest

@pytest.mark.parametrize("y", (
    ["A", "B", "C", "D"],
    ("A", "B", "C", "D"),
    {"A", "B", "C", "D"},
    np.array(["A", "B", "C", "D"]),
    pd.Index(["A", "B", "C", "D"]),
    pd.Series(["A", "B", "C", "D"]),
    ))
def test_diffent_input_types(y):
    df = pd._testing.makeDataFrame()
    types = {t for t in dir(df.hvplot) if not t.startswith("_")}
    ignore_types = {'bivariate', 'heatmap', 'hexbin', 'labels', 'vectorfield'}

    for t in types - ignore_types:
        df.hvplot(y=y, kind=t)
