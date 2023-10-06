import pandas as pd
import hvplot.fugue

import fugue.api as fa

df = pd.DataFrame(
    {
        "g": ["a", "b", "a", "b", "a", "b"],
        "x": [1, 2, 3, 4, 5, 6],
        "y": [1, 2, 3, 4, 5, 6],
    }
)

fa.fugue_sql(
    """
    OUTPUT df USING hvplot:line(
        x="x",
        y="y",
        by="g",
        size=100,
        opts={"width": 500, "height": 500}
    )
    """
)
