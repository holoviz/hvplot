import holoviews as hv
import hvplot.pandas  # noqa
import hvplot.xarray  # noqa
import matplotlib
import numpy as np
import pandas as pd
import panel as pn
import pytest
import xarray as xr

from holoviews.util.transform import dim
from hvplot import bind
from hvplot.interactive import Interactive
from hvplot.tests.util import makeDataFrame, makeMixedDataFrame
from hvplot.xarray import XArrayInteractive


@pytest.fixture(scope='module')
def series():
    return pd.Series(np.arange(5.0), name='A')


@pytest.fixture(scope='module')
def df():
    return makeMixedDataFrame()


@pytest.fixture(scope='module')
def dataset():
    return xr.tutorial.load_dataset('air_temperature')


@pytest.fixture(scope='module')
def dataarray(dataset):
    return dataset.air


class CallCtxt:
    def __init__(self, call_args, call_kwargs, **kwargs):
        for k, v in kwargs.items():
            if k in ['args', 'kwargs']:
                raise ValueError("**kwargs passed to CallCtxt can't be named args or kwargs")
            setattr(self, k, v)
        self.args = call_args
        self.kwargs = call_kwargs

    def __repr__(self):
        inner = ''
        for attr in vars(self):
            inner += f'{attr}={getattr(self, attr)!r}, '
        return f'CallCtxt({inner}args={self.args!r}, kwargs={self.kwargs!r})'

    def is_empty(self):
        return not self.args and not self.kwargs


class Spy:
    def __init__(self):
        self.count = 0
        self.calls = {}

    def __repr__(self):
        return f'Spy(count={self.count!r}, calls={self.calls!r})'

    def register_call(self, called_args, called_kwargs, **kwargs):
        self.calls[self.count] = CallCtxt(called_args, called_kwargs, **kwargs)
        self.count += 1


@pytest.fixture
def clone_spy():
    # In hindsight it might have been a better idea to spy __init__
    # rather than _clone, to check exactly how new instances are created
    # and not depend on the implementation of _clone.
    spy = Spy()

    _clone = Interactive._clone

    def clone_bis(inst, *args, **kwargs):
        cloned = _clone(inst, *args, **kwargs)
        spy.register_call(args, kwargs, depth=cloned._depth)
        return cloned

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
    assert dfi._method is None


def test_interactive_pandas_series(series):
    si = Interactive(series)

    assert type(si) is Interactive
    assert si._obj is series
    assert si._fn is None
    assert si._transform == dim('*')
    assert si._method is None


def test_interactive_xarray_dataarray(dataarray):
    dai = Interactive(dataarray)

    assert type(dai) is XArrayInteractive
    assert (dai._obj == dataarray).all()
    assert dai._fn is None
    assert dai._transform == dim('air')
    assert dai._method is None


def test_interactive_xarray_dataarray_no_name():
    dataarray = xr.DataArray(np.random.rand(2, 2))
    with pytest.raises(ValueError, match='Cannot use interactive API on DataArray without name'):
        Interactive(dataarray)


def test_interactive_xarray_dataset(dataset):
    dsi = Interactive(dataset)

    assert type(dsi) is XArrayInteractive
    assert dsi._obj is dataset
    assert dsi._fn is None
    assert dsi._transform == dim('*')
    assert dsi._method is None


def test_interactive_pandas_function(df):
    select = pn.widgets.Select(options=list(df.columns))

    def sel_col(col):
        return df[col]

    dfi = Interactive(bind(sel_col, select))
    assert type(dfi) is Interactive
    assert dfi._obj is df.A
    assert isinstance(dfi._fn, pn.param.ParamFunction)
    assert dfi._transform == dim('*')
    assert dfi._method is None

    select.value = 'B'
    assert dfi._obj is df.B


def test_interactive_xarray_function(dataset):
    ds = dataset.copy()
    ds['air2'] = ds.air * 2

    select = pn.widgets.Select(options=list(ds))

    def sel_col(sel):
        return ds[sel]

    dsi = Interactive(bind(sel_col, select))

    assert type(dsi) is XArrayInteractive
    assert isinstance(dsi._fn, pn.param.ParamFunction)
    assert dsi._transform == dim('air')
    assert dsi._method is None

    select.value = 'air2'
    assert (dsi._obj == ds.air2).all()
    assert dsi._transform == dim('air2')


def test_interactive_nested_widgets():
    df = makeDataFrame()
    w = pn.widgets.RadioButtonGroup(value='A', options=list('ABC'))

    idf = Interactive(df)
    pipeline = idf.groupby(['D', w]).mean()
    ioutput = pipeline.panel().object().object
    iw = pipeline.widgets()

    output = df.groupby(['D', 'A']).mean()

    pd.testing.assert_frame_equal(ioutput, output)
    assert len(iw) == 1
    assert iw[0] == w


