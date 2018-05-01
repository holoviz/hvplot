from . import patch, _extension

try:
    import intake.plotting # noqa
    patch('intake', 'bokeh')
except:
    _extension('bokeh')
