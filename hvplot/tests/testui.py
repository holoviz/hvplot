import holoviews as hv
import hvplot.pandas

from bokeh.sampledata import penguins
from hvplot.ui import hvDataFrameExplorer

df = penguins.data


def test_explorer_basic():
    explorer = hvplot.explorer(df)

    assert isinstance(explorer, hvDataFrameExplorer)
    assert explorer.kind == 'line'
    assert explorer.x == 'index'
    assert explorer.y == 'species'


def test_explorer_settings():
    explorer = hvplot.explorer(df)

    explorer.param.update(
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


def test_explorer_plot_code():
    explorer = hvplot.explorer(df)

    explorer.param.update(
        kind='scatter',
        x='bill_length_mm',
        y_multi=['bill_depth_mm'],
        by=['species'],
    )

    hvplot_code = explorer.plot_code()

    assert hvplot_code == "df.hvplot(by=['species'], kind='scatter', x='bill_length_mm', y=['bill_depth_mm'])"

    hvplot_code = explorer.plot_code(var_name='othername')

    assert hvplot_code == "othername.hvplot(by=['species'], kind='scatter', x='bill_length_mm', y=['bill_depth_mm'])"


def test_explorer_hvplot():
    explorer = hvplot.explorer(df)

    explorer.param.update(
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

    explorer.param.update(
        kind='scatter',
        x='bill_length_mm',
        y_multi=['bill_depth_mm'],
    )

    outfile = tmp_path / 'plot.html'

    explorer.save(outfile)

    assert outfile.exists()