def test_interactive_slice():
    df = makeDataFrame()
    w = pn.widgets.IntSlider(start=10, end=40)

    idf = Interactive(df)
    pipeline = idf.iloc[:w]
    ioutput = pipeline.panel().object().object
    iw = pipeline.widgets()

    output = df.iloc[:10]

    pd.testing.assert_frame_equal(ioutput, output)
    assert len(iw) == 1
    assert iw[0] == w

    w.value = 15
    ioutput = pipeline.panel().object().object
    output = df.iloc[:15]
    pd.testing.assert_frame_equal(ioutput, output)


def test_interactive_pandas_dataframe_hvplot_accessor(df):
    dfi = df.interactive()

    assert dfi.hvplot(kind='scatter')._transform == dfi.hvplot.scatter()._transform

    with pytest.raises(TypeError):
        dfi.hvplot.scatter(kind='area')


def test_interactive_xarray_dataset_hvplot_accessor(dataarray):
    dai = dataarray.interactive

    assert dai.hvplot(kind='line')._transform == dai.hvplot.line()._transform

    with pytest.raises(TypeError):
        dai.hvplot.line(kind='area')


def test_interactive_pandas_dataframe_hvplot_accessor_dmap(df):
    dfi = df.interactive()
    dfi = dfi.hvplot.line(y='A')

    # TODO: Not sure about the logic
    assert dfi._dmap is True


def test_interactive_pandas_dataframe_hvplot_accessor_dmap_kind_widget(df):
    w = pn.widgets.Select(options=['line', 'scatter'])
    dfi = df.interactive()
    dfi = dfi.hvplot(kind=w, y='A')

    assert dfi._dmap is False


def test_interactive_with_bound_function_calls():
    df = pd.DataFrame({'species': [1, 1, 1, 2, 2, 2], 'sex': 3 * ['MALE', 'FEMALE']})

    w_species = pn.widgets.Select(name='Species', options=[1, 2])
    w_sex = pn.widgets.MultiSelect(name='Sex', value=['MALE'], options=['MALE', 'FEMALE'])

    def load_data(species, watch=True):
        if watch:
            load_data.COUNT += 1
        return df.loc[df['species'] == species]

    load_data.COUNT = 0

    # Setting up interactive with a function
    dfi = bind(load_data, w_species).interactive()
    dfi = dfi.loc[dfi['sex'].isin(w_sex)]

    out = dfi.output()

    assert isinstance(out, pn.param.ParamFunction)
    assert isinstance(out._pane, pn.pane.DataFrame)
    pd.testing.assert_frame_equal(
        out._pane.object, load_data(w_species.value, watch=False).loc[df['sex'].isin(w_sex.value)]
    )

    (dfi.loc[dfi['sex'].isin(w_sex)])
    assert load_data.COUNT == 1

    w_species.value = 2

    pd.testing.assert_frame_equal(
        out._pane.object, load_data(w_species.value, watch=False).loc[df['sex'].isin(w_sex.value)]
    )

    assert load_data.COUNT == 2

    dfi = dfi.head(1)

    assert load_data.COUNT == 2

    out = dfi.output()

    pd.testing.assert_frame_equal(
        out._pane.object,
        load_data(w_species.value, watch=False).loc[df['sex'].isin(w_sex.value)].head(1),
    )

    w_species.value = 1

    pd.testing.assert_frame_equal(
        out._pane.object,
        load_data(w_species.value, watch=False).loc[df['sex'].isin(w_sex.value)].head(1),
    )

    assert load_data.COUNT == 3


def test_interactive_pandas_series_init(series, clone_spy):
    si = Interactive(series)

    assert clone_spy.count == 0

    assert si._obj is series
    assert repr(si._transform) == "dim('*')"
    assert isinstance(si._current, pd.DataFrame)
    pd.testing.assert_series_equal(si._current.A, series)
    assert si._depth == 0
    assert si._method is None


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
    assert si._method is None


def test_interactive_pandas_series_operator(series, clone_spy):
    si = Interactive(series)
    si = si + 2

    assert isinstance(si, Interactive)
    assert isinstance(si._current, pd.DataFrame)
    pd.testing.assert_series_equal(si._current.A, series + 2)
    assert si._obj is series
    assert repr(si._transform) == "dim('*').pd+2"
    assert si._depth == 2
    assert si._method is None

    assert clone_spy.count == 2

    # _clone(copy=True) in _resolve_accessor in _apply_operator
    assert clone_spy.calls[0].depth == 1
    assert not clone_spy.calls[0].args
    assert clone_spy.calls[0].kwargs == {'copy': True}

    # _clone in _apply_operator
    assert clone_spy.calls[1].depth == 2
    assert len(clone_spy.calls[1].args) == 1
    assert repr(clone_spy.calls[1].args[0]) == "dim('*').pd+2"
    assert not clone_spy.calls[1].kwargs


