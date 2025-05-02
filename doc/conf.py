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

exclude_patterns = ['governance']

html_static_path += ['_static']  # noqa

if pydata_sphinx_theme.__version__ == '0.16.1':
    # See https://github.com/pydata/pydata-sphinx-theme/issues/2088
    templates_path.append('_static/patch_templates')  # noqa

html_css_files += ['custom.css']  # noqa

html_js_files = [
    'https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.4/require.min.js',
]

html_theme_options.update(  # noqa
    {
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
        # 'announcement': "hvPlot 0.11 has just been released! Checkout the <a href='https://blog.holoviz.org/posts/hvplot_release_0.11/'>blog post</a> and support hvPlot by giving it a 🌟 on <a href='https://github.com/holoviz/hvplot'>Github</a>.",
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
        'reference': {
            'title': 'Reference Gallery',
            'intro': (
                'Find the list of supported libraries on `this page <../ref/data_libraries.html>`_.'
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

# We replace the automatically generated stub files by notebooks
# that include the API ref and some examples.
autosummary_generate = True
# autosummary_generate_overwrite = False

intersphinx_mapping = {
    'holoviews': ('https://holoviews.org/', None),
    'pandas': (
        'https://pandas.pydata.org/pandas-docs/stable/',
        'https://pandas.pydata.org/pandas-docs/stable/objects.inv',
    ),
    'panel': ('https://panel.holoviz.org/', None),
}
# See https://docs.readthedocs.com/platform/stable/guides/intersphinx.html
intersphinx_disabled_reftypes = ['*']

# To avoid this warning
# hvplot/ui.py:docstring of hvplot.ui.hvPlotExplorer:43: WARNING: autosummary: stub file not found 'hvplot.ui.hvPlotExplorer.hvplot'. Check your autosummary_generate setting.
# See https://stackoverflow.com/a/73294408
numpydoc_class_members_toctree = False

numpydoc_show_inherited_class_members = False
numpydoc_class_members_toctree = False
