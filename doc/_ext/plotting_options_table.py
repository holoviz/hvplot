"""
Sphinx extension to display a table with the options of a specific
options group of the converter. Requires numpydoc

Usage:

.. plotting-options-table:: Style Options
"""

import sys

from textwrap import indent

from hvplot.util import _get_docstring_group_parameters
from sphinx.util.docutils import SphinxDirective


class PlottingOptionsTableDirective(SphinxDirective):
    """
    Directive to display a plotting option group in a Markdown table.

    .. plotting-options-table:: Data Options
    """

    required_arguments = 1
    final_argument_whitespace = True

    def run(self):
        # Get the key passed to the directive
        options_group = self.arguments[0]
        parameters = _get_docstring_group_parameters(options_group)
        table_rst = ['.. list-table::', '   :header-rows: 1', '   :widths: 25 70', '']
        table_rst.append('   * - ')
        table_rst.append('       Parameters')
        table_rst.append('     - ')
        table_rst.append('       Description')

        for param in parameters:
            desc = '\n'.join(param.desc)
            table_rst.append('   * - ')
            table_rst.append(f'       **{param.name}** *({param.type})*')
            table_rst.append('     - ')
            table_rst.append(indent(desc, ' ' * 7))

        raw_rst = '\n'.join(table_rst)

        parsed = self.parse_text_to_nodes(raw_rst)
        return parsed


def setup(app):
    app.add_directive('plotting-options-table', PlottingOptionsTableDirective)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }


if __name__ == '__main__':
    group = ' '.join(sys.argv[1:])
    opts = _get_docstring_group_parameters(group)
    print(opts)
