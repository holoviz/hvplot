"""
Experimental support for fugue.
"""

from typing import Any

import panel as _pn

from . import hvPlotTabular, post_patch, _module_extensions
from .util import _fugue_ipython


def patch(name='hvplot', extension='bokeh', logo=False):
    try:
        from fugue import DataFrames, Outputter
        from fugue.extensions import namespace_candidate, parse_outputter
    except ImportError:
        raise ImportError(
            'Could not add fugue support as it could not be imported. '
            'Please make sure you have installed fugue in your environment.'
        )

    import hvplot.pandas  # noqa: F401

    class _Visualize(Outputter):
        def __init__(self, func: str) -> None:
            super().__init__()
            self._func = func
            getattr(hvPlotTabular, func)  # ensure the func exists

        def process(self, dfs: DataFrames) -> None:
            """
            Process the dataframes and output the result as
            a pn.Column.

            Parameters:
            -----------
            dfs: fugue.DataFrames
            """
            charts = []
            for df in dfs.values():
                params = dict(self.params)
                opts: dict[str, Any] = params.pop('opts', {})
                chart = getattr(df.as_pandas().hvplot, self._func)(**params).opts(**opts)
                charts.append(chart)
            col = _pn.Column(*charts)
            try:
                if not _fugue_ipython:
                    get_ipython()
            except NameError:
                col.show()  # in script
            else:
                from IPython.display import display

                display(col)  # in notebook

    if 'hvplot.fugue' not in _module_extensions:

        @parse_outputter.candidate(namespace_candidate(name, lambda x: isinstance(x, str)))
        def _parse_hvplot(obj: tuple[str, str]) -> Outputter:
            return _Visualize(obj[1])

        _module_extensions.add('hvplot.fugue')

    post_patch(extension, logo)


patch()
