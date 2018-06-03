from . import patch, _hv

try:
    import intake.plotting # noqa
    patch('intake', extension='bokeh')
except:
    if not _hv.extension._loaded:
        _hv.extension('bokeh', logo=False)
