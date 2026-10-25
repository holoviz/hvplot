"""The same hvPlot call must give the same plot whatever the tabular data library.

Each call runs on a pandas DataFrame and on the `tabular_lib` equivalent, and the plots are
compared.
Ibis tables have no index, so the calls set `x` explicitly.
`BUGS` lists the known failures and `SKIPS` the documented differences, by (case, library).
A reason starting with `BUG:` is a bug of hvPlot, the others come from another library.
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
            'neg': [-1.0, 2.0, -3.0, 4.0],
            'cat': ['a', 'b', 'a', 'b'],
            'cat2': ['u', 'u', 'v', 'v'],
            # Not sorted, to see whether `sort_date` sorts it.
            'time': pd.Timestamp('2020-01-01') + pd.to_timedelta([3, 1, 2, 0], unit='h'),
        }
    )


# One entry per call, grouped by option. name: (kind, kwargs)
CASES = {
    # x, y and the kind options
    'scatter': ('scatter', {'x': 'x', 'y': 'y'}),
    'line_default_y': ('line', {'x': 'x'}),
    'line_y_list': ('line', {'x': 'x', 'y': ['y', 'z']}),
    'hist': ('hist', {'y': 'y'}),
    'hist_by': ('hist', {'y': 'y', 'by': 'cat'}),
    'hist_bins': ('hist', {'y': 'y', 'bins': 3, 'bin_range': (0, 10)}),
    'hist_logx': ('hist', {'y': 'y', 'logx': True}),
    'bar': ('bar', {'x': 'cat', 'y': 'y'}),
    'heatmap_C_reduce_function': (
        'heatmap',
        {'x': 'cat', 'y': 'cat2', 'C': 'y', 'reduce_function': np.sum},
    ),
    'heatmap_derived_datetime': ('heatmap', {'x': 'time.hour', 'y': 'cat', 'C': 'y'}),
    'labels_text_column': ('labels', {'x': 'x', 'y': 'y', 'text': 'cat'}),
    'labels_text_template': ('labels', {'x': 'x', 'y': 'y', 'text': '{cat} {z}'}),
    'table': ('table', {}),
    'table_columns': ('table', {'columns': ['x', 'cat']}),
    # by, groupby, row, col, subplots
    'scatter_by': ('scatter', {'x': 'x', 'y': 'y', 'by': 'cat'}),
    'scatter_by_list': ('scatter', {'x': 'x', 'y': 'y', 'by': ['cat', 'cat2']}),
    'scatter_groupby': ('scatter', {'x': 'x', 'y': 'y', 'groupby': 'cat', 'dynamic': False}),
    'scatter_groupby_list': (
        'scatter',
        {'x': 'x', 'y': 'y', 'groupby': ['cat', 'cat2'], 'dynamic': False},
    ),
    'scatter_groupby_derived_datetime': (
        'scatter',
        {'x': 'x', 'y': 'y', 'groupby': 'time.hour', 'dynamic': False},
    ),
    'line_by_derived_datetime': ('line', {'x': 'x', 'y': 'y', 'by': 'time.hour'}),
    'line_by_subplots': ('line', {'x': 'x', 'y': 'y', 'by': 'cat', 'subplots': True}),
    'line_row': ('line', {'x': 'x', 'y': 'y', 'row': 'cat'}),
    'scatter_row_col': ('scatter', {'x': 'x', 'y': 'y', 'row': 'cat', 'col': 'cat2'}),
    'scatter_transforms': ('scatter', {'x': 'x', 'y': 'y', 'transforms': {'y': hv.dim('y') * 2}}),
    'line_sort_date': ('line', {'x': 'time', 'y': 'y', 'sort_date': True}),
    'line_sort_date_false': ('line', {'x': 'time', 'y': 'y', 'sort_date': False}),
    # c, color, s, cmap, clim, symmetric, robust
    'scatter_c_column': ('scatter', {'x': 'x', 'y': 'y', 'c': 'cat'}),
    'scatter_c_numeric': ('scatter', {'x': 'x', 'y': 'y', 'c': 'z'}),
    'scatter_c_clim': ('scatter', {'x': 'x', 'y': 'y', 'c': 'z', 'clim': (0, 1)}),
    'scatter_c_symmetric_deduced': ('scatter', {'x': 'x', 'y': 'y', 'c': 'neg'}),
    'scatter_c_robust': ('scatter', {'x': 'x', 'y': 'y', 'c': 'z', 'robust': True}),
    'scatter_c_cmap_dict': (
        'scatter',
        {'x': 'x', 'y': 'y', 'c': 'cat', 'cmap': {'a': 'red', 'b': 'blue'}},
    ),
    'scatter_color_dim': ('scatter', {'x': 'x', 'y': 'y', 'color': hv.dim('z')}),
    'scatter_s_column': ('scatter', {'x': 'x', 'y': 'y', 's': 'z'}),
    # hover_cols
    'scatter_hover_cols': ('scatter', {'x': 'x', 'y': 'y', 'hover_cols': ['z', 'cat']}),
    'scatter_hover_cols_string': ('scatter', {'x': 'x', 'y': 'y', 'hover_cols': 'cat'}),
    'scatter_hover_cols_derived_datetime': (
        'scatter',
        {'x': 'x', 'y': 'y', 'hover_cols': ['time.hour']},
    ),
    'scatter_hover_cols_all': ('scatter', {'x': 'x', 'y': 'y', 'hover_cols': 'all'}),
    'scatter_hover_cols_all_no_index': (
        'scatter',
        {'x': 'x', 'y': 'y', 'hover_cols': 'all', 'use_index': False},
    ),
    # xlim, ylim, tiles
    'scatter_xlim': ('scatter', {'x': 'x', 'y': 'y', 'xlim': (0, 10)}),
    'points_tiles': ('points', {'x': 'x', 'y': 'y', 'tiles': True}),
    'points_tiles_xlim': ('points', {'x': 'x', 'y': 'y', 'tiles': True, 'xlim': (0, 10)}),
}

# Datashader reductions, slow. name: (kind, kwargs)
DATASHADER_CASES = {
    'rasterize_c': ('scatter', {'x': 'x', 'y': 'y', 'rasterize': True, 'c': 'z'}),
    'rasterize_aggregator_str_c': (
        'scatter',
        {'x': 'x', 'y': 'y', 'rasterize': True, 'aggregator': 'max', 'c': 'z'},
    ),
    'rasterize_selector_str': (
        'scatter',
        {'x': 'x', 'y': 'y', 'rasterize': True, 'selector': 'first'},
    ),
    'rasterize_selector_tuple': (
        'scatter',
        {'x': 'x', 'y': 'y', 'rasterize': True, 'selector': ('max', 'z')},
    ),
    'datashade_by': ('scatter', {'x': 'x', 'y': 'y', 'datashade': True, 'by': 'cat'}),
}

# Reasons used more than once.
IBIS_DTYPE = 'BUG: a color column reads the dtype of an ibis column'
DASK_SYMMETRIC = 'BUG: the symmetric and robust options are missing, a TypeError is swallowed'
COLUMN_SELECTION = 'BUG: the column selection drops the column of the {}'
DERIVED_DATETIME = 'BUG: the column selection does not know time.hour'
IBIS_DERIVED_DATETIME = 'BUG: derived datetimes are not supported'
DASK_SELECTOR = 'HoloViews: rasterize with a selector fails on dask data (unknown chunk size)'
TABLE_NUMERIC_ONLY = 'BUG: table without columns keeps only the numeric columns'
SORT_DATE = 'BUG: sort_date is only applied to pandas data'

# (case, library): reason
BUGS = {
    ('scatter_c_column', 'ibis'): IBIS_DTYPE,
    ('scatter_c_numeric', 'ibis'): IBIS_DTYPE,
    ('scatter_c_clim', 'ibis'): IBIS_DTYPE,
    ('scatter_c_symmetric_deduced', 'ibis'): IBIS_DTYPE,
    ('scatter_c_robust', 'ibis'): IBIS_DTYPE,
    ('scatter_c_cmap_dict', 'ibis'): IBIS_DTYPE,
    ('scatter_color_dim', 'ibis'): IBIS_DTYPE,
    ('rasterize_c', 'ibis'): IBIS_DTYPE,
    ('rasterize_aggregator_str_c', 'ibis'): IBIS_DTYPE,
    ('scatter_c_numeric', 'dask'): DASK_SYMMETRIC,
    ('scatter_c_symmetric_deduced', 'dask'): DASK_SYMMETRIC,
    ('scatter_c_robust', 'dask'): DASK_SYMMETRIC,
    ('scatter_color_dim', 'dask'): DASK_SYMMETRIC,
    ('rasterize_c', 'dask'): DASK_SYMMETRIC,
    ('rasterize_aggregator_str_c', 'dask'): DASK_SYMMETRIC,
    ('scatter_color_dim', 'polars'): COLUMN_SELECTION.format('dim'),
    ('scatter_color_dim', 'duckdb'): COLUMN_SELECTION.format('dim'),
    ('labels_text_template', 'polars'): COLUMN_SELECTION.format('template'),
    ('labels_text_template', 'duckdb'): COLUMN_SELECTION.format('template'),
    ('rasterize_aggregator_column', 'polars'): COLUMN_SELECTION.format('aggregator'),
    ('rasterize_aggregator_column', 'duckdb'): COLUMN_SELECTION.format('aggregator'),
    ('rasterize_selector_tuple', 'polars'): COLUMN_SELECTION.format('selector'),
    ('rasterize_selector_tuple', 'duckdb'): COLUMN_SELECTION.format('selector'),
    (
        'rasterize_selector_tuple',
        'ibis',
    ): 'BUG: the selector column is not a dimension of the ibis data',
    ('rasterize_selector_str', 'dask'): DASK_SELECTOR,
    ('rasterize_selector_tuple', 'dask'): DASK_SELECTOR,
    ('line_by_derived_datetime', 'polars'): DERIVED_DATETIME,
    ('line_by_derived_datetime', 'duckdb'): DERIVED_DATETIME,
    ('line_by_derived_datetime', 'ibis'): IBIS_DERIVED_DATETIME,
    ('scatter_groupby_derived_datetime', 'polars'): DERIVED_DATETIME,
    ('scatter_groupby_derived_datetime', 'duckdb'): DERIVED_DATETIME,
    ('scatter_groupby_derived_datetime', 'ibis'): IBIS_DERIVED_DATETIME,
    ('heatmap_derived_datetime', 'polars'): DERIVED_DATETIME,
    ('heatmap_derived_datetime', 'duckdb'): DERIVED_DATETIME,
    ('heatmap_derived_datetime', 'ibis'): IBIS_DERIVED_DATETIME,
    ('line_sort_date', 'dask'): SORT_DATE,
    ('line_sort_date', 'ibis'): SORT_DATE,
    ('scatter_hover_cols_all', 'duckdb'): 'BUG: hover_cols="all" raises UnboundLocalError',
    (
        'scatter_hover_cols_all_no_index',
        'duckdb',
    ): 'BUG: hover_cols="all" raises UnboundLocalError',
    ('line_default_y', 'ibis'): 'BUG: the default y includes the non-numeric columns',
    ('labels_text_template', 'ibis'): 'BUG: labels copies the ibis table',
    ('table', 'ibis'): 'BUG: table reads the index of an ibis table',
    ('table_columns', 'ibis'): 'BUG: table reads the index of an ibis table',
    ('table_strings_only', 'ibis'): 'BUG: table reads the index of an ibis table',
    ('table', 'duckdb'): TABLE_NUMERIC_ONLY,
    ('table_strings_only', 'duckdb'): 'BUG: the column selection fails without a numeric column',
    ('hist_logx', 'ibis'): 'BUG: the histogram compares an ibis table with a number for logx',
    ('heatmap_C_reduce_function', 'ibis'): 'BUG: reduce_function fails on an ibis table',
}
if POLARS_2:
    BUGS[('line_default_y', 'polars')] = 'BUG: pl.NUMERIC_DTYPES was removed in polars 2.0'
    BUGS[('table', 'polars')] = 'BUG: pl.NUMERIC_DTYPES was removed in polars 2.0'
    BUGS[('table_columns', 'polars')] = 'BUG: pl.NUMERIC_DTYPES was removed in polars 2.0'
    BUGS[('table_strings_only', 'polars')] = 'BUG: pl.NUMERIC_DTYPES was removed in polars 2.0'
else:
    BUGS[('table', 'polars')] = TABLE_NUMERIC_ONLY
    BUGS[('table_strings_only', 'polars')] = (
        'BUG: the column selection keeps only the first column'
    )

# (case, library): reason. Differences that are documented, or that come from the library.
SKIPS = {
    ('scatter_hover_cols_all', 'ibis'): "ibis has no index, which hover_cols='all' adds",
    ('points_tiles', 'dask'): 'tiles does not project lat/lon of lazy data',
    ('points_tiles', 'ibis'): 'tiles does not project lat/lon of lazy data',
    ('points_tiles_xlim', 'dask'): 'tiles does not project lat/lon of lazy data',
    ('points_tiles_xlim', 'ibis'): 'tiles does not project lat/lon of lazy data',
}


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
    if (name, library) in SKIPS:
        pytest.skip(SKIPS[(name, library)])
    if (name, library) in BUGS:
        reason = BUGS[(name, library)]
        # Only the bugs of hvPlot (BUG:) are strict, as the other libraries can fix theirs.
        request.applymarker(pytest.mark.xfail(reason=reason, strict=reason.startswith('BUG:')))

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
@pytest.mark.parametrize('name', DATASHADER_CASES)
def test_same_plot_as_pandas_datashader(request, df, tabular_lib, name):
    kind, kwargs = DATASHADER_CASES[name]
    assert_same_plot_as_pandas(request, df, tabular_lib, name, kind, {**kwargs, 'dynamic': False})


@requires('datashader')
@pytest.mark.slow
@pytest.mark.usefixtures('hvplot_pandas')
def test_rasterize_aggregator_column(request, df, tabular_lib):
    import datashader as ds  # Optional dependency

    kwargs = {'x': 'x', 'y': 'y', 'rasterize': True, 'aggregator': ds.mean('z')}
    assert_same_plot_as_pandas(
        request, df, tabular_lib, 'rasterize_aggregator_column', 'scatter', kwargs
    )


@pytest.mark.usefixtures('hvplot_pandas')
def test_same_plot_as_pandas_without_numeric_column(request, df, tabular_lib):
    assert_same_plot_as_pandas(
        request, df[['cat', 'cat2']], tabular_lib, 'table_strings_only', 'table', {}
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
