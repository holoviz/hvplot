import holoviews as hv
import hvplot.pandas
import pytest

try:
    from bokeh.sampledata import penguins
except ImportError:
    penguins = None

from hvplot.ui import hvDataFrameExplorer

pytestmark = pytest.mark.skipif(
    penguins is None,
    reason='Penguins dataset not available on Python 3.6',
)

df = penguins.data


def test_explorer_basic():
    explorer = hvplot.explorer(df)

    assert isinstance(explorer, hvDataFrameExplorer)
    assert explorer.kind == 'line'
    assert explorer.x is None
    assert explorer.y is None


def test_explorer_settings():
    explorer = hvplot.explorer(df)

    explorer.param.set_param(
        kind='scatter',
        x='bill_length_mm',
        y_multi=['bill_depth_mm'],
        by=['species'],
    )

    settings = explorer.settings()

    assert settings == dict(
        by=['species'],
        kind='scatter',
        x='bill_length_mm',
        y=['bill_depth_mm'],
    )


def test_explorer_repr():
    explorer = hvplot.explorer(df)

    explorer.param.set_param(
        kind='scatter',
        x='bill_length_mm',
        y_multi=['bill_depth_mm'],
        by=['species'],
    )

    hvrepr = explorer.repr()

    assert hvrepr == "df.hvplot(by=['species'], kind='scatter', x='bill_length_mm', y=['bill_depth_mm'])"
    
    hvrepr = explorer.repr(var_name='othername')

    assert hvrepr == "othername.hvplot(by=['species'], kind='scatter', x='bill_length_mm', y=['bill_depth_mm'])"


def test_explorer_hvplot():
    explorer = hvplot.explorer(df)

    explorer.param.set_param(
        kind='scatter',
        x='bill_length_mm',
        y_multi=['bill_depth_mm'],
    )

    plot = explorer.hvplot()

    assert isinstance(plot, hv.Scatter)
    assert plot.kdims[0].name == 'bill_length_mm'
    assert plot.vdims[0].name == 'bill_depth_mm'


def test_explorer_save(tmp_path):
    explorer = hvplot.explorer(df)

    explorer.param.set_param(
        kind='scatter',
        x='bill_length_mm',
        y_multi=['bill_depth_mm'],
    )

    outfile = tmp_path / 'plot.html'

    explorer.save(outfile)

    assert outfile.exists()
