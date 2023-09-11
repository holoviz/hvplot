"""
hvPlot makes data analysis and visualization simple
===================================================

hvPlot provides a familiar, high-level API for interactive data exploration and visualization,
based on the Pandas `.plot` API and the innovative `.interactive` API.

hvPlot

- supports a wide range of data sources including Pandas, Dask, XArray
Rapids cuDF, Streamz, Intake, Geopandas, NetworkX and Ibis.
- supports the plotting backends Bokeh (default), Matplotlib and Plotly.
- exposes the powerful tools from the HoloViz ecosystem in a familiar and convenient API, while
letting you drop down into the underlying HoloViz tools when more power or flexibility is needed.

hvPlot is the recommend entrypoint to the HoloViz ecosystem.

To learn more check out https://hvplot.holoviz.org/. To report issues or contribute go to
https://github.com/holoviz/hvplot. To join the community go to
https://discourse.holoviz.org/.

How to use hvPlot in 3 simple steps
-----------------------------------

Work with the data source you already know and ❤️

>>> import pandas as pd, numpy as np
>>> idx = pd.date_range('1/1/2000', periods=1000)
>>> df  = pd.DataFrame(np.random.randn(1000, 4), index=idx, columns=list('ABCD')).cumsum()

Import the hvplot extension for your data source and optionally set the plotting backend

>>> import hvplot.pandas
>>> # hvplot.extension('matplotlib')

Use the `.hvplot` API as you would use the Pandas `.plot` API.

>>> df.hvplot()

In a Jupyter Notebook, this will display a line plot of the A, B, C and D time series.

For more check out the user guide https://hvplot.holoviz.org/user_guide/index.html

How to get help
---------------

To see the available arguments for a specific `kind` of plot run

>>> import hvplot
>>> hvplot.help(kind='scatter')

In a notebook or ipython environment the usual

- `help` and `?` will provide you with documentation.
- `TAB` and `SHIFT+TAB` completion will help you navigate.

To ask the community go to https://discourse.holoviz.org/.
To report issues go to https://github.com/holoviz/holoviews.
"""
import inspect
import textwrap

import param
import panel as _pn
import holoviews as _hv

from holoviews import Store, render  # noqa

from .converter import HoloViewsConverter
from .interactive import Interactive
from .ui import explorer  # noqa
from .utilities import hvplot_extension, output, save, show # noqa
from .plotting import (hvPlot, hvPlotTabular,  # noqa
                       andrews_curves, lag_plot,
                       parallel_coordinates, scatter_matrix, plot)

__version__ = str(param.version.Version(fpath=__file__, archive_commit="$Format:%h$",
                                        reponame="hvplot"))

_METHOD_DOCS = {}

def _get_doc_and_signature(
    cls, kind, completions=False, docstring=True, generic=True, style=True, signature=None
):
    converter = HoloViewsConverter
    method = getattr(cls, kind)
    kind_opts = converter._kind_options.get(kind, [])
    eltype = converter._kind_mapping[kind]

    formatter = ''
    if completions:
        formatter = "hvplot.{kind}({completions})"
    if docstring:
        if formatter:
            formatter += '\n'
        formatter += "{docstring}"
    if generic:
        if formatter:
            formatter += '\n'
        formatter += "{options}"

    # Bokeh is the default backend
    backend = hvplot_extension.compatibility or Store.current_backend
    if eltype in Store.registry[backend]:
        valid_opts = Store.registry[backend][eltype].style_opts
        if style:
            formatter += '\n{style}'
    else:
        valid_opts = []

    style_opts = 'Style options\n-------------\n\n' + '\n'.join(sorted(valid_opts))

    parameters = []
    extra_kwargs = _hv.core.util.unique_iterator(
        valid_opts + kind_opts + converter._axis_options + converter._op_options
    )

    sig = signature or inspect.signature(method)
    for name, p in list(sig.parameters.items())[1:]:
        if p.kind == 1:
            parameters.append((name, p.default))

    filtered_signature = [p for p in sig.parameters.values()
                            if p.kind != inspect.Parameter.VAR_KEYWORD]
    extra_params = [inspect.Parameter(k, inspect.Parameter.KEYWORD_ONLY)
                    for k in extra_kwargs
                    if k not in [p.name for p in filtered_signature]]
    all_params = (filtered_signature + extra_params
                    + [inspect.Parameter('kwargs', inspect.Parameter.VAR_KEYWORD)])
    signature = inspect.Signature(all_params)

    parameters += [(o, None) for o in extra_kwargs]
    completions = ', '.join([f'{n}={v}' for n, v in parameters])
    options = textwrap.dedent(converter.__doc__)
    method_doc = _METHOD_DOCS.get(kind, method.__doc__)
    _METHOD_DOCS[kind] = method_doc
    docstring = formatter.format(
        kind=kind, completions=completions, docstring=textwrap.dedent(method_doc),
        options=options, style=style_opts)
    return docstring, signature


