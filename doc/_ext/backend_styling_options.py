from docutils import nodes
from docutils.statemachine import StringList
from sphinx.util.docutils import SphinxDirective

import holoviews as hv

from hvplot.util import _get_backend_style_options


hv.extension('bokeh', 'matplotlib')


class BackendStylingOptionsDirective(SphinxDirective):
    """
    Display the Bokeh and Matplotlib styling options for a plot method
    in a tabs layout.

    .. backend-styling-options:: scatter
    """

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True

    def run(self):
        input_string = self.arguments[0]

        bk_opts = _get_backend_style_options(input_string, 'bokeh')
        mpl_opts = _get_backend_style_options(input_string, 'matplotlib')
        bk_opts_info = ', '.join(bk_opts)
        mpl_opts_info = ', '.join(mpl_opts)
        # Sphinx-design syntax
        tab_content = f"""
.. tab-set::

    .. tab-item:: Bokeh

        {bk_opts_info}

    .. tab-item:: Matplotlib

        {mpl_opts_info}
"""

        container = nodes.container()
        container['classes'] = ['backend-styling-options-container']
        content_list = StringList(tab_content.splitlines(), source='')
        self.state.nested_parse(content_list, 0, container)
        return container.children


def setup(app):
    app.add_directive('backend-styling-options', BackendStylingOptionsDirective)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
