import os
import sys

# To include the local extension.
sys.path.insert(0, os.path.abspath('_ext'))

import os
import param
import pydata_sphinx_theme

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

# Useful for SEO on a versioned site
html_baseurl = 'https://hvplot.holoviz.org/en/docs/latest/'

exclude_patterns = ['governance', 'reference']

html_static_path += ['_static']  # noqa

if pydata_sphinx_theme.__version__ == '0.16.1':
    # See https://github.com/pydata/pydata-sphinx-theme/issues/2088
    templates_path.append('_static/patch_templates')  # noqa

html_css_files += ['custom.css']  # noqa

html_js_files = [
    'https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.4/require.min.js',
]
switcher_version = (
    os.getenv('VERSION') or 'dev'
    if any(pr in hvplot.__version__ for pr in ('a', 'b', 'rc', 'dev'))
    else version
)
html_theme_options.update(  # noqa
    {
        'navbar_start': ['navbar-logo', 'version-switcher'],
        'use_edit_page_button': True,
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
        'pygments_dark_style': 'material',
        'announcement': "hvPlot 0.12 has just been released! Checkout the <a href='https://blog.holoviz.org/posts/hvplot_release_0.12/'>blog post</a> and support hvPlot by giving it a 🌟 on <a href='https://github.com/holoviz/hvplot'>Github</a>.",
        'switcher': {
            'json_url': 'https://hvplot.holoviz.org/switcher.json',
            'version_match': switcher_version,
        },
        'show_version_warning_banner': True,
    }
)

# Without this .txt is appended to the files
html_sourcelink_suffix = ''

html_theme = 'pydata_sphinx_theme'
html_logo = '_static/logo_horizontal.svg'
html_favicon = '_static/favicon.ico'

extensions += [  # noqa
    'sphinx.ext.autosummary',
    'nbsite.gallery',
    'nbsite.analytics',
    'nbsite.nb_interactivity_warning',
    'sphinx_copybutton',
    'sphinxext.rediraffe',
    'numpydoc',
    'sphinxcontrib.mermaid',
    'sphinx.ext.intersphinx',
    # Custom extensions
    'backend_styling_options',
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
        'gallery': {
            'title': 'Gallery',
            'intro': (
                'Explore a curated set of example visualizations using hvPlot '
                'with different backends and datasets. For more examples using '
                'hvPlot and other HoloViz tools to solve real world problems, '
                'see the '
                '`HoloViz Examples website <https://examples.holoviz.org>`_.'
            ),
            'sections': [
                {
                    'path': 'basic-charts',
                    'title': 'Basic Charts',
                },
                'categorical',
                'multidimensional',
                'statistical',
                {
                    'path': 'time-series',
                    'title': 'Time Series',
                },
                'geospatial',
                'interactivity',
            ],
            'skip_rst_notebook_directive': True,
            'no_image_thumb': True,
            'titles_from_files': True,
            'card_title_below': True,
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
    # Integrations user guide moved to the reference
    'user_guide/integrations': 'ref/data_libraries',
    # Customizations user guide moved to the reference
    'user_guide/Customization': 'ref/plotting_options/index',
    # Pandas API viz user guide moved to the reference
    'user_guide/pandas_api': 'ref/api_compatibility/pandas/Pandas_API',
}

html_extra_path = ['topics.html']

html_context.update(  # noqa
    {
        'last_release': f'v{release}',
        'default_mode': 'light',
        # Useful for the edit button
        'github_user': 'holoviz',
        'github_repo': 'hvplot',
        'github_version': 'main',
        'doc_path': 'doc',
    }
)

# linkcheck
linkcheck_ignore = [r'https://github.com/holoviz/hvplot/pull/\d+']

# mystnb
nb_execution_excludepatterns = [
    'user_guide/Streaming.ipynb',
]
# cell execution timeout in seconds (-1 to ignore, 30 by default)
nb_execution_timeout = 240

if os.getenv('HVPLOT_EXECUTE_NBS_USER_GUIDE') in ('False', 'false', '0'):
    nb_execution_excludepatterns.append('user_guide/**/*.ipynb')

if os.getenv('HVPLOT_EXECUTE_NBS_TUTORIALS') in ('False', 'false', '0'):
    nb_execution_excludepatterns.append('tutorials/**/*.ipynb')

if os.getenv('HVPLOT_EXECUTE_NBS') in ('False', 'false', '0'):
    nb_execution_mode = 'off'

# We replace the automatically generated stub files by notebooks
# that include the API ref and some examples.
autosummary_generate = True
# autosummary_generate_overwrite = False

intersphinx_mapping = {
    'cartopy': ('https://scitools.org.uk/cartopy/docs/latest/', None),
    'holoviews': ('https://holoviews.org/', None),
    'pandas': (
        'https://pandas.pydata.org/pandas-docs/stable/',
        'https://pandas.pydata.org/pandas-docs/stable/objects.inv',
    ),
    'panel': ('https://panel.holoviz.org/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'xarray': ('https://docs.xarray.dev/en/stable/', None),
    'pyproj': ('https://pyproj4.github.io/pyproj/stable/', None),
}

# To avoid this warning
# hvplot/ui.py:docstring of hvplot.ui.hvPlotExplorer:43: WARNING: autosummary: stub file not found 'hvplot.ui.hvPlotExplorer.hvplot'. Check your autosummary_generate setting.
# See https://stackoverflow.com/a/73294408
numpydoc_class_members_toctree = False

numpydoc_show_inherited_class_members = False
numpydoc_class_members_toctree = False
