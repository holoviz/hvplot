# Todo: Convert to notebook one day
import panel as pn
from bokeh.sampledata.autompg import autompg_clean as df
from hvplot.theme import get_theme, hvplot_extension

THEME = "fast-dark" # "fast"
COLOR = "#f700a1"
CMAP = "Accent"

# Todo: refactor into hvplot.extension
hvplot_extension(theme=THEME, color=COLOR, cmap=CMAP)

# Todo: Figure out how to get rid of using get_theme
theme = get_theme(theme=THEME, color=COLOR, cmap=CMAP)

# Todo: Test all `kind`s of plots

# Todo: Figure out why cmap applied in hvplot_extension does not work
plot = df.hvplot.bivariate("accel", "mpg", cut=False, cmap=theme.cmap, responsive=True, filled=True)

# Todo: Figure out how to add css in hvPlot/ HoloViews directly
pn.config.raw_css.append(theme.bokeh_css)
pn.extension()
pn.panel(plot, sizing_mode="stretch_both").servable()


