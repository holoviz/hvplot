"""Every kind that a pandas DataFrame supports, built and rendered with each backend."""

import pytest

from hvplot.tests._backends import matplotlib_labels_bug, plotly_bivariate_bug
from hvplot.tests._data import makeDataFrame
from hvplot.tests.kinds.test_all_kinds import (
    OHLC_Y,
    TYPES,
    Y,
    assert_kind_element,
    render_marks,
)

BACKENDS = ['bokeh', 'matplotlib', 'plotly']

# The kinds with no hvPlot element for the backend raise an error when called.
NOT_SUPPORTED = [('hexbin', 'plotly'), ('polygons', 'plotly'), ('vectorfield', 'plotly')]

dataset_bug = pytest.mark.xfail(
    reason='BUG: dataset fails with a KeyError, the options of Dataset are not found',
    raises=KeyError,
)
BACKEND_BUGS = {
    ('bivariate', 'plotly'): plotly_bivariate_bug,
    ('dataset', 'matplotlib'): dataset_bug,
    ('dataset', 'plotly'): dataset_bug,
    ('labels', 'matplotlib'): matplotlib_labels_bug,
}

# The kinds that do not plot the columns Y.
KIND_KWARGS = {
    'bivariate': {'x': 'A', 'y': 'B'},
    'heatmap': {'x': 'A', 'y': 'B', 'C': 'C'},
    'ohlc': {'y': OHLC_Y},
    'hexbin': {'x': 'A', 'y': 'B'},
    'labels': {'x': 'A', 'y': 'B', 'text': 'C'},
    'vectorfield': {'x': 'A', 'y': 'B', 'angle': 'C', 'mag': 'D'},
}


def kind_kwargs(kind):
    return KIND_KWARGS.get(kind, {'y': Y})


def kind_and_backend_params():
    params = []
    for kind in sorted(TYPES):
        for backend in BACKENDS:
            if (kind, backend) in NOT_SUPPORTED:
                continue
            marks = render_marks(kind, 'pandas')
            if (kind, backend) in BACKEND_BUGS:
                marks.append(BACKEND_BUGS[kind, backend])
            params.append(pytest.param(kind, backend, marks=marks))
    return params


# A numeric index, as the string index of makeDataFrame cannot be rendered by every kind.
@pytest.fixture
def df():
    return makeDataFrame().reset_index(drop=True)


@pytest.mark.parametrize(('kind', 'backend'), kind_and_backend_params(), indirect=['backend'])
def test_kind(hvplot_pandas, backend, df, kind):
    plot = df.hvplot(kind=kind, **kind_kwargs(kind))
    assert_kind_element(plot, kind)


@pytest.mark.parametrize(('kind', 'backend'), NOT_SUPPORTED, indirect=['backend'])
def test_kind_not_supported(hvplot_pandas, backend, df, kind):
    with pytest.raises(
        NotImplementedError, match=f"'{kind}' plot not supported by the '{backend}'"
    ):
        df.hvplot(kind=kind, **kind_kwargs(kind))
