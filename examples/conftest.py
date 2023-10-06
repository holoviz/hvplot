import holoviews as hv

from packaging.version import Version


collect_ignore_glob = []


# 2023-10: https://github.com/holoviz/hvplot/pull/1164
if Version(hv.__version__) == Version("1.18.0a4"):
    collect_ignore_glob += [
        "reference/xarray/contourf.ipynb",
        "user_guide/Geographic_Data.ipynb",
    ]


def pytest_runtest_makereport(item, call):
    """
    Skip tests that fail because "the kernel died before replying to kernel_info"
    or "Kernel didn't respond in 60 seconds",
    these are common errors when running the example tests in CI.

    Inspired from: https://stackoverflow.com/questions/32451811

    """
    from _pytest.runner import pytest_runtest_makereport

    tr = pytest_runtest_makereport(item, call)

    if call.excinfo is not None:
        msgs = [
            "Kernel died before replying to kernel_info",
            "Kernel didn't respond in 60 seconds",
        ]
        for msg in msgs:
            if call.excinfo.type == RuntimeError and call.excinfo.value.args[0] in msg:
                tr.outcome = "skipped"
                tr.wasxfail = f"reason: {msg}"

    return tr
