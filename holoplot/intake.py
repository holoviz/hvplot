from . import patch, _hv

try:
    import intake.plotting # noqa
    patch('intake', 'bokeh')
except:
    _hv.extension('bokeh', logo=False)
