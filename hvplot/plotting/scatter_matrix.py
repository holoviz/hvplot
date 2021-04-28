from __future__ import absolute_import

import holoviews as _hv

from ..converter import HoloViewsConverter
from ..util import with_hv_extension


@with_hv_extension
def scatter_matrix(data, c=None, chart='scatter', diagonal='hist',
                   alpha=0.5, nonselection_alpha=0.1,
                   tools=None, cmap=None, colormap=None,
                   diagonal_kwds=None, hist_kwds=None, density_kwds=None,
                   **kwds):
    """
    Scatter matrix of numeric columns.

    A scatter_matrix shows all the pairwise relationships between the columns.
    Each non-diagonal plots the corresponding columns against each other,
    while the diagonal plot shows the distribution of each individual column.

    This function is closely modelled on :func:`pandas.plotting.scatter_matrix`.

    Parameters:
    -----------
    data: DataFrame
        The data to plot. Every column is compared to every other column.
    c: str, optional
        Column to color by
    chart: str, optional
        Chart type for the off-diagonal plots (one of 'scatter', 'bivariate', 'hexbin')
    diagonal: str, optional
        Chart type for the diagonal plots (one of 'hist', 'kde')
    alpha: float, optional
        Transparency level for the off-diagonal plots
    nonselection_alpha: float, optional
        Transparency level for nonselected object in the off-diagonal plots
    tools: str or list of str, optional
        Interaction tools to include
        Defaults are 'box_select' and 'lasso_select'
    cmap/colormap: str or colormap object, optional
        Colormap to use for off-diagonal plots
        Default is `Category10 <https://github.com/d3/d3-3.x-api-reference/blob/master/Ordinal-Scales.md#category10>`.
    diagonal_kwds/hist_kwds/density_kwds: dict, optional
        Keyword options for the diagonal plots
    kwds: Keyword options for the off-diagonal plots, optional

    Returns:
    --------
    obj : HoloViews object
        The HoloViews representation of the plot.

    See Also
    --------
        :func:`pandas.plotting.scatter_matrix` : Equivalent pandas function.
    """
    data = _hv.Dataset(data)
    supported = list(HoloViewsConverter._kind_mapping)
    if diagonal not in supported:
        raise ValueError('diagonal type must be one of: %s, found %s' %
                         (supported, diagonal))
    if chart not in supported:
        raise ValueError('Chart type must be one of: %s, found %s' %
                         (supported, chart))
    diagonal = HoloViewsConverter._kind_mapping[diagonal]
    chart = HoloViewsConverter._kind_mapping[chart]

    if cmap and colormap:
        raise TypeError("Only specify one of `cmap` and `colormap`.")
    colors = cmap or colormap or _hv.plotting.util.process_cmap('Category10', categorical=True)
    tools = tools or ['box_select', 'lasso_select']
    chart_opts = dict(alpha=alpha, cmap=colors, tools=tools,
                      nonselection_alpha=nonselection_alpha, **kwds)

    grid = _hv.operation.gridmatrix(data, diagonal_type=diagonal, chart_type=chart)
    if c:
        chart_opts['color_index'] = c
        grid = grid.map(lambda x: x.clone(vdims=x.vdims+[c]), 'Scatter')
        groups = _hv.operation.gridmatrix(data.groupby(c).overlay(),
                                          chart_type=chart,
                                          diagonal_type=diagonal)
        grid = (grid * groups).map(lambda x: x.get(0) if isinstance(x.get(0), chart) else x.get(1),
                                   _hv.Overlay)

    if (diagonal_kwds and hist_kwds) or \
       (diagonal_kwds and density_kwds) or \
       (hist_kwds and density_kwds):
        raise TypeError('Specify at most one of `diagonal_kwds`, `hist_kwds`, or '
                        '`density_kwds`.')

    diagonal_kwds = diagonal_kwds or hist_kwds or density_kwds or {}
    diagonal_opts = dict(fill_color=_hv.Cycle(values=colors), **diagonal_kwds)
    return grid.options({chart.__name__: chart_opts, diagonal.__name__: diagonal_opts})
