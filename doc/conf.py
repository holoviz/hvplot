# -*- coding: utf-8 -*-
import param

param.parameterized.docstring_signature = False
param.parameterized.docstring_describe_params = False

from nbsite.shared_conf import *

project = u'hvPlot'
authors = u'HoloViz developers'
copyright = u'2018-2022 ' + authors
description = 'A high-level plotting API for the PyData ecosystem built on HoloViews'

import hvplot
version = release = base_version(hvplot.__version__)

nbbuild_cell_timeout = 600

html_static_path += ['_static']
templates_path = ['_templates']

html_css_files = [
    'nbsite.css',
    'custom.css'
]

html_theme_options = {
    "github_url": "https://github.com/holoviz/hvplot",
    "icon_links": [
        {
            "name": "Twitter",
            "url": "https://twitter.com/HoloViews",
            "icon": "fab fa-twitter-square",
        },
        {
            "name": "Discourse",
            "url": "https://discourse.holoviz.org/",
            "icon": "fab fa-discourse",
        },
    ],
    "footer_items": [
        "copyright",
        "last-updated",
    ],
    "google_analytics_id": "UA-154795830-5",
}

html_theme = "pydata_sphinx_theme"
html_logo = "_static/logo_horizontal.svg"
html_favicon = "_static/favicon.ico"

extensions += [
    'nbsite.gallery',
    'sphinx_copybutton',
]
napoleon_numpy_docstring = True

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
    "github_user": "holoviz",
    "github_repo": "panel",
})

# Override the Sphinx default title that appends `documentation`
html_title = f'{project} v{version}'
# Format of the last updated section in the footer
html_last_updated_fmt = '%Y-%m-%d'
