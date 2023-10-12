import holoviews as hv

from packaging.version import Version


collect_ignore_glob = []


# 2023-10: https://github.com/holoviz/hvplot/pull/1164
if Version(hv.__version__) == Version("1.18.0a6"):
    collect_ignore_glob += [
        "reference/xarray/contourf.ipynb",
        "user_guide/Geographic_Data.ipynb",
    ]
