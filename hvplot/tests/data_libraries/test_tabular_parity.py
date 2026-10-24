"""The same hvPlot call must give the same plot whatever the tabular data library.

Each call runs on a pandas DataFrame and on the `tabular_lib` equivalent, and the plots are
compared.
Ibis tables have no index, so the calls set `x` explicitly.
"""

import holoviews as hv
import numpy as np
import pandas as pd
import pytest
from holoviews import NdMapping

from hvplot.tests._deps import POLARS_2, requires


@pytest.fixture
def df():
    return pd.DataFrame(
        {
            'x': [1.0, 2.0, 3.0, 4.0],
            'y': [2.0, 4.0, 3.0, 5.0],
            'z': [0.1, 0.2, 0.3, 0.4],
            'cat': ['a', 'b', 'a', 'b'],
            'time': pd.date_range('2020-01-01', periods=4, freq='h'),
        }
    )


# name: (kind, kwargs)
CASES = {
    'scatter': ('scatter', {'x': 'x', 'y': 'y'}),
    'scatter_c_column': ('scatter', {'x': 'x', 'y': 'y', 'c': 'cat'}),
    'scatter_c_numeric': ('scatter', {'x': 'x', 'y': 'y', 'c': 'z'}),
    'scatter_color_dim': ('scatter', {'x': 'x', 'y': 'y', 'color': hv.dim('z')}),
    'scatter_s_column': ('scatter', {'x': 'x', 'y': 'y', 's': 'z'}),
    'scatter_by': ('scatter', {'x': 'x', 'y': 'y', 'by': 'cat'}),
    'scatter_groupby': ('scatter', {'x': 'x', 'y': 'y', 'groupby': 'cat', 'dynamic': False}),
    'scatter_hover_cols': ('scatter', {'x': 'x', 'y': 'y', 'hover_cols': ['z', 'cat']}),
    'scatter_hover_cols_all': ('scatter', {'x': 'x', 'y': 'y', 'hover_cols': 'all'}),
    'scatter_transforms': ('scatter', {'x': 'x', 'y': 'y', 'transforms': {'y': hv.dim('y') * 2}}),
    'scatter_xlim': ('scatter', {'x': 'x', 'y': 'y', 'xlim': (0, 10)}),
    'line_default_y': ('line', {'x': 'x'}),
    'line_y_list': ('line', {'x': 'x', 'y': ['y', 'z']}),
    'line_datetime_x': ('line', {'x': 'time', 'y': 'y'}),
    'line_sort_date': ('line', {'x': 'time', 'y': 'y', 'sort_date': True}),
    'line_row': ('line', {'x': 'x', 'y': 'y', 'row': 'cat'}),
    'line_by_subplots': ('line', {'x': 'x', 'y': 'y', 'by': 'cat', 'subplots': True}),
    'line_by_derived_datetime': ('line', {'x': 'x', 'y': 'y', 'by': 'time.hour'}),
    'hist': ('hist', {'y': 'y'}),
    'hist_by': ('hist', {'y': 'y', 'by': 'cat'}),
    'bar': ('bar', {'x': 'cat', 'y': 'y'}),
    'heatmap_derived_datetime': ('heatmap', {'x': 'time.hour', 'y': 'cat', 'C': 'y'}),
    'labels_text_column': ('labels', {'x': 'x', 'y': 'y', 'text': 'cat'}),
    'labels_text_template': ('labels', {'x': 'x', 'y': 'y', 'text': '{cat} {z}'}),
    'table_columns': ('table', {'columns': ['x', 'cat']}),
}

# (case, library): reason
BUGS = {
    ('scatter_c_column', 'ibis'): 'BUG: c=<column> reads the dtype of an ibis column',
    ('scatter_c_numeric', 'ibis'): 'BUG: c=<column> reads the dtype of an ibis column',
    ('scatter_color_dim', 'ibis'): 'BUG: c=<column> reads the dtype of an ibis column',
    (
        'scatter_c_numeric',
        'dask',
    ): 'BUG: the symmetric option is missing, its TypeError is swallowed',
    (
        'scatter_color_dim',
        'dask',
    ): 'BUG: the symmetric option is missing, its TypeError is swallowed',
    (
        'scatter_color_dim',
        'polars',
    ): 'BUG: the column of the dim is dropped by the column selection',
    (
        'scatter_color_dim',
        'duckdb',
    ): 'BUG: the column of the dim is dropped by the column selection',
    ('scatter_hover_cols_all', 'duckdb'): 'BUG: hover_cols="all" raises UnboundLocalError',
    ('line_default_y', 'ibis'): 'BUG: the default y includes the non-numeric columns',
    ('line_by_derived_datetime', 'polars'): 'BUG: the column selection does not know time.hour',
    ('line_by_derived_datetime', 'duckdb'): 'BUG: the column selection does not know time.hour',
    ('line_by_derived_datetime', 'ibis'): 'BUG: derived datetimes are not supported',
    ('heatmap_derived_datetime', 'polars'): 'BUG: the column selection does not know time.hour',
    ('heatmap_derived_datetime', 'duckdb'): 'BUG: the column selection does not know time.hour',
    ('heatmap_derived_datetime', 'ibis'): 'BUG: derived datetimes are not supported',
    (
        'labels_text_template',
        'polars',
    ): 'BUG: the columns of the template are dropped by the column selection',
    (
        'labels_text_template',
        'duckdb',
    ): 'BUG: the columns of the template are dropped by the column selection',
    ('labels_text_template', 'ibis'): 'BUG: labels copies the ibis table',
    ('table_columns', 'ibis'): 'BUG: table reads the index of an ibis table',
    (
        'rasterize_aggregator_column',
        'polars',
    ): 'BUG: the column of the aggregator is dropped by the column selection',
    (
        'rasterize_aggregator_column',
        'duckdb',
    ): 'BUG: the column of the aggregator is dropped by the column selection',
}
if POLARS_2:
    BUGS[('line_default_y', 'polars')] = 'BUG: pl.NUMERIC_DTYPES was removed in polars 2.0'
    BUGS[('table_columns', 'polars')] = 'BUG: pl.NUMERIC_DTYPES was removed in polars 2.0'

