import itertools

import pytest

pytest.importorskip('numpydoc')

from hvplot.converter import HoloViewsConverter  # noqa: E402
from hvplot.util import _get_docstring_group_parameters  # noqa: E402


@pytest.mark.parametrize('section', HoloViewsConverter._docstring_sections.values())
def test_docstring_converter_sections_present(section):
    assert section in HoloViewsConverter.__doc__


@pytest.mark.parametrize('section', HoloViewsConverter._docstring_sections.values())
def test_docstring_converter_sections_include_parameters(section):
    assert _get_docstring_group_parameters(section)


def parse_docstring_for_param_names(section_title):
    parameters = _get_docstring_group_parameters(section_title)
    parameter_names = []
    for param in parameters:
        sparams = param.name.split('/')
        parameter_names.extend(sparams)
    return parameter_names


@pytest.mark.parametrize(
    'section, options',
    [(k, v) for k, v in HoloViewsConverter._options_groups.items()],
)
def test_docstring_converter_options_match_per_section(section, options):
    section_title = HoloViewsConverter._docstring_sections[section]
    parameter_names = parse_docstring_for_param_names(section_title)
    assert set(options) == set(parameter_names)


def test_docstring_converter_no_duplicate_and_match_options():
    all_doc_params = []
    for section_title in HoloViewsConverter._docstring_sections.values():
        params = parse_docstring_for_param_names(section_title)
        all_doc_params.extend(params)

    assert len(all_doc_params) == len(set(all_doc_params))

    all_options = list(itertools.chain(*HoloViewsConverter._options_groups.values()))

    assert len(all_options) == len(set(all_options))

    assert set(all_doc_params) == set(all_options)
