from functools import partial

import holoviews as _hv
import numpy as _np

from packaging.version import Version

from ..backend_transforms import _transfer_opts_cur_backend
from ..converter import HoloViewsConverter
from ..util import with_hv_extension, _convert_col_names_to_str


@with_hv_extension
def scatter_matrix(
    data,
    c=None,
    chart='scatter',
    diagonal='hist',
    alpha=0.5,
    nonselection_alpha=0.1,
    tools=None,
    cmap=None,
    colormap=None,
    diagonal_kwds=None,
    hist_kwds=None,
    density_kwds=None,
    datashade=False,
    rasterize=False,
    dynspread=False,
    spread=False,
    **kwds,
):
    """
    Scatter matrix of numeric columns.

    A scatter_matrix shows all the pairwise relationships between the columns.
    Each non-diagonal plots the corresponding columns against each other,
    while the diagonal plot shows the distribution of each individual column.

    This function is closely modelled on :func:`pandas.plotting.scatter_matrix`.

    Parameters
    ----------
    data : DataFrame
        The data to plot. Every column is compared to every other column.
    c : str, optional
        Column to color by.
    chart : str, optional
        Chart type for the off-diagonal plots (one of ``'scatter'``,
        ``'bivariate'``, ``'hexbin'``). Default is ``'scatter'``.
    diagonal : str, optional
        Chart type for the diagonal plots (one of ``'hist'``, ``'kde'``).
        Default is ``'hist'``.
    alpha : float, optional
        Transparency level for the off-diagonal plots. Default is 0.5.
    nonselection_alpha : float, optional
        Transparency level for nonselected object in the off-diagonal plots.
        Default is 0.1.
    tools : list of str, optional
        Interaction tools to include. Defaults are ``'box_select'`` and
        ``'lasso_select'``.
    cmap/colormap : str or colormap object, optional
        Colormap to use when ``c`` is set.
        Default is ``Category10`` (see `<https://github.com/d3/d3-3.x-api-reference/blob/master/Ordinal-Scales.md#category10>`_).
    diagonal_kwds/hist_kwds/density_kwds : dict, optional
        Keyword options for the diagonal plots.
    datashade : bool, default=False
        Whether to apply rasterization and shading (colormapping) using
        the Datashader library, returning an RGB object instead of
        individual points.
    rasterize : bool, default=False
        Whether to apply rasterization using the Datashader library,
        returning an aggregated Image (to be colormapped by the
        plotting backend) instead of individual points.
    dynspread : bool, default=False
        For plots generated with datashade=True or rasterize=True,
        automatically increase the point size when the data is sparse
        so that individual points become more visible.
        kwds supported include ``max_px``, ``threshold``,  ``shape``, ``how`` and ``mask``.
    spread : bool, default=False
        Make plots generated with datashade=True or rasterize=True
        increase the point size to make points more visible, by
        applying a fixed spreading of a certain number of cells/pixels. kwds
        supported include: ``px``, ``shape``, ``how`` and ``mask``.
    **kwds : optional
        Keyword options for the off-diagonal plots and datashader's spreading , optional

    Returns
    -------
    obj : HoloViews object
        The HoloViews representation of the plot.

    See Also
    --------
        :func:`pandas.plotting.scatter_matrix` : Equivalent pandas function.
    """

    data = _hv.Dataset(_convert_col_names_to_str(data))
    supported = list(HoloViewsConverter._kind_mapping)
    if diagonal not in supported:
        raise ValueError(f'diagonal type must be one of: {supported}, found {diagonal}')
    if chart not in supported:
        raise ValueError(f'Chart type must be one of: {supported}, found {chart}')
    diagonal = HoloViewsConverter._kind_mapping[diagonal]
    chart = HoloViewsConverter._kind_mapping[chart]

    if rasterize or datashade:
        try:
            import datashader  # noqa
        except ImportError:
            raise ImportError('rasterize and datashade require datashader to be installed.')

    if rasterize and datashade:
        raise ValueError('Choose to either rasterize or datashade the scatter matrix, not both.')

    if not rasterize and not datashade and (spread or dynspread):
        raise ValueError('dynspread or spread need rasterize or datashade to be set to True.')

    if rasterize:
        import datashader as ds
        import holoviews.operation.datashader as hd

        if dynspread or spread:
            if Version(ds.__version__) < Version('0.12.0'):
                raise RuntimeError(
                    'Any version of datashader less than 0.12.0 does '
                    'not support rasterize with dynspread or spread.'
                )

    # remove datashade kwds
    if datashade or rasterize:
        import holoviews.operation.datashader as hd

        ds_kwds = {}
        if 'aggregator' in kwds:
            ds_kwds['aggregator'] = kwds.pop('aggregator')

    # remove dynspread kwds
    sp_kwds = {}
    if dynspread:
        if 'max_px' in kwds:
            sp_kwds['max_px'] = kwds.pop('max_px')
        if 'threshold' in kwds:
            sp_kwds['threshold'] = kwds.pop('threshold')
        if 'shape' in kwds:
            sp_kwds['shape'] = kwds.pop('shape')
        if 'how' in kwds:
            sp_kwds['how'] = kwds.pop('how')
        if 'mask' in kwds:
            sp_kwds['mask'] = kwds.pop('mask')
    if spread:
        if 'px' in kwds:
            sp_kwds['px'] = kwds.pop('px')
        if 'shape' in kwds:
            sp_kwds['shape'] = kwds.pop('shape')
        if 'how' in kwds:
            sp_kwds['how'] = kwds.pop('how')
        if 'mask' in kwds:
            sp_kwds['mask'] = kwds.pop('mask')

    tools = tools or ['box_select', 'lasso_select']
    chart_opts = dict(alpha=alpha, tools=tools, nonselection_alpha=nonselection_alpha, **kwds)
    if c:
        if cmap and colormap:
            raise TypeError('Only specify `cmap` or `colormap`.')
        ncolors = len(_np.unique(data.dimension_values(c)))
        cmap = cmap or colormap or 'Category10'
        cmap = _hv.plotting.util.process_cmap(cmap, ncolors=ncolors, categorical=True)
        chart_opts['cmap'] = cmap

    # get initial scatter matrix.  No color.
    grid = _hv.operation.gridmatrix(data, diagonal_type=diagonal, chart_type=chart)

    if c:
        # change colors for scatter matrix
        chart_opts['color'] = c
        # Add color vdim to each plot.
        grid = grid.map(lambda x: x.clone(vdims=x.vdims + [c]), 'Scatter')
        # create a new scatter matrix with groups for each catetory, so now the histogram will
        # show separate colors for each group.
        groups = _hv.operation.gridmatrix(
            data.groupby(c).overlay(), chart_type=chart, diagonal_type=diagonal
        )
        # take the correct layer from each Overlay object within the scatter matrix.
        grid = (grid * groups).map(
            lambda x: x.get(0) if isinstance(x.get(0), chart) else x.get(1), _hv.Overlay
        )

    if (
        (diagonal_kwds and hist_kwds)
        or (diagonal_kwds and density_kwds)
        or (hist_kwds and density_kwds)
    ):
        raise TypeError('Specify at most one of `diagonal_kwds`, `hist_kwds`, or `density_kwds`.')

    diagonal_opts = diagonal_kwds or hist_kwds or density_kwds or {}
    # set the histogram colors
    if c:
        diagonal_opts['fill_color'] = _hv.Cycle(cmap)
    # actually changing to the same color scheme for both scatter and histogram plots.
    grid = grid.options(
        {chart.__name__: chart_opts, diagonal.__name__: diagonal_opts},
        backend='bokeh',
    )

    # Perform datashade options after all the coloring is finished.
    if datashade or rasterize:
        aggregatefn = hd.datashade if datashade else hd.rasterize
        grid = grid.map(partial(aggregatefn, **ds_kwds), specs=chart)
        if spread or dynspread:
            spreadfn = hd.dynspread if dynspread else (hd.spread if spread else lambda z, **_: z)
            eltype = _hv.RGB if datashade else _hv.Image
            grid = grid.map(partial(spreadfn, **sp_kwds), specs=eltype)

    grid = _transfer_opts_cur_backend(grid)
    return grid
