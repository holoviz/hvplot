import panel as _pn
import holoviews as _hv

renderer = _hv.renderer('bokeh')

save = _hv.save

def show(obj, title=None, port=0, **kwargs):
    """
    Displays HoloViews objects in and outside the notebook

    Parameters
    ----------
    obj : HoloViews object
        HoloViews object to export
    title : str
        A string title to give the Document (if served as an app)
    port: int (optional, default=0)
        Allows specifying a specific port
    **kwargs: dict
        Additional keyword arguments passed to Panel show method.
    """
    if not isinstance(obj, _hv.core.Dimensioned):
        raise ValueError('%s type object not recognized and cannot be shown.' %
                         type(obj).__name__)
    _pn.pane.HoloViews(obj).show(title, port, **kwargs)
