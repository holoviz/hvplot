import hvplot.pandas  # noqa
import hvplot.xarray  # noqa
import numpy as np
import pandas as pd
import panel as pn
import pytest
import xarray as xr

from holoviews.util.transform import dim
from hvplot import bind
from hvplot.interactive import Interactive
from hvplot.xarray import XArrayInteractive


@pytest.fixture(scope='module')
def series():
    return pd.Series(np.arange(5.0), name='A')


@pytest.fixture(scope='module')
def df():
    return pd._testing.makeMixedDataFrame()


@pytest.fixture(scope='module')
def dataset():
    return xr.tutorial.load_dataset('air_temperature')


@pytest.fixture(scope='module')
def dataarray(dataset):
    return dataset.air


class CallArgs:
    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return f'CallArgs(args={self.args!r}, kwargs={self.kwargs!r})'

    def is_empty(self):
        return not self.args and not self.kwargs


class Spy:
    def __init__(self):
        self.count = 0
        self.calls = {}

    def __repr__(self):
        return f'Spy(count={self.count!r}, calls={self.calls!r})'

    def register_call(self, args, kwargs):
        self.calls[self.count] = CallArgs(args, kwargs)
        self.count += 1


@pytest.fixture
def clone_spy():
    spy = Spy()

    _clone = Interactive._clone

    def clone_bis(inst, *args, **kwargs):
        spy.register_call(args, kwargs)
        return _clone(inst, *args, **kwargs)

    Interactive._clone = clone_bis

    yield spy

    Interactive._clone = _clone


def test_spy(clone_spy, series):
    si = Interactive(series)
    si._clone()

    assert clone_spy.count == 1
    assert clone_spy.calls[0].is_empty()

    si._clone(x='X')
    
    assert clone_spy.count == 2
    assert not clone_spy.calls[1].is_empty()
    assert clone_spy.calls[1].kwargs == dict(x='X')


def test_interactive_pandas_dataframe(df):
    dfi = Interactive(df)

    assert type(dfi) is Interactive
    assert dfi._obj is df
    assert dfi._fn is None
    assert dfi._transform == dim('*')


def test_interactive_pandas_series(series):
    si = Interactive(series)

    assert type(si) is Interactive
    assert si._obj is series
    assert si._fn is None
    assert si._transform == dim('*')


def test_interactive_xarray_dataarray(dataarray):
    dai = Interactive(dataarray)

    assert type(dai) is XArrayInteractive
    assert (dai._obj == dataarray).all()
    assert dai._fn is None
    assert dai._transform == dim('air')


def test_interactive_xarray_dataset(dataset):
    dsi = Interactive(dataset)

    assert type(dsi) is XArrayInteractive
    assert dsi._obj is dataset
    assert dsi._fn is None
    assert dsi._transform == dim('*')


def test_interactive_pandas_function(df):
    select = pn.widgets.Select(options=list(df.columns))

    def sel_col(col):
        return df[col]

    dfi = Interactive(bind(sel_col, select))
    assert type(dfi) is Interactive
    assert dfi._obj is df.A
    assert isinstance(dfi._fn, pn.param.ParamFunction)
    assert dfi._transform == dim('*')

    select.value = 'B'
    assert dfi._obj is df.B


def test_interactive_xarray_function(dataset):
    ds = dataset.copy()
    ds['air2'] = ds.air*2

    select = pn.widgets.Select(options=list(ds))

    def sel_col(sel):
        return ds[sel]

    dsi = Interactive(bind(sel_col, select))

    assert type(dsi) is XArrayInteractive
    assert isinstance(dsi._fn, pn.param.ParamFunction)
    assert dsi._transform == dim('air')

    select.value = 'air2'
    assert (dsi._obj == ds.air2).all()
    assert dsi._transform == dim('air2')


def test_interactive_pandas_dataframe_accessor(df):
    dfi = df.interactive()

    assert dfi.hvplot(kind="scatter")._transform == dfi.hvplot.scatter()._transform

    with pytest.raises(TypeError):
        dfi.hvplot.scatter(kind="area")


