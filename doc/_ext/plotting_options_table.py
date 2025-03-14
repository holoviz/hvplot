"""
Sphinx extension to display a table with the options of a specific
options group of the converter.

Usage:

.. plotting-options-table:: Style Options
"""

import sys

from contextlib import contextmanager
from textwrap import indent

from hvplot.converter import HoloViewsConverter
from numpydoc.docscrape import NumpyDocString, Parameter
from sphinx.util.docutils import SphinxDirective


EXTRA_OPTIONS = list(HoloViewsConverter._docstring_sections.values())


def _parse(self):
    self._doc.reset()
    self._parse_summary()

    sections = list(self._read_sections())
    section_names = {section for section, content in sections}

    has_returns = 'Returns' in section_names
    has_yields = 'Yields' in section_names
    # We could do more tests, but we are not. Arbitrarily.
    if has_returns and has_yields:
        msg = 'Docstring contains both a Returns and Yields section.'
        raise ValueError(msg)
    if not has_yields and 'Receives' in section_names:
        msg = 'Docstring contains a Receives section but not Yields.'
        raise ValueError(msg)

    for section, content in sections:
        if not section.startswith('..'):
            section = (s.capitalize() for s in section.split(' '))
            section = ' '.join(section)
            if self.get(section):
                self._error_location(
                    'The section %s appears twice in  %s'  # noqa
                    % (section, '\n'.join(self._doc._str))  # noqa
                )

        # Patch is here, extending the sections with these other options
        if section in ('Parameters', 'Other Parameters', 'Attributes', 'Methods') + tuple(
            EXTRA_OPTIONS
        ):
            self[section] = self._parse_param_list(content)
        elif section in ('Returns', 'Yields', 'Raises', 'Warns', 'Receives'):
            self[section] = self._parse_param_list(content, single_element_is_type=True)
        elif section.startswith('.. index::'):
            self['index'] = self._parse_index(section, content)
        elif section == 'See Also':
            self['See Also'] = self._parse_see_also(content)
        else:
            self[section] = content


@contextmanager
def patch_numpy_docstring():
    old_parse = NumpyDocString._parse
    old_sections = NumpyDocString.sections
    NumpyDocString._parse = _parse
    # Extend
    for option_group in EXTRA_OPTIONS:
        NumpyDocString.sections[option_group] = []
    try:
        yield
    finally:
        NumpyDocString._parse = old_parse
        NumpyDocString.sections = old_sections


def get_group_parameters(option_group: str) -> list[Parameter]:
    with patch_numpy_docstring():
        cdoc = NumpyDocString(HoloViewsConverter.__doc__)
        return cdoc[option_group]


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
        parameters = get_group_parameters(options_group)
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


if __name__ == '__main__':
    group = ' '.join(sys.argv[1:])
    opts = get_group_parameters(group)
    breakpoint()
    print(opts)
