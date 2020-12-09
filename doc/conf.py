# -*- coding: utf-8 -*-

from nbsite.shared_conf import *

project = u'hvPlot'
authors = u'HoloViz developers'
copyright = u'2018-2020 ' + authors
description = 'A high-level plotting API for the PyData ecosystem built on HoloViews'

import hvplot
version = release = hvplot.__version__

nbbuild_cell_timeout = 600

html_static_path += ['_static']
html_theme = 'sphinx_holoviz_theme'
html_theme_options = {
    'logo': 'logo_horizontal.svg',
    'include_logo_text': False,
    'favicon': 'favicon.ico',
    'primary_color': '#266498',
    'primary_color_dark': '#1b486e',
    'second_nav': True,
    'custom_css': 'custom.css',
}

_NAV =  (
    ('Getting Started', 'getting_started/index'),
    ('User Guide', 'user_guide/index'),
    ('Reference Gallery', 'reference/index'),
    ('Topics',  'topics'),
    ('Developer Guide', 'developer_guide/index'),
    ('About', 'about')
)

extensions += ['nbsite.gallery']

nbsite_gallery_conf = {
    'github_org': 'holoviz',
    'github_project': 'hvplot',
    'galleries': {
        'reference': {
            'title': 'Reference Gallery',
            'intro': (
                'Incomplete Reference Gallery containing some small '
                'examples of different plot types.'),
            'sections': [
                'pandas',
                'geopandas',
                'xarray',
            ]
        }
    },
}


html_context.update({
    'PROJECT': project,
    'DESCRIPTION': description,
    'AUTHOR': authors,
    # canonical URL (for search engines); can ignore for local builds
    'WEBSITE_SERVER': 'https://hvplot.holoviz.org',
    'VERSION': version,
    'GOOGLE_ANALYTICS_UA': 'UA-154795830-5',
    'NAV': _NAV,
    'LINKS': _NAV,
    'SOCIAL': (
        ('Gitter', '//gitter.im/pyviz/pyviz'),
        ('Github', '//github.com/holoviz/hvplot'),
    )
})
