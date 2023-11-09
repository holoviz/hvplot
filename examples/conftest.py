import numpy as np

from packaging.version import Version


collect_ignore_glob = []

# 2023-11: Newer version of numpy renames amin/amax to min/max
# This can be removed when we drop Python 3.8 support
if Version(np.__version__) < Version("1.26"):
    collect_ignore_glob += [
        "user_guide/Plotting*.ipynb",
    ]
