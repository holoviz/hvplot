# -*- coding: utf-8 -*-

from nbsite.shared_conf import *

project = u'hvPlot'
authors = u'PyViz developers'
copyright = u'2018 ' + authors
description = 'A high-level plotting API for the PyData ecosystem built on HoloViews'

import hvplot
version = release = hvplot.__version__

html_static_path += ['_static']
html_theme = 'sphinx_ioam_theme'
html_theme_options = {
    'logo': 'hvplot-logo.png',
    'favicon': 'favicon.ico',
    'css': 'main.css'
}

_NAV =  (
    ('Getting Started', 'getting_started/index'),
    ('User Guide', 'user_guide/index'),
    ('About', 'about')
)

templates_path = ['_templates']

html_context.update({
    'PROJECT': project,
    'DESCRIPTION': description,
    'AUTHOR': authors,
    # will work without this - for canonical (so can ignore when building locally or test deploying)
    'WEBSITE_SERVER': 'https://pyviz.github.io/hvplot',
    'VERSION': version,
    'NAV': _NAV,
    'LINKS': _NAV,
    'SOCIAL': (
        ('Gitter', '//gitter.im/pyviz/pyviz'),
        ('Github', '//github.com/pyviz/hvplot'),
    )
})