def test_interactive_xarray_dataset_accessor(dataarray):
    dai = dataarray.interactive

    assert dai.hvplot(kind="line")._transform == dai.hvplot.line()._transform

    with pytest.raises(TypeError):
        dai.hvplot.line(kind="area")


def test_interactive_with_bound_function_calls():
    df = pd.DataFrame({"species": [1, 1, 2, 2], "sex": 2 * ["MALE", "FEMALE"]})

    w_species = pn.widgets.Select(name='Species', options=[1, 2])
    w_sex = pn.widgets.MultiSelect(name='Sex', value=['MALE'], options=['MALE', 'FEMALE'])

    def load_data(species):
        """Simluate loading data from e.g a database or from a web API."""
        data = df.loc[df['species'] == species]
        load_data.COUNT += 1
        return data

    load_data.COUNT = 0

    # Setting up interactive with a function
    dfi = bind(load_data, w_species).interactive()
    (dfi.loc[dfi['sex'].isin(w_sex)])
    assert load_data.COUNT ==  1

    # w_species.value = 2
    # assert load_data.COUNT == 2


def test_interactive_pandas_series_init(series, clone_spy):
    si = Interactive(series)

    assert clone_spy.count == 0

    assert si._obj is series
    assert repr(si._transform) == "dim('*')"
    assert isinstance(si._current, pd.DataFrame)
    pd.testing.assert_series_equal(si._current.A, series)
    assert si._depth == 0


def test_interactive_pandas_series_accessor(series, clone_spy):

    si = series.interactive()

    assert isinstance(si, Interactive)
    assert clone_spy.count == 1
    assert clone_spy.calls[0].is_empty()

    assert si._obj is series
    assert repr(si._transform) == "dim('*')"
    assert isinstance(si._current, pd.DataFrame)
    pd.testing.assert_series_equal(si._current.A, series)
    assert si._depth == 1


def test_interactive_pandas_series_operator(series, clone_spy):
    si = Interactive(series)
    si = si + 2

    assert isinstance(si, Interactive)
    assert isinstance(si._current, pd.DataFrame)
    pd.testing.assert_series_equal(si._current.A, series + 2)
    assert si._obj is series
    assert repr(si._transform) == "dim('*').pd+2"
    assert si._depth == 2

    assert clone_spy.count == 2

    assert not clone_spy.calls[0].args
    assert clone_spy.calls[0].kwargs == {'copy': True}

    assert len(clone_spy.calls[1].args) == 1
    assert repr(clone_spy.calls[1].args[0]) == "dim('*').pd+2"
    assert not clone_spy.calls[1].kwargs


def test_interactive_pandas_series_method(series, clone_spy):
    si = Interactive(series)
    si = si.head(2)

    assert isinstance(si, Interactive)
    assert isinstance(si._current, pd.DataFrame)
    pd.testing.assert_series_equal(si._current.A, series.head(2))
    assert si._obj is series
    assert repr(si._transform) == "dim('*').pd.head(2)"
    assert si._depth == 3

    assert clone_spy.count == 3

    assert not clone_spy.calls[0].args
    assert clone_spy.calls[0].kwargs == {'copy': True}

    assert not clone_spy.calls[1].args
    assert clone_spy.calls[1].kwargs == {'copy': True}

    assert len(clone_spy.calls[2].args) == 1
    assert repr(clone_spy.calls[2].args[0]) == "dim('*').pd.head(2)"
    assert clone_spy.calls[2].kwargs == {'plot': False}


def test_interactive_pandas_series_operator_and_method(series, clone_spy):
    si = Interactive(series)

    assert isinstance(si, Interactive)
    
    si = (si + 2).head(2)

    assert isinstance(si, Interactive)
    assert isinstance(si._current, pd.DataFrame)
    pd.testing.assert_series_equal(si._current.A, (series + 2).head(2))
    assert si._obj is series
    assert repr(si._transform) == "(dim('*').pd+2).head(2)"
    assert si._depth == 5

    assert clone_spy.count == 5

    assert not clone_spy.calls[0].args
    assert clone_spy.calls[0].kwargs == {'copy': True}

    assert len(clone_spy.calls[1].args) == 1
    assert repr(clone_spy.calls[1].args[0]) == "dim('*').pd+2"
    assert not clone_spy.calls[1].kwargs

    assert not clone_spy.calls[2].args
    assert clone_spy.calls[2].kwargs == {'copy': True}

    assert not clone_spy.calls[3].args
    assert clone_spy.calls[3].kwargs == {'copy': True}

    assert len(clone_spy.calls[4].args) == 1
    assert repr(clone_spy.calls[4].args[0]) == "(dim('*').pd+2).head(2)"
    assert clone_spy.calls[4].kwargs == {'plot': False}


