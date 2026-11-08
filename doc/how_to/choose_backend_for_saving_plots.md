# How to Choose a Backend for Saving Plots

hvPlot can render plots with Bokeh (the default, interactive) or Matplotlib (static, well suited to batch jobs). When your goal is to save plots to files, pick the backend based on what you will do with them.

## Use Bokeh for interactive plots

Choose Bokeh when you need to interact with the plot and explore the data: zooming, panning, hovering, toggling legend entries. Bokeh is far superior for this, and saved as HTML files, Bokeh plots stay fully interactive and can be opened in any web browser.

For a one-off static snapshot, no code is needed: use the Save button in the plot toolbar to download a PNG.

Bokeh can also export PNG images programmatically, but this requires a headless browser (Playwright) and is slower than Matplotlib, so it is better suited to the occasional snapshot than to batch jobs.

See [How to Save Bokeh Plots](save_bokeh_plots.ipynb).

## Use Matplotlib for static images

Choose Matplotlib when:

- You only need a static image (PNG, PDF, SVG) in the end, for example for a paper, a report or a slide, and you don't need to explore the data interactively.
- You run batch jobs or simulations, in scripts or notebooks, that save many plots.

Matplotlib renders images directly in Python, with no browser involved, so it is simple to install and fast to save many files. Select it at the top of your script or notebook:

```python
import hvplot.pandas  # noqa

hvplot.extension('matplotlib')
```

See [How to Save Matplotlib Plots](save_matplotlib_plots.ipynb).
