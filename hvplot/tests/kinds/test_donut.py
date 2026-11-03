import holoviews as hv
import pandas as pd
import pytest
from holoviews import Store

from hvplot.util import _HV_GE_1_23_0

pytestmark = [
    pytest.mark.usefixtures('hvplot_pandas'),
    pytest.mark.skipif(not _HV_GE_1_23_0, reason='Donut requires HoloViews >= 1.23.0'),
]

if _HV_GE_1_23_0:
    from holoviews.element import Donut

df = pd.DataFrame(
    {
        'expense': ['Rent', 'Food', 'Travel', 'Misc'],
        'amount': [1200, 400, 300, 100],
        'budget': [1300, 350, 200, 150],
        'year': [2024, 2024, 2025, 2025],
    }
)


def plot_opts(element):
    return Store.lookup_options('bokeh', element, 'plot').kwargs


def test_x(tabular_lib):
    plot = tabular_lib(df).hvplot.donut(x='expense', y='amount')
    assert isinstance(plot, Donut)
    assert plot.kdims == ['expense']
    assert list(plot.dimension_values('expense')) == list(df['expense'])


def test_x_default_index():
    plot = df.set_index('expense').hvplot.donut(y='amount')
    assert plot.kdims == ['expense']


def test_y(tabular_lib):
    plot = tabular_lib(df).hvplot.donut(x='expense', y='amount')
    assert plot.vdims == ['amount']
    assert list(plot.dimension_values('amount')) == list(df['amount'])


def test_y_default_first_numeric_column():
    plot = df.hvplot.donut(x='expense')
    assert plot.vdims == ['amount']


def test_y_multiple_laid_out():
    plot = df.hvplot.donut(x='expense', y=['amount', 'budget'])
    assert isinstance(plot, hv.NdLayout)
    assert list(plot.keys()) == ['amount', 'budget']
    assert all(isinstance(el, Donut) for el in plot)


def test_series():
    plot = df.set_index('expense')['amount'].hvplot.donut()
    assert isinstance(plot, Donut)
    assert plot.kdims == ['expense']
    assert plot.vdims == ['amount']


def test_by_laid_out():
    plot = df.hvplot.donut(x='expense', y='amount', by='year')
    assert isinstance(plot, hv.NdLayout)
    assert list(plot.keys()) == [2024, 2025]
    assert list(plot[2024].dimension_values('expense')) == ['Rent', 'Food']


def test_inner_radius():
    plot = df.hvplot.donut(x='expense', y='amount', inner_radius=0)
    assert plot_opts(plot)['inner_radius'] == 0


def test_outer_radius():
    plot = df.hvplot.donut(x='expense', y='amount', outer_radius=0.9)
    assert plot_opts(plot)['outer_radius'] == 0.9


def test_start_angle():
    plot = df.hvplot.donut(x='expense', y='amount', start_angle=1.5)
    assert plot_opts(plot)['start_angle'] == 1.5


def test_show_labels():
    plot = df.hvplot.donut(x='expense', y='amount', show_labels='{expense}: {amount}')
    assert plot_opts(plot)['show_labels'] == '{expense}: {amount}'


def test_label_radius():
    plot = df.hvplot.donut(x='expense', y='amount', show_labels=True, label_radius=1.1)
    assert plot_opts(plot)['label_radius'] == 1.1


def test_center_label():
    plot = df.hvplot.donut(x='expense', y='amount', center_label='total')
    assert plot_opts(plot)['center_label'] == 'total'


def test_cmap():
    cmap = {'Rent': 'red', 'Food': 'green', 'Travel': 'blue', 'Misc': 'grey'}
    plot = df.hvplot.donut(x='expense', y='amount', cmap=cmap)
    assert Store.lookup_options('bokeh', plot, 'style').kwargs['cmap'] == cmap


def test_square_by_default():
    plot = df.hvplot.donut(x='expense', y='amount')
    opts = plot_opts(plot)
    assert opts['aspect'] == 1
    assert 'width' not in opts and 'height' not in opts


def test_width_sets_square_frame():
    plot = df.hvplot.donut(x='expense', y='amount', width=400)
    opts = plot_opts(plot)
    assert opts['aspect'] == 1
    assert opts['frame_width'] == 400


def test_width_and_height_respected():
    plot = df.hvplot.donut(x='expense', y='amount', width=400, height=200)
    opts = plot_opts(plot)
    assert opts['width'] == 400
    assert opts['height'] == 200
    assert 'aspect' not in opts


@pytest.mark.parametrize('backend', ['bokeh', 'matplotlib'], indirect=True)
def test_render(backend):
    plot = df.hvplot.donut(x='expense', y='amount', show_labels=True, center_label='total')
    hv.render(plot, backend=backend)
