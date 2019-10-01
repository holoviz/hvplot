from __future__ import absolute_import

import holoviews as hv
import colorcet as cc

from ..util import with_hv_extension


@with_hv_extension
def parallel_coordinates(data, class_column, cols=None, alpha=0.5,
                         width=600, height=300, var_name='variable',
                         value_name='value', cmap=None, colormap=None,
                         **kwds):
    """
    Parallel coordinates plotting.

    Parameters
    ----------
    frame: DataFrame
    class_column: str
        Column name containing class names
    cols: list, optional
        A list of column names to use
    alpha: float, optional
        The transparency of the lines
    cmap/colormap: str or colormap object
        Colormap to use for groups

    Returns
    -------
    obj : HoloViews object
        The HoloViews representation of the plot.

    See Also
    --------
    pandas.plotting.parallel_coordinates : matplotlib version of this routine
    """
    # Transform the dataframe to be used in Vega-Lite
    if cols is not None:
        data = data[list(cols) + [class_column]]
    cols = data.columns
    df = data.reset_index()
    index = (set(df.columns) - set(cols)).pop()
    assert index in df.columns
    df = df.melt([index, class_column],
                 var_name=var_name, value_name=value_name)

    labelled = [] if var_name == 'variable' else ['x']
    if value_name != 'value':
        labelled.append('y')
    options = {'Curve': dict(kwds, labelled=labelled, alpha=alpha, width=width, height=height),
               'Overlay': dict(legend_limit=5000)}

    dataset = hv.Dataset(df)
    groups = dataset.to(hv.Curve, var_name, value_name).overlay(index).items()

    if cmap and colormap:
        raise TypeError("Only specify one of `cmap` and `colormap`.")
    cmap = cmap or colormap or cc.palette['glasbey_category10']
    colors = hv.plotting.util.process_cmap(cmap, categorical=True, ncolors=len(groups))

    return hv.Overlay([curve.relabel(k).options('Curve', color=c)
                       for c, (k, v) in zip(colors, groups) for curve in v]).options(options)
