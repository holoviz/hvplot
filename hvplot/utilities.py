import panel as _pn
import param
import holoviews as _hv

renderer = _hv.renderer('bokeh')

output = _hv.output

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


class hvplot_extension(_hv.extension):

    compatibility = param.ObjectSelector(
        allow_None=True, objects=['bokeh', 'matplotlib', 'plotly'], doc="""
            Plotting library used to process extra keyword arguments.""")

    logo = param.Boolean(default=False)

    def __call__(self, *args, **params):
        # importing e.g. hvplot.pandas always loads the bokeh extension.
        # so hvplot.extension('matplotlib', compatibility='bokeh') doesn't
        # require the user or the code to explicitely load bokeh.
        compatibility = params.pop('compatibility', None)
        super().__call__(*args, **params)
        backend = _hv.Store.current_backend
        if compatibility in ['matplotlib', 'plotly'] and backend != compatibility:
            param.main.param.warning(
                f'Compatibility from {compatibility} to {backend} '
                'not yet implemented. Defaults to bokeh.'
            )
        hvplot_extension.compatibility = compatibility
        # Patch or re-patch the docstrings/signatures to display
        # the right styling options.
        from . import _patch_hvplot_docstrings
        _patch_hvplot_docstrings()