def test_interactive_pandas_series_method_args(series, clone_spy):
    si = Interactive(series)
    si = si.head(2)

    assert isinstance(si, Interactive)
    assert isinstance(si._current, pd.DataFrame)
    pd.testing.assert_series_equal(si._current.A, series.head(2))
    assert si._obj is series
    assert repr(si._transform) == "dim('*').pd.head(2)"
    assert si._depth == 3
    assert si._method is None

    assert clone_spy.count == 3

    # _clone in _resolve_accessor in __getattribute__(name='head')
    assert clone_spy.calls[0].depth == 1
    assert not clone_spy.calls[0].args
    assert clone_spy.calls[0].kwargs == {'copy': True}

    # 1st _clone(copy=True) in __call__
    assert clone_spy.calls[1].depth == 2
    assert not clone_spy.calls[1].args
    assert clone_spy.calls[1].kwargs == {'copy': True}

    # 2nd _clone in __call__
    assert clone_spy.calls[2].depth == 3
    assert len(clone_spy.calls[2].args) == 1
    assert repr(clone_spy.calls[2].args[0]) == "dim('*').pd.head(2)"
    assert clone_spy.calls[2].kwargs == {'plot': False}


def test_interactive_pandas_series_method_kwargs(series, clone_spy):
    si = Interactive(series)
    si = si.head(n=2)

    assert isinstance(si, Interactive)
    assert isinstance(si._current, pd.DataFrame)
    pd.testing.assert_series_equal(si._current.A, series.head(2))
    assert si._obj is series
    assert repr(si._transform) == "dim('*').pd.head(n=2)"
    assert si._depth == 3
    assert si._method is None

    assert clone_spy.count == 3

    # _clone in _resolve_accessor in __getattribute__(name='head')
    assert clone_spy.calls[0].depth == 1
    assert not clone_spy.calls[0].args
    assert clone_spy.calls[0].kwargs == {'copy': True}

    # 1st _clone(copy=True) in __call__
    assert clone_spy.calls[1].depth == 2
    assert not clone_spy.calls[1].args
    assert clone_spy.calls[1].kwargs == {'copy': True}

    # 2nd _clone in __call__
    assert clone_spy.calls[2].depth == 3
    assert len(clone_spy.calls[2].args) == 1
    assert repr(clone_spy.calls[2].args[0]) == "dim('*').pd.head(n=2)"
    assert clone_spy.calls[2].kwargs == {'plot': False}


def test_interactive_pandas_series_method_not_called(series, clone_spy):
    si = Interactive(series)
    si = si.head

    assert isinstance(si, Interactive)
    assert isinstance(si._current, pd.DataFrame)
    pd.testing.assert_series_equal(si._current.A, si._obj)
    assert si._obj is series
    assert repr(si._transform) == "dim('*')"
    assert si._depth == 1
    assert si._method == 'head'

    assert clone_spy.count == 1

    # _clone in _resolve_accessor in __getattribute__(name='head')
    assert clone_spy.calls[0].depth == 1
    assert not clone_spy.calls[0].args
    assert clone_spy.calls[0].kwargs == {'copy': True}


def test_interactive_pandas_frame_attrib(df, clone_spy):
    dfi = Interactive(df)
    dfi = dfi.A

    assert isinstance(dfi, Interactive)
    assert isinstance(dfi._current, pd.DataFrame)
    pd.testing.assert_frame_equal(dfi._current, dfi._obj)
    assert dfi._obj is df
    assert repr(dfi._transform) == "dim('*')"
    assert dfi._depth == 1
    assert dfi._method == 'A'

    assert clone_spy.count == 1

    # _clone in _resolve_accessor in __getattribute__(name='A')
    assert clone_spy.calls[0].depth == 1
    assert not clone_spy.calls[0].args
    assert clone_spy.calls[0].kwargs == {'copy': True}


def test_interactive_pandas_series_operator_and_method(series, clone_spy):
    si = Interactive(series)

    si = (si + 2).head(2)

    assert isinstance(si, Interactive)
    assert isinstance(si._current, pd.DataFrame)
    pd.testing.assert_series_equal(si._current.A, (series + 2).head(2))
    assert si._obj is series
    assert repr(si._transform) == "(dim('*').pd+2).head(2)"
    assert si._depth == 5
    assert si._method is None

    assert clone_spy.count == 5

    # _clone(copy=True) in _resolve_accessor in _apply_operator
    assert clone_spy.calls[0].depth == 1
    assert not clone_spy.calls[0].args
    assert clone_spy.calls[0].kwargs == {'copy': True}

    # _clone in _apply_operator
    assert clone_spy.calls[1].depth == 2
    assert len(clone_spy.calls[1].args) == 1
    assert repr(clone_spy.calls[1].args[0]) == "dim('*').pd+2"
    assert not clone_spy.calls[1].kwargs

    # _clone in _resolve_accessor in __getattribute__(name='head')
    assert clone_spy.calls[2].depth == 3
    assert not clone_spy.calls[2].args
    assert clone_spy.calls[2].kwargs == {'copy': True}

    # 1st _clone(copy=True) in __call__
    assert clone_spy.calls[3].depth == 4
    assert not clone_spy.calls[3].args
    assert clone_spy.calls[3].kwargs == {'copy': True}

    # 2nd _clone in __call__
    assert clone_spy.calls[4].depth == 5
    assert len(clone_spy.calls[4].args) == 1
    assert repr(clone_spy.calls[4].args[0]) == "(dim('*').pd+2).head(2)"
    assert clone_spy.calls[4].kwargs == {'plot': False}


