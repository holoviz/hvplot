import pytest


try:
    import pandas as pd
    import hvplot.pandas
    import fugue.api as fa
    from hvplot.fugue import _parse_hvplot
except:
    pytest.skip(allow_module_level=True)


@pytest.fixture
def table():
    df = pd.DataFrame(
        {
            "g": ["a", "b", "a", "b", "a", "b"],
            "x": [1, 2, 3, 4, 5, 6],
            "y": [1, 2, 3, 4, 5, 6],
        }
    )
    return df


def test_can_hvplot(table, capsys):
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
    # :NdOverlay   [g]
    #     :Curve   [x]   (y)
    output = capsys.readouterr().out
    assert ":NdOverlay" in output
    assert ":Curve" in output
    assert "[g]" in output
    assert "[x]" in output
    assert "(y)" in output
