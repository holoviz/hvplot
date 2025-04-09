import os
import sys

# To include the local extension.
sys.path.insert(0, os.path.abspath('_ext'))

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
switcher_version = os.getenv(
    'VERSION',
    'dev' if any(pr in hvplot.__version__ for pr in ('a', 'b', 'rc', 'dev')) else version,
)
html_theme_options.update(  # noqa
    {
        'navbar_start': ['navbar-logo', 'version-switcher'],
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
        # 'announcement': "hvPlot 0.11 has just been released! Checkout the <a href='https://blog.holoviz.org/posts/hvplot_release_0.11/'>blog post</a> and support hvPlot by giving it a 🌟 on <a href='https://github.com/holoviz/hvplot'>Github</a>.",
        'switcher': {
            # 'json_url': 'http://127.0.0.1:5500/_static/switcher.json',
            # 'json_url': 'https://s3.us-east-1.amazonaws.com/hvplot.holoviz.org/en/docs/latest/_static/switcher.json',
            'json_url': 'https://hvplot-test.holoviz.org/en/docs/latest/_static/switcher.json',
            'version_match': switcher_version,
        },
    }
)

html_theme = 'pydata_sphinx_theme'
html_logo = '_static/logo_horizontal.svg'
html_favicon = '_static/favicon.ico'

extensions += [  # noqa
    'nbsite.gallery',
    'nbsite.analytics',
    'nbsite.nb_interactivity_warning',
    'sphinx_copybutton',
    'sphinxext.rediraffe',
    'numpydoc',
    # Custom extensions
    'plotting_options_table',
]

myst_enable_extensions = [
    # To also use ::: delimiters to denote directives, instead of ```.
    'colon_fence',
    # MySt-Parser will attempt to convert any isolated img tags (i.e. not
    # wrapped in any other HTML) to the internal representation used in sphinx.
    'html_image',
]

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
    'developer_guide/testing': 'developer_guide',
    # Removal of the developer_guide folder
    'developer_guide/index': 'developer_guide',
    # Redirecting removed "getting started" pages to the new location
    'getting_started/index': 'tutorials/index',
    'getting_started/explorer': 'tutorials/getting_started',
    'getting_started/hvplot': 'tutorials/getting_started',
    'getting_started/installation': 'tutorials/getting_started',
    'getting_started/interactive': 'tutorials/getting_started',
}

html_context.update(  # noqa
    {
        'last_release': f'v{release}',
        'github_user': 'holoviz',
        'github_repo': 'hvplot',
        'default_mode': 'light',
    }
)

# mystnb
nb_execution_excludepatterns = [
    'user_guide/Streaming.ipynb',
]
# cell execution timeout in seconds (-1 to ignore, 30 by default)
nb_execution_timeout = 240

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
    exclude_patterns.append('reference')
    nb_execution_excludepatterns.append('reference/**/*.ipynb')

if os.getenv('HVPLOT_EXECUTE_NBS_USER_GUIDE') in ('False', 'false', '0'):
    nb_execution_excludepatterns.append('user_guide/**/*.ipynb')

if os.getenv('HVPLOT_EXECUTE_NBS_TUTORIALS') in ('False', 'false', '0'):
    nb_execution_excludepatterns.append('tutorials/**/*.ipynb')

if os.getenv('HVPLOT_EXECUTE_NBS') in ('False', 'false', '0'):
    nb_execution_mode = 'off'
