import holoviews as hv
import pandas as pd
import panel as pn
import pytest
from holoviews import Store

from hvplot.tests._deps import requires

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


@pytest.fixture
def fugue_sql(hvplot_pandas):
    import fugue.api as fa

    import hvplot.fugue  # noqa: F401

    return fa.fugue_sql


@pytest.fixture
def shown(monkeypatch):
    """Columns that hvPlot would show in a new browser tab."""
    import hvplot.fugue

    columns = []
    # Patched on hvplot.fugue as it copies the flag from hvplot.util when first imported.
    monkeypatch.setattr(hvplot.fugue, '_fugue_ipython', False)
    monkeypatch.setattr(pn.Column, 'show', lambda self, *args, **kwargs: columns.append(self))
    return columns


def test_fugue_ipython_line(table, capsys, monkeypatch, fugue_sql):
    """hvPlot works with Fugue"""
    import hvplot.fugue

    monkeypatch.setattr(hvplot.fugue, '_fugue_ipython', True)
    fugue_sql(
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


def test_fugue_script_shows_column(table, fugue_sql, shown):
    fugue_sql('OUTPUT table USING hvplot:scatter(x="x", y="y", opts={"width": 500})')
    (column,) = shown
    (pane,) = column
    assert isinstance(pane.object, hv.Scatter)
    assert pane.object.kdims == ['x']
    assert pane.object.vdims == ['y']
    assert Store.lookup_options('bokeh', pane.object, 'plot').kwargs['width'] == 500


def test_fugue_unknown_plot_method(table, fugue_sql, shown):
    with pytest.raises(AttributeError, match="no attribute 'nope'"):
        fugue_sql('OUTPUT table USING hvplot:nope(x="x")')
    assert not shown


def test_patch_without_fugue(fugue_sql, block_import):
    import hvplot.fugue

    block_import('fugue')
    with pytest.raises(ImportError, match='Could not add fugue support'):
        hvplot.fugue.patch()
