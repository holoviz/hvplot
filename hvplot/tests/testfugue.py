"""Fugue test suite"""

import hvplot
import pandas as pd
import pytest

# Patch required before importing hvplot.fugue
hvplot.util._fugue_ipython = True

try:
    import fugue.api as fa
    import fugue_sql_antlr  # noqa: F401
    import hvplot.fugue  # noqa: F401
except ImportError:
    pytest.skip(allow_module_level=True)


@pytest.fixture
def table():
    df = pd.DataFrame(
        {
            'g': ['a', 'b', 'a', 'b', 'a', 'b'],
            'x': [1, 2, 3, 4, 5, 6],
            'y': [1, 2, 3, 4, 5, 6],
        }
    )
    return df


def test_fugure_ipython_line(table, capsys):
    """hvplot works with Fugue"""
    fa.fugue_sql(
        """
        OUTPUT table USING hvplot:line(
            x="x",
            y="y",
            by="g",
            size=100,
            opts={"width": 500, "height": 500}
        )
        """
    )
    # Check that the output contains the following:
    # Column
    #     [0] HoloViews(NdOverlay)
    output = capsys.readouterr().out
    assert output == 'Column\n    [0] HoloViews(NdOverlay)\n'
