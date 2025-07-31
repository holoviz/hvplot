import hvplot.pandas
import pytest

from holoviews.core import Store
from holoviews.element import Curve

from hvplot.util import _get_doc_and_signature


@pytest.fixture
def reset_default_backend():
    yield
    hvplot.extension('bokeh')
    hvplot.extension.compatibility = None


def test_help_style_extension_output(reset_default_backend):
    # default, after e.g. import hvplot.pandas
    docstring, signature = _get_doc_and_signature(
        cls=hvplot.hvPlot,
        kind='line',
        completions=False,
        docstring=False,
        generic=False,
        style=True,
        signature=None,
    )
    assert docstring == '\nBokeh Styling options\n---------------\n' + '\n'.join(
        sorted(Store.registry['bokeh'][Curve].style_opts)
    )

    # The current backend becomes matplotlib
    hvplot.extension('matplotlib', 'plotly')
    docstring, signature = _get_doc_and_signature(
        cls=hvplot.hvPlot,
        kind='line',
        completions=False,
        docstring=False,
        generic=False,
        style=True,
        signature=None,
    )
    assert docstring == '\nMatplotlib Styling options\n---------------\n' + '\n'.join(
        sorted(Store.registry['matplotlib'][Curve].style_opts)
    )

    # The current backend becomes plotly
    hvplot.output(backend='plotly')
    docstring, signature = _get_doc_and_signature(
        cls=hvplot.hvPlot,
        kind='line',
        completions=False,
        docstring=False,
        generic=False,
        style=True,
        signature=None,
    )
    assert docstring == '\nPlotly Styling options\n---------------\n' + '\n'.join(
        sorted(Store.registry['plotly'][Curve].style_opts)
    )


@pytest.mark.usefixtures('disable_param_warnings_as_exceptions')
def test_help_style_compatibility(reset_default_backend):
    # The current backend is plotly but the style options are those of matplotlib
    hvplot.extension('plotly', 'matplotlib', compatibility='matplotlib')
    docstring, signature = _get_doc_and_signature(
        cls=hvplot.hvPlot,
        kind='line',
        completions=False,
        docstring=False,
        generic=False,
        style=True,
        signature=None,
    )
    assert docstring == '\nMatplotlib Styling options\n---------------\n' + '\n'.join(
        sorted(Store.registry['matplotlib'][Curve].style_opts)
    )
