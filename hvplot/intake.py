from distutils.version import LooseVersion

from . import patch, _hv

try:
    import intake.plotting # noqa
    patch('intake', extension='bokeh')
except:
    import intake
    if LooseVersion(intake.__version__) <= '0.1.5':
        patch('intake', extension='bokeh')
        patch('intake', 'plot')
    else:
        if not _hv.extension._loaded:
            _hv.extension('bokeh', logo=False)
