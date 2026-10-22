from unittest import SkipTest, TestCase

import pandas as pd
import pytest

import hvplot
from hvplot.plotting import hvPlotTabular


class TestPatchDuckDB(TestCase):
    def setUp(self):
        try:
            import duckdb  # noqa: F401
        except ImportError:
            raise SkipTest('DuckDB not available')
        import hvplot.duckdb  # noqa: F401

    def test_duckdb_relation_patched(self):
        import duckdb

        df = pd.DataFrame({'x': [1, 2, 3], 'y': [1, 2, 3]})
        connection = duckdb.connect(':memory:')
        relation = duckdb.from_df(df, connection=connection)
        self.assertIsInstance(relation.hvplot, hvPlotTabular)

    def test_duckdb_connection_patched(self):
        import duckdb

        df = pd.DataFrame({'x': [1, 2, 3], 'y': [1, 2, 3]})
        connection = duckdb.connect(':memory:')
        duckdb.from_df(df, connection=connection).to_view('test_connection')
        self.assertIsInstance(
            connection.execute('SELECT * FROM test_connection').hvplot, hvPlotTabular
        )


def _patched(classes, attrs):
    return all(attr in vars(cls) for cls in classes for attr in attrs)


def _unpatched(classes, attrs):
    return not any(attr in vars(cls) for cls in classes for attr in attrs)


def _round_trip(ext, classes, attrs=('hvplot',)):
    # Ends patched, so the _isolate_hvplot fixture unpatches the extension
    # and removes its module from sys.modules after the test.
    ext.patch()
    assert _patched(classes, attrs)
    assert ext.__name__ in hvplot._module_extensions

    ext._unpatch()
    assert _unpatched(classes, attrs)
    assert ext.__name__ not in hvplot._module_extensions

    ext.patch()
    assert _patched(classes, attrs)
    assert ext.__name__ in hvplot._module_extensions


def test_unpatch_duckdb():
    duckdb = pytest.importorskip('duckdb')
    import hvplot.duckdb

    _round_trip(hvplot.duckdb, [duckdb.DuckDBPyRelation, duckdb.DuckDBPyConnection])
