import os
import subprocess
import sys

from hvplot.converter import HoloViewsConverter
from hvplot.util import _PatchHvplotDocstrings, _in_ipython, _parse_docstring_sections


def run_script(script, env_vars=None):
    env_vars = env_vars or {}
    process = subprocess.run(
        [sys.executable, '-c', script],
        text=True,
        capture_output=True,
        env=os.environ | env_vars,
    )
    if process.returncode != 0:
        raise RuntimeError(f'Subprocess failed: {process.stderr}')
    return process.stdout.strip()


def test_no_automatic_patching():
    script = """
import inspect
from hvplot import hvPlot

print(inspect.signature(hvPlot.line))
"""
    assert not _in_ipython()
    out = run_script(script)
    assert out == '(self, x=None, y=None, **kwds)'


def test_no_automatic_patching_extension_import():
    script = """
import inspect
import hvplot.pandas

print(inspect.signature(hvplot.hvPlot.line))
"""
    assert not _in_ipython()
    out = run_script(script)
    assert out == '(self, x=None, y=None, **kwds)'


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
