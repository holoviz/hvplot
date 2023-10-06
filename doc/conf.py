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

html_css_files += [
    'custom.css'
]

html_js_files = [
    'https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.4/require.min.js',
]

html_theme_options.update({
    "github_url": "https://github.com/holoviz/hvplot",
    "icon_links": [
        {
            "name": "Twitter",
            "url": "https://twitter.com/HoloViews",
            "icon": "fa-brands fa-twitter-square",
        },
        {
            "name": "Discourse",
            "url": "https://discourse.holoviz.org/c/hvplot",
            "icon": "fa-brands fa-discourse",
        },
        {
            "name": "Discord",
            "url": "https://discord.gg/AXRHnJU6sP",
            "icon": "fa-brands fa-discord",
        },
    ],
    "analytics": {"google_analytics_id": "G-FV5FQGDK24"},
    "pygment_dark_style": "material",
})

html_theme = "pydata_sphinx_theme"
html_logo = "_static/logo_horizontal.svg"
html_favicon = "_static/favicon.ico"

extensions += [
    'nbsite.gallery',
    'sphinx_copybutton',
]

myst_enable_extensions = ["colon_fence"]

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
    "default_mode": "light",
})
