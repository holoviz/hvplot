import os
import param

param.parameterized.docstring_signature = False
param.parameterized.docstring_describe_params = False

import hvplot  # noqa
from nbsite.shared_conf import *  # noqa

project = 'hvPlot'
authors = 'HoloViz developers'
copyright_years['start_year'] = '2016'  # noqa
copyright = copyright_fmt.format(**copyright_years)  # noqa
description = 'A high-level plotting API for the PyData ecosystem built on HoloViews'

version = release = base_version(hvplot.__version__)  # noqa
nbbuild_cell_timeout = 600

exclude_patterns = ['governance']

html_static_path += ['_static']  # noqa

html_css_files += ['custom.css']  # noqa

html_js_files = [
    'https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.4/require.min.js',
]

html_theme_options.update(  # noqa
    {
        'github_url': 'https://github.com/holoviz/hvplot',
        'icon_links': [
            {
                'name': 'Twitter',
                'url': 'https://twitter.com/HoloViews',
                'icon': 'fa-brands fa-twitter-square',
            },
            {
                'name': 'Discourse',
                'url': 'https://discourse.holoviz.org/c/hvplot',
                'icon': 'fa-brands fa-discourse',
            },
            {
                'name': 'Discord',
                'url': 'https://discord.gg/AXRHnJU6sP',
                'icon': 'fa-brands fa-discord',
            },
        ],
        'pygment_dark_style': 'material',
        'announcement': "hvPlot 0.10 has just been released! Checkout the <a href='https://blog.holoviz.org/posts/hvplot_release_0.10/'>blog post</a> and support hvPlot by giving it a 🌟 on <a href='https://github.com/holoviz/hvplot'>Github</a>.",
    }
)

html_theme = 'pydata_sphinx_theme'
html_logo = '_static/logo_horizontal.svg'
html_favicon = '_static/favicon.ico'

extensions += [  # noqa
    'nbsite.gallery',
    'nbsite.analytics',
    'sphinx_copybutton',
    'sphinxext.rediraffe',
]

myst_enable_extensions = ['colon_fence']

nbsite_gallery_conf = {
    'github_org': 'holoviz',
    'github_project': 'hvplot',
    'examples_dir': '.',
    'galleries': {
        'reference': {
            'title': 'Reference Gallery',
            'intro': (
                'Find the list of supported libraries on the `Integrations <../user_guide/Integrations.html>`_ page.'
            ),
            'sections': [
                'tabular',
                'geopandas',
                'xarray',
            ],
            'skip_rst_notebook_directive': True,
        }
    },
    'thumbnail_url': 'https://assets.holoviz.org/hvplot/thumbnails',
}

nbsite_analytics = {
    'goatcounter_holoviz': True,
}

rediraffe_redirects = {
    # Removal of the developer testing page
    'developer_guide/testing': 'developer_guide/index',
}

html_context.update(  # noqa
    {
        'last_release': f'v{release}',
        'github_user': 'holoviz',
        'github_repo': 'panel',
        'default_mode': 'light',
    }
)

# mystnb
nb_execution_excludepatterns = [
    'user_guide/Streaming.ipynb',
]

if os.getenv('HVPLOT_REFERENCE_GALLERY') not in ('False', 'false', '0'):
    rediraffe_redirects.update(
        {
            # When the pandas section was renamed tabular:
            'reference/pandas/andrewscurves': 'reference/tabular/andrewscurves',
            'reference/pandas/area': 'reference/tabular/area',
            'reference/pandas/bar': 'reference/tabular/bar',
            'reference/pandas/barh': 'reference/tabular/barh',
            'reference/pandas/bivariate': 'reference/tabular/bivariate',
            'reference/pandas/box': 'reference/tabular/box',
            'reference/pandas/errorbars': 'reference/tabular/errorbars',
            'reference/pandas/heatmap': 'reference/tabular/heatmap',
            'reference/pandas/hexbin': 'reference/tabular/hexbin',
            'reference/pandas/hist': 'reference/tabular/hist',
            'reference/pandas/kde': 'reference/tabular/kde',
            'reference/pandas/labels': 'reference/tabular/labels',
            'reference/pandas/lagplot': 'reference/tabular/lagplot',
            'reference/pandas/line': 'reference/tabular/line',
            'reference/pandas/ohlc': 'reference/tabular/ohlc',
            'reference/pandas/parallelcoordinates': 'reference/tabular/parallelcoordinates',
            'reference/pandas/scatter': 'reference/tabular/scatter',
            'reference/pandas/scattermatrix': 'reference/tabular/scattermatrix',
            'reference/pandas/step': 'reference/tabular/step',
            'reference/pandas/table': 'reference/tabular/table',
            'reference/pandas/violin': 'reference/tabular/violin',
        }
    )
else:
    if 'nbsite.gallery' in extensions:
        extensions.remove('nbsite.gallery')
    exclude_patterns.append('doc/reference')
    nb_execution_excludepatterns.append('doc/reference/**/*.ipynb')