def test_interactive_pandas_series_operator_widget(series):
    w = pn.widgets.FloatSlider(value=2., start=1., end=5.)

    si = Interactive(series)

    si = si + w

    assert isinstance(si, Interactive)
    assert isinstance(si._current, pd.DataFrame)
    pd.testing.assert_series_equal(si._current.A, series + w.value)
    assert si._obj is series
    assert repr(si._transform) == "dim('*').pd+FloatSlider(end=5.0, start=1.0, value=2.0)"
    assert si._depth == 2

    assert len(si._params) == 1
    assert si._params[0] is w.param.value


def test_interactive_pandas_series_method_widget(series):
    w = pn.widgets.IntSlider(value=2, start=1, end=5)

    si = Interactive(series)

    si = si.head(w)

    assert isinstance(si, Interactive)
    assert isinstance(si._current, pd.DataFrame)
    pd.testing.assert_series_equal(si._current.A, series.head(w.value))
    assert si._obj is series
    assert repr(si._transform) == "dim('*').pd.head(IntSlider(end=5, start=1, value=2))"
    assert si._depth == 3

    assert len(si._params) == 1
    assert si._params[0] is w.param.value


def test_interactive_pandas_series_operator_and_method_widget(series):
    w1 = pn.widgets.FloatSlider(value=2., start=1., end=5.)
    w2 = pn.widgets.IntSlider(value=2, start=1, end=5)

    si = Interactive(series)

    assert isinstance(si, Interactive)
    
    si = (si + w1).head(w2)

    assert isinstance(si, Interactive)
    assert isinstance(si._current, pd.DataFrame)
    pd.testing.assert_series_equal(si._current.A, (series + w1.value).head(w2.value))
    assert si._obj is series
    assert repr(si._transform) == "(dim('*').pd+FloatSlider(end=5.0, start=1.0, value=2.0)).head(IntSlider(end=5, start=1, value=2))"
    assert si._depth == 5

    assert len(si._params) == 2
    assert si._params[0] is w1.param.value
    assert si._params[1] is w2.param.value


def test_interactive_pandas_series_operator_widget_update(series):
    w = pn.widgets.FloatSlider(value=2., start=1., end=5.)
    si = Interactive(series)
    si = si + w

    w.value = 3.
    assert repr(si._transform) == "dim('*').pd+FloatSlider(end=5.0, start=1.0, value=3.0)"
    
    out = si._callback()
    assert isinstance(out, pn.pane.DataFrame)
    pd.testing.assert_series_equal(out.object.A, series + 3.)


def test_interactive_pandas_series_method_widget_update(series):
    w = pn.widgets.IntSlider(value=2, start=1, end=5)
    si = Interactive(series)
    si = si.head(w)

    w.value = 3
    assert repr(si._transform) =="dim('*').pd.head(IntSlider(end=5, start=1, value=3))"
    
    out = si._callback()
    assert isinstance(out, pn.pane.DataFrame)
    pd.testing.assert_series_equal(out.object.A, series.head(3))


def test_interactive_pandas_series_operator_and_method_widget_update(series):
    w1 = pn.widgets.FloatSlider(value=2., start=1., end=5.)
    w2 = pn.widgets.IntSlider(value=2, start=1, end=5)
    si = Interactive(series)
    si = (si + w1).head(w2)

    w1.value = 3.
    w2.value = 3

    assert repr(si._transform) == "(dim('*').pd+FloatSlider(end=5.0, start=1.0, value=3.0)).head(IntSlider(end=5, start=1, value=3))"

    out = si._callback()
    assert isinstance(out, pn.pane.DataFrame)
    pd.testing.assert_series_equal(out.object.A, (series + 3.).head(3))


