# -*- coding: utf-8 -*-

from nbsite.shared_conf import *

project = u'HvPlot'
authors = u'Philipp Rudiger'
copyright = u'2017 ' + authors
description = 'A high-level plotting API for the PyData ecosystem built on HoloViews'

# TODO: gah, version
version = '0.0.1'
release = '0.0.1'

html_static_path += ['_static']
html_theme = 'sphinx_ioam_theme'
html_theme_options = {
    'logo':'pyviz-logo.png',
    'favicon':'favicon.ico'
#    'css':'pyviz.css'
}

_NAV =  (
    ('Getting Started', 'getting_started/index'),
    ('About', 'about')
)

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
        ('Gitter', '//gitter.im/ioam/holoviews'),
        ('Github', '//github.com/pyviz/hvplot'),
    )
})
