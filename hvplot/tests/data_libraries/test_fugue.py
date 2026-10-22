import pandas as pd
import pytest

from hvplot.tests._deps import requires
from hvplot.util import _PD_GE_3_0_0

# fugue is optional, it is imported in the tests.
pytestmark = requires('fugue', 'fugue_sql_antlr')


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


@pytest.mark.skipif(_PD_GE_3_0_0, reason='breaks with Pandas 3')
def test_fugue_ipython_line(table, capsys, monkeypatch, hvplot_pandas):
    """hvPlot works with Fugue"""
    import fugue.api as fa

    import hvplot.fugue

    # Patched on hvplot.fugue as it copies the flag from hvplot.util when first imported.
    monkeypatch.setattr(hvplot.fugue, '_fugue_ipython', True)
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
