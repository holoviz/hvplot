import holoviews as hv
import pandas as pd
import panel as pn
from holoviews import Store

import hvplot
from hvplot.interactive import Interactive


def test_post_patch_loads_extension():
    hvplot.post_patch('matplotlib')
    assert Store.current_backend == 'matplotlib'


def test_post_patch_check_loaded_skips_loaded_extension(monkeypatch):
    monkeypatch.setattr(hv.extension, '_loaded', True)
    hvplot.post_patch('matplotlib', check_loaded=True)
    assert Store.current_backend == 'bokeh'


def test_post_patch_check_loaded_loads_extension(monkeypatch):
    monkeypatch.setattr(hv.extension, '_loaded', False)
    hvplot.post_patch('matplotlib', check_loaded=True)
    assert Store.current_backend == 'matplotlib'


def test_bind():
    def double(x):
        return x * 2

    slider = pn.widgets.IntSlider(value=1, start=0, end=5)
    bound = hvplot.bind(double, slider)
    assert bound() == 2
    slider.value = 3
    assert bound() == 6


def test_bind_interactive():
    slider = pn.widgets.IntSlider(value=2, start=0, end=5)
    bound = hvplot.bind(lambda n: pd.DataFrame({'a': range(n)}), slider)
    dfi = bound.interactive()
    assert isinstance(dfi, Interactive)
    assert len(dfi.eval()) == 2
    slider.value = 4
    assert len(dfi.eval()) == 4


def test_module_extensions_patch_once(hvplot_pandas):
    from hvplot.pandas import patch

    assert 'hvplot.pandas' in hvplot._module_extensions
    accessor = vars(pd.DataFrame)['hvplot']
    # Patching again (e.g. re-importing in IPython) keeps the registered accessor.
    patch()
    assert vars(pd.DataFrame)['hvplot'] is accessor
