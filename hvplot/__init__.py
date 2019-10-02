from __future__ import absolute_import

import sys
import inspect
import textwrap

import param
import holoviews as _hv

from holoviews import Store

from .converter import HoloViewsConverter
from .util import get_ipy
from .utilities import save, show # noqa
from .plotting import (hvPlot, hvPlotTabular,  # noqa
                       andrews_curves, lag_plot,
                       parallel_coordinates, scatter_matrix)

__version__ = str(param.version.Version(fpath=__file__, archive_commit="$Format:%h$",
                                        reponame="hvplot"))

_METHOD_DOCS = {}

def _get_doc(cls, kind, completions=False, docstring=True, generic=True, style=True):
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

    if eltype in Store.registry['bokeh']:
        valid_opts = Store.registry['bokeh'][eltype].style_opts
        if style:
            formatter += '\n{style}'
    else:
        valid_opts = []

    style_opts = 'Style options\n-------------\n\n' + '\n'.join(sorted(valid_opts))

    parameters = []
    if sys.version_info.major < 3:
        argspec = inspect.getargspec(method)
        args = argspec.args[1:]
        defaults = argspec.defaults or [None]*len(args)
        for arg, dflt in zip(args, defaults):
            parameters.append((arg, dflt))
    else:
        sig = inspect.signature(method)
        for name, p in list(sig.parameters.items())[1:]:
            if p.kind == 1:
                parameters.append((name, p.default))
    parameters += [(o, None) for o in
                   valid_opts+kind_opts+converter._axis_options+converter._op_options]

    completions = ', '.join(['%s=%s' % (n, v) for n, v in parameters])
    options = textwrap.dedent(converter.__doc__)
    method_doc = _METHOD_DOCS.get(kind, method.__doc__)
    _METHOD_DOCS[kind] = method_doc
    return formatter.format(
        kind=kind, completions=completions, docstring=textwrap.dedent(method_doc),
        options=options, style=style_opts)


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
    print(_get_doc(cls=hvPlot, kind=kind, docstring=docstring, generic=generic, style=style))


def post_patch(extension='bokeh', logo=False):
    if extension and not getattr(_hv.extension, '_loaded', False):
        _hv.extension(extension, logo=logo)


def _patch_doc(cls, kind):
    method = getattr(cls, kind)
    docstring = _get_doc(cls, kind, get_ipy())
    if sys.version_info.major == 2:
        method.__func__.__doc__ = docstring
    else:
        method.__doc__ = docstring


# Patch docstrings
for cls in [hvPlot, hvPlotTabular]:
    for _kind in HoloViewsConverter._kind_mapping:
        if hasattr(cls, _kind):
            _patch_doc(cls, _kind)
