import holoviews as hv
import pandas as pd
import pytest
from holoviews import Store

from hvplot.util import _HV_GE_1_23_0

pytestmark = [
    pytest.mark.usefixtures('hvplot_pandas'),
    pytest.mark.skipif(not _HV_GE_1_23_0, reason='Waterfall requires HoloViews >= 1.23.0'),
]

if _HV_GE_1_23_0:
    from holoviews.element import Waterfall

df = pd.DataFrame(
    {
        'step': ['Revenue', 'Costs', 'Taxes', 'Other'],
        'change': [1000, -400, -150, 50],
        'forecast': [900, -350, -100, 20],
        'region': ['EU', 'EU', 'US', 'US'],
    }
)


def plot_opts(element):
    return Store.lookup_options('bokeh', element, 'plot').kwargs


def test_x(tabular_lib):
    plot = tabular_lib(df).hvplot.waterfall(x='step', y='change')
    assert isinstance(plot, Waterfall)
    assert plot.kdims == ['step']
    assert list(plot.dimension_values('step')) == list(df['step'])


def test_x_default_index():
    plot = df.set_index('step').hvplot.waterfall(y='change')
    assert plot.kdims == ['step']


def test_y(tabular_lib):
    plot = tabular_lib(df).hvplot.waterfall(x='step', y='change')
    assert plot.vdims == ['change']
    assert list(plot.dimension_values('change')) == list(df['change'])


def test_y_default_first_numeric_column():
    plot = df.hvplot.waterfall(x='step')
    assert plot.vdims == ['change']


def test_y_multiple_laid_out():
    plot = df.hvplot.waterfall(x='step', y=['change', 'forecast'])
    assert isinstance(plot, hv.NdLayout)
    assert list(plot.keys()) == ['change', 'forecast']
    assert all(isinstance(el, Waterfall) for el in plot)


def test_series():
    plot = df.set_index('step')['change'].hvplot.waterfall()
    assert isinstance(plot, Waterfall)
    assert plot.kdims == ['step']
    assert plot.vdims == ['change']


def test_by_laid_out():
    plot = df.hvplot.waterfall(x='step', y='change', by='region')
    assert isinstance(plot, hv.NdLayout)
    assert list(plot.keys()) == ['EU', 'US']
    assert list(plot['US'].dimension_values('step')) == ['Taxes', 'Other']


def test_show_total():
    plot = df.hvplot.waterfall(x='step', y='change', show_total=False)
    assert plot_opts(plot)['show_total'] is False


def test_total_label():
    plot = df.hvplot.waterfall(x='step', y='change', total_label='Net')
    assert plot_opts(plot)['total_label'] == 'Net'


def test_positive_color():
    plot = df.hvplot.waterfall(x='step', y='change', positive_color='blue')
    assert plot_opts(plot)['positive_color'] == 'blue'


def test_negative_color():
    plot = df.hvplot.waterfall(x='step', y='change', negative_color='orange')
    assert plot_opts(plot)['negative_color'] == 'orange'


def test_start_color():
    plot = df.hvplot.waterfall(x='step', y='change', start_color=None)
    assert plot_opts(plot)['start_color'] is None


def test_total_color():
    plot = df.hvplot.waterfall(x='step', y='change', total_color='black')
    assert plot_opts(plot)['total_color'] == 'black'


def test_show_connectors():
    plot = df.hvplot.waterfall(x='step', y='change', show_connectors=False)
    assert plot_opts(plot)['show_connectors'] is False


def test_invert():
    plot = df.hvplot.waterfall(x='step', y='change', invert=True)
    assert plot_opts(plot)['invert_axes'] is True


@pytest.mark.parametrize('backend', ['bokeh', 'matplotlib'], indirect=True)
def test_render(backend):
    plot = df.hvplot.waterfall(x='step', y='change', total_label='Net')
    hv.render(plot, backend=backend)
