import panel as pn
import param
import pytest
from holoviews.core import Store
from holoviews.element import Curve

import hvplot
from hvplot.util import _get_doc_and_signature


def test_help_style_extension_output():
    # default, bokeh is the current backend
    docstring, _signature = _get_doc_and_signature(
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
    docstring, _signature = _get_doc_and_signature(
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
    docstring, _signature = _get_doc_and_signature(
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
def test_help_style_compatibility():
    # The current backend is plotly but the style options are those of matplotlib
    hvplot.extension('plotly', 'matplotlib', compatibility='matplotlib')
    docstring, _signature = _get_doc_and_signature(
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


def test_help(capsys):
    hvplot.help('line', generic=False)
    out = capsys.readouterr().out
    assert 'Create a line plot' in out
    assert 'Bokeh Styling options' in out
    assert 'Data Options' not in out  # generic=False


def test_save_holoviews_html(tmp_path):
    filename = tmp_path / 'plot.html'
    hvplot.save(Curve([1, 2, 3]), filename, title='My plot')
    content = filename.read_text()
    assert '<title>My plot</title>' in content
    # The serialized plot depends on the Bokeh version, so only check for a Bokeh document.
    assert 'Bokeh' in content


def test_save_panel_html(tmp_path):
    filename = tmp_path / 'panel.html'
    hvplot.save(pn.Column(pn.pane.Markdown('Some text')), filename, title='My panel')
    content = filename.read_text()
    assert '<title>My panel</title>' in content
    assert 'Some text' in content


def test_save_unsupported_type(tmp_path):
    with pytest.raises(TypeError, match="Saving not supported for objects of type <class 'dict'>"):
        hvplot.save({}, tmp_path / 'plot.html')


@pytest.fixture
def show_calls(monkeypatch):
    """Record the calls to Panel's `show` instead of starting a server."""
    calls = []

    def fake_show(self, *args, **kwargs):
        calls.append((self, args, kwargs))
        return 'server'

    monkeypatch.setattr(pn.viewable.Viewable, 'show', fake_show)
    return calls


def test_show_holoviews(show_calls):
    curve = Curve([1, 2, 3])
    assert hvplot.show(curve, title='My plot', port=5006, threaded=True) == 'server'
    [(obj, args, kwargs)] = show_calls
    assert isinstance(obj, pn.pane.HoloViews)
    assert obj.object is curve
    assert args == ('My plot', 5006)
    assert kwargs == {'threaded': True}


def test_show_panel(show_calls):
    column = pn.Column()
    assert hvplot.show(column) == 'server'
    assert show_calls == [(column, (None, 0), {})]


def test_show_param_rx(show_calls):
    hvplot.show(param.rx(1))
    [(obj, _args, _kwargs)] = show_calls
    assert isinstance(obj, pn.viewable.Viewable)


def test_show_unsupported_type():
    with pytest.raises(ValueError, match='dict type object not recognized and cannot be shown'):
        hvplot.show({})


@pytest.mark.usefixtures('disable_param_warnings_as_exceptions')
def test_extension_compatibility_not_implemented(caplog):
    hvplot.extension('bokeh', compatibility='matplotlib')
    assert 'Compatibility from matplotlib to bokeh not yet implemented' in caplog.text
    assert hvplot.extension.compatibility == 'matplotlib'


def test_extension_patches_docstrings(monkeypatch):
    calls = []
    monkeypatch.setattr(hvplot, '_PATCH_PLOT_SIGNATURES', True)
    # Only defined when hvplot is imported with signature patching enabled.
    monkeypatch.setattr(
        hvplot, '_patch_hvplot_docstrings', lambda: calls.append(True), raising=False
    )
    hvplot.extension('matplotlib')
    assert calls == [True]