def test_interactive_pandas_series_operator_widget(series):
    w = pn.widgets.FloatSlider(value=2.0, start=1.0, end=5.0)

    si = Interactive(series)

    si = si + w

    assert isinstance(si, Interactive)
    assert isinstance(si._current, pd.DataFrame)
    pd.testing.assert_series_equal(si._current.A, series + w.value)
    assert si._obj is series
    assert repr(si._transform) == "dim('*').pd+FloatSlider(end=5.0, start=1.0, value=2.0)"
    assert si._depth == 2
    assert si._method is None

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
    assert si._method is None

    assert len(si._params) == 1
    assert si._params[0] is w.param.value


def test_interactive_pandas_series_operator_and_method_widget(series):
    w1 = pn.widgets.FloatSlider(value=2.0, start=1.0, end=5.0)
    w2 = pn.widgets.IntSlider(value=2, start=1, end=5)

    si = Interactive(series)

    si = (si + w1).head(w2)

    assert isinstance(si, Interactive)
    assert isinstance(si._current, pd.DataFrame)
    pd.testing.assert_series_equal(si._current.A, (series + w1.value).head(w2.value))
    assert si._obj is series
    assert (
        repr(si._transform)
        == "(dim('*').pd+FloatSlider(end=5.0, start=1.0, value=2.0)).head(IntSlider(end=5, start=1, value=2))"
    )
    assert si._depth == 5
    assert si._method is None

    assert len(si._params) == 2
    assert si._params[0] is w1.param.value
    assert si._params[1] is w2.param.value


def test_interactive_pandas_series_operator_ipywidgets(series):
    ipywidgets = pytest.importorskip('ipywidgets')

    w = ipywidgets.FloatSlider(value=2.0, min=1.0, max=5.0)

    si = Interactive(series)

    si = si + w

    assert isinstance(si, Interactive)
    assert isinstance(si._current, pd.DataFrame)
    pd.testing.assert_series_equal(si._current.A, series + w.value)
    assert si._obj is series
    assert repr(si._transform) == "dim('*').pd+FloatSlider(value=2.0, max=5.0, min=1.0)"
    assert si._depth == 2
    assert si._method is None

    # TODO: Isn't that a bug?
    assert len(si._params) == 0

    widgets = si.widgets()

    assert isinstance(widgets, pn.Column)
    assert len(widgets) == 1
    assert isinstance(widgets[0], pn.pane.IPyWidget)
    assert widgets[0].object is w


def test_interactive_pandas_series_operator_out_widgets(series):
    w = pn.widgets.FloatSlider(value=2.0, start=1.0, end=5.0)
    si = Interactive(series)
    si = si + w

    widgets = si.widgets()

    assert isinstance(widgets, pn.Column)
    assert len(widgets) == 1
    assert widgets[0] is w


def test_interactive_pandas_series_method_out_widgets(series):
    w = pn.widgets.IntSlider(value=2, start=1, end=5)
    si = Interactive(series)
    si = si.head(w)

    widgets = si.widgets()

    assert isinstance(widgets, pn.Column)
    assert len(widgets) == 1
    assert widgets[0] is w


def test_interactive_pandas_series_operator_and_method_out_widgets(series):
    w1 = pn.widgets.FloatSlider(value=2.0, start=1.0, end=5.0)
    w2 = pn.widgets.IntSlider(value=2, start=1, end=5)
    si = Interactive(series)

    si = (si + w1).head(w2)

    widgets = si.widgets()

    assert isinstance(widgets, pn.Column)
    assert len(widgets) == 2
    assert widgets[0] is w1
    assert widgets[1] is w2


def test_interactive_pandas_frame_bind_out_widgets(df):
    select = pn.widgets.Select(options=list(df.columns))

    def sel_col(col):
        return df[col]

    dfi = Interactive(bind(sel_col, select))

    widgets = dfi.widgets()

    assert isinstance(widgets, pn.Column)
    assert len(widgets) == 1
    assert widgets[0] is select


def test_interactive_pandas_frame_bind_operator_out_widgets(df):
    select = pn.widgets.Select(value='A', options=list(df.columns))

    def sel_col(col):
        return df[col]

    dfi = Interactive(bind(sel_col, select))

    w = pn.widgets.FloatSlider(value=2.0, start=1.0, end=5.0)
    dfi = dfi + w

    widgets = dfi.widgets()

    assert isinstance(widgets, pn.Column)
    assert len(widgets) == 2
    assert widgets[0] is select
    assert widgets[1] is w


