from __future__ import absolute_import

import holoviews as _hv

from ..converter import HoloViewsConverter
from ..util import with_hv_extension


@with_hv_extension
def scatter_matrix(data, c=None, chart='scatter', diagonal='hist', alpha=0.5,
                   diagonal_kwds=None, **kwds):
    """
    Scatter matrix of numeric columns.

    Parameters:
    -----------
    data: DataFrame
    c: str, optional
        Column to color by
    chart: str, optional
        Chart type for the off-diagonal plots (one of 'scatter', 'bivariate', 'hexbin')
    diagonal: str, optional
        Chart type for the diagonal plots (one of 'hist', 'kde')
    diagonal_kwds: dict, optional
        Keyword options for the diagonal plots
    kwds: Keyword options for the off-diagonal plots, optional

    Returns:
    --------
    obj : HoloViews object
        The HoloViews representation of the plot.
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

    colors = _hv.plotting.util.process_cmap('Category10', categorical=True)
    chart_opts = dict(alpha=alpha, cmap=colors, tools=['box_select', 'lasso_select'],
                      nonselection_alpha=0.1, **kwds)

    grid = _hv.operation.gridmatrix(data, diagonal_type=diagonal, chart_type=chart)
    if c:
        chart_opts['color_index'] = c
        grid = grid.map(lambda x: x.clone(vdims=x.vdims+[c]), 'Scatter')
        groups = _hv.operation.gridmatrix(data.groupby(c).overlay(),
                                          chart_type=chart,
                                          diagonal_type=diagonal)
        grid = (grid * groups).map(lambda x: x.get(0) if isinstance(x.get(0), chart) else x.get(1),
                                   _hv.Overlay)

    if diagonal_kwds is None:
        diagonal_kwds = {}
    diagonal_opts = dict(fill_color=_hv.Cycle(values=colors), **diagonal_kwds)
    return grid.options({chart.__name__: chart_opts, diagonal.__name__: diagonal_opts})
