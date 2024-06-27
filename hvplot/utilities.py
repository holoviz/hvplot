import panel as _pn
import param
import holoviews as _hv

renderer = _hv.renderer('bokeh')

output = _hv.output


def save(
    obj, filename, fmt='auto', backend=None, resources='cdn', toolbar=None, title=None, **kwargs
):
    """
    Saves the supplied object to file.

    This function delegates saving to `holoviews.util.save` when the
    object is a HoloViews element, which is the type of object mostly
    created by hvPlot. This function inherits the same signature and
    docstring below. However, in some cases hvPlot creates Panel objects,
    in which case saving is delegated to the method `panel.io.Viewable.save`.
    It shares a few common parameters with `holoviews.util.save`, and extra
    parameters can be passed as kwargs.

    The available output formats depend on the backend being used. By
    default and if the filename is a string the output format will be
    inferred from the file extension. Otherwise an explicit format
    will need to be specified. For ambiguous file extensions such as
    html it may be necessary to specify an explicit fmt to override
    the default, e.g. in the case of 'html' output the widgets will
    default to fmt='widgets', which may be changed to scrubber widgets
    using fmt='scrubber'.

    Arguments
    ---------
    obj: HoloViews object
        The HoloViews object to save to file
    filename: string or IO object
        The filename or BytesIO/StringIO object to save to
    fmt: string
        The format to save the object as, e.g. png, svg, html, or gif
        and if widgets are desired either 'widgets' or 'scrubber'
    backend: string
        A valid HoloViews rendering backend, e.g. bokeh or matplotlib
    resources: string or bokeh.resource.Resources
        Bokeh resources used to load bokehJS components. Defaults to
        CDN, to embed resources inline for offline usage use 'inline'
        or bokeh.resources.INLINE.
    toolbar: bool or None
        Whether to include toolbars in the exported plot. If None,
        display the toolbar unless fmt is `png` and backend is `bokeh`.
        If `True`, always include the toolbar.  If `False`, do not include the
        toolbar.
    title: string
        Custom title for exported HTML file
    **kwargs: dict
        Additional keyword arguments passed to the renderer,
        e.g. fps for animations
    """
    if isinstance(obj, _hv.core.Dimensioned):
        _hv.save(
            obj,
            filename,
            fmt=fmt,
            backend=backend,
            resources=resources,
            toolbar=toolbar,
            title=title,
            **kwargs,
        )
    elif isinstance(obj, _pn.layout.Panel):
        obj.save(filename, resources=resources, title=title, **kwargs)
    else:
        raise TypeError(f'Saving not supported for objects of type {type(obj)!r}')


def show(obj, title=None, port=0, **kwargs):
    """
    Displays hvplot plots in and outside the notebook

    Parameters
    ----------
    obj : HoloViews/Panel object
        HoloViews/Panel object to show
    title : str
        A string title to give the Document (if served as an app)
    port: int (optional, default=0)
        Allows specifying a specific port
    **kwargs: dict
        Additional keyword arguments passed to Panel show method.
    Returns
    -------
    a panel.io.server.Server | panel.io.server.StoppableThread (if threaded=true)
    """
    if isinstance(obj, _hv.core.Dimensioned):
        return _pn.pane.HoloViews(obj).show(title, port, **kwargs)
    elif isinstance(obj, _pn.viewable.Viewable):
        return obj.show(title, port, **kwargs)
    else:
        raise ValueError('{type(obj).__name__} type object not recognized and cannot be shown.')


class hvplot_extension(_hv.extension):
    compatibility = param.ObjectSelector(
        allow_None=True,
        objects=['bokeh', 'matplotlib', 'plotly'],
        doc="""
            Plotting library used to process extra keyword arguments.""",
    )

    logo = param.Boolean(default=False)

    def __call__(self, *args, **params):
        # importing e.g. hvplot.pandas always loads the bokeh extension.
        # so hvplot.extension('matplotlib', compatibility='bokeh') doesn't
        # require the user or the code to explicitly load bokeh.
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