def test_interactive_reevaluate_uses_cached_value(series):
    w = pn.widgets.FloatSlider(value=2.0, start=1.0, end=5.0)
    si = Interactive(series)
    si = si + w

    w.value = 3.0
    assert repr(si._transform) == "dim('*').pd+FloatSlider(end=5.0, start=1.0, value=3.0)"

    assert si._callback().object is si._callback().object


def test_interactive_pandas_series_operator_widget_update(series):
    w = pn.widgets.FloatSlider(value=2.0, start=1.0, end=5.0)
    si = Interactive(series)
    si = si + w

    w.value = 3.0
    assert repr(si._transform) == "dim('*').pd+FloatSlider(end=5.0, start=1.0, value=3.0)"

    out = si._callback()
    assert out.object is si.eval()
    assert isinstance(out, pn.pane.DataFrame)
    pd.testing.assert_series_equal(out.object.A, series + 3.0)


def test_interactive_pandas_series_method_widget_update(series):
    w = pn.widgets.IntSlider(value=2, start=1, end=5)
    si = Interactive(series)
    si = si.head(w)

    w.value = 3
    assert repr(si._transform) == "dim('*').pd.head(IntSlider(end=5, start=1, value=3))"

    out = si._callback()
    assert out.object is si.eval()
    assert isinstance(out, pn.pane.DataFrame)
    pd.testing.assert_series_equal(out.object.A, series.head(3))


def test_interactive_pandas_series_operator_and_method_widget_update(series):
    w1 = pn.widgets.FloatSlider(value=2.0, start=1.0, end=5.0)
    w2 = pn.widgets.IntSlider(value=2, start=1, end=5)
    si = Interactive(series)
    si = (si + w1).head(w2)

    w1.value = 3.0
    w2.value = 3

    assert (
        repr(si._transform)
        == "(dim('*').pd+FloatSlider(end=5.0, start=1.0, value=3.0)).head(IntSlider(end=5, start=1, value=3))"
    )

    out = si._callback()
    assert out.object is si.eval()
    assert isinstance(out, pn.pane.DataFrame)
    pd.testing.assert_series_equal(out.object.A, (series + 3.0).head(3))


def test_interactive_pandas_frame_loc(df):
    dfi = Interactive(df)

    dfi = dfi.loc[:, 'A']

    assert isinstance(dfi, Interactive)

    assert dfi._obj is df
    assert isinstance(dfi._current, pd.Series)
    pd.testing.assert_series_equal(dfi._current, df.loc[:, 'A'])
    assert repr(dfi._transform) == "dim('*').pd.loc, getitem, (slice(None, None, None), 'A')"
    assert dfi._depth == 3
    assert dfi._method is None


def test_interactive_pandas_frame_filtering(df, clone_spy):
    dfi = Interactive(df)

    dfi = dfi[dfi.A > 1]

    assert isinstance(dfi, Interactive)

    assert dfi._obj is df
    assert isinstance(dfi._current, pd.DataFrame)
    pd.testing.assert_frame_equal(dfi._current, df[df.A > 1])
    assert repr(dfi._transform) == "dim('*', getitem, dim('*').pd.A)>1"
    # The depth of that Interactive instance is 2 because the last part of
    # the chain executed, i.e. dfi[], leads to two clones being created,
    # incrementing the _depth up to 2.
    assert dfi._depth == 2
    assert dfi._method is None

    assert clone_spy.count == 5

    # _clone(True) in _resolve_accessor in __getattribute__(name='A')
    assert clone_spy.calls[0].depth == 1
    assert not clone_spy.calls[0].args
    assert clone_spy.calls[0].kwargs == {'copy': True}

    # _clone in _resolve_accessor in _apply_operator(__gt__)
    assert clone_spy.calls[1].depth == 2
    assert len(clone_spy.calls[1].args) == 1
    assert repr(clone_spy.calls[1].args[0]) == "dim('*').pd.A()"
    assert clone_spy.calls[1].kwargs == {'inherit_kwargs': {}}

    # _clone in _apply_operator(__gt__)
    assert clone_spy.calls[2].depth == 3
    assert len(clone_spy.calls[2].args) == 1
    assert repr(clone_spy.calls[2].args[0]) == "(dim('*').pd.A())>1"
    assert not clone_spy.calls[2].kwargs

    # _clone(True) in _resolve_accessor in _apply_operator(getitem)
    assert clone_spy.calls[3].depth == 1
    assert not clone_spy.calls[3].args
    assert clone_spy.calls[3].kwargs == {'copy': True}

    # _clone in _apply_operator(getitem)
    assert clone_spy.calls[4].depth == 2
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
    assert dfi._method is None

    assert clone_spy.count == 4

    # _clone(True) in _resolve_accessor in __getattribute__(name='A')
    assert clone_spy.calls[0].depth == 1
    assert not clone_spy.calls[0].args
    assert clone_spy.calls[0].kwargs == {'copy': True}

    # _clone(True) in _resolve_accessor in __getattribute__(name='max')
    assert clone_spy.calls[1].depth == 2
    assert len(clone_spy.calls[1].args) == 1
    assert repr(clone_spy.calls[1].args[0]) == "dim('*').pd.A()"
    assert clone_spy.calls[1].kwargs == {'inherit_kwargs': {}}

    # 1st _clone(copy=True) in __call__
    assert clone_spy.calls[2].depth == 3
    assert not clone_spy.calls[2].args
    assert clone_spy.calls[2].kwargs == {'copy': True}

    # 2nd _clone in __call__
    assert clone_spy.calls[3].depth == 4
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
    assert si._method is None

    # Equivalent to eval
    out = si._callback()

    assert isinstance(out, pd.Series)
    assert out.A == pytest.approx(series.max())


