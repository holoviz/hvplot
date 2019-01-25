import holoviews as _hv

from bokeh.io import export_png as _export_png, show as _show, save as _save
from bokeh.resources import CDN as _CDN

renderer = _hv.renderer('bokeh')


def save(obj, filename, title=None, resources=None):
    """
    Saves HoloViews objects and bokeh plots to file.

    Parameters
    ----------
    obj : HoloViews object
       HoloViews object to export
    filename : string
       Filename to save the plot to
    title : string
       Optional title for the plot
    resources: bokeh resources
       One of the valid bokeh.resources (e.g. CDN or INLINE)
    """
    if isinstance(obj, _hv.core.Dimensioned):
        plot = renderer.get_plot(obj).state
    else:
        raise ValueError('%s type object not recognized and cannot be saved.' %
                         type(obj).__name__)

    if filename.endswith('png'):
        _export_png(plot, filename=filename)
        return
    if not filename.endswith('.html'):
        filename = filename + '.html'

    if title is None:
        title = 'hvPlot Plot'
    if resources is None:
        resources = _CDN

    if obj.traverse(lambda x: x, [_hv.HoloMap]):
        renderer.save(plot, filename)
    else:
        _save(plot, filename, title=title, resources=resources)


def show(obj, filename=None):
    """
    Displays HoloViews objects in and outside the notebook

    Parameters
    ----------
    obj : HoloViews object
       HoloViews object to export
    """
    if not isinstance(obj, _hv.core.Dimensioned):
        raise ValueError('%s type object not recognized and cannot be shown.' %
                         type(obj).__name__)

    if obj.traverse(lambda x: x, [_hv.HoloMap]):
        renderer.app(obj, show=True, new_window=True)
    else:
        from bokeh.io import output_file
        output_file(filename or 'default.html')
        _show(renderer.get_plot(obj).state)
