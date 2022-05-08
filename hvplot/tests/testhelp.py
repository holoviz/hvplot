import hvplot.pandas

from holoviews.core import Store
from holoviews.element import Curve

def test_help_style_extension_output():
    # default, after e.g. import hvplot.pandas
    docstring, signature = hvplot._get_doc_and_signature(
        cls=hvplot.hvPlot,
        kind='line',
        completions=False,
        docstring=False,
        generic=False,
        style=True,
        signature=None,
    )
    assert docstring == '\nStyle options\n-------------\n\n' + '\n'.join(sorted(Store.registry['bokeh'][Curve].style_opts))

    # The current backend becomes matplotlib
    hvplot.extension('matplotlib', 'plotly')
    docstring, signature = hvplot._get_doc_and_signature(
        cls=hvplot.hvPlot,
        kind='line',
        completions=False,
        docstring=False,
        generic=False,
        style=True,
        signature=None,
    )
    assert docstring == '\nStyle options\n-------------\n\n' + '\n'.join(sorted(Store.registry['matplotlib'][Curve].style_opts))

    # The current backend becomes plotly
    hvplot.output(backend='plotly')
    docstring, signature = hvplot._get_doc_and_signature(
        cls=hvplot.hvPlot,
        kind='line',
        completions=False,
        docstring=False,
        generic=False,
        style=True,
        signature=None,
    )
    assert docstring == '\nStyle options\n-------------\n\n' + '\n'.join(sorted(Store.registry['plotly'][Curve].style_opts))

def test_help_style_compatibility():
    # The current backend is plotly but the style options are those of matplotlib
    hvplot.extension('plotly', 'matplotlib', compatibility='matplotlib')
    docstring, signature = hvplot._get_doc_and_signature(
        cls=hvplot.hvPlot,
        kind='line',
        completions=False,
        docstring=False,
        generic=False,
        style=True,
        signature=None,
    )
    assert docstring == '\nStyle options\n-------------\n\n' + '\n'.join(sorted(Store.registry['matplotlib'][Curve].style_opts))
