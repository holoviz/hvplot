import subprocess
import sys

from hvplot.util import _in_ipython


def run_script(script, env_vars=None):
    process = subprocess.run(
        [sys.executable, '-c', script],
        text=True,
        capture_output=True,
        env=env_vars or {},
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
