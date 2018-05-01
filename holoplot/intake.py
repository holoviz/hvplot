from distutils.version import LooseVersion

import intake

from . import patch, _extension

if LooseVersion(intake.__version__) > '0.0.4':
    # Intake version > 0.0.4 provide inbuilt support for holoplot
    _extension('bokeh')
else:
    patch('intake', 'bokeh')
