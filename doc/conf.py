import param

param.parameterized.docstring_signature = False
param.parameterized.docstring_describe_params = False

from nbsite.shared_conf import *

project = 'hvPlot'
authors = 'HoloViz developers'
copyright_years['start_year'] = '2016'
copyright = copyright_fmt.format(**copyright_years)
description = 'A high-level plotting API for the PyData ecosystem built on HoloViews'

import hvplot
version = release  = base_version(hvplot.__version__)
nbbuild_cell_timeout = 600

html_static_path += ['_static']
templates_path += ['_templates']

html_css_files = [
    'nbsite.css',
    'custom.css'
]

html_theme_options.update({
    "github_url": "https://github.com/holoviz/hvplot",
    "icon_links": [
        {
            "name": "Twitter",
            "url": "https://twitter.com/HoloViews",
            "icon": "fab fa-twitter-square",
        },
        {
            "name": "Discourse",
            "url": "https://discourse.holoviz.org/c/hvplot",
            "icon": "fab fa-discourse",
        },
    ],
    "google_analytics_id": "UA-154795830-5",
})

html_theme = "pydata_sphinx_theme"
html_logo = "_static/logo_horizontal.svg"
html_favicon = "_static/favicon.ico"

extensions += [
    'nbsite.gallery',
    'sphinx_copybutton',
]

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
    "last_release": f"v{release}",
    "github_user": "holoviz",
    "github_repo": "panel",
})
