# Todo:
# [] Convert .css file to jinja template
# [] Improve styling (css) of tooltip: rounding, background color etc
# [] Change Fast mouse curser from crosshair to pointer (I think its much more modern)
# [] Get the toolbar to autohide via css instead of plot.toolbar.autohide = True which does not work
# [] Figure out if some kind of (horizontal) grid should be shown in the background.
# [] Go over the FastStyle Bokeh Theme once again comparing it to existing Bokeh Themes, to other
# themes from Matplotlib, Seaborn and Plotly. Comparing it to .js themes from chart.js, HighCharts and Tableau.
# Minimize the amount of custom css
# Change away from using scientific notation as default for axis labels. I have never seen that used in enterprise.
# [] realign with Panel FastTemplate FastStyle

import pathlib

import holoviews as hv
import panel as pn
import param
from bokeh.events import DoubleTap
from bokeh.models import CustomJS
from bokeh.sampledata.autompg import autompg_clean as df
from bokeh.themes.theme import Theme
from holoviews import opts

import hvplot.pandas

CSS_ROOT = pathlib.Path(__file__).parent

BOKEH_FAST_CSS = (CSS_ROOT/"theme_bokeh_fast.css").read_text()

class FastStyle(param.Parameterized):
    """
    The FastStyle class provides the different colors and icons used
    to style the Fast Templates.
    """

    accent_foreground_active = param.String(default="#0072B5")
    background_color = param.String(default="#ffffff")
    neutral_color = param.String(default="#000000")
    neutral_fill_card_rest = param.String(default="#F7F7F7")
    neutral_focus = param.String(default="#888888")
    neutral_foreground_rest = param.String(default="#2B2B2B")

    font = param.String(default="Open Sans, sans-serif")

    corner_radius = param.Integer(0)

    active_tools = param.List(default=["pan", "wheel_zoom"])
    hooks = param.List()
    cmap = param.String('Blues')

    def __init__(self, **params):
        super().__init__(**params)

        self.hooks = [self.bokeh_css]       

    @property
    def bokeh_theme(self):
        """Returns a custom bokeh theme based on the style parameters
        Returns:
            Dict: A Bokeh Theme
        """

        return Theme(
            json={
                "attrs": {
                    "Figure": {
                        "background_fill_color": self.background_color,
                        "border_fill_color": self.background_color,
                        "border_fill_alpha": 1,
                        "outline_line_color": self.neutral_focus,
                        "outline_line_alpha": 0.5,
                        "outline_line_width": 1,
                    },
                    "Grid": {"grid_line_color": self.neutral_focus, "grid_line_alpha": 0.25},
                    "Axis": {
                        "major_tick_line_alpha": 0.25,
                        "major_tick_line_color": self.neutral_foreground_rest,
                        "minor_tick_line_alpha": 0,
                        "minor_tick_line_color": self.neutral_foreground_rest,
                        "axis_line_alpha": 0.0,
                        "axis_line_color": self.neutral_foreground_rest,
                        "major_label_text_color": self.neutral_foreground_rest,
                        "major_label_text_font": self.font,
                        # Should be added back when bokeh 2.3.3 is released and https://github.com/bokeh/bokeh/issues/11110 fixed
                        # "major_label_text_font_size": "1.025em",
                        "axis_label_standoff": 10,
                        "axis_label_text_color": self.neutral_foreground_rest,
                        "axis_label_text_font": self.font,
                        "axis_label_text_font_size": "1.25em",
                        "axis_label_text_font_style": "normal",
                    },
                    "Legend": {
                        "spacing": 8,
                        "glyph_width": 15,
                        "label_standoff": 8,
                        "label_text_color": self.neutral_foreground_rest,
                        "label_text_font": self.font,
                        "label_text_font_size": "1.025em",
                        "border_line_alpha": 0.5,
                        "border_line_color": self.neutral_focus,
                        "background_fill_alpha": 0.25,
                        "background_fill_color": self.neutral_fill_card_rest,
                    },
                    "ColorBar": {
                        "background_fill_color": self.background_color,
                        "title_text_color": self.neutral_foreground_rest,
                        "title_text_font": self.font,
                        "title_text_font_size": "1.025em",
                        "title_text_font_style": "normal",
                        "major_label_text_color": self.neutral_foreground_rest,
                        "major_label_text_font": self.font,
                        "major_label_text_font_size": "1.025em",
                        "major_tick_line_alpha": 0,
                        "bar_line_alpha": 0,
                    },
                    "Title": {
                        "text_color": self.neutral_foreground_rest,
                        "text_font": self.font,
                        "text_font_size": "1.15em",
                    },
                }
            }
        )

    @property
    def bokeh_css(self):
        return BOKEH_FAST_CSS.replace(
            "var(--body-font)", self.font
            ).replace(
            "var(--accent-foreground-active)", self.accent_foreground_active
            ).replace(
            "var(--neutral-foreground-rest)", self.neutral_foreground_rest
            ).replace(
            "calc(var(--corner-radius) * 1px)", "2px"
            ).replace(
            "var(--neutral-fill-stealth-hover)", self.neutral_fill_card_rest
            )

    def bokeh_hook(self, plot, element):
        plot = plot.handles["plot"]
        plot.toolbar.autohide = True
        plot.js_on_event(DoubleTap, CustomJS(args=dict(p=plot), code="p.reset.emit()"))
        plot.toolbar_location="above"

class FastDarkStyle(FastStyle):
    background_color=param.String("#181818")
    neutral_fill_card_rest=param.String("#414141")
    neutral_focus=param.String("#717171")
    neutral_foreground_rest=param.String("#e5e5e5")

THEMES = {
    "fast": FastStyle,
    "fast-dark": FastDarkStyle,
}



def get_theme(theme="fast", color=None, cmap=None, font=None):
    theme = THEMES[theme]()
    # Rename accent to color etc
    if color: 
        theme.accent_foreground_active = color
    if cmap:
        theme.cmap = cmap
    if font:
        theme.font = font
    
    return theme

# Todo: Figure out we should supports named themes that can be applied across all backends. Or just individual themes for each backend

def _configure_bokeh_theme(theme):
    hv.renderer("bokeh").theme = theme.bokeh_theme
    # Todo: Set default opts across all `kind`s of plots
    opts.defaults(
        opts.Bivariate(active_tools=theme.active_tools, hooks=[theme.bokeh_hook])
    )

# Todo: Figure out if more arguments are needed
def hvplot_extension(backend="bokeh", theme="fast", color=None, cmap=None, font=None):
    """Configures hvplot

    Args:
        backend (str, optional): The name of the default backend. One of 'bokeh', 'matplotlib' or 'plotly'. 
            Defaults to 'bokeh'
        theme (str, optional): The name of the default theme. One of 'fast' and 'fast-dark'. Defaults to 'fast'.
        color (_type_, optional): _description_. Defaults to None.
        cmap (_type_, optional): _description_. Defaults to None.
        font (_type_, optional): _description_. Defaults to None.
    """
    hv.extension(backend)
    
    theme = get_theme(theme, color, cmap, font)
    
    _configure_bokeh_theme(theme)
    # Todo: configure matplotlib and plotly theme