def test_interactive_pandas_frame_loc(df):
    dfi = Interactive(df)

    dfi = dfi.loc[:, 'A']

    assert isinstance(dfi, Interactive)

    assert dfi._obj is df
    assert isinstance(dfi._current, pd.Series)
    pd.testing.assert_series_equal(dfi._current, df.loc[:, 'A'])
    assert repr(dfi._transform) == "dim('*').pd.loc, getitem, (slice(None, None, None), 'A')"
    assert dfi._depth == 3


def test_interactive_pandas_frame_selection(df, clone_spy):
    dfi = Interactive(df)

    # There are 2 references to dfi in the right part of this expression,
    # so it's cloned twice from its root, which is why in the end dfi._depth
    # only reaches 1. 
    # TODO: Comment no longer true...
    dfi = dfi[dfi.A > 1]

    assert isinstance(dfi, Interactive)

    assert dfi._obj is df
    assert isinstance(dfi._current, pd.DataFrame)
    pd.testing.assert_frame_equal(dfi._current, df[df.A > 1])
    assert repr(dfi._transform) == "dim('*', getitem, dim('*').pd.A)>1"
    assert dfi._depth == 2

    assert clone_spy.count == 5

    assert not clone_spy.calls[0].args
    assert clone_spy.calls[0].kwargs == {'copy': True}

    assert len(clone_spy.calls[1].args) == 1
    assert repr(clone_spy.calls[1].args[0]) == "dim('*').pd.A()"
    assert clone_spy.calls[1].kwargs == {'inherit_kwargs': {}}

    assert len(clone_spy.calls[2].args) == 1
    assert repr(clone_spy.calls[2].args[0]) == "(dim('*').pd.A())>1"
    assert not clone_spy.calls[2].kwargs

    assert not clone_spy.calls[3].args
    assert clone_spy.calls[3].kwargs == {'copy': True}

    assert len(clone_spy.calls[4].args) == 1
    assert repr(clone_spy.calls[4].args[0]) == "dim('*', getitem, (dim('*').pd.A())>1)"
    assert not clone_spy.calls[4].kwargs


def test_interactive_pandas_frame_chained_attrs(df, clone_spy):
    dfi = Interactive(df)

    dfi = dfi.A.max()

    assert isinstance(dfi, Interactive)

    assert dfi._obj is df
    assert isinstance(dfi._current, float)
    assert dfi._current == pytest.approx(df.A.max())
    # This is a weird repr! Bug?
    assert repr(dfi._transform) == "dim('*').pd.A).max("
    assert dfi._depth == 4

    assert clone_spy.count == 4

    assert not clone_spy.calls[0].args
    assert clone_spy.calls[0].kwargs == {'copy': True}

    assert len(clone_spy.calls[1].args) == 1
    assert repr(clone_spy.calls[1].args[0]) == "dim('*').pd.A()"
    assert clone_spy.calls[1].kwargs == {'inherit_kwargs': {}}

    assert not clone_spy.calls[2].args
    assert clone_spy.calls[2].kwargs == {'copy': True}

    assert len(clone_spy.calls[3].args) == 1
    assert repr(clone_spy.calls[3].args[0]) == "(dim('*').pd.A()).max()"
    assert clone_spy.calls[3].kwargs == {'plot': False}


def test_interactive_pandas_out_repr(series):
    si = Interactive(series)
    si = si.max()

    assert isinstance(si, Interactive)
    assert isinstance(si._current, pd.Series)
    assert si._current.A == pytest.approx(series.max())
    assert si._obj is series
    assert repr(si._transform) == "dim('*').pd.max()"
    # One _clone from _resolve_accessor, two from _clone
    assert si._depth == 3

    # Equivalent to eval
    out = si._callback()

    assert isinstance(out, pd.Series)
    assert out.A == pytest.approx(series.max())


