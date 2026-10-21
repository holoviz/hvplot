"""
Tests for panel widgets and param objects as arguments
"""

from unittest import TestCase

import holoviews as hv
import pandas as pd
import panel as pn
import pytest
from holoviews import Store

from hvplot.util import process_xarray  # noqa: F401


def look_for_class(panel, classname, items=None):
    """
    Descend a panel object and find any instances of the given class
    """
    if items is None:
        items = []
    if isinstance(panel, pn.layout.ListPanel):
        for p in panel:
            items = look_for_class(p, classname, items)
    elif isinstance(panel, classname):
        items.append(panel)
    return items


class TestPanelObjects(TestCase):
    def setUp(self):
        from bokeh.sampledata.iris import flowers

        import hvplot.pandas  # noqa: F401

        self.flowers = flowers
        self.cols = list(self.flowers.columns[:-1])

    def test_using_explicit_widgets_works(self):
        x = pn.widgets.Select(label='x', value='sepal_length', options=self.cols)
        y = pn.widgets.Select(label='y', value='sepal_width', options=self.cols)
        kind = pn.widgets.Select(label='kind', value='scatter', options=['bivariate', 'scatter'])
        by_species = pn.widgets.Checkbox(label='By species')
        color = pn.widgets.ColorPicker(value='#ff0000')

        @pn.depends(by_species.param.value, color.param.value)
        def by_species_fn(by_species, color):
            return 'species' if by_species else color

        self.flowers.hvplot(x, y=y, kind=kind.param.value, c=color)

    def test_casting_widgets_to_different_classes(self):
        pane = self.flowers.hvplot.scatter(
            groupby='species', legend='top_right', widgets={'species': pn.widgets.DiscreteSlider}
        )

        assert len(look_for_class(pane, pn.widgets.DiscreteSlider)) == 1

    def test_using_explicit_widgets_with_groupby_does_not_raise_error(self):
        x = pn.widgets.Select(label='x', value='sepal_length', options=self.cols)
        y = pn.widgets.Select(label='y', value='sepal_width', options=self.cols)

        pane = self.flowers.hvplot(x, y, groupby='species')
        assert isinstance(pane, pn.param.ParamFunction)


@pytest.fixture(scope='module')
def df():
    return pd.DataFrame(
        [[1, 2, 'A', 0.1], [3, 4, 'B', 0.2], [5, 6, 'C', 0.3]],
        columns=['x', 'y', 'category', 'number'],
    )


@pytest.mark.usefixtures('hvplot_pandas')
class TestOptions:
    def test_hvplot_defaults(self, df, backend):
        plot = df.hvplot.scatter('x', 'y', c='category')
        opts = Store.lookup_options(backend, plot, 'plot')
        if backend == 'bokeh':
            assert opts.kwargs['height'] == 300
            assert opts.kwargs['width'] == 700
        elif backend == 'matplotlib':
            assert opts.kwargs['aspect'] == pytest.approx(2.333333)
            assert opts.kwargs['fig_size'] == pytest.approx(233.333333)
        if backend == 'bokeh':
            assert opts.kwargs['responsive'] is False
            assert opts.kwargs['shared_axes'] is True
            # legend_position shouldn't only be for Bokeh
            assert opts.kwargs['legend_position'] == 'right'
        assert opts.kwargs['show_grid'] is False
        assert opts.kwargs['show_legend'] is True
        assert opts.kwargs['logx'] is False
        assert opts.kwargs['logy'] is False
        assert opts.kwargs.get('logz') is None

    def test_holoviews_defined_default_opts(self, df, backend):
        if backend != 'bokeh':
            pytest.xfail(f'default opts not supported w/ {backend}')

        hv.opts.defaults(hv.opts.Scatter(height=400, width=900, show_grid=True))
        plot = df.hvplot.scatter('x', 'y', c='category')
        opts = Store.lookup_options(backend, plot, 'plot')
        # legend_position shouldn't apply only to bokeh
        if backend == 'bokeh':
            assert opts.kwargs['legend_position'] == 'right'
        assert opts.kwargs['show_grid'] is True
        assert opts.kwargs['height'] == 400
        assert opts.kwargs['width'] == 900

    def test_holoviews_defined_default_opts_overwritten_in_call(self, df, backend):
        if backend != 'bokeh':
            pytest.xfail(f'default opts not supported w/ {backend}')

        hv.opts.defaults(hv.opts.Scatter(height=400, width=900, show_grid=True))
        plot = df.hvplot.scatter('x', 'y', c='category', width=300, legend='left')
        opts = Store.lookup_options(backend, plot, 'plot')
        # legend_position shouldn't apply only to bokeh
        if backend == 'bokeh':
            assert opts.kwargs['legend_position'] == 'left'
        assert opts.kwargs['show_grid'] is True
        assert opts.kwargs['height'] == 400
        assert opts.kwargs['width'] == 300

    def test_holoviews_defined_default_opts_are_not_mutable(self, df, backend):
        if backend != 'bokeh':
            pytest.xfail(f'default opts not supported w/ {backend}')

        hv.opts.defaults(hv.opts.Scatter(tools=['tap']))
        plot = df.hvplot.scatter('x', 'y', c='category')
        opts = Store.lookup_options(backend, plot, 'plot')
        assert opts.kwargs['tools'] == ['tap', 'hover']
        default_opts = Store.options(backend=backend)['Scatter'].groups['plot'].options
        assert default_opts['tools'] == ['tap']
