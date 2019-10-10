# -*- coding: utf-8 -*-

from nbsite.shared_conf import *

project = u'hvPlot'
authors = u'PyViz developers'
copyright = u'2018 ' + authors
description = 'A high-level plotting API for the PyData ecosystem built on HoloViews'

import hvplot
version = release = hvplot.__version__

nbbuild_cell_timeout = 600

html_static_path += ['_static']
html_theme = 'sphinx_pyviz_theme'
html_theme_options = {
    'logo': 'hvplot-logo.png',
    'favicon': 'favicon.ico',
    'primary_color': '#266498',
    'primary_color_dark': '#1b486e',
    'second_nav': True,
}

_NAV =  (
    ('Getting Started', 'getting_started/index'),
    ('User Guide', 'user_guide/index'),
    ('Developer Guide', 'developer_guide/index'),
    ('About', 'about')
)

html_context.update({
    'PROJECT': project,
    'DESCRIPTION': description,
    'AUTHOR': authors,
    # will work without this - for canonical (so can ignore when building locally or test deploying)
    'WEBSITE_SERVER': 'https://hvplot.pyviz.org',
    'VERSION': version,
    'NAV': _NAV,
    'LINKS': _NAV,
    'SOCIAL': (
        ('Gitter', '//gitter.im/pyviz/pyviz'),
        ('Github', '//github.com/pyviz/hvplot'),
    )
})