def test_interactive_xarray_dataarray_out_repr(dataarray):
    dai = Interactive(dataarray)

    assert isinstance(dai._current, xr.DataArray)
    assert dai._obj is dataarray
    assert repr(dai._transform) == "dim('air')"
    assert dai._depth == 0
    assert dai._method is None

    # Equivalent to eval
    out = dai._callback()

    assert isinstance(out, xr.DataArray)


def test_interactive_pandas_out_frame(series):
    si = Interactive(series)
    si = si.head(2)

    assert isinstance(si, Interactive)
    assert isinstance(si._current, pd.DataFrame)
    pd.testing.assert_series_equal(si._current.A, series.head(2))
    assert si._obj is series
    assert repr(si._transform) == "dim('*').pd.head(2)"
    assert si._depth == 3
    assert si._method is None

    # Equivalent to eval
    out = si._callback()

    assert isinstance(out, pn.pane.DataFrame)
    pd.testing.assert_frame_equal(out.object, si._current)


def test_interactive_pandas_out_frame_max_rows(series):
    si = Interactive(series, max_rows=5)
    si = si.head(2)

    # Equivalent to eval
    out = si._callback()

    assert isinstance(out, pn.pane.DataFrame)
    assert out.max_rows == 5


def test_interactive_pandas_out_frame_max_rows_accessor_called(series):
    si = series.interactive(max_rows=5)
    si = si.head(2)

    # Equivalent to eval
    out = si._callback()

    assert isinstance(out, pn.pane.DataFrame)
    assert out.max_rows == 5


def test_interactive_pandas_out_frame_kwargs(series):
    si = Interactive(series, width=111)
    si = si.head(2)

    # Equivalent to eval
    out = si._callback()

    assert isinstance(out, pn.pane.DataFrame)
    assert out.width == 111


def test_interactive_pandas_out_frame_kwargs_accessor_called(series):
    si = series.interactive(width=111)
    si = si.head(2)

    # Equivalent to eval
    out = si._callback()

    assert isinstance(out, pn.pane.DataFrame)
    assert out.width == 111


def test_interactive_pandas_out_frame_attrib(df):
    dfi = Interactive(df)
    dfi = dfi.A

    assert dfi._method == 'A'

    # Equivalent to eval
    out = dfi._callback()

    # In that case the default behavior is to return the object transformed
    # and to which _method is applied
    assert isinstance(out, pd.Series)
    pd.testing.assert_series_equal(df.A, out)


@pytest.mark.parametrize(
    'op',
    [
        '-',  # __neg__
        # Doesn't any of the supported data implement __not__?
        # e.g. `not series` raises an error.
        # 'not', # __not__
        '+',  # _pos__
    ],
)
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
    assert si._method is None


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
    assert si._method is None


@pytest.mark.parametrize(
    'op',
    [
        '+',  # __add__
        '&',  # __and__
        '/',  # __div__
        '==',  # __eq__
        '//',  # __floordiv__
        '>=',  # __ge__
        '>',  # __gt__
        '<=',  # __le__
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
    ],
)
def test_interactive_pandas_series_operator_binary(series, op):
    if op in ['&', '|']:
        series = pd.Series([True, False, True], name='A')
        val = True
    else:
        val = 2.0
    si = Interactive(series)
    si = eval(f'si {op} {val}')

    assert isinstance(si, Interactive)
    assert isinstance(si._current, pd.DataFrame)
    pd.testing.assert_series_equal(si._current.A, eval(f'series {op} {val}'))
    assert si._obj is series
    val_repr = '2.0' if isinstance(val, float) else 'True'
    assert repr(si._transform) == f"dim('*').pd{op}{val_repr}"
    assert si._depth == 2
    assert si._method is None


