import pytest
from holoviews.core.options import AbbreviatedException


def plotly_without(option):
    """Parametrize `backend` with plotly when its elements have no such option.

    hvPlot drops the option, so the test can't find it in the plotly options.
    """
    reason = f'HoloViews: plotly has no {option} option'
    return pytest.param('plotly', marks=pytest.mark.xfail(reason=reason, raises=KeyError))


def size_opt(backend):
    """The name of the size option, as set by hvPlot for the backend."""
    return 's' if backend == 'matplotlib' else 'size'


# The plotly and matplotlib plots that hvPlot builds but that fail to render.
plotly_bivariate_bug = pytest.mark.render_xfail(
    reason='BUG: bivariate on plotly fails to render with a KeyError, not a NotImplementedError',
    raises=KeyError,
)
matplotlib_labels_bug = pytest.mark.render_xfail(
    reason='BUG: labels fail to render on matplotlib, Axes.text() gets s twice (converter.py)',
    raises=AbbreviatedException,
)
