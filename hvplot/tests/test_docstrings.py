import itertools
import os
import subprocess
import sys

import pytest

pytest.importorskip('numpydoc')

from hvplot.converter import HoloViewsConverter
from hvplot.util import (
    _get_docstring_group_parameters,
    _in_ipython,
    _parse_docstring_sections,
    _PatchHvplotDocstrings,
)


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


def run_script(script, env_vars=None):
    env_vars = env_vars or {}
    process = subprocess.run(
        [sys.executable, '-c', script],
        text=True,
        capture_output=True,
        env=os.environ | env_vars,
        check=False,
    )
    if process.returncode != 0:
        raise RuntimeError(f'Subprocess failed: {process.stderr}')
    return process.stdout.strip()


@pytest.mark.slow
def test_no_automatic_patching():
    script = """
import inspect
from hvplot import hvPlot

print(inspect.signature(hvPlot.line))
"""
    assert not _in_ipython()
    out = run_script(script)
    assert out == '(self, x=None, y=None, **kwds)'


@pytest.mark.slow
def test_no_automatic_patching_extension_import():
    script = """
import inspect
import hvplot.pandas

print(inspect.signature(hvplot.hvPlot.line))
"""
    assert not _in_ipython()
    out = run_script(script)
    assert out == '(self, x=None, y=None, **kwds)'


@pytest.mark.slow
def test_patching_env_var():
    script = """
import inspect
from hvplot import hvPlot

print(inspect.signature(hvPlot.line))
"""
    assert not _in_ipython()
    out = run_script(script, {'HVPLOT_PATCH_PLOT_DOCSTRING_SIGNATURE': 'true'})
    assert out != '(self, x=None, y=None, **kwds)'
    assert 'xlim' in out


def test_patch_hvplot_docstrings():
    patchd = _PatchHvplotDocstrings()
    assert patchd.orig
    try:
        patchd()
        for (cls, _kind), (osig, odoc) in patchd.orig.items():
            obj = getattr(cls, _kind)
            assert obj.__signature__ != osig
            assert obj.__doc__ != odoc
    finally:
        patchd.reset()
    for (cls, _kind), (osig, odoc) in patchd.orig.items():
        obj = getattr(cls, _kind)
        assert obj.__signature__ == osig
        assert obj.__doc__ == odoc


def test_converter_docstrings_sections():
    sections = _parse_docstring_sections(HoloViewsConverter.__doc__)
    assert set(sections) == set(HoloViewsConverter._docstring_sections.values())


def test_converter_options_docstrings():
    assert (
        HoloViewsConverter._docstring_sections.keys() == HoloViewsConverter._options_groups.keys()
    )
