"""
Sphinx extension to display a table with the options of a specific
options group of the converter. Requires numpydoc

Usage:

.. plotting-options-table:: Style Options
"""

import sys
from textwrap import indent

from sphinx.util.docutils import SphinxDirective

from hvplot.util import _get_docstring_group_parameters

# Deprecated options that have no definition section to link to
OPTIONS_WITHOUT_DEFINITION = {'hover_formatters'}


def option_label(name):
    """Label of an option definition, e.g. 'xlim/ylim' -> 'option-xlim__ylim'."""
    return 'option-' + name.replace('/', '__')


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
        table_rst = [
            '.. list-table::',
            '   :header-rows: 1',
            '   :widths: 25 70',
            '   :class: plotting-options-table',
            '',
        ]
        table_rst.append('   * - ')
        table_rst.append('       Parameters')
        table_rst.append('     - ')
        table_rst.append('       Description')

        for param in parameters:
            if param.name in OPTIONS_WITHOUT_DEFINITION:
                name = f'**{param.name}**'
            else:
                # A role cannot be nested in **bold**, custom.css makes the link bold
                name = f':ref:`{param.name} <{option_label(param.name)}>`'
            desc = '\n'.join(param.desc)
            table_rst.append('   * - ')
            table_rst.append(f'       {name} *({param.type})*')
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