@pytest.mark.parametrize(
    'op',
    [
        '+',  # __radd__
        '&',  # __rand__
        '/',  # __rdiv__
        '//',  # __rfloordiv__
        # '<<',  # __rlshift__
        '%',  # __rmod__
        '*',  # __rmul__
        '|',  # __ror__
        '**',  # __rpow__
        # '>>',  # __rshift__
        '-',  # __rsub__
        '/',  # __rtruediv__
    ],
)
def test_interactive_pandas_series_operator_reverse_binary(op):
    if op in ['&', '|']:
        series = pd.Series([True, False, True], name='A')
        val = True
    else:
        series = pd.Series([1.0, 2.0, 3.0], name='A')
        val = 2.0
    si = Interactive(series)
    si = eval(f'{val} {op} si')

    assert isinstance(si, Interactive)
    assert isinstance(si._current, pd.DataFrame)
    pd.testing.assert_series_equal(si._current.A, eval(f'{val} {op} series'))
    assert si._obj is series
    val_repr = '2.0' if isinstance(val, float) else 'True'
    assert repr(si._transform) == f"{val_repr}{op}dim('*')"
    assert si._depth == 2
    assert si._method is None


def test_interactive_pandas_series_operator_abs(series):
    si = Interactive(series)
    si = abs(si)

    assert isinstance(si, Interactive)
    assert isinstance(si._current, pd.DataFrame)
    pd.testing.assert_series_equal(si._current.A, abs(series))
    assert si._obj is series
    assert repr(si._transform) == "absdim('*')"
    assert si._depth == 2
    assert si._method is None


def test_interactive_pandas_series_operator_round(series):
    si = Interactive(series)
    si = round(si)

    assert isinstance(si, Interactive)
    assert isinstance(si._current, pd.DataFrame)
    pd.testing.assert_series_equal(si._current.A, round(series))
    assert si._obj is series
    assert repr(si._transform) == "dim('*', round)"
    assert si._depth == 2
    assert si._method is None


def test_interactive_pandas_series_plot(series, clone_spy):
    si = Interactive(series)

    si = si.plot()

    assert isinstance(si, Interactive)
    assert isinstance(si._current, matplotlib.axes.Axes)
    assert si._obj is series
    assert "dim('*').pd.plot(ax=<function Interactive._get_ax_fn.<locals>.get_ax" in repr(
        si._transform
    )
    assert si._depth == 3
    assert si._method is None

    assert clone_spy.count == 3

    # _clone(True) in _resolve_accessor in __getattribute__(name='plot')
    assert clone_spy.calls[0].depth == 1
    assert not clone_spy.calls[0].args
    assert clone_spy.calls[0].kwargs == {'copy': True}

    # 1st _clone(copy=True) in __call__
    assert clone_spy.calls[1].depth == 2
    assert not clone_spy.calls[1].args
    assert clone_spy.calls[1].kwargs == {'copy': True}

    # 2nd _clone in __call__
    assert clone_spy.calls[2].depth == 3
    assert len(clone_spy.calls[2].args) == 1
    # Not the complete repr as the function doesn't have a nice repr,
    # its repr displays  the memory address.
    assert "dim('*').pd.plot(ax=<function Interactive._get_ax_fn.<locals>.get_ax" in repr(
        clone_spy.calls[2].args[0]
    )
    assert clone_spy.calls[2].kwargs == {'plot': True}

    assert not si._dmap
    assert isinstance(si._fig, matplotlib.figure.Figure)

    # Just test that it doesn't raise any error.
    si.output()


def test_interactive_pandas_series_plot_kind_attr(series, clone_spy):
    # TODO: Not checking the dim reprs in this test as that was
    # affecting the pipeline.
    si = Interactive(series)

    si = si.plot.line()

    assert isinstance(si, Interactive)
    assert isinstance(si._current, matplotlib.axes.Axes)
    assert si._obj is series
    # assert "dim('*').pd.plot).line(ax=<function Interactive._get_ax_fn.<locals>.get_ax" in repr(si._transform)
    assert si._depth == 4
    assert si._method is None

    assert clone_spy.count == 4

    # _clone(True) in _resolve_accessor in __getattribute__(name='plot')
    assert clone_spy.calls[0].depth == 1
    assert not clone_spy.calls[0].args
    assert clone_spy.calls[0].kwargs == {'copy': True}

    # _clone in _resolve_accessor in __getattribute__(name='line')
    assert clone_spy.calls[1].depth == 2
    assert len(clone_spy.calls[1].args) == 1
    # assert repr(clone_spy.calls[1].args[0]) == "dim('*').pd.plot()"
    assert len(clone_spy.calls[1].kwargs) == 1
    assert 'inherit_kwargs' in clone_spy.calls[1].kwargs
    assert 'ax' in clone_spy.calls[1].kwargs['inherit_kwargs']

    # 1st _clone(copy=True) in __call__
    assert clone_spy.calls[2].depth == 3
    assert not clone_spy.calls[2].args
    assert clone_spy.calls[2].kwargs == {'copy': True}

    # 2nd _clone in __call__
    assert clone_spy.calls[3].depth == 4
    assert len(clone_spy.calls[3].args) == 1
    # assert "(dim('*').pd.plot()).line(ax=<function Interactive._get_ax_fn.<locals>.get_ax" in repr(clone_spy.calls[3].args[0])
    # TODO: Looks like a bug, 'plot' should be True?
    assert clone_spy.calls[3].kwargs == {'plot': False}

    assert not si._dmap
    assert isinstance(si._fig, matplotlib.figure.Figure)

    # Just test that it doesn't raise any error.
    si.output()


