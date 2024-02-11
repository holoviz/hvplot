collect_ignore_glob = []

try:
    import pygraphviz
except ModuleNotFoundError:
    collect_ignore_glob += [
        "user_guide/NetworkX.ipynb",
    ]