def help(kind=None, docstring=True, generic=True, style=True):
    """
    Provide a docstring with all valid options which apply to the plot
    type.

    Parameters
    ----------
    kind: str
        The kind of plot to provide help for
    docstring: boolean (default=True)
        Whether to display the docstring
    generic: boolean (default=True)
        Whether to provide list of generic options
    style: boolean (default=True)
        Whether to provide list of style options
    """
    doc, sig = _get_doc_and_signature(cls=hvPlot, kind=kind,
                                      docstring=docstring, generic=generic, style=style)
    print(doc)


def post_patch(extension='bokeh', logo=False):
    if extension and not getattr(_hv.extension, '_loaded', False):
        hvplot_extension(extension, logo=logo)


def _patch_doc(cls, kind, signature=None):
    method = getattr(cls, kind)
    docstring, signature = _get_doc_and_signature(cls, kind, False, signature=signature)
    method.__doc__ = docstring
    method.__signature__ = signature


class _PatchHvplotDocstrings:

    def __init__(self):
        # Store the original signatures because the method signatures
        # are going to be patched everytime an extension is changed.
        signatures = {}
        for cls in [hvPlot, hvPlotTabular]:
            for _kind in HoloViewsConverter._kind_mapping:
                if hasattr(cls, _kind):
                    method = getattr(cls, _kind)
                    sig = inspect.signature(method)
                    signatures[(cls, _kind)] = sig
        self.orig_signatures = signatures

    def __call__(self):
        for cls in [hvPlot, hvPlotTabular]:
            for _kind in HoloViewsConverter._kind_mapping:
                if hasattr(cls, _kind):
                    signature = self.orig_signatures[(cls, _kind)]
                    _patch_doc(cls, _kind, signature=signature)


_patch_hvplot_docstrings = _PatchHvplotDocstrings()
_patch_hvplot_docstrings()

def _hook_patch_docstrings(backend):
    # Patch or re-patch the docstrings/signatures to display
    # the right styling options.
    from . import _patch_hvplot_docstrings
    _patch_hvplot_docstrings()

Store._backend_switch_hooks.append(_hook_patch_docstrings)

extension = hvplot_extension

def bind(function, *args, **kwargs):
    """
    Returns a *reactive* function that can be used to start your `.interactive` pipeline by running
    a model or loading data depending on inputs from widgets, parameters or python objects.

    The widgets can be Panel or ipywidgets.

    Reference: https://hvplot.holoviz.org/user_guide/Interactive.html#functions-as-inputs

    Parameters
    ----------
    function : callable
        The function to bind constant or dynamic args and kwargs to.
    args : object, param.Parameter, panel.widget.Widget, or ipywidget
        Positional arguments to bind to the function.
    kwargs : object, param.Parameter, panel.widget.Widget, or ipywidget
        Keyword arguments to bind to the function.

    Returns
    -------
    Returns a new function with the args and kwargs bound to it and
    annotated with all dependencies. This function has an `interactive`
    attribute that can be called to instantiate an `Interactive` pipeline.

    Examples
    --------

    Develop your **algorithm** or data extraction method with the tools you know and love.

    >>> import pandas as pd
    >>> import numpy as np

    >>> def algorithm(alpha):
    ...     # An example algorithm that uses alpha ...
    ...     return pd.DataFrame({"output": (np.array(range(0,100)) ** alpha)*50})

    Make it **interactive** using `.bind`, `.interactive` and widgets.

    >>> import hvplot
    >>> import panel as pn

    >>> alpha = pn.widgets.FloatSlider(value=0.5, start=0, end=1.0, step=0.1, name="Alpha")
    >>> top = pn.widgets.RadioButtonGroup(value=10, options=[5, 10, 25], name="Top")
    >>> interactive_table = (
    ...     hvplot
    ...     .bind(algorithm, alpha=alpha)
    ...     .interactive()
    ...     .head(n=top)
    ... )
    >>> interactive_table

    In a notebook or data app you can now select the appropriate `alpha` and `top` values via
    widgets and see the `top` results of the algorithm in a table depending on the value of `alpha`
    selected.
    """
    bound = _pn.bind(function, *args, **kwargs)
    bound.interactive = lambda **kwargs: Interactive(bound, **kwargs)
    return bound