def test_interactive_pandas_dir_no_type_change(df):
    dfi = Interactive(df)
    dfi = dfi.head()

    attrs = dir(dfi)

    assert all(col in attrs for col in list(df.columns))
    assert 'describe' in attrs


def test_interactive_pandas_dir_with_type_change(df):
    dfi = Interactive(df)
    dfi = dfi.head().A.head()

    attrs = dir(dfi)

    assert not any(col in attrs for col in list(df.columns))
    assert 'T' in attrs


@pytest.mark.xfail(
    reason='hvplot.util.check_library expects the obj to have __module__, which is not true for a float'
)
def test_interactive_pandas_dir_with_type_change_to_float(df):
    dfi = Interactive(df)
    dfi = dfi.head().A.max()

    attrs = dir(dfi)

    assert not any(col in attrs for col in list(df.columns))
    assert 'describe' not in attrs
    assert 'real' not in attrs


def test_interactive_pandas_dir_attrib(df):
    dfi = Interactive(df)
    dfi = dfi.head().A

    attrs = dir(dfi)

    assert not any(col in attrs for col in list(df.columns))
    assert 'T' in attrs


def test_interactive_pandas_layout_default_no_widgets(df):
    dfi = Interactive(df)
    dfi = dfi.head()

    assert dfi._center is False
    assert dfi._loc == 'top_left'

    layout = dfi.layout()

    assert isinstance(layout, pn.Row)
    assert len(layout) == 1


def test_interactive_pandas_layout_default_no_widgets_kwargs(df):
    dfi = Interactive(df)
    dfi = dfi.head()

    layout = dfi.layout(width=200)

    assert isinstance(layout, pn.Row)
    assert layout.width == 200


def test_interactive_pandas_layout_default_with_widgets_bk3(df):
    w = pn.widgets.IntSlider(value=2, start=1, end=5)
    dfi = Interactive(df)
    dfi = dfi.head(w)

    assert dfi._center is False
    assert dfi._loc == 'top_left'

    layout = dfi.layout()

    assert isinstance(layout, pn.Row)
    assert len(layout) == 1
    assert isinstance(layout[0], pn.Column)
    assert len(layout[0]) == 2
    assert isinstance(layout[0][0], pn.Column)
    assert isinstance(layout[0][1], pn.pane.PaneBase)
    assert len(layout[0][0]) == 1
    assert isinstance(layout[0][0][0], pn.widgets.IntSlider)


def test_interactive_pandas_eval(df):
    dfi = Interactive(df)
    dfi = dfi.head(2)

    pd.testing.assert_frame_equal(dfi.eval(), df.head(2))


def test_interactive_pandas_eval_attrib(df):
    dfi = Interactive(df)
    dfi = dfi.head(2).A

    pd.testing.assert_series_equal(dfi.eval(), df.head(2).A)


def test_interactive_pandas_eval_hvplot(df):
    dfi = Interactive(df)
    dfi = dfi.head(2).hvplot(y='A')

    evaled = dfi.eval()

    assert isinstance(evaled, hv.Curve)


def test_interactive_pandas_series_widget_value(series):
    w = pn.widgets.FloatSlider(value=2.0, start=1.0, end=5.0)

    si = Interactive(series)

    si = si + w.param.value

    assert isinstance(si, Interactive)
    assert isinstance(si._current, pd.DataFrame)
    pd.testing.assert_series_equal(si._current.A, series + w.value)
    assert si._obj is series
    assert "dim('*').pd+<param.parameters.Number object" in repr(si._transform)
    assert si._depth == 2
    assert si._method is None

    assert len(si._params) == 1
    assert si._params[0] is w.param.value

    widgets = si.widgets()

    assert isinstance(widgets, pn.Column)
    assert len(widgets) == 1
    assert widgets[0] is w


def test_clones_dont_reexecute_transforms():
    # Fixes https://github.com/holoviz/hvplot/issues/832
    df = pd.DataFrame()
    msgs = []

    def piped(df, msg):
        msgs.append(msg)
        return df

    df.interactive.pipe(piped, msg='1').pipe(piped, msg='2')

    assert len(msgs) == 3


def test_interactive_accept_non_str_columnar_data():
    df = pd.DataFrame(np.random.random((10, 2)))
    assert all(not isinstance(col, str) for col in df.columns)
    dfi = Interactive(df)

    w = pn.widgets.FloatSlider(start=0, end=1, step=0.05)

    # Column names converted as string so can no longer use dfi[1]
    dfi = dfi['1'] + w.param.value

    w.value = 0.5

    pytest.approx(dfi.eval().sum(), (df[1] + 0.5).sum())
