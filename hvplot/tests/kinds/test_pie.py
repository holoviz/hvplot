import holoviews as hv
import pandas as pd
import pytest
from bokeh.models import CategoricalColorMapper, HoverTool
from holoviews import Store

from hvplot.converter import HoloViewsConverter
from hvplot.util import _HV_GE_1_24_0

pytestmark = [
    pytest.mark.usefixtures('hvplot_pandas'),
    pytest.mark.skipif(not _HV_GE_1_24_0, reason='pie requires HoloViews >= 1.24.0'),
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


def style_opts(element, backend='bokeh'):
    return Store.lookup_options(backend, element, 'style').kwargs


def test_x(tabular_lib):
    plot = tabular_lib(df).hvplot.pie(x='expense', y='amount')
    assert isinstance(plot, HoloViewsConverter._kind_mapping['pie'])
    assert plot.kdims == ['expense']
    assert list(plot.dimension_values('expense')) == list(df['expense'])


def test_x_default_index():
    plot = df.set_index('expense').hvplot.pie(y='amount')
    assert plot.kdims == ['expense']


def test_y(tabular_lib):
    plot = tabular_lib(df).hvplot.pie(x='expense', y='amount')
    assert plot.vdims == ['amount']
    assert list(plot.dimension_values('amount')) == list(df['amount'])


def test_y_default_numeric_column():
    plot = df[['expense', 'amount']].hvplot.pie(x='expense')
    assert plot.vdims == ['amount']


def test_y_multiple_laid_out():
    plot = df.hvplot.pie(x='expense', y=['amount', 'budget'])
    assert isinstance(plot, hv.NdLayout)
    assert list(plot.keys()) == ['amount', 'budget']
    assert [el.vdims for el in plot] == [['amount'], ['budget']]


def test_y_multiple_with_by_raises():
    with pytest.raises(ValueError, match='multiple y'):
        df.hvplot.pie(x='expense', y=['amount', 'budget'], by='year')


def test_series():
    plot = df.set_index('expense')['amount'].hvplot.pie()
    assert plot.kdims == ['expense']
    assert plot.vdims == ['amount']


def test_by_laid_out():
    plot = df.hvplot.pie(x='expense', y='amount', by='year')
    assert isinstance(plot, hv.NdLayout)
    assert list(plot.keys()) == [2024, 2025]
    assert list(plot[2025].dimension_values('expense')) == ['Travel', 'Misc']


def test_by_subplots_false_still_laid_out():
    plot = df.hvplot.pie(x='expense', y='amount', by='year', subplots=False)
    assert isinstance(plot, hv.NdLayout)


def test_groupby():
    plot = df.hvplot.pie(x='expense', y='amount', groupby='year', dynamic=False)
    assert isinstance(plot, hv.HoloMap)
    assert list(plot.keys()) == [2024, 2025]


by_colors_df = pd.DataFrame(
    {
        'expense': ['Rent', 'Food', 'Travel', 'Misc', 'Misc', 'Food'],
        'amount': [1200, 400, 300, 100, 50, 70],
        'year': [2024, 2024, 2024, 2024, 2025, 2025],
    }
)


def assert_one_color_per_category(color_by_category):
    for category, colors in color_by_category.items():
        assert len(set(colors)) == 1, f'{category} has several colors: {colors}'


def test_by_same_colors_bokeh():
    plot = by_colors_df.hvplot.pie(x='expense', y='amount', by='year')
    mappers = list(hv.render(plot).select({'type': CategoricalColorMapper}))
    colors = {}
    for mapper in mappers:
        for category, color in zip(mapper.factors, mapper.palette, strict=False):
            colors.setdefault(category, []).append(color)
    assert len(mappers) == 2
    assert_one_color_per_category(colors)


@pytest.mark.parametrize('backend', ['matplotlib'], indirect=True)
def test_by_same_colors_matplotlib(backend):
    plot = by_colors_df.hvplot.pie(x='expense', y='amount', by='year')
    colors = {}
    for ax in hv.render(plot, backend='matplotlib').axes:
        categories = [text.get_text() for text in ax.get_legend().get_texts()]
        for category, wedge in zip(categories, ax.patches, strict=True):
            colors.setdefault(category, []).append(wedge.get_facecolor())
    assert_one_color_per_category(colors)


def test_show_labels():
    plot = df.hvplot.pie(x='expense', y='amount', show_labels='{fraction:.0%}')
    assert plot_opts(plot)['show_labels'] == '{fraction:.0%}'


def test_no_hole():
    plot = df.hvplot.pie(x='expense', y='amount')
    assert plot_opts(plot)['inner_radius'] == 0


@pytest.mark.usefixtures('disable_param_warnings_as_exceptions')
def test_inner_radius_not_an_option(caplog):
    plot = df.hvplot.pie(x='expense', y='amount', inner_radius=0.5)
    assert plot_opts(plot)['inner_radius'] == 0
    assert 'inner_radius option not found for pie plot' in caplog.text


def test_round():
    plot = df.hvplot.pie(x='expense', y='amount')
    opts = plot_opts(plot)
    assert opts['data_aspect'] == 1
    assert 'width' not in opts and 'height' not in opts


# bokeh warns (expected) when data_aspect and width are both set.
@pytest.mark.usefixtures('disable_param_warnings_as_exceptions')
def test_width():
    plot = df.hvplot.pie(x='expense', y='amount', width=400)
    opts = plot_opts(plot)
    assert opts['data_aspect'] == 1
    assert opts['width'] == 400
    assert 'height' not in opts


def test_legend_right():
    plot = df.hvplot.pie(x='expense', y='amount')
    assert plot_opts(plot)['legend_position'] == 'right'


def test_legend_position():
    plot = df.hvplot.pie(x='expense', y='amount', legend='bottom')
    assert plot_opts(plot)['legend_position'] == 'bottom'


def test_cmap_default_categorical():
    plot = df.hvplot.pie(x='expense', y='amount')
    assert style_opts(plot)['cmap'] == HoloViewsConverter._default_cmaps['categorical']


def test_cmap():
    cmap = {'Rent': 'red', 'Food': 'green', 'Travel': 'blue', 'Misc': 'grey'}
    plot = df.hvplot.pie(x='expense', y='amount', cmap=cmap)
    assert style_opts(plot)['cmap'] == cmap


def test_hover_default():
    plot = df.hvplot.pie(x='expense', y='amount')
    hover_tools = [t for t in hv.render(plot).tools if isinstance(t, HoverTool)]
    assert len(hover_tools) == 1
    tooltips = dict(hover_tools[0].tooltips)
    assert '@{expense}' in tooltips.values()
    assert '@{amount}' in tooltips.values()


def test_hover_false():
    plot = df.hvplot.pie(x='expense', y='amount', hover=False)
    assert not [t for t in hv.render(plot).tools if isinstance(t, HoverTool)]


@pytest.mark.parametrize('backend', ['bokeh', 'matplotlib'], indirect=True)
def test_backends(backend):
    plot = df.hvplot.pie(x='expense', y='amount', show_labels=True)
    assert plot_opts(plot, backend)['inner_radius'] == 0
    assert style_opts(plot, backend)['cmap'] == HoloViewsConverter._default_cmaps['categorical']


def test_requires_holoviews_1_24(monkeypatch):
    monkeypatch.setattr('hvplot.converter._HV_GE_1_24_0', False)
    with pytest.raises(ImportError, match=r'HoloViews >= 1\.24\.0'):
        df.hvplot.pie(x='expense', y='amount')