# Ibis tables have no index, which hover_cols='all' adds to the hover columns.
NO_INDEX = {('scatter_hover_cols_all', 'ibis')}


def to_pandas(element):
    # `dframe()` returns a Narwhals frame for ibis.
    return pd.DataFrame({d.name: element.dimension_values(d) for d in element.dimensions()})


def assert_same_plot(plot, expected):
    if isinstance(plot, hv.DynamicMap):
        plot, expected = plot[()], expected[()]
    if isinstance(plot, NdMapping):
        # HoloViews groups dask, polars and ibis data in another order: the key order is ignored.
        assert type(plot) is type(expected)
        assert set(plot.keys()) == set(expected.keys())
        for key in expected.keys():
            assert_same_plot(plot[key], expected[key])
        return
    backend = hv.Store.current_backend
    elements = plot.traverse(lambda el: el, [hv.Element])
    expected_elements = expected.traverse(lambda el: el, [hv.Element])
    for element, expected_element in zip(elements, expected_elements, strict=True):
        assert type(element) is type(expected_element)
        assert element.kdims == expected_element.kdims
        assert element.vdims == expected_element.vdims
        pd.testing.assert_frame_equal(
            to_pandas(element), to_pandas(expected_element), check_dtype=False
        )
        for group in ('plot', 'style'):
            options = hv.Store.lookup_options(backend, element, group).kwargs
            assert options == hv.Store.lookup_options(backend, expected_element, group).kwargs


def assert_same_plot_as_pandas(request, df, tabular_lib, name, kind, kwargs):
    # With pandas it compares the plot with itself, which checks that the comparison is stable.
    library = request.node.callspec.params['tabular_lib']
    if (name, library) in NO_INDEX:
        pytest.skip(f'{library} has no index')
    if (name, library) in BUGS:
        request.applymarker(pytest.mark.xfail(strict=True, reason=BUGS[(name, library)]))

    expected = df.hvplot(kind=kind, **kwargs)
    plot = tabular_lib(df).hvplot(kind=kind, **kwargs)

    assert_same_plot(plot, expected)


@pytest.mark.usefixtures('hvplot_pandas')
@pytest.mark.parametrize('name', CASES)
def test_same_plot_as_pandas(request, df, tabular_lib, name):
    kind, kwargs = CASES[name]
    assert_same_plot_as_pandas(request, df, tabular_lib, name, kind, kwargs)


@requires('datashader')
@pytest.mark.slow
@pytest.mark.usefixtures('hvplot_pandas')
def test_rasterize_aggregator_column(request, df, tabular_lib):
    import datashader as ds  # Optional dependency

    kwargs = {'x': 'x', 'y': 'y', 'rasterize': True, 'aggregator': ds.mean('z')}
    assert_same_plot_as_pandas(
        request, df, tabular_lib, 'rasterize_aggregator_column', 'scatter', kwargs
    )


@pytest.fixture
def duckdb_connection():
    duckdb = pytest.importorskip('duckdb')
    import hvplot.duckdb  # noqa: F401

    connection = duckdb.connect(':memory:')
    yield connection
    connection.close()


@pytest.mark.usefixtures('hvplot_pandas')
@pytest.mark.parametrize(
    'kwargs',
    [
        {},
        {'hover_cols': ['z']},
        pytest.param(
            {'hover_cols': 'all'},
            marks=pytest.mark.xfail(reason='BUG: hover_cols="all" raises UnboundLocalError'),
        ),
    ],
    ids=['default', 'hover_cols', 'hover_cols_all'],
)
def test_duckdb_connection_result(duckdb_connection, kwargs):
    df = pd.DataFrame({'x': [1.0, 2.0, 3.0], 'y': [2.0, 4.0, 3.0], 'z': [0.1, 0.2, 0.3]})
    duckdb_connection.register('test_connection', df)

    plot = duckdb_connection.execute('SELECT * FROM test_connection').hvplot.scatter(
        x='x', y='y', **kwargs
    )

    expected = df.hvplot.scatter(x='x', y='y', **kwargs)
    assert plot.kdims == expected.kdims
    assert plot.vdims == expected.vdims
    np.testing.assert_array_equal(plot.dimension_values('y'), df['y'])
