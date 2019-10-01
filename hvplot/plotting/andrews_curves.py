from __future__ import absolute_import

import numpy as np
import pandas as pd

import holoviews as hv
import colorcet as cc

from ..util import with_hv_extension


@with_hv_extension
def andrews_curves(data, class_column, samples=200, alpha=0.5,
                   width=600, height=300, cmap=None, colormap=None,
                   **kwds):
    """
    Andrews curve plot.

    Parameters
    ----------
    frame: DataFrame
    class_column: str
        Column name containing class names
    samples: int, optional
        Number of samples to draw
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
    t = np.linspace(-np.pi, np.pi, samples)
    vals = data.drop(class_column, axis=1).values.T

    curves = np.outer(vals[0], np.ones_like(t))
    for i in range(1, len(vals)):
        ft = ((i + 1) // 2) * t
        if i % 2 == 1:
            curves += np.outer(vals[i], np.sin(ft))
        else:
            curves += np.outer(vals[i], np.cos(ft))

    df = pd.DataFrame({'t': np.tile(np.arange(samples), curves.shape[0]),
                       'sample': np.repeat(np.arange(curves.shape[0]), curves.shape[1]),
                       'value': curves.ravel(),
                       class_column: np.repeat(data[class_column], samples)})

    labelled = ['x']
    options = {'Overlay': dict(legend_limit=5000),
               'Curve': dict(kwds, labelled=labelled, alpha=alpha,
                             width=width, height=height, **kwds)}
    dataset = hv.Dataset(df)
    groups = dataset.to(hv.Curve, 't', 'value').overlay('sample').items()

    if cmap and colormap:
        raise TypeError("Only specify one of `cmap` and `colormap`.")
    cmap = cmap or colormap or cc.palette['glasbey_category10']
    colors = hv.plotting.util.process_cmap(cmap, categorical=True, ncolors=len(groups))

    return hv.Overlay([curve.relabel(k).options('Curve', color=c)
                       for c, (k, v) in zip(colors, groups) for curve in v]).options(options)
