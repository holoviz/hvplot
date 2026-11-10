import holoviews as hv
import pandas as pd
import pytest
from holoviews import Store

from hvplot.converter import HoloViewsConverter
from hvplot.util import _HV_GE_1_24_0

pytestmark = [
    pytest.mark.usefixtures('hvplot_pandas'),
    pytest.mark.skipif(not _HV_GE_1_24_0, reason='donut requires HoloViews >= 1.24.0'),
]

df = pd.DataFrame(
    {
        'expense': ['Rent', 'Food', 'Travel', 'Misc'],
        'amount': [1200, 400, 300, 100],
        'budget': [1300, 350, 200, 150],
        'year': [2024, 2024, 2025, 2025],
    }
)


def plot_opts(element, backend='bokeh'):
    return Store.lookup_options(backend, element, 'plot').kwargs


def test_x(tabular_lib):
    plot = tabular_lib(df).hvplot.donut(x='expense', y='amount')
    assert isinstance(plot, HoloViewsConverter._kind_mapping['donut'])
    assert plot.kdims == ['expense']


def test_y():
    plot = df.hvplot.donut(x='expense', y='amount')
    assert plot.vdims == ['amount']


def test_y_multiple_laid_out():
    plot = df.hvplot.donut(x='expense', y=['amount', 'budget'])
    assert isinstance(plot, hv.NdLayout)
    assert list(plot.keys()) == ['amount', 'budget']


def test_by_laid_out():
    plot = df.hvplot.donut(x='expense', y='amount', by='year')
    assert isinstance(plot, hv.NdLayout)


def test_inner_radius_default():
    plot = df.hvplot.donut(x='expense', y='amount')
    assert plot_opts(plot)['inner_radius'] == 0.5


def test_inner_radius_default_kind():
    plot = df.hvplot(kind='donut', x='expense', y='amount')
    assert plot_opts(plot)['inner_radius'] == 0.5


def test_inner_radius():
    plot = df.hvplot.donut(x='expense', y='amount', inner_radius=0.7)
    assert plot_opts(plot)['inner_radius'] == 0.7


def test_show_labels():
    plot = df.hvplot.donut(x='expense', y='amount', show_labels=True)
    assert plot_opts(plot)['show_labels'] is True


def test_center_label():
    plot = df.hvplot.donut(x='expense', y='amount', center_label='Total: {total:,.0f}')
    assert plot_opts(plot)['center_label'] == 'Total: {total:,.0f}'


def test_legend_right():
    plot = df.hvplot.donut(x='expense', y='amount')
    assert plot_opts(plot)['legend_position'] == 'right'


@pytest.mark.parametrize('backend', ['bokeh', 'matplotlib'], indirect=True)
def test_backends(backend):
    plot = df.hvplot.donut(x='expense', y='amount', inner_radius=0.6)
    assert plot_opts(plot, backend)['inner_radius'] == 0.6
