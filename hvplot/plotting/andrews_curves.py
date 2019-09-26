from __future__ import absolute_import

import numpy as _np
import holoviews as _hv


def andrews_curves(data, class_column, samples=200, alpha=0.5,
                   width=600, height=300, **kwds):
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

    Returns
    -------
    obj : HoloViews object
        The HoloViews representation of the plot.

    See Also
    --------
    pandas.plotting.parallel_coordinates : matplotlib version of this routine
    """
    t = _np.linspace(-_np.pi, _np.pi, samples)
    vals = data.drop(class_column, axis=1).values.T

    curves = _np.outer(vals[0], _np.ones_like(t))
    for i in range(1, len(vals)):
        ft = ((i + 1) // 2) * t
        if i % 2 == 1:
            curves += _np.outer(vals[i], _np.sin(ft))
        else:
            curves += _np.outer(vals[i], _np.cos(ft))

    df = _pd.DataFrame({'t': _np.tile(_np.arange(samples), curves.shape[0]),
                       'sample': _np.repeat(_np.arange(curves.shape[0]), curves.shape[1]),
                       'value': curves.ravel(),
                       class_column: _np.repeat(data[class_column], samples)})

    labelled = ['x']
    colors = _hv.plotting.util.process_cmap('Category10', categorical=True)
    options = {'Overlay': dict(legend_limit=5000),
               'Curve': dict(kwds, labelled=labelled, alpha=alpha,
                             width=width, height=height, **kwds)}
    dataset = _hv.Dataset(df)
    groups = dataset.to(_hv.Curve, 't', 'value').overlay('sample').items()
    return _hv.Overlay([curve.relabel(k).options('Curve', color=c)
                        for c, (k, v) in zip(colors, groups) for curve in v]).options(options)
