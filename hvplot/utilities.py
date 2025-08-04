import panel as _pn
import param
import holoviews as _hv

from .util import _get_doc_and_signature

renderer = _hv.renderer('bokeh')

output = _hv.output


def help(kind=None, docstring=True, generic=True, style=True):
    """
    Print a docstring with all valid options which apply to the plot
    type.

    Parameters
    ----------
    kind: str, optional
        The kind of plot to provide help for.
    docstring: boolean, default=True
        Whether to display the docstring.
    generic: boolean, default=True
        Whether to provide list of generic options.
    style: str or boolean, default=True
        Plotting backend used to get the styling options. True by default
        to automatically infer it based on the loaded extension.

    Examples
    --------
    >>> import hvplot
    >>> hvplot.help('line')
    """
    from .plotting.core import hvPlot

    doc, sig = _get_doc_and_signature(
        cls=hvPlot, kind=kind, docstring=docstring, generic=generic, style=style
    )
    print(doc)


def save(
    obj, filename, fmt='auto', backend=None, resources='cdn', toolbar=None, title=None, **kwargs
):
    """
    Saves the supplied object to file.

    This function delegates saving to :func:`holoviews:holoviews.util.save`  when the
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

    Parameters
    ----------
    obj: HoloViews object
        The HoloViews object to save to file
    filename: str or IO object
        The filename or BytesIO/StringIO object to save to
    fmt: str
        The format to save the object as, e.g. png, svg, html, or gif
        and if widgets are desired either 'widgets' or 'scrubber'
    backend: str
        A valid HoloViews rendering backend, e.g. bokeh or matplotlib
    resources: str or bokeh.resource.Resources
        Bokeh resources used to load bokehJS components. Defaults to
        CDN, to embed resources inline for offline usage use 'inline'
        or bokeh.resources.INLINE.
    toolbar: bool or None
        Whether to include toolbars in the exported plot. If None,
        display the toolbar unless fmt is `png` and backend is `bokeh`.
        If `True`, always include the toolbar.  If `False`, do not include the
        toolbar.
    title: str
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
    Starts a Bokeh server and displays the plot in a new tab.

    Parameters
    ----------
    obj : HoloViews/Panel object
        HoloViews/Panel object to show
    title : str
        A string title to give the Document (if served as an app)
    port: int, default=0
        Allows specifying a specific port
    **kwargs: dict
        Additional keyword arguments passed to :meth:`panel:panel.viewable.Viewer.show`.

    Returns
    -------
    server: bokeh.server.Server or panel.io.server.StoppableThread
        Returns the Bokeh server instance or the thread the server
        was launched on (if threaded=True)
    """
    if isinstance(obj, _hv.core.Dimensioned):
        return _pn.pane.HoloViews(obj).show(title, port, **kwargs)
    elif isinstance(obj, _pn.viewable.Viewable):
        return obj.show(title, port, **kwargs)
    elif isinstance(obj, param.rx):
        return _pn.panel(obj).show(title, port, **kwargs)
    else:
        raise ValueError(f'{type(obj).__name__} type object not recognized and cannot be shown.')


class hvplot_extension(_hv.extension):
    """
    Helper utility used to load hvPlot/HoloViews extensions and control
    the notebook environment.

    Extends :class:`holoviews.util.extension` by adding `compatibility`.

    Notes
    -----

    - Installing a data source with e.g. `import hvplot.pandas` automatically
      calls this extension, enabling the Bokeh plotting backend.
    - Calling the extension in a notebook environment injects some CSS/HTML/JS
      content in the cell output, content that is required for the plots to
      be rendered and interacted with.

    Examples
    --------
    Enable the Bokeh and Matplotlib plotting extensions:

    >>> import hvplot
    >>> hvplot.extension('bokeh', 'matplotlib')
    """

    compatibility = param.ObjectSelector(
        allow_None=True,
        objects=['bokeh', 'matplotlib', 'plotly'],
        doc="""
            Plotting library used to process extra keyword arguments.""",
    )

    logo = param.Boolean(default=False)

    def __call__(self, *args, **params):
        from . import _PATCH_PLOT_SIGNATURES

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
        if _PATCH_PLOT_SIGNATURES:
            # Patch or re-patch the docstrings/signatures to display
            # the right styling options.
            from . import _patch_hvplot_docstrings

            _patch_hvplot_docstrings()
