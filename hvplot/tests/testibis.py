"""Ibis works with hvplot"""
import pytest

try:
    import ibis
    import hvplot.ibis # noqa
    import pandas as pd
except:
    pytest.skip(allow_module_level=True)


@pytest.fixture
def table():
    df = pd.DataFrame({
        "x": [pd.Timestamp("2022-01-01"), pd.Timestamp("2022-01-02")], "y": [1,2]
    })
    con = ibis.pandas.connect({"df": df})
    return con.table("df")

def test_can_hvplot(table):
    """hvplot works with Ibis"""
    table.hvplot(x="x", y="y")
