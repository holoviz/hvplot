"""
Tests for panel widgets and param objects as arguments
"""

from unittest import TestCase

import panel as pn

from hvplot.util import process_xarray  # noqa


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
        import hvplot.pandas  # noqa
        from bokeh.sampledata.iris import flowers

        self.flowers = flowers
        self.cols = list(self.flowers.columns[:-1])

    def test_using_explicit_widgets_works(self):
        x = pn.widgets.Select(name='x', value='sepal_length', options=self.cols)
        y = pn.widgets.Select(name='y', value='sepal_width', options=self.cols)
        kind = pn.widgets.Select(name='kind', value='scatter', options=['bivariate', 'scatter'])
        by_species = pn.widgets.Checkbox(name='By species')
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
        x = pn.widgets.Select(name='x', value='sepal_length', options=self.cols)
        y = pn.widgets.Select(name='y', value='sepal_width', options=self.cols)

        pane = self.flowers.hvplot(x, y, groupby='species')
        assert isinstance(pane, pn.param.ParamFunction)