def test_interactive_pandas_out_frame(series):
    si = Interactive(series)
    si = si.head(2)

    assert isinstance(si, Interactive)
    assert isinstance(si._current, pd.DataFrame)
    pd.testing.assert_series_equal(si._current.A, series.head(2))
    assert si._obj is series
    assert repr(si._transform) == "dim('*').pd.head(2)"
    # One _clone from _resolve_accessor, two from _clone
    assert si._depth == 3

    # Equivalent to eval
    out = si._callback()

    assert isinstance(out, pn.pane.DataFrame)
    pd.testing.assert_frame_equal(out.object, si._current)


@pytest.mark.parametrize('op', [
    '-',   # __neg__

    # Doesn't any of the supported data implement __not__?
    # e.g. `not series` raises an error.
    # 'not', # __not__

    '+',   # _pos__
])
def test_interactive_pandas_series_operator_unary(series, op):
    if op == '~':
        series = pd.Series([True, False, True], name='A')
    si = Interactive(series)
    si = eval(f'{op} si')

    assert isinstance(si, Interactive)
    assert isinstance(si._current, pd.DataFrame)
    pd.testing.assert_series_equal(si._current.A, eval(f'{op} series'))
    assert si._obj is series
    assert repr(si._transform) == f"{op}dim('*')"
    assert si._depth == 2


def test_interactive_pandas_series_operator_unary_invert():  # __invert__
    series = pd.Series([True, False, True], name='A')
    si = Interactive(series)
    si = ~si

    assert isinstance(si, Interactive)
    assert isinstance(si._current, pd.DataFrame)
    pd.testing.assert_series_equal(si._current.A, ~series)
    assert si._obj is series
    assert repr(si._transform) == "dim('*', inv)"
    assert si._depth == 2


@pytest.mark.parametrize('op', [
    '+',  # __add__
    '&',  # __and__
    '/',  # __div__
    '==', # __eq__
    '//', # __floordiv__
    '>=', # __ge__
    '>',  # __gt__
    '<=', # __le__
    '<',  # __lt__
    '<',  # __lt__
    # '<<',  # __lshift__
    '%',  # __mod__
    '*',  # __mul__
    '!=',  # __ne__
    '|',  # __or__
    # '>>',  # __rshift__
    '**',  # __pow__
    '-',  # __sub__
    '/',  # __truediv__
])
def test_interactive_pandas_series_operator_binary(series, op):
    if op in ['&', '|']:
        series = pd.Series([True, False, True], name='A')
        val = True
    else:
        val = 2.
    si = Interactive(series)
    si = eval(f'si {op} {val}')

    assert isinstance(si, Interactive)
    assert isinstance(si._current, pd.DataFrame)
    pd.testing.assert_series_equal(si._current.A, eval(f'series {op} {val}'))
    assert si._obj is series
    val_repr = '2.0' if isinstance(val, float) else 'True'
    assert repr(si._transform) == f"dim('*').pd{op}{val_repr}"
    assert si._depth == 2


@pytest.mark.xfail()
@pytest.mark.parametrize('op', [
    '+',  # __radd__
    '&',  # __rand__
    '/',  # __rdiv__
    '//', # __rfloordiv__
    # '<<',  # __rlshift__
    '%',  # __rmod__
    '*',  # __rmul__
    '|',  # __ror__
    '**',  # __rpow__
    # '>>',  # __rshift__
    '-',  # __rsub__
    '/',  # __rtruediv__
])
def test_interactive_pandas_series_operator_reverse_binary(op):
    if op in ['&', '|']:
        series = pd.Series([True, False, True], name='A')
        val = True
    else:
        series = pd.Series([1.0, 2.0, 3.0], name='A')
        val = 2.
    si = Interactive(series)
    si = eval(f'{val} {op} si')

    assert isinstance(si, Interactive)
    assert isinstance(si._current, pd.DataFrame)
    pd.testing.assert_series_equal(si._current.A, eval(f'{val} {op} series'))
    assert si._obj is series
    val_repr = '2.0' if isinstance(val, float) else 'True'
    assert repr(si._transform) == f"{val_repr}{op}dim('*')"
    assert si._depth == 2
